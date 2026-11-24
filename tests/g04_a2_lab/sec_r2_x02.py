"""SEC-R2-X02 initial C1/C1+C2 comparison, disposable DB only.

Trusted test control plane, not production broker. Fresh schemas and logins
per variant. No real network service, external effects or production DDL.
"""
from contextlib import contextmanager
from pathlib import Path
import os
import secrets
import time

import jwt
import psycopg
from psycopg import sql
from cryptography.hazmat.primitives.asymmetric import rsa
from rightware_si.g04_a1_lab import SyntheticVerifier, Snapshot, TrustKey, PROFILES, CredentialRejected

NOW=2000000000
LAB=Path(__file__).resolve().parents[2]/"database/labs/g04_a2"
BODY="synthetic:syn-task"


class Candidate:
    def __init__(self,case,variant):
        if variant not in ("c1","c2"):
            raise ValueError("unknown lab variant")
        if (os.getenv("GITHUB_ACTIONS")!="true"
                or os.getenv("RUNNER_ENVIRONMENT")!="github-hosted"
                or os.getenv("RW_SI_ENABLE_G04_A2_LAB")!="1"
                or case.admin.execute("SELECT current_database(),session_user").fetchone()
                    !=("rw_g04_a2_lab","g04_bootstrap")
                or case.admin.execute("SELECT marker FROM public.g04_ephemeral_marker").fetchall()
                    !=[(os.environ["RW_G04_A2_MARKER"],)]):
            raise RuntimeError("X02 guard refused")
        self.case=case
        self.db=case.admin
        self.variant=variant
        self.schema="x02_"+variant
        self.roles={p:self.schema+"_"+r for p,r in
                    (("syn-a","alpha"),("syn-b","beta"),("syn-s","service"))}
        self.passwords={p:secrets.token_hex(32) for p in self.roles}
        self.sink=[]
        self.keys={g:rsa.generate_private_key(public_exponent=65537,key_size=2048) for g in (1,2,3)}
        snap=Snapshot(NOW-1,NOW+59,tuple(TrustKey("syn-issuer-a","syn-key"+str(g),
            "AGENT",k.public_key(),g) for g,k in self.keys.items()))
        self.verifier=SyntheticVerifier(lambda:snap,lambda:NOW)
        self.setup()

    def q(self,statement,params=None):
        # Fixed test-only schema identifier, never request data.
        return self.db.execute(statement.replace("@s",self.schema),params)

    def setup(self):
        def translate(s):
            s=s.replace("g04_lab",self.schema)
            for p,r in (("syn-a","alpha"),("syn-b","beta"),("syn-s","service")):
                s=s.replace("g04_"+r,self.roles[p])
            return s
        schema=translate((LAB/"schema.sql").read_text())
        seed=translate((LAB/"seed.sql").read_text())
        # No edits to C0. Derive a candidate predicate with explicit persistent
        # lifecycle and identity presence. Reuse all other baseline predicates.
        target="JOIN "+self.schema+".principal a ON a.id=l.principal_id"
        insert=(target+"\n JOIN "+self.schema+".external_identity e ON e.principal_id=a.id AND e.kind=a.kind"
                +"\n JOIN "+self.schema+".lifecycle lc ON lc.principal_id=a.id AND lc.state='ACTIVE'")
        if schema.count(target)!=1:
            raise RuntimeError("baseline predicate changed")
        # Create lifecycle before function references it.
        pos=schema.index("CREATE FUNCTION "+self.schema+".permitted")
        lifecycle=translate("""
CREATE TABLE g04_lab.lifecycle (
 principal_id g04_lab.syn_id PRIMARY KEY REFERENCES g04_lab.principal(id),
 state text NOT NULL CHECK(state IN ('ACTIVE','REVOKING','REVOKED')),
 generation integer NOT NULL CHECK(generation>0)
);
ALTER TABLE g04_lab.resource_grant ADD COLUMN epoch integer NOT NULL DEFAULT 1 CHECK(epoch>0);
CREATE TABLE g04_lab.release_permit (
 id text PRIMARY KEY, principal_id g04_lab.syn_id REFERENCES g04_lab.principal(id),
 generation integer NOT NULL, resource_id g04_lab.syn_id NOT NULL,
 grant_epoch integer NOT NULL,
 status text NOT NULL CHECK(status IN ('RESERVED','ADMITTED','EMITTING','RELEASED','CANCELLED')),
 body text NOT NULL CHECK(body LIKE 'synthetic:%')
);
""")
        schema=(schema[:pos]+lifecycle+schema[pos:]).replace(target,insert)
        with self.db.transaction():
            self.case.assertEqual(self.db.execute("SELECT count(*) FROM pg_namespace WHERE nspname=%s",
                (self.schema,)).fetchone()[0],0)
            for p,role in self.roles.items():
                password=self.passwords[p]
                print("::add-mask::"+password,flush=True)
                self.db.execute(sql.SQL("CREATE ROLE {} LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE "
                    "NOREPLICATION NOBYPASSRLS NOINHERIT PASSWORD {}").format(
                    sql.Identifier(role),sql.Literal(password)))
                self.db.execute(sql.SQL("GRANT CONNECT ON DATABASE rw_g04_a2_lab TO {}").format(sql.Identifier(role)))
            self.db.execute("GRANT CREATE ON DATABASE rw_g04_a2_lab TO g04_owner")
            self.db.execute("SET LOCAL ROLE g04_owner")
            self.db.execute(schema)
            self.db.execute("RESET ROLE")
            self.db.execute("REVOKE CREATE ON DATABASE rw_g04_a2_lab FROM g04_owner")
            self.db.execute(seed)
            self.q("INSERT INTO @s.lifecycle SELECT id,'ACTIVE',1 FROM @s.principal")
        self.original=self.payload()
        print("SEC_R2_X02_SETUP variant="+self.variant+" isolated_schema=true",flush=True)

    def payload(self):
        return self.q("SELECT org_id,project_id,resource_id,owner_id,body FROM @s.payload ORDER BY resource_id").fetchall()

    def issue(self,g=1):
        return jwt.encode(dict(iss="syn-issuer-a",sub="syn-sub",aud=PROFILES["AGENT"][1],
            iat=NOW-5,nbf=NOW-5,exp=NOW+120,jti="syn-jti"+str(g),gen=g),
            self.keys[g],algorithm="RS256",headers={"typ":PROFILES["AGENT"][0],"kid":"syn-key"+str(g)})

    @contextmanager
    def login(self,p="syn-a",password=None):
        with psycopg.connect(host="127.0.0.1",port=55432,dbname="rw_g04_a2_lab",
            user=self.roles[p],password=self.passwords[p] if password is None else password,
            sslmode="disable",connect_timeout=5,autocommit=True) as c:
            self.case.assertEqual(c.execute("SELECT session_user,current_user").fetchone(),
                                  (self.roles[p],self.roles[p]))
            yield c

    def read(self,c,resource="syn-task",p="syn-a"):
        with c.transaction():
            c.execute("SET LOCAL statement_timeout='2000ms'")
            self.case.scope(c,*("syn-other","syn-beta") if p=="syn-b" else ("syn-rw","syn-alpha"))
            return c.execute(sql.SQL("SELECT body FROM {}.payload WHERE resource_id=%s").format(
                sql.Identifier(self.schema)),(resource,)).fetchall()

    def state(self):
        return self.q("SELECT state,generation FROM @s.lifecycle WHERE principal_id='syn-a'").fetchone()

    def lock_state(self):
        return self.q("SELECT state,generation FROM @s.lifecycle WHERE principal_id='syn-a' FOR UPDATE").fetchone()

    def grant(self):
        return self.q("SELECT active,epoch FROM @s.resource_grant WHERE principal_id='syn-a' "
                      "AND resource_id='syn-task' AND action='task:read' AND purpose='syn-work'").fetchone()

    def reserve(self,token):
        # Fixed exact fixture identity/action. Caller token supplies no role,
        # schema, resource grant, generation override or DB connection string.
        try:
            candidate=self.verifier.verify(token,"AGENT")
            with self.db.transaction():
                self.db.execute("SET LOCAL lock_timeout='1000ms'")
                state,g=self.lock_state()
                binding=self.q("SELECT principal_id FROM @s.external_identity WHERE issuer=%s "
                    "AND subject=%s AND kind=%s",(candidate.issuer,candidate.subject,candidate.kind)).fetchone()
                if state!="ACTIVE" or g!=candidate.generation or binding!=("syn-a",):
                    return None
                active,epoch=self.grant()
                if not active:
                    return None
                with self.login() as c:
                    rows=self.read(c)
                if rows!=[(BODY,)]:
                    return None
                if self.variant=="c1":
                    return rows[0][0]
                permit=secrets.token_hex(16)
                self.q("INSERT INTO @s.release_permit VALUES (%s,'syn-a',%s,'syn-task',%s,'RESERVED',%s)",
                       (permit,g,epoch,rows[0][0]))
                return permit
        except (CredentialRejected,psycopg.Error,RuntimeError):
            return None

    def admit(self,permit):
        with self.db.transaction():
            self.db.execute("SET LOCAL lock_timeout='1000ms'")
            state,g=self.lock_state()
            active,epoch=self.grant()
            if state!="ACTIVE" or not active:
                return False
            return self.q("UPDATE @s.release_permit SET status='ADMITTED' WHERE id=%s "
                "AND status='RESERVED' AND generation=%s AND grant_epoch=%s",
                (permit,g,epoch)).rowcount==1

    def emit(self,permit,uncertain=False):
        if self.variant=="c1":
            self.sink.append(permit.encode("utf-8"))
            return True
        # Persist an in-progress marker before irreversible local sink write.
        # If delivery outcome is unknown, leave EMITTING; never auto-retry.
        with self.db.transaction():
            state,g=self.lock_state()
            if state=="REVOKED":
                return False
            row=self.q("UPDATE @s.release_permit SET status='EMITTING' WHERE id=%s "
                "AND status='ADMITTED' RETURNING body",(permit,)).fetchone()
            if row is None:
                return False
        self.sink.append(row[0].encode("utf-8"))
        if uncertain:
            return False
        with self.db.transaction():
            self.lock_state()
            self.case.assertEqual(self.q("UPDATE @s.release_permit SET status='RELEASED' "
                "WHERE id=%s AND status='EMITTING'",(permit,)).rowcount,1)
        return True

    def revoke(self):
        with self.db.transaction():
            self.db.execute("SET LOCAL lock_timeout='1000ms'")
            state,g=self.lock_state()
            if state=="ACTIVE":
                self.q("UPDATE @s.lifecycle SET state='REVOKING',generation=generation+1 WHERE principal_id='syn-a'")
                self.db.execute(sql.SQL("ALTER ROLE {} NOLOGIN").format(sql.Identifier(self.roles["syn-a"])))
                if self.variant=="c2":
                    self.q("UPDATE @s.release_permit SET status='CANCELLED' WHERE status='RESERVED'")
        return time.monotonic_ns()

    def sessions(self):
        return self.db.execute("SELECT pid FROM pg_stat_activity WHERE datname=current_database() "
            "AND usename=%s",(self.roles["syn-a"],)).fetchall()

    def contain(self):
        # Bootstrap control-plane only; bounded termination of exact lab role.
        for (pid,) in self.sessions():
            if not self.db.execute("SELECT pg_terminate_backend(%s,2000)",(pid,)).fetchone()[0]:
                return False
        return not self.sessions()

    def complete(self):
        if self.variant!="c2":
            return False
        with self.db.transaction():
            state,g=self.lock_state()
            if state!="REVOKING" or self.sessions():
                return False
            if self.q("SELECT count(*) FROM @s.release_permit WHERE status IN "
                      "('RESERVED','ADMITTED','EMITTING')").fetchone()[0]:
                return False
            self.q("UPDATE @s.lifecycle SET state='REVOKED' WHERE principal_id='syn-a'")
            return True

    def regrant(self):
        with self.db.transaction():
            state,g=self.lock_state()
            # C1 deliberately has no release registry containment semantics.
            if state!=("REVOKED" if self.variant=="c2" else "REVOKING") or self.sessions():
                return False
            password=secrets.token_hex(32)
            print("::add-mask::"+password,flush=True)
            self.db.execute(sql.SQL("ALTER ROLE {} LOGIN PASSWORD {}").format(
                sql.Identifier(self.roles["syn-a"]),sql.Literal(password)))
            self.q("UPDATE @s.lifecycle SET state='ACTIVE' WHERE principal_id='syn-a'")
        self.passwords["syn-a"]=password
        return True

    def grant_revoke(self):
        with self.db.transaction():
            self.lock_state()
            self.q("UPDATE @s.resource_grant SET active=false,epoch=epoch+1 WHERE principal_id='syn-a' "
                   "AND resource_id='syn-task' AND action='task:read' AND purpose='syn-work'")
            self.q("UPDATE @s.release_permit SET status='CANCELLED' WHERE status='RESERVED'")
    
    def grant_restore(self):
        with self.db.transaction():
            self.lock_state()
            self.q("UPDATE @s.resource_grant SET active=true,epoch=epoch+1 WHERE principal_id='syn-a' "
                   "AND resource_id='syn-task' AND action='task:read' AND purpose='syn-work'")


def exercise(case,variant):
    c=Candidate(case,variant)
    old=c.issue()
    p=c.reserve(old)
    case.assertIsNotNone(p)
    with c.login("syn-b") as beta:
        case.assertEqual(c.read(beta,"syn-beta-task","syn-b"),[("synthetic:syn-beta-task",)])
    with c.login() as alpha:
        case.assertEqual(c.read(alpha),[(BODY,)])
        case.deny_sql(alpha,"UPDATE "+c.schema+".lifecycle SET state='ACTIVE'")
        case.deny_sql(alpha,"SELECT * FROM "+c.schema+".release_permit")
    print("SEC_R2_X02_CONTROL variant="+variant+" positive_and_privilege=PASS",flush=True)
    # Selective grant revoke must not suspend identity or unrelated memory.
    c.grant_revoke()
    case.assertEqual(c.state(),("ACTIVE",1))
    case.assertIsNone(c.reserve(old))
    with c.login() as alpha:
        case.assertEqual(c.read(alpha),[])
        case.assertEqual(c.read(alpha,"syn-memory"),[("synthetic:syn-memory",)])
    if variant=="c2":
        case.assertFalse(c.admit(p))
    c.grant_restore()
    p=c.reserve(old)
    case.assertIsNotNone(p)
    # Persistent state fence, independently authenticated existing and fresh DB.
    old_password=c.passwords["syn-a"]
    with c.login() as existing, c.login() as stale:
        with stale.transaction():
            stale.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ")
            case.scope(stale)
            case.assertEqual(stale.execute(sql.SQL("SELECT body FROM {}.payload WHERE resource_id='syn-task'").format(
                sql.Identifier(c.schema))).fetchall(),[(BODY,)])
            r0=c.revoke()
            case.assertEqual(c.state(),("REVOKING",2))
            case.assertIsNone(c.reserve(old))
            case.assertEqual(c.read(existing),[])
            with case.assertRaises(psycopg.OperationalError):
                with c.login():
                    case.fail("fresh login unexpectedly accepted")
            # Observe old MVCC snapshot separately; NOLOGIN is not termination.
            stale_rows=stale.execute(sql.SQL("SELECT body FROM {}.payload WHERE resource_id='syn-task'").format(
                sql.Identifier(c.schema))).fetchall()
            case.assertIn(stale_rows,([],[(BODY,)]))
            print("SEC_R2_X02_R0 variant=%s new_signed=DENY fresh_login=DENY existing_fresh=DENY stale_snapshot=%s" %
                  (variant,"ALLOW" if stale_rows else "DENY"),flush=True)
        # Keep one old session open to verify R1 cannot precede containment.
        if variant=="c2":
            case.assertFalse(c.complete())
            case.assertFalse(c.admit(p))
            case.assertFalse(c.emit(p))
        else:
            case.assertTrue(c.emit(p)) # reference observation, not a security PASS
        case.assertTrue(c.contain())
        with case.assertRaises(psycopg.Error):
            existing.execute("SELECT 1")
    if variant=="c2":
        case.assertTrue(c.complete())
        case.assertEqual(c.state(),("REVOKED",2))
        case.assertFalse(c.emit(p))
        print("SEC_R2_X02_R1 variant=c2 contained=true reserved_cancelled=true elapsed_ms=%.3f" %
              ((time.monotonic_ns()-r0)/1e6),flush=True)
    case.assertTrue(c.regrant())
    case.assertIsNone(c.reserve(old))
    with case.assertRaises(psycopg.OperationalError):
        with c.login(password=old_password):
            case.fail("old DB credential accepted")
    new=c.issue(2)
    p=c.reserve(new)
    case.assertIsNotNone(p)
    if variant=="c2":
        case.assertTrue(c.admit(p))
        c.revoke()
        case.assertFalse(c.complete())
        case.assertTrue(c.emit(p))
        case.assertTrue(c.complete())
        case.assertFalse(c.emit(p))
        case.assertTrue(c.regrant())
        # Indeterminate delivery must block completion, and replay denied.
        p=c.reserve(c.issue(3))
        case.assertIsNotNone(p)
        case.assertTrue(c.admit(p))
        case.assertFalse(c.emit(p,uncertain=True))
        c.revoke()
        case.assertFalse(c.complete())
        case.assertFalse(c.emit(p))
        case.assertIsNone(c.reserve(c.issue(3)))
        case.assertEqual(c.state(),("REVOKING",4))
        print("SEC_R2_X02_UNCERTAIN variant=c2 r1=BLOCKED replay=DENY new_admission=DENY",flush=True)
    with c.login("syn-b") as beta:
        case.assertEqual(c.read(beta,"syn-beta-task","syn-b"),[("synthetic:syn-beta-task",)])
    case.assertEqual(c.payload(),c.original)
    print("SEC_R2_X02_SUMMARY variant=%s sink_releases=%d sink_bytes=%d old_generation=DENY "
          "unrelated=PASS integrity=PASS" %
          (variant,len(c.sink),sum(map(len,c.sink))),flush=True)

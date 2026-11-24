"""DB_REAL_LAB: run only on the marked dedicated ephemeral CI container.
Never connect to the Core, production, a remote host, or an existing database.
"""
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
import os
from pathlib import Path
import re
import secrets
import unittest
from urllib.parse import urlsplit

import psycopg
from psycopg import sql

ROOT = Path(__file__).resolve().parents[2]
LAB = ROOT / "database/labs/g04_a2"
ROLES = ("g04_alpha","g04_beta","g04_service")
DB = "rw_g04_a2_lab"
DENIED = (psycopg.errors.InsufficientPrivilege,)


def guarded_bootstrap():
    if (os.getenv("GITHUB_ACTIONS") != "true"
            or os.getenv("RUNNER_ENVIRONMENT") != "github-hosted"
            or os.getenv("RW_SI_ENABLE_G04_A2_LAB") != "1"):
        raise RuntimeError("G04-A2 disposable CI guard refused")
    if any(k.startswith("PG") for k in os.environ):
        raise RuntimeError("G04-A2 libpq environment override refused")
    uri = urlsplit(os.environ["RW_G04_A2_DSN"])
    marker = os.environ["RW_G04_A2_MARKER"]
    if (uri.scheme != "postgresql" or uri.hostname != "127.0.0.1"
            or uri.port != 55432 or uri.username != "g04_bootstrap"
            or uri.path != "/"+DB or uri.query or uri.fragment
            or not re.fullmatch(r"[0-9a-f]{64}",uri.password or "")
            or not re.fullmatch(r"[0-9a-f]{64}",marker)):
        raise RuntimeError("G04-A2 target guard refused")
    conn=psycopg.connect(host="127.0.0.1",port=55432,dbname=DB,
                         user="g04_bootstrap",password=uri.password,
                         connect_timeout=5,sslmode="disable",autocommit=True)
    try:
        row=conn.execute("SELECT current_database(),session_user,current_setting('server_version_num')::int").fetchone()
        if row[:2] != (DB,"g04_bootstrap") or not 160000<=row[2]<170000:
            raise RuntimeError("G04-A2 wrong database/version")
        if conn.execute("SELECT marker FROM public.g04_ephemeral_marker").fetchall()!=[(marker,)]:
            raise RuntimeError("G04-A2 marker mismatch")
        if conn.execute("SELECT nspname FROM pg_namespace WHERE nspname NOT IN "
                        "('pg_catalog','information_schema','public','pg_toast') "
                        "AND nspname NOT LIKE 'pg_temp_%' AND nspname NOT LIKE 'pg_toast_temp_%'").fetchall():
            raise RuntimeError("G04-A2 unexpected schema")
        if conn.execute("SELECT relname FROM pg_class WHERE relnamespace='public'::regnamespace "
                        "AND relkind IN ('r','p','v','m','S','f')").fetchall()!=[("g04_ephemeral_marker",)]:
            raise RuntimeError("G04-A2 unexpected public object")
        if conn.execute("SELECT rolname FROM pg_roles WHERE rolname=ANY(%s)",
                        (list(ROLES)+["g04_owner"],)).fetchall():
            raise RuntimeError("G04-A2 preexisting role")
        print("G04_A2_GUARD_PASS postgres_version_num="+str(row[2]),flush=True)
        return conn
    except Exception:
        conn.close()
        raise


class DatabaseIsolation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.admin=guarded_bootstrap()
        cls.addClassCleanup(cls.admin.close)
        cls.passwords={role:secrets.token_hex(32) for role in ROLES}
        for password in cls.passwords.values():
            print("::add-mask::"+password,flush=True)
        with cls.admin.transaction():
            cls.admin.execute("REVOKE ALL ON DATABASE rw_g04_a2_lab FROM PUBLIC")
            cls.admin.execute("REVOKE ALL ON SCHEMA public FROM PUBLIC")
            cls.admin.execute("CREATE ROLE g04_owner NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS")
            for role,password in cls.passwords.items():
                cls.admin.execute(sql.SQL("CREATE ROLE {} LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE "
                    "NOREPLICATION NOBYPASSRLS NOINHERIT PASSWORD {}").format(
                    sql.Identifier(role),sql.Literal(password)))
                cls.admin.execute(sql.SQL("GRANT CONNECT ON DATABASE rw_g04_a2_lab TO {}").format(sql.Identifier(role)))
            cls.admin.execute("GRANT CREATE ON DATABASE rw_g04_a2_lab TO g04_owner")
            cls.admin.execute("SET LOCAL ROLE g04_owner")
            cls.admin.execute((LAB/"schema.sql").read_text())
            cls.admin.execute("RESET ROLE")
            cls.admin.execute("REVOKE CREATE ON DATABASE rw_g04_a2_lab FROM g04_owner")
            cls.admin.execute((LAB/"seed.sql").read_text())

    @contextmanager
    def login(self,role):
        # Direct independent password-authenticated connection, never SET ROLE.
        with psycopg.connect(host="127.0.0.1",port=55432,dbname=DB,user=role,
            password=self.passwords[role],sslmode="disable",connect_timeout=5,autocommit=True) as conn:
            self.assertEqual(conn.execute("SELECT session_user,current_user").fetchone(),(role,role))
            yield conn

    def scope(self,conn,org="syn-rw",project="syn-alpha",purpose="syn-work"):
        for k,v in (("rw_g04.org",org),("rw_g04.project",project),("rw_g04.purpose",purpose)):
            conn.execute("SELECT set_config(%s,%s,true)",(k,v))

    def ids(self,c):
        return [r[0] for r in c.execute("SELECT resource_id FROM g04_lab.payload ORDER BY resource_id").fetchall()]

    def baseline(self):
        return self.admin.execute("SELECT org_id,project_id,resource_id,owner_id,body FROM g04_lab.payload ORDER BY resource_id").fetchall()

    def deny_sql(self,c,statement,params=None,error=DENIED):
        with self.assertRaises(error):
            with c.transaction():
                c.execute(statement,params)

    def test_01_distinct_issuer_subject(self):
        rows=self.admin.execute("SELECT issuer,subject,principal_id FROM g04_lab.external_identity WHERE subject='syn-sub' ORDER BY issuer").fetchall()
        self.assertEqual(rows,[("syn-issuer-a","syn-sub","syn-a"),("syn-issuer-b","syn-sub","syn-b")])
        self.deny_sql(self.admin,"INSERT INTO g04_lab.external_identity VALUES ('syn-issuer-a','syn-sub','syn-s','SERVICE')",
                      error=psycopg.errors.UniqueViolation)

    def test_02_explicit_allowed_scope(self):
        with self.login("g04_alpha") as c,c.transaction():
            self.scope(c)
            self.assertEqual(self.ids(c),["syn-memory","syn-task"])
        with self.login("g04_service") as c,c.transaction():
            self.scope(c,purpose="syn-audit")
            self.assertEqual(self.ids(c),["syn-task"])

    def test_03_foreign_org_and_project(self):
        with self.login("g04_alpha") as c,c.transaction():
            for org,project in (("syn-other","syn-beta"),("syn-third","syn-gamma"),
                                ("syn-rw","syn-hidden"),("syn-rw","syn-beta")):
                self.scope(c,org,project)
                self.assertEqual(self.ids(c),[])

    def test_04_same_project_no_object_acl(self):
        with self.login("g04_alpha") as c,c.transaction():
            self.scope(c)
            self.assertEqual(c.execute("SELECT body FROM g04_lab.payload WHERE resource_id='syn-hidden-task'").fetchall(),[])

    def test_05_broad_select_and_rls_catalog(self):
        flags=self.admin.execute("SELECT relrowsecurity,relforcerowsecurity FROM pg_class WHERE oid='g04_lab.payload'::regclass").fetchone()
        self.assertEqual(flags,(True,True))
        policies=self.admin.execute("SELECT policyname,cmd,qual IS NOT NULL,with_check IS NOT NULL FROM pg_policies WHERE schemaname='g04_lab' AND tablename='payload' ORDER BY policyname").fetchall()
        self.assertEqual(policies,[("payload_read","SELECT",True,False),("payload_write","UPDATE",True,True)])
        with self.login("g04_beta") as c,c.transaction():
            self.scope(c,"syn-other","syn-beta")
            self.assertEqual(self.ids(c),["syn-beta-task"])
        # FORCE also restricts the owner; superuser is explicitly not covered.
        with self.admin.transaction():
            self.admin.execute("SET LOCAL ROLE g04_owner")
            self.scope(self.admin)
            self.assertEqual(self.ids(self.admin),[])

    def test_06_read_does_not_authorize_write(self):
        before=self.baseline()
        with self.login("g04_service") as c,c.transaction():
            self.scope(c,purpose="syn-audit")
            self.assertEqual(c.execute("UPDATE g04_lab.payload SET body='synthetic:forbidden' WHERE resource_id='syn-task'").rowcount,0)
        self.assertEqual(self.baseline(),before)
        with self.login("g04_alpha") as c:
            with c.transaction():
                self.scope(c)
                self.assertEqual(c.execute("UPDATE g04_lab.payload SET body='synthetic:allowed' WHERE resource_id='syn-task' RETURNING resource_id").fetchall(),[("syn-task",)])
                # Roll back positive mutation to preserve fixture.
                c.execute("UPDATE g04_lab.payload SET body='synthetic:syn-task' WHERE resource_id='syn-task'")
        self.assertEqual(self.baseline(),before)

    def test_07_with_check_and_column_privileges(self):
        before=self.baseline()
        with self.login("g04_alpha") as c,c.transaction():
            self.scope(c)
            for column,value in (("org_id","syn-other"),("project_id","syn-hidden"),("owner_id","syn-b")):
                q=sql.SQL("UPDATE g04_lab.payload SET {}=%s WHERE resource_id='syn-task'").format(sql.Identifier(column))
                self.deny_sql(c,q,(value,))
        # Isolated adversarial test only: temporarily grant these columns to
        # prove WITH CHECK independently of ordinary column privilege denial.
        self.admin.execute("GRANT UPDATE(org_id,project_id,owner_id) ON g04_lab.payload TO g04_alpha")
        try:
            with self.login("g04_alpha") as c,c.transaction():
                self.scope(c)
                for column,value in (("org_id","syn-other"),("project_id","syn-hidden"),("owner_id","syn-b")):
                    q=sql.SQL("UPDATE g04_lab.payload SET {}=%s WHERE resource_id='syn-task'").format(sql.Identifier(column))
                    self.deny_sql(c,q,(value,))
        finally:
            self.admin.execute("REVOKE UPDATE(org_id,project_id,owner_id) ON g04_lab.payload FROM g04_alpha")
        self.assertEqual(self.baseline(),before)

    def test_08_composite_fk(self):
        self.deny_sql(self.admin,"INSERT INTO g04_lab.payload VALUES ('syn-rw','syn-alpha','syn-beta-task','syn-b','synthetic:wrong')",
                      error=psycopg.errors.ForeignKeyViolation)
        self.deny_sql(self.admin,"INSERT INTO g04_lab.project_member VALUES ('syn-a','syn-rw','syn-beta',true,now()+interval '1 hour')",
                      error=psycopg.errors.ForeignKeyViolation)

    def test_09_missing_malformed_context(self):
        with self.login("g04_alpha") as c,c.transaction():
            self.assertEqual(self.ids(c),[])
            for org,project,purpose in (("","syn-alpha","syn-work"),("syn-rw","*","syn-work"),
                                        ("syn-rw","syn-alpha",""),("syn-rw","syn-alpha","syn-audit")):
                self.scope(c,org,project,purpose)
                self.assertEqual(self.ids(c),[])

    def test_10_no_guc_or_role_impersonation(self):
        with self.login("g04_alpha") as c,c.transaction():
            self.scope(c,"syn-other","syn-beta")
            c.execute("SELECT set_config('rw_g04.principal','syn-b',true)")
            self.assertEqual(self.ids(c),[])
            self.deny_sql(c,"SET ROLE g04_beta")
            self.deny_sql(c,"SET ROLE g04_owner")
            self.deny_sql(c,"SET SESSION AUTHORIZATION g04_beta")
            c.execute("SET LOCAL row_security=off")
            self.deny_sql(c,"SELECT * FROM g04_lab.payload")

    def test_11_runtime_privileges(self):
        attrs=self.admin.execute("SELECT rolname,rolsuper,rolbypassrls,rolcreatedb,rolcreaterole,rolreplication,rolcanlogin FROM pg_roles WHERE rolname=ANY(%s) ORDER BY rolname",(list(ROLES)+["g04_owner"],)).fetchall()
        self.assertEqual(len(attrs),4)
        for name,*flags in attrs:
            self.assertEqual(flags,[False,False,False,False,False,name!="g04_owner"])
        self.assertEqual(self.admin.execute("SELECT count(*) FROM pg_auth_members m JOIN pg_roles r ON r.oid=m.member WHERE r.rolname=ANY(%s)",(list(ROLES),)).fetchone()[0],0)
        for role in ROLES:
            with self.login(role) as c,c.transaction():
                self.assertFalse(c.execute("SELECT has_database_privilege(current_user,current_database(),'CREATE')").fetchone()[0])
                for stmt in ("SELECT * FROM g04_lab.login_binding","SELECT * FROM g04_lab.resource_grant",
                             "UPDATE g04_lab.resource_grant SET active=true","TRUNCATE g04_lab.payload",
                             "CREATE TABLE g04_lab.bad(id int)","CREATE TEMP TABLE bad(id int)",
                             "ALTER TABLE g04_lab.payload DISABLE ROW LEVEL SECURITY"):
                    self.deny_sql(c,stmt)

    def test_12_revocation_and_expiry_fresh_transaction(self):
        with self.login("g04_alpha") as c:
            for table,where in (("org_member","principal_id='syn-a' AND org_id='syn-rw'"),
                                ("project_member","principal_id='syn-a' AND project_id='syn-alpha'"),
                                ("resource_grant","principal_id='syn-a' AND resource_id='syn-task' AND action='task:read'")):
                # constant lab-only identifiers/conditions, not user input.
                for update in ("active=false","expires_at=now()-interval '1 second'"):
                    self.admin.execute("UPDATE g04_lab."+table+" SET "+update+" WHERE "+where)
                    try:
                        with c.transaction():
                            self.scope(c)
                            self.assertNotIn("syn-task",self.ids(c))
                    finally:
                        self.admin.execute("UPDATE g04_lab."+table+" SET active=true,expires_at=now()+interval '1 hour' WHERE "+where)

    def test_13_context_cleared_on_commit_and_rollback(self):
        with self.login("g04_alpha") as c:
            with c.transaction():
                self.scope(c)
                self.assertIn("syn-task",self.ids(c))
            self.assertEqual(self.ids(c),[])
            with self.assertRaises(ValueError):
                with c.transaction():
                    self.scope(c)
                    self.assertIn("syn-task",self.ids(c))
                    raise ValueError("rollback probe")
            self.assertEqual(self.ids(c),[])

    def test_14_concurrent_direct_logins(self):
        from threading import Barrier
        barrier=Barrier(2,timeout=10)
        def read(role,org,project):
            with self.login(role) as c,c.transaction():
                self.scope(c,org,project)
                barrier.wait()
                return self.ids(c)
        with ThreadPoolExecutor(max_workers=2) as pool:
            a=pool.submit(read,"g04_alpha","syn-rw","syn-alpha")
            b=pool.submit(read,"g04_beta","syn-other","syn-beta")
            self.assertEqual(a.result(),["syn-memory","syn-task"])
            self.assertEqual(b.result(),["syn-beta-task"])

    def test_15_no_privileged_operations(self):
        with self.login("g04_service") as c,c.transaction():
            self.scope(c,purpose="syn-audit")
            self.assertFalse(c.execute("SELECT g04_lab.permitted('syn-rw','syn-alpha','syn-task','syn-a','APPROVE')").fetchone()[0])
            self.deny_sql(c,"DELETE FROM g04_lab.payload")
        self.deny_sql(self.admin,"INSERT INTO g04_lab.resource_grant VALUES ('syn-s','syn-rw','syn-alpha','syn-task','TASK','task:approve','syn-audit',true,now()+interval '1 hour')",
                      error=psycopg.errors.CheckViolation)

    def test_16_failure_preserves_foreign_rows(self):
        before=self.baseline()
        with self.login("g04_alpha") as c,c.transaction():
            self.scope(c)
            self.assertEqual(c.execute("UPDATE g04_lab.payload SET body='synthetic:attack' WHERE resource_id='syn-beta-task'").rowcount,0)
            self.deny_sql(c,"UPDATE g04_lab.payload SET body='invalid' WHERE resource_id='syn-task'",
                          error=psycopg.errors.CheckViolation)
        self.assertEqual(self.baseline(),before)


if __name__=="__main__":
    unittest.main(verbosity=2)

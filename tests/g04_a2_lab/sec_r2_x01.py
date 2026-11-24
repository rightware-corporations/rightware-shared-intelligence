"""SEC-R2-X01 diagnostic probes, synthetic disposable PostgreSQL only.

A diagnostic PASS means a valid observation, NOT a security guarantee.
No changes to production or laboratory enforcement code. No external targets.
"""
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from threading import Event

from signed_reader import ReadResult

ALLOW = ReadResult("ALLOW_SYNTHETIC_READ","syn-task","synthetic:syn-task")
DENY = ReadResult("DENY_SYNTHETIC")


def classify(result):
    if result == ALLOW:
        return "ALLOW"
    if result == DENY:
        return "DENY"
    raise AssertionError("unexpected synthetic reader result")


def direct_observation(case,conn):
    with conn.transaction():
        case.scope(conn)
        ids=case.ids(conn)
    if ids not in ([],["syn-memory","syn-task"]):
        raise AssertionError("unexpected synthetic scope result")
    return "ALLOW" if "syn-task" in ids else "DENY"


def identity_revocation(case):
    before=case.baseline()
    observations=[]
    for trial in range(1,4):
        f=case.reader_fixture()
        token=f.issue()
        case.assertEqual(case.read_signed(f,token),ALLOW)
        with case.login("g04_alpha") as existing:
            case.assertEqual(direct_observation(case,existing),"ALLOW")
            with case.admin.transaction():
                changed=case.admin.execute(
                    "DELETE FROM g04_lab.external_identity WHERE principal_id='syn-a'").rowcount
                case.assertEqual(changed,1)
            try:
                case.assertEqual(case.admin.execute(
                    "SELECT count(*) FROM g04_lab.external_identity WHERE principal_id='syn-a'"
                ).fetchone()[0],0)
                signed=classify(case.read_signed(f,token))
                existing_result=direct_observation(case,existing)
                with case.login("g04_alpha") as fresh:
                    fresh_result=direct_observation(case,fresh)
                # Control: unrelated identity still works; database remains live.
                beta=f.issue("syn-issuer-b")
                control=case.read_signed(f,beta,org="syn-other",project="syn-beta",
                                         resource="syn-beta-task")
                case.assertEqual(control,ReadResult("ALLOW_SYNTHETIC_READ",
                    "syn-beta-task","synthetic:syn-beta-task"))
                observations.append((signed,existing_result,fresh_result))
                print("SEC_R2_X01_F01 trial=%d signed=%s existing_db=%s fresh_db=%s "
                      "unrelated_control=PASS committed=true" %
                      (trial,signed,existing_result,fresh_result),flush=True)
            finally:
                case.admin.execute("INSERT INTO g04_lab.external_identity VALUES "
                                   "('syn-issuer-a','syn-sub','syn-a','AGENT')")
        case.assertEqual(case.read_signed(f,token),ALLOW)
    case.assertEqual(case.baseline(),before)
    reproduced=sum(x==("DENY","ALLOW","ALLOW") for x in observations)
    print("SEC_R2_X01_F01_SUMMARY trials=3 divergence=%d fixture_restored=true" %
          reproduced,flush=True)


class ObservedCursor:
    """Observe real fetch results before pausing; never fabricate rows."""
    def __init__(self,cursor,barrier):
        self._cursor=cursor
        self._barrier=barrier

    def fetchall(self):
        rows=self._cursor.fetchall()
        self._barrier(rows)
        return rows


class ObservedConnection:
    """Test-only synchronization wrapper; all SQL runs on the real connection."""
    def __init__(self,conn,at,reached,released,observed):
        self._conn=conn
        self._at=at
        self._reached=reached
        self._released=released
        self._observed=observed
        self._queries=0

    def transaction(self):
        return self._conn.transaction()

    def execute(self,query,*args,**kwargs):
        cur=self._conn.execute(query,*args,**kwargs)
        if isinstance(query,str) and query.startswith("SELECT resource_id,body FROM g04_lab.payload "):
            self._queries+=1
            self._observed["queries"]=self._queries
            if self._queries==self._at:
                return ObservedCursor(cur,self._pause)
        return cur

    def _pause(self,rows):
        self._observed["allowed_at_barrier"]=(rows==[("syn-task","synthetic:syn-task")])
        self._observed["isolation"]=self._conn.execute("SHOW transaction_isolation").fetchone()[0]
        self._reached.set()
        if not self._released.wait(timeout=10):
            self._observed["timeout"]=True
            raise RuntimeError("synthetic diagnostic synchronization timeout")


def revocation_race(case,at):
    before=case.baseline()
    observations=[]
    for trial in range(1,4):
        # Establish legitimate baseline before enabling the synchronization hook.
        control=case.reader_fixture()
        case.assertEqual(case.read_signed(control),ALLOW)
        reached,released=Event(),Event()
        observed={}
        @contextmanager
        def observe(role):
            with case.login(role) as conn:
                yield ObservedConnection(conn,at,reached,released,observed)
        f=case.reader_fixture(connect=observe)
        token=f.issue()
        with ThreadPoolExecutor(max_workers=1) as pool:
            future=pool.submit(case.read_signed,f,token)
            revoked=False
            try:
                case.assertTrue(reached.wait(timeout=10),"actual read never reached barrier")
                case.assertTrue(observed.get("allowed_at_barrier"),"positive row control failed")
                case.assertEqual(observed.get("isolation"),"read committed")
                # Independent bootstrap connection; transaction commits before
                # the reader is allowed to continue. No timing-based sleeps.
                with case.admin.transaction():
                    changed=case.admin.execute("UPDATE g04_lab.resource_grant SET active=false "
                        "WHERE principal_id='syn-a' AND resource_id='syn-task' "
                        "AND action='task:read' AND purpose='syn-work'").rowcount
                    case.assertEqual(changed,1)
                revoked=True
                case.assertEqual(case.admin.execute("SELECT active FROM g04_lab.resource_grant "
                    "WHERE principal_id='syn-a' AND resource_id='syn-task' "
                    "AND action='task:read' AND purpose='syn-work'").fetchone(),(False,))
                released.set()
                in_flight=classify(future.result(timeout=10))
                case.assertFalse(observed.get("timeout",False))
                case.assertEqual(observed.get("queries"),2)
                # Fresh reader with no hook, started only after committed revocation.
                new_request=classify(case.read_signed(control))
                observations.append((in_flight,new_request))
                print("SEC_R2_X01_F02 trial=%d barrier=%d in_flight=%s new_request=%s "
                      "committed=true isolation=read_committed queries=2" %
                      (trial,at,in_flight,new_request),flush=True)
            finally:
                released.set()
                # Ensure the worker leaves the read transaction before restore.
                try:
                    future.result(timeout=12)
                finally:
                    if revoked:
                        case.admin.execute("UPDATE g04_lab.resource_grant SET active=true "
                            "WHERE principal_id='syn-a' AND resource_id='syn-task' "
                            "AND action='task:read' AND purpose='syn-work'")
        case.assertEqual(case.read_signed(control),ALLOW)
    case.assertEqual(case.baseline(),before)
    print("SEC_R2_X01_F02_SUMMARY barrier=%d trials=3 in_flight_allow=%d "
          "new_request_allow=%d fixture_restored=true" %
          (at,sum(a=="ALLOW" for a,b in observations),
           sum(b=="ALLOW" for a,b in observations)),flush=True)

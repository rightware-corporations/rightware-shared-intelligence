"""G04-A0: synthetic in-memory policy experiment, NEVER an authenticator.

Unverified claims, no OIDC signature, no DB queries, no HTTP/MCP/Mem0 wiring.
This deliberately cannot authorize a real tenant, private source or release.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
import os
from rightware_si.lab_boundary import require_disposable_postgres

AUDIO="rw-si-g04-a0-synthetic-only"
ACTIONS=frozenset(("task:read","task:write","memory:read"))

@dataclass(frozen=True)
class Claim:
    issuer: str
    subject: str
    audience: str
    kind: str
    expires_at: datetime

@dataclass(frozen=True)
class Principal:
    id: str
    issuer: str
    subject: str
    kind: str

@dataclass(frozen=True)
class Membership:
    principal_id: str
    organization_id: str
    project_id: str
    active: bool
    expires_at: datetime

@dataclass(frozen=True)
class Resource:
    id: str
    organization_id: str
    project_id: str
    classification: str

@dataclass(frozen=True)
class Grant:
    principal_id: str
    resource_id: str
    action: str
    purpose: str
    active: bool
    expires_at: datetime

class G04A0LabPolicy:
    """Only a synthetic contract evaluator. Never accept claims from requests."""
    def __init__(self, dsn, *, principals, memberships, resources, grants):
        if (os.environ.get("RW_SI_ENVIRONMENT")!="lab" or
            os.environ.get("RW_SI_ENABLE_G04_A0_SYNTHETIC_LAB")!="1"):
            raise RuntimeError("synthetic G04 A0 disabled")
        require_disposable_postgres(dsn,expected_user="rw")
        self.principals=tuple(principals)
        self.memberships=tuple(memberships)
        self.resources=tuple(resources)
        self.grants=tuple(grants)

    def allows(self, claim, organization, project, resource_id, action, purpose, *, now):
        if (not isinstance(claim,Claim) or not isinstance(now,datetime)
            or now.tzinfo is None or now.utcoffset() is None
            or not isinstance(claim.expires_at,datetime)
            or claim.expires_at.tzinfo is None or claim.expires_at<=now
            or claim.audience!=AUDIO or claim.kind not in ("HUMAN","AGENT","SERVICE")
            or action not in ACTIONS or not isinstance(purpose,str)
            or not purpose.startswith("syn-purpose-")
            or not all(isinstance(x,str) and x.startswith("syn-") for x in
                (claim.issuer,claim.subject,organization,project,resource_id))):
            return False
        who=[p for p in self.principals
             if p.issuer==claim.issuer and p.subject==claim.subject]
        if len(who)!=1 or who[0].kind!=claim.kind or not who[0].id.startswith("syn-"):
            return False
        resource=[r for r in self.resources if r.id==resource_id]
        if len(resource)!=1 or resource[0].classification!="SYNTHETIC":
            return False
        r=resource[0]
        if r.organization_id!=organization or r.project_id!=project:
            return False
        member=[m for m in self.memberships
                if m.principal_id==who[0].id and m.organization_id==r.organization_id
                and m.project_id==r.project_id]
        if len(member)!=1 or not member[0].active or member[0].expires_at<=now:
            return False
        grants=[g for g in self.grants
                if g.principal_id==who[0].id and g.resource_id==resource_id
                and g.action==action and g.purpose==purpose]
        return len(grants)==1 and grants[0].active and grants[0].expires_at>now

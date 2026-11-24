-- G04-A2-LAB-01 only. Run as dedicated NOLOGIN owner in empty disposable DB.
-- Never apply to database/migrations or operational database.
CREATE SCHEMA g04_lab AUTHORIZATION g04_owner;
REVOKE ALL ON SCHEMA g04_lab FROM PUBLIC;
CREATE DOMAIN g04_lab.syn_id AS text CHECK (VALUE ~ '^syn-[A-Za-z0-9_-]{1,64}$');
CREATE TABLE g04_lab.principal (
 id g04_lab.syn_id PRIMARY KEY,
 kind text NOT NULL CHECK (kind IN ('HUMAN','AGENT','SERVICE')),
 UNIQUE(id,kind)
);
CREATE TABLE g04_lab.external_identity (
 issuer g04_lab.syn_id NOT NULL, subject g04_lab.syn_id NOT NULL,
 principal_id g04_lab.syn_id NOT NULL UNIQUE, kind text NOT NULL,
 PRIMARY KEY(issuer,subject), FOREIGN KEY(principal_id,kind) REFERENCES g04_lab.principal(id,kind)
);
-- Only bootstrap can provision these mappings. SESSION_USER, not a GUC, is identity.
CREATE TABLE g04_lab.login_binding (
 login_name name PRIMARY KEY, principal_id g04_lab.syn_id NOT NULL UNIQUE REFERENCES g04_lab.principal(id)
);
CREATE TABLE g04_lab.organization (
 id g04_lab.syn_id PRIMARY KEY, active boolean NOT NULL
);
CREATE TABLE g04_lab.project (
 org_id g04_lab.syn_id REFERENCES g04_lab.organization(id),
 id g04_lab.syn_id NOT NULL UNIQUE, active boolean NOT NULL,
 PRIMARY KEY(org_id,id)
);
CREATE TABLE g04_lab.org_member (
 principal_id g04_lab.syn_id REFERENCES g04_lab.principal(id),
 org_id g04_lab.syn_id REFERENCES g04_lab.organization(id),
 active boolean NOT NULL, expires_at timestamptz NOT NULL,
 PRIMARY KEY(principal_id,org_id)
);
CREATE TABLE g04_lab.project_member (
 principal_id g04_lab.syn_id NOT NULL, org_id g04_lab.syn_id NOT NULL,
 project_id g04_lab.syn_id NOT NULL, active boolean NOT NULL, expires_at timestamptz NOT NULL,
 PRIMARY KEY(principal_id,org_id,project_id),
 FOREIGN KEY(principal_id,org_id) REFERENCES g04_lab.org_member(principal_id,org_id),
 FOREIGN KEY(org_id,project_id) REFERENCES g04_lab.project(org_id,id)
);
CREATE TABLE g04_lab.resource (
 org_id g04_lab.syn_id NOT NULL, project_id g04_lab.syn_id NOT NULL,
 id g04_lab.syn_id NOT NULL UNIQUE, owner_id g04_lab.syn_id NOT NULL REFERENCES g04_lab.principal(id),
 kind text NOT NULL CHECK(kind IN ('TASK','MEMORY','EVIDENCE')),
 classification text NOT NULL CHECK(classification='SYNTHETIC'),
 active boolean NOT NULL,
 PRIMARY KEY(org_id,project_id,id), UNIQUE(org_id,project_id,id,owner_id),
 UNIQUE(org_id,project_id,id,kind),
 FOREIGN KEY(org_id,project_id) REFERENCES g04_lab.project(org_id,id)
);
CREATE TABLE g04_lab.resource_grant (
 principal_id g04_lab.syn_id NOT NULL REFERENCES g04_lab.principal(id),
 org_id g04_lab.syn_id NOT NULL, project_id g04_lab.syn_id NOT NULL,
 resource_id g04_lab.syn_id NOT NULL, kind text NOT NULL,
 action text NOT NULL, purpose text NOT NULL CHECK(purpose IN ('syn-work','syn-audit')),
 active boolean NOT NULL, expires_at timestamptz NOT NULL,
 CHECK ((kind='TASK' AND action IN ('task:read','task:write'))
     OR (kind='MEMORY' AND action='memory:read')
     OR (kind='EVIDENCE' AND action='evidence:read')),
 PRIMARY KEY(principal_id,org_id,project_id,resource_id,action,purpose),
 FOREIGN KEY(org_id,project_id,resource_id,kind) REFERENCES g04_lab.resource(org_id,project_id,id,kind)
);
CREATE TABLE g04_lab.payload (
 org_id g04_lab.syn_id NOT NULL, project_id g04_lab.syn_id NOT NULL,
 resource_id g04_lab.syn_id NOT NULL, owner_id g04_lab.syn_id NOT NULL,
 body text NOT NULL CHECK(length(body) BETWEEN 1 AND 200 AND body LIKE 'synthetic:%'),
 PRIMARY KEY(org_id,project_id,resource_id),
 FOREIGN KEY(org_id,project_id,resource_id,owner_id)
  REFERENCES g04_lab.resource(org_id,project_id,id,owner_id)
);
-- SECURITY DEFINER reads only protected metadata, returns boolean. No dynamic SQL.
-- session_user remains the authenticated login even inside SECURITY DEFINER.
CREATE FUNCTION g04_lab.permitted(o text,p text,r text,own text,operation text)
RETURNS boolean LANGUAGE sql STABLE SECURITY DEFINER
SET search_path = pg_catalog
AS $fn$
 SELECT EXISTS (
  SELECT 1 FROM g04_lab.login_binding l
  JOIN g04_lab.principal a ON a.id=l.principal_id
  JOIN g04_lab.org_member om ON om.principal_id=a.id AND om.org_id=o
  JOIN g04_lab.organization og ON og.id=om.org_id
  JOIN g04_lab.project_member pm ON pm.principal_id=a.id AND pm.org_id=o AND pm.project_id=p
  JOIN g04_lab.project pr ON pr.org_id=pm.org_id AND pr.id=pm.project_id
  JOIN g04_lab.resource res ON res.org_id=o AND res.project_id=p AND res.id=r AND res.owner_id=own
  JOIN g04_lab.resource_grant g ON g.principal_id=a.id AND g.org_id=o AND g.project_id=p AND g.resource_id=r
  WHERE l.login_name=session_user
    AND o=current_setting('rw_g04.org',true)
    AND p=current_setting('rw_g04.project',true)
    AND g.purpose=current_setting('rw_g04.purpose',true)
    AND og.active AND pr.active AND om.active AND pm.active AND res.active AND g.active
    AND om.expires_at>statement_timestamp() AND pm.expires_at>statement_timestamp()
    AND g.expires_at>statement_timestamp()
    AND ((operation='READ' AND g.action=lower(res.kind)||':read')
      OR (operation='WRITE' AND res.kind='TASK' AND g.action='task:write'))
 )
$fn$;
REVOKE ALL ON FUNCTION g04_lab.permitted(text,text,text,text,text) FROM PUBLIC;
ALTER TABLE g04_lab.payload ENABLE ROW LEVEL SECURITY;
ALTER TABLE g04_lab.payload FORCE ROW LEVEL SECURITY;
CREATE POLICY payload_read ON g04_lab.payload FOR SELECT
 USING(g04_lab.permitted(org_id,project_id,resource_id,owner_id,'READ'));
CREATE POLICY payload_write ON g04_lab.payload FOR UPDATE
 USING(g04_lab.permitted(org_id,project_id,resource_id,owner_id,'WRITE'))
 WITH CHECK(g04_lab.permitted(org_id,project_id,resource_id,owner_id,'WRITE'));
REVOKE ALL ON ALL TABLES IN SCHEMA g04_lab FROM PUBLIC;
REVOKE ALL ON DOMAIN g04_lab.syn_id FROM PUBLIC;
GRANT USAGE ON SCHEMA g04_lab TO g04_alpha,g04_beta,g04_service;
GRANT USAGE ON DOMAIN g04_lab.syn_id TO g04_alpha,g04_beta,g04_service;
GRANT SELECT, UPDATE(body) ON g04_lab.payload TO g04_alpha,g04_beta,g04_service;
GRANT EXECUTE ON FUNCTION g04_lab.permitted(text,text,text,text,text) TO g04_alpha,g04_beta,g04_service;

-- G04-A2-LAB-02: revalidate the provisioned external identity on the very
-- statement that reads RLS-protected data. No caller-selected login.
CREATE FUNCTION g04_lab.bound_identity(i text,s text,p text,k text)
RETURNS boolean LANGUAGE sql STABLE SECURITY DEFINER
SET search_path = pg_catalog
AS $fn$
 SELECT EXISTS (
  SELECT 1 FROM g04_lab.login_binding l
  JOIN g04_lab.external_identity e ON e.principal_id=l.principal_id
  JOIN g04_lab.principal a ON a.id=e.principal_id AND a.kind=e.kind
  WHERE l.login_name=session_user AND e.issuer=i AND e.subject=s
    AND e.principal_id=p AND e.kind=k
 )
$fn$;
REVOKE ALL ON FUNCTION g04_lab.bound_identity(text,text,text,text) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION g04_lab.bound_identity(text,text,text,text) TO g04_alpha,g04_beta,g04_service;

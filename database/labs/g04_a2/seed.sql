-- Synthetic fixture only; bootstrap superuser inserts payload under FORCE RLS.
INSERT INTO g04_lab.principal VALUES ('syn-a','AGENT'),('syn-b','AGENT'),('syn-s','SERVICE');
INSERT INTO g04_lab.external_identity VALUES
 ('syn-issuer-a','syn-sub','syn-a','AGENT'),('syn-issuer-b','syn-sub','syn-b','AGENT'),
 ('syn-issuer-s','syn-service','syn-s','SERVICE');
INSERT INTO g04_lab.login_binding VALUES ('g04_alpha','syn-a'),('g04_beta','syn-b'),('g04_service','syn-s');
INSERT INTO g04_lab.organization VALUES ('syn-rw',true),('syn-other',true),('syn-third',true);
INSERT INTO g04_lab.project VALUES
 ('syn-rw','syn-alpha',true),('syn-rw','syn-hidden',true),
 ('syn-other','syn-beta',true),('syn-third','syn-gamma',true);
INSERT INTO g04_lab.org_member VALUES
 ('syn-a','syn-rw',true,now()+interval '1 hour'),
 ('syn-b','syn-other',true,now()+interval '1 hour'),
 ('syn-s','syn-rw',true,now()+interval '1 hour');
INSERT INTO g04_lab.project_member VALUES
 ('syn-a','syn-rw','syn-alpha',true,now()+interval '1 hour'),
 ('syn-b','syn-other','syn-beta',true,now()+interval '1 hour'),
 ('syn-s','syn-rw','syn-alpha',true,now()+interval '1 hour');
INSERT INTO g04_lab.resource VALUES
 ('syn-rw','syn-alpha','syn-task','syn-a','TASK','SYNTHETIC',true),
 ('syn-rw','syn-alpha','syn-hidden-task','syn-a','TASK','SYNTHETIC',true),
 ('syn-rw','syn-alpha','syn-memory','syn-a','MEMORY','SYNTHETIC',true),
 ('syn-rw','syn-hidden','syn-other-task','syn-a','TASK','SYNTHETIC',true),
 ('syn-other','syn-beta','syn-beta-task','syn-b','TASK','SYNTHETIC',true),
 ('syn-third','syn-gamma','syn-gamma-task','syn-b','TASK','SYNTHETIC',true);
INSERT INTO g04_lab.payload SELECT org_id,project_id,id,owner_id,'synthetic:'||id FROM g04_lab.resource;
INSERT INTO g04_lab.resource_grant VALUES
 ('syn-a','syn-rw','syn-alpha','syn-task','TASK','task:read','syn-work',true,now()+interval '1 hour'),
 ('syn-a','syn-rw','syn-alpha','syn-task','TASK','task:write','syn-work',true,now()+interval '1 hour'),
 ('syn-a','syn-rw','syn-alpha','syn-memory','MEMORY','memory:read','syn-work',true,now()+interval '1 hour'),
 ('syn-b','syn-other','syn-beta','syn-beta-task','TASK','task:read','syn-work',true,now()+interval '1 hour'),
 ('syn-s','syn-rw','syn-alpha','syn-task','TASK','task:read','syn-audit',true,now()+interval '1 hour'),
 -- Deliberately misassigned grants: no corresponding membership.
 ('syn-a','syn-other','syn-beta','syn-beta-task','TASK','task:read','syn-work',true,now()+interval '1 hour'),
 ('syn-a','syn-third','syn-gamma','syn-gamma-task','TASK','task:read','syn-work',true,now()+interval '1 hour');

-- WORK-02D: scrub formerly replayable lease credentials from all idempotency responses.
-- Apply ONLY after WORK-02A + WORK-02B migrations. Safe on isolated lab DB.
BEGIN;
UPDATE si_idempotency
   SET response = response - 'lease_token'
 WHERE jsonb_typeof(response) = 'object'
   AND response ? 'lease_token';
COMMIT;

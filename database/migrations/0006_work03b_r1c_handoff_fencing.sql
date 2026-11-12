-- RIGHTWARE Shared Intelligence WORK-03B R1C
-- Additive, laboratory-only. Preserve historical unbound handoffs explicitly.
-- A task with checkpoints now requires the latest checkpoint to be bound on offer.
BEGIN;

CREATE TABLE si_lease_fences (
    task_id UUID PRIMARY KEY REFERENCES si_tasks(id) ON DELETE CASCADE,
    generation INTEGER NOT NULL CHECK (generation > 0)
);
INSERT INTO si_lease_fences(task_id,generation)
SELECT task_id,generation FROM si_task_leases
ON CONFLICT (task_id) DO UPDATE
    SET generation = GREATEST(si_lease_fences.generation,EXCLUDED.generation);

ALTER TABLE si_handoffs
    ADD COLUMN checkpoint_id UUID,
    ADD COLUMN checkpoint_seq INTEGER,
    ADD COLUMN checkpoint_task_version INTEGER,
    ADD CONSTRAINT ck_si_handoff_checkpoint_bundle CHECK (
      (checkpoint_id IS NULL AND checkpoint_seq IS NULL AND checkpoint_task_version IS NULL)
      OR
      (checkpoint_id IS NOT NULL AND checkpoint_seq > 0 AND checkpoint_task_version > 0)
    ),
    ADD CONSTRAINT fk_si_handoff_checkpoint_same_task
      FOREIGN KEY(project_id,task_id,checkpoint_id)
      REFERENCES si_task_checkpoints(project_id,task_id,id);

-- A foreign key alone cannot validate a checkpoint's seq/version. Prevent
-- forged metadata and changing a handoff's immutable checkpoint binding.
CREATE FUNCTION si_guard_handoff_checkpoint() RETURNS trigger
LANGUAGE plpgsql AS $$
DECLARE stored_seq INTEGER;
DECLARE stored_version INTEGER;
BEGIN
    IF TG_OP = 'UPDATE' THEN
        IF NEW.checkpoint_id IS DISTINCT FROM OLD.checkpoint_id
           OR NEW.checkpoint_seq IS DISTINCT FROM OLD.checkpoint_seq
           OR NEW.checkpoint_task_version IS DISTINCT FROM OLD.checkpoint_task_version THEN
            RAISE EXCEPTION 'handoff checkpoint binding cannot be changed'
                USING ERRCODE='23514';
        END IF;
        RETURN NEW;
    END IF;
    IF NEW.checkpoint_id IS NOT NULL THEN
        SELECT checkpoint_seq,task_version_recorded
          INTO stored_seq,stored_version
          FROM si_task_checkpoints
         WHERE project_id=NEW.project_id
           AND task_id=NEW.task_id
           AND id=NEW.checkpoint_id;
        IF NOT FOUND OR stored_seq IS DISTINCT FROM NEW.checkpoint_seq
           OR stored_version IS DISTINCT FROM NEW.checkpoint_task_version THEN
            RAISE EXCEPTION 'invalid checkpoint sequence/version binding'
                USING ERRCODE='23514';
        END IF;
    END IF;
    RETURN NEW;
END;
$$;
CREATE TRIGGER trg_si_handoff_checkpoint_guard
BEFORE INSERT OR UPDATE ON si_handoffs
FOR EACH ROW EXECUTE FUNCTION si_guard_handoff_checkpoint();

ALTER TABLE si_continuity_events
    DROP CONSTRAINT si_continuity_events_event_type_check;
ALTER TABLE si_continuity_events
    ADD CONSTRAINT si_continuity_events_event_type_check
    CHECK (event_type IN (
      'AGENT_RUN_STARTED','SOURCE_REGISTERED',
      'OBSERVATION_ASSERTED','CHECKPOINT_RECORDED','LEASE_REKEYED'
    ));
COMMIT;

-- Production privileges. Applied once, against slotwise_prod, before the
-- schema and data fixtures — the ALTER DEFAULT PRIVILEGES statements below
-- only cover tables created after they run.
--
-- The roles and databases are created by the repository-specific initdb
-- script before PostgreSQL starts; this file only grants object privileges.
--
-- slotwise_readonly is used by ./ops/prod-status.sh, ./ops/prod-psql.sh and
-- ./ops/prod-verify.sh. Investigating production never needs write access.

GRANT CONNECT ON DATABASE slotwise_prod TO slotwise_readonly;
GRANT USAGE ON SCHEMA public TO slotwise_readonly;

-- Covers tables a later migration creates, so verification keeps working
-- without a follow-up grant.
ALTER DEFAULT PRIVILEGES FOR ROLE slotwise_app IN SCHEMA public
    GRANT SELECT ON TABLES TO slotwise_readonly;
ALTER DEFAULT PRIVILEGES FOR ROLE slotwise_app IN SCHEMA public
    GRANT SELECT ON SEQUENCES TO slotwise_readonly;

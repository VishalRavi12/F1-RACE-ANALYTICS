-- ============================================================================
-- Formula 1 Race Analytics - Role-Based Access Control (RBAC)
-- EAS 550 - Data Mining Query Language
-- Team: Karisha Ananya Neelakandan, Swaminathan Sankaran, Vishal Ravi Muthaiah
-- ============================================================================
-- This script implements RBAC with two roles:
--   1. analyst_role  : Read-only access (SELECT) for data analysis.
--   2. app_user_role : Read/Write access (SELECT, INSERT, UPDATE) for the app.
-- ============================================================================

-- Drop roles if they already exist (idempotent)
DO $$
BEGIN
    -- Revoke privileges before dropping
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'analyst_role') THEN
        EXECUTE 'REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA public FROM analyst_role';
        EXECUTE 'REVOKE USAGE ON SCHEMA public FROM analyst_role';
    END IF;
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'app_user_role') THEN
        EXECUTE 'REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA public FROM app_user_role';
        EXECUTE 'REVOKE USAGE ON SCHEMA public FROM app_user_role';
        EXECUTE 'REVOKE USAGE ON ALL SEQUENCES IN SCHEMA public FROM app_user_role';
    END IF;
END
$$;

-- Drop and recreate roles
DROP ROLE IF EXISTS analyst_role;
DROP ROLE IF EXISTS app_user_role;

-- ============================================================================
-- Role 1: Analyst (SELECT only)
-- Purpose: Data analysts can query all tables but cannot modify data.
-- ============================================================================
CREATE ROLE analyst_role NOLOGIN;
GRANT USAGE ON SCHEMA public TO analyst_role;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO analyst_role;

-- Ensure future tables also grant SELECT to analyst
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT SELECT ON TABLES TO analyst_role;

-- ============================================================================
-- Role 2: App User (SELECT, INSERT, UPDATE)
-- Purpose: The Streamlit/FastAPI application can read and write data.
-- ============================================================================
CREATE ROLE app_user_role NOLOGIN;
GRANT USAGE ON SCHEMA public TO app_user_role;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO app_user_role;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_user_role;

-- Ensure future tables also grant appropriate privileges
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT SELECT, INSERT, UPDATE ON TABLES TO app_user_role;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT USAGE, SELECT ON SEQUENCES TO app_user_role;

-- ============================================================================
-- Example: Create actual login users and assign roles
-- Uncomment and customize the passwords when deploying.
-- ============================================================================
-- CREATE USER f1_analyst WITH PASSWORD 'secure_analyst_password_here';
-- GRANT analyst_role TO f1_analyst;

-- CREATE USER f1_app WITH PASSWORD 'secure_app_password_here';
-- GRANT app_user_role TO f1_app;

-- ============================================================================
-- Verification: Run these queries to confirm role privileges
-- ============================================================================
-- SELECT grantee, table_name, privilege_type
-- FROM information_schema.role_table_grants
-- WHERE grantee IN ('analyst_role', 'app_user_role')
-- ORDER BY grantee, table_name;

-- ============================================================================
-- Oracle Hybrid Query POC - Step 0: Prepare Vector Tablespace
-- ============================================================================
-- Creates the USERS_ASSM tablespace required for Vector operations.
-- Vector Data Types require Automatic Segment Space Management (ASSM).
-- ============================================================================

-- Create tablespace if it doesn't exist
DECLARE
    ts_exists INTEGER;
BEGIN
    SELECT count(*) INTO ts_exists FROM dba_tablespaces WHERE tablespace_name = 'USERS_ASSM';
    IF ts_exists = 0 THEN
        EXECUTE IMMEDIATE 'CREATE TABLESPACE users_assm DATAFILE ''users_assm.dbf'' SIZE 100M AUTOEXTEND ON NEXT 10M MAXSIZE UNLIMITED SEGMENT SPACE MANAGEMENT AUTO';
        EXECUTE IMMEDIATE 'ALTER USER system QUOTA UNLIMITED ON users_assm';
    ELSE
        -- Ensure quota
        EXECUTE IMMEDIATE 'ALTER USER system QUOTA UNLIMITED ON users_assm';
    END IF;
END;
/

-- ============================================================================
-- Oracle Hybrid Query POC - Step 1: Create Relational Tables
-- ============================================================================
-- This script creates the relational tables for patient data
--
-- Tables created:
--   - PATIENTS: Patient demographic and diagnosis information
--
-- Author: Oracle GraphRAG POC
-- ============================================================================

-- Drop existing tables if they exist
BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE patients CASCADE CONSTRAINTS';
EXCEPTION
    WHEN OTHERS THEN
        IF SQLCODE != -942 THEN
            RAISE;
        END IF;
END;
/

-- Create PATIENTS table
CREATE TABLE patients (
    patient_id       NUMBER PRIMARY KEY,
    customer_name    VARCHAR2(100) NOT NULL,
    age              NUMBER NOT NULL,
    diagnosis        VARCHAR2(200) NOT NULL,
    admission_date   DATE,
    primary_physician VARCHAR2(100),

    CONSTRAINT chk_age CHECK (age > 0 AND age < 150),
    CONSTRAINT chk_diagnosis CHECK (diagnosis IN ('Type 1 Diabetes', 'Type 2 Diabetes'))
);

-- Add comments for documentation
COMMENT ON TABLE patients IS 'Patient demographic and diagnosis information for hybrid query demo';
COMMENT ON COLUMN patients.patient_id IS 'Unique patient identifier';
COMMENT ON COLUMN patients.customer_name IS 'Patient full name';
COMMENT ON COLUMN patients.age IS 'Patient age in years';
COMMENT ON COLUMN patients.diagnosis IS 'Primary diagnosis (Type 1 or Type 2 Diabetes)';
COMMENT ON COLUMN patients.admission_date IS 'Date of hospital admission';
COMMENT ON COLUMN patients.primary_physician IS 'Assigned primary care physician';

-- Create indexes for performance
CREATE INDEX idx_patients_diagnosis ON patients(diagnosis);
CREATE INDEX idx_patients_age ON patients(age);

COMMIT;

PROMPT
PROMPT ============================================================================
PROMPT Relational tables created successfully!
PROMPT
PROMPT Created tables:
PROMPT   - PATIENTS (with indexes on diagnosis and age)
PROMPT
PROMPT Next step: Run 02_create_graph_tables.sql
PROMPT ============================================================================
PROMPT

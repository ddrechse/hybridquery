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

-- Create CLINICAL_OUTCOMES table
CREATE TABLE clinical_outcomes (
    treatment_name          VARCHAR2(200) PRIMARY KEY,
    effectiveness_score     NUMBER(3,1) NOT NULL CHECK (effectiveness_score BETWEEN 0 AND 10),
    side_effect_risk        NUMBER(2,1) NOT NULL CHECK (side_effect_risk BETWEEN 0 AND 5),
    monthly_cost            NUMBER(8,2) NOT NULL,
    fda_approval_year       NUMBER(4),
    recommended_min_age     NUMBER(3),
    recommended_max_age     NUMBER(3)
);

-- Add comments for clinical outcomes
COMMENT ON TABLE clinical_outcomes IS 'Historical effectiveness and cost data for treatments';
COMMENT ON COLUMN clinical_outcomes.treatment_name IS 'Name of the treatment/drug';
COMMENT ON COLUMN clinical_outcomes.effectiveness_score IS 'Real-world effectiveness (0-10 scale)';
COMMENT ON COLUMN clinical_outcomes.side_effect_risk IS 'Risk profile (0-5 scale, 5 is highest risk)';
COMMENT ON COLUMN clinical_outcomes.monthly_cost IS 'Average monthly cost in USD';

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

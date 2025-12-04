-- =====================================================================
-- Load Clinical Trial Outcomes Data
-- =====================================================================
-- This script creates and loads the clinical_outcomes table with
-- treatment effectiveness, safety, and cost data
--
-- Source: clinical_trial_outcomes.csv (or .xlsx)
--
-- Usage:
--   For local Docker Oracle:
--     docker exec -i oracle23ai sqlplus system/oracle@FREEPDB1 @load_clinical_outcomes.sql
--   Or from SQL*Plus/SQLcl:
--     @load_clinical_outcomes.sql
-- =====================================================================

SET ECHO ON
SET FEEDBACK ON

PROMPT ======================================================================
PROMPT Creating Clinical Outcomes Table
PROMPT ======================================================================

-- Drop table if exists
BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE clinical_outcomes CASCADE CONSTRAINTS';
EXCEPTION
    WHEN OTHERS THEN
        IF SQLCODE != -942 THEN  -- ORA-00942: table or view does not exist
            RAISE;
        END IF;
END;
/

-- Create clinical outcomes table
CREATE TABLE clinical_outcomes (
    treatment_name          VARCHAR2(200) PRIMARY KEY,
    effectiveness_score     NUMBER(3,1) NOT NULL CHECK (effectiveness_score BETWEEN 0 AND 10),
    side_effect_risk        NUMBER(2,1) NOT NULL CHECK (side_effect_risk BETWEEN 0 AND 5),
    monthly_cost            NUMBER(8,2) NOT NULL,
    fda_approval_year       NUMBER(4),
    recommended_min_age     NUMBER(3),
    recommended_max_age     NUMBER(3)
);

PROMPT Table created: CLINICAL_OUTCOMES
PROMPT

PROMPT ======================================================================
PROMPT Loading Clinical Trial Outcomes Data
PROMPT ======================================================================

-- Insert clinical trial outcomes for all 14 treatments
INSERT INTO clinical_outcomes VALUES ('GLP-1 Agonists', 8.5, 2.0, 450.00, 2005, 18, 85);
INSERT INTO clinical_outcomes VALUES ('SGLT2 Inhibitors', 8.0, 1.5, 380.00, 2013, 18, 90);
INSERT INTO clinical_outcomes VALUES ('DPP-4 Inhibitors', 7.2, 1.2, 320.00, 2006, 18, 95);
INSERT INTO clinical_outcomes VALUES ('Insulin Therapy', 7.8, 2.5, 120.00, 1982, 0, 999);
INSERT INTO clinical_outcomes VALUES ('Basal Insulin', 7.5, 2.3, 95.00, 1990, 0, 999);
INSERT INTO clinical_outcomes VALUES ('Metformin', 7.5, 1.0, 25.00, 1995, 18, 80);
INSERT INTO clinical_outcomes VALUES ('Sulfonylureas', 6.8, 2.8, 35.00, 1984, 18, 75);
INSERT INTO clinical_outcomes VALUES ('Semaglutide', 9.0, 2.1, 500.00, 2017, 18, 85);
INSERT INTO clinical_outcomes VALUES ('Liraglutide', 8.3, 2.0, 475.00, 2010, 18, 85);
INSERT INTO clinical_outcomes VALUES ('Empagliflozin', 8.2, 1.4, 395.00, 2014, 18, 90);
INSERT INTO clinical_outcomes VALUES ('Dapagliflozin', 7.9, 1.6, 385.00, 2014, 18, 90);
INSERT INTO clinical_outcomes VALUES ('Canagliflozin', 7.8, 1.7, 390.00, 2013, 18, 90);
INSERT INTO clinical_outcomes VALUES ('Sitagliptin', 7.0, 1.1, 310.00, 2006, 18, 95);
INSERT INTO clinical_outcomes VALUES ('Linagliptin', 7.1, 1.2, 325.00, 2011, 18, 95);

COMMIT;

PROMPT Loaded 14 clinical trial outcomes
PROMPT

PROMPT ======================================================================
PROMPT Verifying Data
PROMPT ======================================================================

SELECT COUNT(*) AS total_treatments FROM clinical_outcomes;

PROMPT
PROMPT Top 5 Most Effective Treatments:
PROMPT

SELECT treatment_name, effectiveness_score, side_effect_risk, monthly_cost
FROM clinical_outcomes
ORDER BY effectiveness_score DESC
FETCH FIRST 5 ROWS ONLY;

PROMPT
PROMPT Most Cost-Effective (High Effectiveness, Low Cost):
PROMPT

SELECT treatment_name, effectiveness_score, monthly_cost,
       ROUND(effectiveness_score / (monthly_cost / 100), 2) AS cost_effectiveness_ratio
FROM clinical_outcomes
WHERE effectiveness_score >= 7.0
ORDER BY cost_effectiveness_ratio DESC
FETCH FIRST 5 ROWS ONLY;

PROMPT
PROMPT Safest Treatments (Low Side Effect Risk):
PROMPT

SELECT treatment_name, side_effect_risk, effectiveness_score
FROM clinical_outcomes
ORDER BY side_effect_risk ASC, effectiveness_score DESC
FETCH FIRST 5 ROWS ONLY;

PROMPT
PROMPT ======================================================================
PROMPT SUCCESS! Clinical outcomes data loaded and ready.
PROMPT ======================================================================
PROMPT
PROMPT Next steps:
PROMPT 1. Run 3-way hybrid query combining patients + graph + clinical outcomes
PROMPT 2. See: hybridQuery/three_way_hybrid_query.sql
PROMPT
PROMPT ======================================================================

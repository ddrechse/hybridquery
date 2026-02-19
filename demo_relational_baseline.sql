-- ============================================================================
-- Demo: Relational Baseline (The "Before" State)
-- ============================================================================
-- Objective: Show that we have Patient Data and Treatment Data, but NO LINK.
--
-- 1. We know David Thompson has "Type 2 Diabetes".
-- 2. We know we have treatment data for "Metformin", "Insulin", etc.
-- 3. BUT: There is no FOREIGN KEY joining "Patients" to "Clinical Outcomes".
--    The database doesn't know which treatments are for Diabetes.
-- ============================================================================

SET LINESIZE 200
SET PAGESIZE 100
COLUMN customer_name FORMAT A20
COLUMN diagnosis FORMAT A20
COLUMN treatment_name FORMAT A20

PROMPT 
PROMPT ============================================================================
PROMPT QUERY 1: The Patient Record
PROMPT ============================================================================
PROMPT Looking for "David Thompson"...
PROMPT

SELECT customer_name, age, diagnosis 
FROM patients 
WHERE customer_name = 'David Thompson';

PROMPT 
PROMPT ============================================================================
PROMPT QUERY 2: The Treatment Data
PROMPT ============================================================================
PROMPT We have clinical outcomes data, but who is it for?
PROMPT

SELECT treatment_name, effectiveness_score, side_effect_risk, monthly_cost
FROM clinical_outcomes
FETCH FIRST 10 ROWS ONLY;

PROMPT 
PROMPT ============================================================================
PROMPT CRITICAL GAP:
PROMPT The database knows David has Diabetes.
PROMPT The database knows Metformin exists.
PROMPT But the database DOES NOT KNOW that Metformin treats Diabetes.
PROMPT 
PROMPT We need a Knowledge Graph to bridge this gap.
PROMPT ============================================================================
PROMPT

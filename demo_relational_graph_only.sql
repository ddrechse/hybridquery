-- ============================================================================
-- Demo: Relational + Property Graph Fusion
-- ============================================================================
-- This query demonstrates joining relational patient data with knowledge
-- extracted from medical literature via property graph traversal.
--
-- Question: "What treatments are mentioned in our literature for 
--            David Thompson's condition?"
-- ============================================================================

SET LINESIZE 200
SET PAGESIZE 100
COLUMN customer_name FORMAT A20
COLUMN age FORMAT 999
COLUMN diagnosis FORMAT A30
COLUMN treatment FORMAT A30
COLUMN paper_title FORMAT A50

PROMPT 
PROMPT ============================================================================
-- QUERY: Modern GRAPH_TABLE Approach (Match Clause)
PROMPT ============================================================================
PROMPT Relational + Graph Query: Treatments for Patient Conditions (Using GRAPH_TABLE)
PROMPT ============================================================================
PROMPT 

-- Note: GRAPH_TABLE cannot reference external tables in its WHERE clause,
-- so we retrieve all graph patterns and filter patients in the outer query
SELECT DISTINCT
    p.customer_name,
    p.age,
    p.diagnosis,
    gt.treatment_name,
    gt.paper_title
FROM 
    -- RELATIONAL: Patient Data
    patients p
    -- FUSION: Join Patient ROW with Graph Pattern Result
    CROSS JOIN LATERAL (
        SELECT *
        FROM GRAPH_TABLE (
            medical_literature_kg
            -- CYPHER-LIKE MATCH PATTERN:
            -- Find Papers that MENTION Treatments that TREAT Conditions
            MATCH 
                (paper IS Paper) -[m IS MENTIONS]-> (treatment IS Treatment) 
                                 -[tr IS TREATS]-> (condition IS Condition)
            COLUMNS (
                condition.name AS condition_name,
                treatment.entity_name AS treatment_name,
                paper.title AS paper_title
            )
        )
        -- LINK: Connect Graph Condition Name to Patient Diagnosis
        WHERE UPPER(condition_name) = UPPER(p.diagnosis)
    ) gt
WHERE 
    p.customer_name = 'David Thompson'
ORDER BY 
    p.customer_name, gt.treatment_name;

PROMPT 
PROMPT ============================================================================
PROMPT Summary: This demonstrates 2-model fusion (Relational + Graph)
PROMPT - Relational: Patient demographics and diagnoses
PROMPT - Graph: Knowledge extraction from medical literature
PROMPT 
PROMPT Why is this success?
PROMPT 1. Fusion: We joined structured Patient data (Age/Diagnosis) with unstructured Medical Knowledge (Treatments).
PROMPT 2. Traversal: We found treatments relevant to "Type 2 Diabetes" by traversing the graph (Condition <- Treats <- Treatment).
PROMPT 3. Evidence: We retrieved the specific "Paper Title" that justifies each treatment.
PROMPT 
PROMPT ============================================================================


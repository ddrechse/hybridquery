-- =====================================================================
-- 3-Model Fusion Demo: Vector + Graph + Relational
-- =====================================================================
-- This script demonstrates combining:
-- 1. VECTOR SEARCH: Find treatments semantically similar to each other
-- 2. GRAPH TRAVERSAL: Verify treatments are mentioned in research papers
-- 3. RELATIONAL: Patient demographics and diagnoses
--
-- Scenario: Find treatments similar to what's already working for patients
-- =====================================================================

SET PAGESIZE 100
SET LINESIZE 200
COLUMN treatment_name FORMAT A25
COLUMN similar_treatment FORMAT A25
COLUMN paper_title FORMAT A60
COLUMN similarity_score FORMAT 999.9999

PROMPT ======================================================================
-- QUERY 1: Vector Similarity - Find Related Treatments
PROMPT ======================================================================
PROMPT Goal: Find treatments semantically similar to "Semaglutide"
PROMPT (Uses vector embeddings to find conceptually related treatments)
PROMPT ======================================================================
PROMPT

SELECT 
    t1.entity_name AS base_treatment,
    t2.entity_name AS similar_treatment,
    -- VECTOR OPERATION: Calculate distance between treatment descriptions
    -- 0 means identical, small numbers mean very similar
    ROUND(VECTOR_DISTANCE(
        t1.description_embedding, 
        t2.description_embedding, 
        COSINE
    ), 4) as similarity_score
FROM 
    treatments_nodes t1,
    treatments_nodes t2
WHERE 
    t1.entity_name = 'Semaglutide'
    AND t2.entity_name != 'Semaglutide'
ORDER BY similarity_score ASC  -- Lower distance = More similar
FETCH FIRST 5 ROWS ONLY;

PROMPT
PROMPT ======================================================================
-- QUERY 2: 3-Model Fusion - Patients + Similar Treatments + Evidence
PROMPT ======================================================================
PROMPT This combines:
PROMPT 1. (Relational) Patient data - elderly diabetics
PROMPT 2. (Vector) Find treatments similar to Semaglutide
PROMPT 3. (Graph) Show which papers mention these treatments
PROMPT ======================================================================
PROMPT

SELECT DISTINCT
    p.customer_name,
    p.age,
    p.diagnosis,
    t2.entity_name AS recommended_treatment,
    ROUND(VECTOR_DISTANCE(
        t1.description_embedding, 
        t2.description_embedding, 
        COSINE
    ), 4) as similarity_to_semaglutide,
    pa.title AS evidence_source
FROM 
    -- RELATIONAL: Patients table (Structured Data)
    patients p
    -- GRAPH: Join to their conditions via nodes
    INNER JOIN conditions_nodes c 
        ON UPPER(c.name) = UPPER(p.diagnosis)
    -- VECTOR: Find base treatment (Semaglutide)
    CROSS JOIN treatments_nodes t1
    -- GRAPH: Find all treatments for this condition (Traversal)
    INNER JOIN treats_edges te 
        ON te.to_node_id = c.node_id
    INNER JOIN treatments_nodes t2 
        ON t2.node_id = te.from_node_id
    -- GRAPH: Find papers mentioning the treatment (Evidence)
    INNER JOIN mentions_edges me 
        ON me.to_node_id = t2.node_id
    INNER JOIN papers_nodes pa 
        ON pa.node_id = me.from_node_id
WHERE 
    p.age >= 65
    AND t1.entity_name = 'Semaglutide'
    AND t2.entity_name != 'Semaglutide'
    -- VECTOR FILTER: Only show treatments similar to Semaglutide (< 0.3 distance)
    AND VECTOR_DISTANCE(
        t1.description_embedding, 
        t2.description_embedding, 
        COSINE
    ) < 0.3  -- High similarity threshold
ORDER BY 
    p.customer_name,
    similarity_to_semaglutide ASC
FETCH FIRST 20 ROWS ONLY;

PROMPT
PROMPT ======================================================================
-- QUERY 3: Paper Similarity - Find Related Research
PROMPT ======================================================================
PROMPT Goal: Find papers semantically similar to the diabetes study
PROMPT (Vector search on paper content embeddings)
PROMPT ======================================================================
PROMPT

SELECT 
    p1.title AS base_paper,
    p2.title AS similar_paper,
    -- VECTOR OPERATION: Compare entire document content embeddings
    ROUND(VECTOR_DISTANCE(
        p1.content_embedding, 
        p2.content_embedding, 
        COSINE
    ), 4) as similarity_score
FROM 
    papers_nodes p1,
    papers_nodes p2
WHERE 
    p1.filename = 'diabetes-treatment-study.pdf'
    AND p2.filename != 'diabetes-treatment-study.pdf'
ORDER BY similarity_score ASC;

PROMPT
PROMPT ======================================================================
-- QUERY 4: Value-Based Analysis - Effectiveness vs. Cost
PROMPT ======================================================================
PROMPT Goal: Find high-value treatments similar to Semaglutide
PROMPT Metric: Value Score = Effectiveness / (Monthly Cost / 100)
PROMPT ======================================================================
PROMPT

SELECT 
    t.entity_name AS treatment,
    co.monthly_cost,
    co.effectiveness_score,
    -- CALCULATION: ROI metric (Value Score)
    ROUND(co.effectiveness_score / (co.monthly_cost / 100), 2) AS value_score,
    ROUND(VECTOR_DISTANCE(
        t.description_embedding, 
        anchor.description_embedding, 
        COSINE
    ), 4) as similarity_to_semaglutide
FROM 
    treatments_nodes t,
    treatments_nodes anchor,
    -- RELATIONAL: Clinical Outcomes table with Cost data
    clinical_outcomes co
WHERE 
    anchor.entity_name = 'Semaglutide'
    AND t.entity_name = co.treatment_name
    -- VECTOR FILTER: Filter for relevant (similar) treatments
    AND VECTOR_DISTANCE(
        t.description_embedding, 
        anchor.description_embedding, 
        COSINE
    ) < 0.25
ORDER BY 
    value_score DESC;

PROMPT
PROMPT ======================================================================
-- =====================================================================
-- QUERY 5: The "Wow" Factor - Clinical Decision Support Engine
-- =====================================================================
-- Scenario: "David Thompson" (81, Diabetic) needs a treatment that is:
-- 1. MODERN: Conceptually similar to SGLT2 Inhibitors (Vector Search)
-- 2. SAFE: Side Effect Risk < 3 and Age Appropriate (Relational)
-- 3. PROVEN: Cited in actual clinical trials (Graph Traversal)
-- =====================================================================

SET SQLBLANKLINES ON

-- CTE (Common Table Expression) to pre-calculate Vector Distance
-- This allows us to sort/filter by relevance BEFORE grouping aggregations
WITH relevance_cte AS (
    SELECT 
        t.node_id,
        t.entity_name,
        co.effectiveness_score,
        co.side_effect_risk,
        -- VECTOR OPERATION: Calculate Cosine Similarity to "Dapagliflozin"
        -- Lower distance = Higher semantic similarity
        -- "Dapagliflozin" is our anchor for "Modern Cardiovascular Treatment"
        ROUND(VECTOR_DISTANCE(
            t.description_embedding, 
            anchor.description_embedding, 
            COSINE
        ), 4) as relevance_score
    FROM 
        treatments_nodes t
        -- CROSS JOIN allows us to compare every treatment against our anchor
        CROSS JOIN treatments_nodes anchor
        -- RELATIONAL JOIN: Get safety/cost data from standard tables
        JOIN clinical_outcomes co ON t.entity_name = co.treatment_name
    WHERE 
        anchor.entity_name = 'Dapagliflozin'
        -- RELATIONAL FILTER: "Safety First" - Filter out high-risk drugs
        AND co.side_effect_risk < 3
        -- RELATIONAL FILTER: Age Appropriateness Check (for 81-year-old)
        AND (co.recommended_max_age IS NULL OR co.recommended_max_age >= 81)
)
SELECT 
    'David Thompson (81)' AS patient,
    r.entity_name AS recommended_treatment,
    r.effectiveness_score,
    r.side_effect_risk,
    -- GRAPH OPERATION: Count distinct papers citing this treatment
    -- Proves the AI isn't hallucinating - backing it with evidence
    COUNT(DISTINCT p.node_id) as num_papers_citing,
    r.relevance_score
FROM 
    relevance_cte r
    -- GRAPH TRAVERSAL: Treatment <- MENTIONS <- Paper
    JOIN mentions_edges m ON r.node_id = m.to_node_id
    JOIN papers_nodes p ON m.from_node_id = p.node_id
    -- GRAPH TRAVERSAL: Treatment -> TREATS -> Condition -> Patient Diagnosis
    -- Ensures the drug actually treats the patient's specific condition
    JOIN treats_edges te ON r.node_id = te.from_node_id
    JOIN conditions_nodes c ON te.to_node_id = c.node_id
    JOIN patients pat ON UPPER(c.name) = UPPER(pat.diagnosis)
WHERE 
    pat.customer_name = 'David Thompson'
    -- VECTOR FILTER: Only show highly relevant (similar) treatments
    AND r.relevance_score < 0.4
GROUP BY 
    r.entity_name, r.effectiveness_score, r.side_effect_risk, r.relevance_score
ORDER BY 
    r.effectiveness_score DESC;

PROMPT
PROMPT ======================================================================
PROMPT DEMO SUMMARY
PROMPT ======================================================================
PROMPT The "Wow" Factor:
PROMPT
PROMPT 1. COMPLEXITY -> SIMPLICITY
PROMPT    You just ran a "Semantic Clinical Decision Support System" in ONE SQL query.
PROMPT    No vector DB, no graph DB, no complex glue code. Just Oracle.
PROMPT
PROMPT 2. AI SAFETY
PROMPT    Notice how we filtered by "Side Effect Risk < 3"? 
PROMPT    This is "Safe AI" - LLM intelligence constrained by hard clinical data.
PROMPT
PROMPT 3. EXPLAINABILITY
PROMPT    Every recommendation is backed by citations (Graph).
PROMPT ======================================================================

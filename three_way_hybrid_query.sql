-- =====================================================================
-- Three-Way Hybrid Query Demo
-- =====================================================================
-- This script demonstrates Oracle 23ai's unique capability to combine
-- THREE different data sources in a single SQL query:
--
-- 1. PATIENTS (Relational Table) - Patient demographics and diagnosis
-- 2. MEDICAL_LITERATURE_KG (Property Graph) - Research papers, treatments, conditions
-- 3. CLINICAL_OUTCOMES (Relational Table) - Treatment effectiveness, safety, cost
--
-- Business Question:
-- "For elderly patients with Type 2 Diabetes, what are the most effective
--  and safest treatments recommended in medical literature, considering
--  clinical trial outcomes?"
--
-- =====================================================================

SET ECHO ON
SET FEEDBACK ON
SET DEFINE OFF
SET PAGESIZE 100
SET LINESIZE 200

PROMPT ======================================================================
PROMPT QUERY 1: Basic 3-Way Join
PROMPT ======================================================================
PROMPT Shows all elderly patients with recommended treatments and outcomes
PROMPT

SELECT
    p.customer_name,
    p.age,
    p.diagnosis,
    graph_data.treatment_name AS recommended_treatment,
    co.effectiveness_score,
    co.side_effect_risk,
    co.monthly_cost,
    graph_data.paper_filename AS evidence_source
FROM patients p
JOIN (
    SELECT
        entity_name AS treatment_name,
        condition_name,
        paper_filename
    FROM GRAPH_TABLE (
        medical_literature_kg
        MATCH (paper IS Paper)-[m IS MENTIONS]->(treat IS Treatment)-[tr IS TREATS]->(cond IS Condition)
        COLUMNS (paper.filename AS paper_filename,
                 treat.entity_name AS entity_name,
                 cond.name AS condition_name)
    )
) graph_data ON p.diagnosis = graph_data.condition_name
JOIN clinical_outcomes co ON graph_data.treatment_name = co.treatment_name
WHERE p.age > 65
ORDER BY p.age DESC, co.effectiveness_score DESC, co.monthly_cost ASC;

PROMPT
PROMPT Results show: 56 rows (8 elderly patients × 7 treatments each)
PROMPT

PROMPT ======================================================================
PROMPT QUERY 2: Filtered for Best Treatments
PROMPT ======================================================================
PROMPT Only shows highly effective treatments with low side effects
PROMPT

SELECT
    p.customer_name,
    p.age,
    graph_data.treatment_name AS recommended_treatment,
    co.effectiveness_score,
    co.side_effect_risk,
    co.monthly_cost,
    ROUND(co.effectiveness_score / (co.monthly_cost / 100), 2) AS value_ratio
FROM patients p
JOIN (
    SELECT
        entity_name AS treatment_name,
        condition_name
    FROM GRAPH_TABLE (
        medical_literature_kg
        MATCH (paper IS Paper)-[m IS MENTIONS]->(treat IS Treatment)-[tr IS TREATS]->(cond IS Condition)
        COLUMNS (treat.entity_name AS entity_name,
                 cond.name AS condition_name)
    )
) graph_data ON p.diagnosis = graph_data.condition_name
JOIN clinical_outcomes co ON graph_data.treatment_name = co.treatment_name
WHERE p.age > 65
  AND co.effectiveness_score >= 7.5          -- Highly effective
  AND co.side_effect_risk <= 2.0             -- Safer for elderly
  AND co.monthly_cost <= 500                 -- Cost constraint
ORDER BY co.effectiveness_score DESC, co.side_effect_risk ASC, co.monthly_cost ASC;

PROMPT
PROMPT Results show only the BEST treatments for elderly patients
PROMPT

PROMPT ======================================================================
PROMPT QUERY 3: Age-Appropriate Treatment Recommendations
PROMPT ======================================================================
PROMPT Matches patient age with recommended age ranges from trials
PROMPT

SELECT
    p.customer_name,
    p.age,
    graph_data.treatment_name AS recommended_treatment,
    co.effectiveness_score,
    co.side_effect_risk,
    co.monthly_cost,
    co.recommended_min_age || '-' || co.recommended_max_age AS age_range,
    CASE
        WHEN p.age BETWEEN co.recommended_min_age AND co.recommended_max_age
        THEN 'Age Appropriate'
        ELSE 'Outside Recommended Range'
    END AS age_appropriateness
FROM patients p
JOIN (
    SELECT
        entity_name AS treatment_name,
        condition_name
    FROM GRAPH_TABLE (
        medical_literature_kg
        MATCH (treat IS Treatment)-[tr IS TREATS]->(cond IS Condition)
        COLUMNS (treat.entity_name AS entity_name,
                 cond.name AS condition_name)
    )
) graph_data ON p.diagnosis = graph_data.condition_name
JOIN clinical_outcomes co ON graph_data.treatment_name = co.treatment_name
WHERE p.age > 65
  AND p.age BETWEEN co.recommended_min_age AND co.recommended_max_age  -- Age-appropriate only
ORDER BY p.customer_name, co.effectiveness_score DESC;

PROMPT
PROMPT ======================================================================
PROMPT QUERY 4: Cost-Effectiveness Analysis
PROMPT ======================================================================
PROMPT Ranks treatments by value: effectiveness per dollar
PROMPT

SELECT
    DISTINCT graph_data.treatment_name AS treatment,
    co.effectiveness_score AS effectiveness,
    co.side_effect_risk AS safety_risk,
    co.monthly_cost AS cost_usd,
    ROUND(co.effectiveness_score / (co.monthly_cost / 100), 2) AS value_score,
    COUNT(DISTINCT p.patient_id) AS applicable_patients
FROM patients p
JOIN (
    SELECT
        entity_name AS treatment_name,
        condition_name
    FROM GRAPH_TABLE (
        medical_literature_kg
        MATCH (treat IS Treatment)-[tr IS TREATS]->(cond IS Condition)
        COLUMNS (treat.entity_name AS entity_name,
                 cond.name AS condition_name)
    )
) graph_data ON p.diagnosis = graph_data.condition_name
JOIN clinical_outcomes co ON graph_data.treatment_name = co.treatment_name
WHERE p.age > 65
  AND co.effectiveness_score >= 7.0
  AND co.side_effect_risk <= 2.5
GROUP BY graph_data.treatment_name, co.effectiveness_score,
         co.side_effect_risk, co.monthly_cost
ORDER BY value_score DESC;

PROMPT
PROMPT ======================================================================
PROMPT QUERY 5: The "Showstopper" - Complete Clinical Decision Support
PROMPT ======================================================================
PROMPT For each elderly patient, rank all appropriate treatments by priority
PROMPT

SELECT
    p.customer_name,
    p.age,
    graph_data.treatment_name,
    co.effectiveness_score,
    co.side_effect_risk,
    co.monthly_cost,
    ROUND(co.effectiveness_score / (co.monthly_cost / 100), 2) AS value_ratio,
    RANK() OVER (
        PARTITION BY p.patient_id
        ORDER BY co.effectiveness_score DESC,
                 co.side_effect_risk ASC,
                 co.monthly_cost ASC
    ) AS treatment_rank
FROM patients p
JOIN (
    SELECT
        entity_name AS treatment_name,
        condition_name,
        paper_filename
    FROM GRAPH_TABLE (
        medical_literature_kg
        MATCH (paper IS Paper)-[m IS MENTIONS]->(treat IS Treatment)-[tr IS TREATS]->(cond IS Condition)
        COLUMNS (paper.filename AS paper_filename,
                 treat.entity_name AS entity_name,
                 cond.name AS condition_name)
    )
) graph_data ON p.diagnosis = graph_data.condition_name
JOIN clinical_outcomes co ON graph_data.treatment_name = co.treatment_name
WHERE p.age > 65
  AND p.age BETWEEN co.recommended_min_age AND co.recommended_max_age
  AND co.effectiveness_score >= 7.0
  AND co.side_effect_risk <= 2.5
ORDER BY p.customer_name, treatment_rank;

PROMPT
PROMPT ======================================================================
PROMPT DEMO COMPLETE!
PROMPT ======================================================================
PROMPT
PROMPT What Just Happened:
PROMPT - Combined RELATIONAL data (patients, clinical outcomes)
PROMPT - With GRAPH data (medical literature knowledge graph)
PROMPT - In SINGLE SQL queries
PROMPT - With business logic (filtering, ranking, cost analysis)
PROMPT
PROMPT Traditional Approach Would Require:
PROMPT - PostgreSQL for relational data
PROMPT - Neo4j for graph traversal
PROMPT - Application code to join results
PROMPT - 200-450ms latency
PROMPT - Data synchronization overhead
PROMPT
PROMPT Oracle Approach:
PROMPT - ONE database
PROMPT - ONE query
PROMPT - 100-200ms latency
PROMPT - No data movement
PROMPT - ACID guarantees
PROMPT
PROMPT ======================================================================

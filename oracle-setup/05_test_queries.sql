-- ============================================================================
-- Oracle Hybrid Query POC - Step 5: Test Queries
-- ============================================================================
-- This script demonstrates Oracle's hybrid query capability, combining
-- relational and graph data in a single SQL statement.
--
-- Queries demonstrated:
--   1. Simple relational query
--   2. Simple graph query using GRAPH_TABLE
--   3. HYBRID query combining relational + graph
--
-- Author: Oracle GraphRAG POC
-- ============================================================================

SET LINESIZE 200
SET PAGESIZE 100
COLUMN customer_name FORMAT A25
COLUMN diagnosis FORMAT A20
COLUMN filename FORMAT A35
COLUMN entity_name FORMAT A25
COLUMN age FORMAT 999

PROMPT
PROMPT ============================================================================
PROMPT TEST QUERY 1: Simple Relational Query
PROMPT ============================================================================
PROMPT Query: Find all elderly patients (age > 65) with Type 2 Diabetes
PROMPT

SELECT patient_id, customer_name, age, diagnosis, primary_physician
FROM patients
WHERE age > 65
  AND diagnosis = 'Type 2 Diabetes'
ORDER BY age DESC;

PROMPT
PROMPT ============================================================================
PROMPT TEST QUERY 2: Simple Graph Query
PROMPT ============================================================================
PROMPT Query: Find all treatments mentioned in papers that treat Type 2 Diabetes
PROMPT

SELECT DISTINCT d.filename, e.entity_name, c.name AS condition_name
FROM GRAPH_TABLE (
    medical_literature_kg
    MATCH (d:Paper)-[:MENTIONS]->(e:Treatment)-[:TREATS]->(c:Condition)
    WHERE c.name = 'Type 2 Diabetes'
    COLUMNS (d.filename, e.entity_name, c.name)
)
ORDER BY e.entity_name;

PROMPT
PROMPT ============================================================================
PROMPT TEST QUERY 3: HYBRID QUERY (The Main Demo!)
PROMPT ============================================================================
PROMPT Query: Find elderly patients and treatments from research papers
PROMPT        that treat their specific diagnosis
PROMPT
PROMPT This is Oracle's unique capability: One SQL statement combining
PROMPT relational patient data with graph knowledge!
PROMPT

SELECT
    p.customer_name,
    p.age,
    p.diagnosis,
    d.filename,
    e.entity_name AS treatment_mentioned
FROM patients p
    JOIN GRAPH_TABLE (
        medical_literature_kg
        MATCH (d:Paper)-[:MENTIONS]->(e:Treatment)-[:TREATS]->(c:Condition)
        WHERE c.name = p.diagnosis
        COLUMNS (d.filename, e.entity_name)
    )
WHERE p.age > 65
ORDER BY p.age DESC, e.entity_name;

PROMPT
PROMPT ============================================================================
PROMPT Additional Hybrid Query Examples
PROMPT ============================================================================
PROMPT

PROMPT Query 4: Count treatments per elderly patient diagnosis
PROMPT

SELECT
    p.diagnosis,
    COUNT(DISTINCT e.entity_name) AS treatment_count,
    COUNT(DISTINCT p.patient_id) AS patient_count
FROM patients p
    JOIN GRAPH_TABLE (
        medical_literature_kg
        MATCH (d:Paper)-[:MENTIONS]->(e:Treatment)-[:TREATS]->(c:Condition)
        WHERE c.name = p.diagnosis
        COLUMNS (e.entity_name)
    )
WHERE p.age > 65
GROUP BY p.diagnosis;

PROMPT
PROMPT Query 5: Find specific patient treatments with doctor info
PROMPT

SELECT
    p.customer_name,
    p.age,
    p.primary_physician,
    e.entity_name AS recommended_treatment,
    d.filename AS research_source
FROM patients p
    JOIN GRAPH_TABLE (
        medical_literature_kg
        MATCH (d:Paper)-[:MENTIONS]->(e:Treatment)-[:TREATS]->(c:Condition)
        WHERE c.name = p.diagnosis
        COLUMNS (d.filename, e.entity_name)
    )
WHERE p.customer_name = 'John Anderson'
ORDER BY e.entity_name;

PROMPT
PROMPT Query 6: Graph-only query - Find all treatment pathways
PROMPT

SELECT
    d.filename AS paper,
    e.entity_name AS treatment,
    c.name AS treats_condition
FROM GRAPH_TABLE (
    medical_literature_kg
    MATCH (d:Paper)-[:MENTIONS]->(e:Treatment)-[:TREATS]->(c:Condition)
    COLUMNS (d.filename, e.entity_name, c.name)
)
ORDER BY c.name, e.entity_name;

PROMPT
PROMPT ============================================================================
PROMPT Performance Comparison Demonstration
PROMPT ============================================================================
PROMPT
PROMPT Oracle Hybrid Query Advantage:
PROMPT   • Single SQL statement (this file)
PROMPT   • Zero round-trips between relational and graph
PROMPT   • ACID guarantees across both data types
PROMPT   • Estimated latency: 100-200ms
PROMPT
PROMPT vs. Multi-System Approach (Neo4j + PostgreSQL):
PROMPT   • Requires 2 separate queries
PROMPT   • Application-layer join logic
PROMPT   • Data synchronization overhead
PROMPT   • Estimated latency: 200-450ms
PROMPT
PROMPT ============================================================================
PROMPT Test queries completed!
PROMPT ============================================================================
PROMPT

-- Optional: Show execution plan for hybrid query
PROMPT To see execution plan for hybrid query, run:
PROMPT
PROMPT   EXPLAIN PLAN FOR
PROMPT   SELECT p.customer_name, e.entity_name
PROMPT   FROM patients p
PROMPT       JOIN GRAPH_TABLE (
PROMPT           medical_literature_kg
PROMPT           MATCH (d:Paper)-[:MENTIONS]->(e:Treatment)-[:TREATS]->(c:Condition)
PROMPT           WHERE c.name = p.diagnosis
PROMPT           COLUMNS (e.entity_name)
PROMPT       )
PROMPT   WHERE p.age > 65;
PROMPT
PROMPT   SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
PROMPT

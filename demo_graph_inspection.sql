-- ============================================================================
-- Demo: Graph Inspection (Looking Under the Hood)
-- ============================================================================
-- Before we query the graph, let's see what the AI actually created.
-- We will look at the Nodes (Treatments/Conditions) and Edges (Relationships).
-- ============================================================================

SET LINESIZE 200
SET PAGESIZE 100
COLUMN entity_name FORMAT A30
COLUMN treatment_type FORMAT A30
COLUMN from_node FORMAT A20
COLUMN to_node FORMAT A20
COLUMN relation FORMAT A15

PROMPT 
PROMPT ============================================================================
PROMPT QUERY 1: Inspect Nodes (What did the AI find?)
PROMPT ============================================================================
PROMPT Showing top 5 extracted Treatments (with their Vector Embeddings hidden)...
PROMPT

SELECT entity_name, treatment_type 
FROM treatments_nodes 
FETCH FIRST 5 ROWS ONLY;

PROMPT 
PROMPT ============================================================================
PROMPT QUERY 2: Inspect Edges (How are they connected?)
PROMPT ============================================================================
PROMPT Showing relationships: Condition <- TREATS <- Treatment
PROMPT

SELECT 
    c.name AS condition_name,
    '<- TREATS -' AS relation,
    t.entity_name AS treatment_name
FROM 
    treats_edges te
    JOIN conditions_nodes c ON c.node_id = te.to_node_id
    JOIN treatments_nodes t ON t.node_id = te.from_node_id
FETCH FIRST 5 ROWS ONLY;

PROMPT 
PROMPT ============================================================================
PROMPT SUMMARY:
PROMPT The AI has successfully populated our graph tables with entities and 
PROMPT relationships extracted from the PDF.
PROMPT 
PROMPT Next: Let's use this graph to find treatments for David.
PROMPT ============================================================================
PROMPT

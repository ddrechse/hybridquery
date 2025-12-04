-- ============================================================================
-- Oracle Hybrid Query POC - Step 3: Create Property Graph
-- ============================================================================
-- This script creates the Oracle Property Graph from the node and edge tables.
--
-- Graph created:
--   - MEDICAL_LITERATURE_KG: Knowledge graph of medical literature
--
-- Graph schema:
--   Nodes: Paper, Treatment, Condition
--   Edges: MENTIONS (Paper -> Treatment), TREATS (Treatment -> Condition)
--
-- Author: Oracle GraphRAG POC
-- ============================================================================

-- Drop existing property graph if it exists
BEGIN
    EXECUTE IMMEDIATE 'DROP PROPERTY GRAPH medical_literature_kg';
EXCEPTION
    WHEN OTHERS THEN
        IF SQLCODE != -40926 THEN  -- ORA-40926: property graph does not exist
            RAISE;
        END IF;
END;
/

-- ============================================================================
-- CREATE PROPERTY GRAPH
-- ============================================================================

CREATE PROPERTY GRAPH medical_literature_kg
    VERTEX TABLES (
        -- Paper vertices
        papers_nodes AS Paper
            KEY (node_id)
            PROPERTIES (node_id, filename, title, publication_date),

        -- Treatment vertices
        treatments_nodes AS Treatment
            KEY (node_id)
            PROPERTIES (node_id, entity_name, treatment_type),

        -- Condition vertices
        conditions_nodes AS Condition
            KEY (node_id)
            PROPERTIES (node_id, name, icd10_code)
    )
    EDGE TABLES (
        -- MENTIONS edges: Paper -> Treatment
        mentions_edges AS MENTIONS
            KEY (edge_id)
            SOURCE KEY (from_node_id) REFERENCES Paper (node_id)
            DESTINATION KEY (to_node_id) REFERENCES Treatment (node_id)
            PROPERTIES (edge_id),

        -- TREATS edges: Treatment -> Condition
        treats_edges AS TREATS
            KEY (edge_id)
            SOURCE KEY (from_node_id) REFERENCES Treatment (node_id)
            DESTINATION KEY (to_node_id) REFERENCES Condition (node_id)
            PROPERTIES (edge_id)
    );

COMMIT;

PROMPT
PROMPT ============================================================================
PROMPT Property Graph created successfully!
PROMPT
PROMPT Graph: MEDICAL_LITERATURE_KG
PROMPT
PROMPT Vertex Labels:
PROMPT   - Paper (from papers_nodes)
PROMPT   - Treatment (from treatments_nodes)
PROMPT   - Condition (from conditions_nodes)
PROMPT
PROMPT Edge Labels:
PROMPT   - MENTIONS (Paper -> Treatment)
PROMPT   - TREATS (Treatment -> Condition)
PROMPT
PROMPT Graph Pattern:
PROMPT   (Paper)-[:MENTIONS]->(Treatment)-[:TREATS]->(Condition)
PROMPT
PROMPT Next step: Run 04_load_sample_data.sql
PROMPT ============================================================================
PROMPT

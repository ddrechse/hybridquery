-- ============================================================================
-- Oracle Hybrid Query POC - Step 2: Create Property Graph Tables
-- ============================================================================
-- This script creates the node and edge tables for the medical literature
-- knowledge graph.
--
-- Tables created:
--   NODE TABLES:
--     - PAPERS_NODES: Medical research papers
--     - TREATMENTS_NODES: Medical treatments/therapies
--     - CONDITIONS_NODES: Medical conditions/diseases
--
--   EDGE TABLES:
--     - MENTIONS_EDGES: Papers mentioning treatments
--     - TREATS_EDGES: Treatments that treat conditions
--
-- Author: Oracle GraphRAG POC
-- ============================================================================

-- Drop existing tables if they exist
BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE mentions_edges CASCADE CONSTRAINTS';
    EXECUTE IMMEDIATE 'DROP TABLE treats_edges CASCADE CONSTRAINTS';
    EXECUTE IMMEDIATE 'DROP TABLE papers_nodes CASCADE CONSTRAINTS';
    EXECUTE IMMEDIATE 'DROP TABLE treatments_nodes CASCADE CONSTRAINTS';
    EXECUTE IMMEDIATE 'DROP TABLE conditions_nodes CASCADE CONSTRAINTS';
EXCEPTION
    WHEN OTHERS THEN
        IF SQLCODE != -942 THEN
            RAISE;
        END IF;
END;
/

-- ============================================================================
-- NODE TABLES
-- ============================================================================

-- Papers (research documents)
CREATE TABLE papers_nodes (
    node_id          NUMBER PRIMARY KEY,
    filename         VARCHAR2(200) NOT NULL,
    title            VARCHAR2(500),
    publication_date DATE
);

COMMENT ON TABLE papers_nodes IS 'Medical research papers and documents';
COMMENT ON COLUMN papers_nodes.node_id IS 'Unique node identifier';
COMMENT ON COLUMN papers_nodes.filename IS 'Original document filename';
COMMENT ON COLUMN papers_nodes.title IS 'Paper title';
COMMENT ON COLUMN papers_nodes.publication_date IS 'Publication date';

-- Treatments (medical interventions)
CREATE TABLE treatments_nodes (
    node_id         NUMBER PRIMARY KEY,
    entity_name     VARCHAR2(200) NOT NULL,
    treatment_type  VARCHAR2(100)
);

COMMENT ON TABLE treatments_nodes IS 'Medical treatments and therapeutic interventions';
COMMENT ON COLUMN treatments_nodes.node_id IS 'Unique node identifier';
COMMENT ON COLUMN treatments_nodes.entity_name IS 'Treatment name (e.g., "Metformin", "Insulin Therapy")';
COMMENT ON COLUMN treatments_nodes.treatment_type IS 'Type of treatment (e.g., "Pharmaceutical", "Lifestyle")';

-- Conditions (diseases/diagnoses)
CREATE TABLE conditions_nodes (
    node_id     NUMBER PRIMARY KEY,
    name        VARCHAR2(200) NOT NULL,
    icd10_code  VARCHAR2(20)
);

COMMENT ON TABLE conditions_nodes IS 'Medical conditions and diseases';
COMMENT ON COLUMN conditions_nodes.node_id IS 'Unique node identifier';
COMMENT ON COLUMN conditions_nodes.name IS 'Condition name (e.g., "Type 2 Diabetes")';
COMMENT ON COLUMN conditions_nodes.icd10_code IS 'ICD-10 diagnostic code';

-- ============================================================================
-- EDGE TABLES
-- ============================================================================

-- MENTIONS edges: Paper -> Treatment
CREATE TABLE mentions_edges (
    edge_id       NUMBER PRIMARY KEY,
    from_node_id  NUMBER NOT NULL,  -- References papers_nodes.node_id
    to_node_id    NUMBER NOT NULL,  -- References treatments_nodes.node_id

    CONSTRAINT fk_mentions_from FOREIGN KEY (from_node_id)
        REFERENCES papers_nodes(node_id) ON DELETE CASCADE,
    CONSTRAINT fk_mentions_to FOREIGN KEY (to_node_id)
        REFERENCES treatments_nodes(node_id) ON DELETE CASCADE
);

COMMENT ON TABLE mentions_edges IS 'Papers that mention specific treatments';
COMMENT ON COLUMN mentions_edges.edge_id IS 'Unique edge identifier';
COMMENT ON COLUMN mentions_edges.from_node_id IS 'Source paper node';
COMMENT ON COLUMN mentions_edges.to_node_id IS 'Target treatment node';

-- TREATS edges: Treatment -> Condition
CREATE TABLE treats_edges (
    edge_id       NUMBER PRIMARY KEY,
    from_node_id  NUMBER NOT NULL,  -- References treatments_nodes.node_id
    to_node_id    NUMBER NOT NULL,  -- References conditions_nodes.node_id

    CONSTRAINT fk_treats_from FOREIGN KEY (from_node_id)
        REFERENCES treatments_nodes(node_id) ON DELETE CASCADE,
    CONSTRAINT fk_treats_to FOREIGN KEY (to_node_id)
        REFERENCES conditions_nodes(node_id) ON DELETE CASCADE
);

COMMENT ON TABLE treats_edges IS 'Treatments that treat specific conditions';
COMMENT ON COLUMN treats_edges.edge_id IS 'Unique edge identifier';
COMMENT ON COLUMN treats_edges.from_node_id IS 'Source treatment node';
COMMENT ON COLUMN treats_edges.to_node_id IS 'Target condition node';

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

CREATE INDEX idx_mentions_from ON mentions_edges(from_node_id);
CREATE INDEX idx_mentions_to ON mentions_edges(to_node_id);
CREATE INDEX idx_treats_from ON treats_edges(from_node_id);
CREATE INDEX idx_treats_to ON treats_edges(to_node_id);
CREATE INDEX idx_treatments_name ON treatments_nodes(entity_name);
CREATE INDEX idx_conditions_name ON conditions_nodes(name);

COMMIT;

PROMPT
PROMPT ============================================================================
PROMPT Graph tables created successfully!
PROMPT
PROMPT Created node tables:
PROMPT   - PAPERS_NODES
PROMPT   - TREATMENTS_NODES
PROMPT   - CONDITIONS_NODES
PROMPT
PROMPT Created edge tables:
PROMPT   - MENTIONS_EDGES (Paper -> Treatment)
PROMPT   - TREATS_EDGES (Treatment -> Condition)
PROMPT
PROMPT Next step: Run 03_create_property_graph.sql
PROMPT ============================================================================
PROMPT

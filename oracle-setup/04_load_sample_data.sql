-- ============================================================================
-- Oracle Hybrid Query POC - Step 4: Load Sample Data
-- ============================================================================
-- This script loads sample data into all tables.
--
-- Data loaded:
--   - PATIENTS: 10 patient records
--   - PAPERS_NODES: 1 research paper
--   - TREATMENTS_NODES: 7 diabetes treatments
--   - CONDITIONS_NODES: 2 diabetes conditions
--   - MENTIONS_EDGES: Paper-to-treatment relationships
--   - TREATS_EDGES: Treatment-to-condition relationships
--
-- Author: Oracle GraphRAG POC
-- ============================================================================

-- ============================================================================
-- LOAD RELATIONAL DATA (PATIENTS)
-- ============================================================================

PROMPT Loading patient data...

INSERT INTO patients (patient_id, customer_name, age, diagnosis, admission_date, primary_physician)
VALUES (1001, 'John Anderson', 72, 'Type 2 Diabetes', DATE '2024-01-15', 'Dr. Sarah Mitchell');

INSERT INTO patients (patient_id, customer_name, age, diagnosis, admission_date, primary_physician)
VALUES (1002, 'Maria Garcia', 68, 'Type 2 Diabetes', DATE '2024-02-03', 'Dr. James Chen');

INSERT INTO patients (patient_id, customer_name, age, diagnosis, admission_date, primary_physician)
VALUES (1003, 'Robert Chen', 45, 'Type 1 Diabetes', DATE '2024-01-22', 'Dr. Sarah Mitchell');

INSERT INTO patients (patient_id, customer_name, age, diagnosis, admission_date, primary_physician)
VALUES (1004, 'Jennifer Williams', 78, 'Type 2 Diabetes', DATE '2024-02-18', 'Dr. Michael Brown');

INSERT INTO patients (patient_id, customer_name, age, diagnosis, admission_date, primary_physician)
VALUES (1005, 'David Thompson', 81, 'Type 2 Diabetes', DATE '2024-03-05', 'Dr. Sarah Mitchell');

INSERT INTO patients (patient_id, customer_name, age, diagnosis, admission_date, primary_physician)
VALUES (1006, 'Lisa Martinez', 52, 'Type 1 Diabetes', DATE '2024-01-30', 'Dr. James Chen');

INSERT INTO patients (patient_id, customer_name, age, diagnosis, admission_date, primary_physician)
VALUES (1007, 'Michael Johnson', 69, 'Type 2 Diabetes', DATE '2024-02-14', 'Dr. Michael Brown');

INSERT INTO patients (patient_id, customer_name, age, diagnosis, admission_date, primary_physician)
VALUES (1008, 'Patricia Davis', 75, 'Type 2 Diabetes', DATE '2024-03-12', 'Dr. Sarah Mitchell');

INSERT INTO patients (patient_id, customer_name, age, diagnosis, admission_date, primary_physician)
VALUES (1009, 'James Wilson', 83, 'Type 2 Diabetes', DATE '2024-01-28', 'Dr. James Chen');

INSERT INTO patients (patient_id, customer_name, age, diagnosis, admission_date, primary_physician)
VALUES (1010, 'Mary Brown', 71, 'Type 2 Diabetes', DATE '2024-02-25', 'Dr. Michael Brown');

PROMPT   → Loaded 10 patient records

-- ============================================================================
-- LOAD GRAPH DATA - NODES
-- ============================================================================

PROMPT Loading graph nodes...

-- Paper nodes
INSERT INTO papers_nodes (node_id, filename, title, publication_date)
VALUES (1, 'diabetes_treatment_study.pdf',
        'Comparative Effectiveness of Second-Line Diabetes Treatments',
        DATE '2023-01-01');

PROMPT   → Loaded 1 paper

-- Treatment nodes
INSERT INTO treatments_nodes (node_id, entity_name, treatment_type)
VALUES (101, 'Metformin', 'Pharmaceutical');

INSERT INTO treatments_nodes (node_id, entity_name, treatment_type)
VALUES (102, 'GLP-1 Agonists', 'Pharmaceutical');

INSERT INTO treatments_nodes (node_id, entity_name, treatment_type)
VALUES (103, 'SGLT2 Inhibitors', 'Pharmaceutical');

INSERT INTO treatments_nodes (node_id, entity_name, treatment_type)
VALUES (104, 'DPP-4 Inhibitors', 'Pharmaceutical');

INSERT INTO treatments_nodes (node_id, entity_name, treatment_type)
VALUES (105, 'Insulin Therapy', 'Pharmaceutical');

INSERT INTO treatments_nodes (node_id, entity_name, treatment_type)
VALUES (106, 'Sulfonylureas', 'Pharmaceutical');

INSERT INTO treatments_nodes (node_id, entity_name, treatment_type)
VALUES (107, 'Basal Insulin', 'Pharmaceutical');

PROMPT   → Loaded 7 treatments

-- Condition nodes
INSERT INTO conditions_nodes (node_id, name, icd10_code)
VALUES (201, 'Type 1 Diabetes', 'E10');

INSERT INTO conditions_nodes (node_id, name, icd10_code)
VALUES (202, 'Type 2 Diabetes', 'E11');

PROMPT   → Loaded 2 conditions

-- ============================================================================
-- LOAD GRAPH DATA - EDGES
-- ============================================================================

PROMPT Loading graph edges...

-- MENTIONS edges (Paper -> Treatment)
-- The paper mentions all treatments
INSERT INTO mentions_edges (edge_id, from_node_id, to_node_id)
VALUES (1001, 1, 101);  -- Paper mentions Metformin

INSERT INTO mentions_edges (edge_id, from_node_id, to_node_id)
VALUES (1002, 1, 102);  -- Paper mentions GLP-1 Agonists

INSERT INTO mentions_edges (edge_id, from_node_id, to_node_id)
VALUES (1003, 1, 103);  -- Paper mentions SGLT2 Inhibitors

INSERT INTO mentions_edges (edge_id, from_node_id, to_node_id)
VALUES (1004, 1, 104);  -- Paper mentions DPP-4 Inhibitors

INSERT INTO mentions_edges (edge_id, from_node_id, to_node_id)
VALUES (1005, 1, 105);  -- Paper mentions Insulin Therapy

INSERT INTO mentions_edges (edge_id, from_node_id, to_node_id)
VALUES (1006, 1, 106);  -- Paper mentions Sulfonylureas

INSERT INTO mentions_edges (edge_id, from_node_id, to_node_id)
VALUES (1007, 1, 107);  -- Paper mentions Basal Insulin

PROMPT   → Loaded 7 MENTIONS edges

-- TREATS edges (Treatment -> Condition)
-- Map treatments to conditions
INSERT INTO treats_edges (edge_id, from_node_id, to_node_id)
VALUES (2001, 101, 202);  -- Metformin treats Type 2 Diabetes

INSERT INTO treats_edges (edge_id, from_node_id, to_node_id)
VALUES (2002, 102, 202);  -- GLP-1 Agonists treat Type 2 Diabetes

INSERT INTO treats_edges (edge_id, from_node_id, to_node_id)
VALUES (2003, 103, 202);  -- SGLT2 Inhibitors treat Type 2 Diabetes

INSERT INTO treats_edges (edge_id, from_node_id, to_node_id)
VALUES (2004, 104, 202);  -- DPP-4 Inhibitors treat Type 2 Diabetes

INSERT INTO treats_edges (edge_id, from_node_id, to_node_id)
VALUES (2005, 105, 201);  -- Insulin Therapy treats Type 1 Diabetes

INSERT INTO treats_edges (edge_id, from_node_id, to_node_id)
VALUES (2006, 105, 202);  -- Insulin Therapy treats Type 2 Diabetes

INSERT INTO treats_edges (edge_id, from_node_id, to_node_id)
VALUES (2007, 106, 202);  -- Sulfonylureas treat Type 2 Diabetes

INSERT INTO treats_edges (edge_id, from_node_id, to_node_id)
VALUES (2008, 107, 202);  -- Basal Insulin treats Type 2 Diabetes

PROMPT   → Loaded 8 TREATS edges

COMMIT;

-- ============================================================================
-- VERIFY DATA LOAD
-- ============================================================================

PROMPT
PROMPT ============================================================================
PROMPT Data loading complete! Verification summary:
PROMPT ============================================================================
PROMPT

SELECT 'Patients' AS table_name, COUNT(*) AS row_count FROM patients
UNION ALL
SELECT 'Papers', COUNT(*) FROM papers_nodes
UNION ALL
SELECT 'Treatments', COUNT(*) FROM treatments_nodes
UNION ALL
SELECT 'Conditions', COUNT(*) FROM conditions_nodes
UNION ALL
SELECT 'MENTIONS edges', COUNT(*) FROM mentions_edges
UNION ALL
SELECT 'TREATS edges', COUNT(*) FROM treats_edges;

PROMPT

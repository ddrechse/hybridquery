# Expected Query Results

This document shows the expected output from each test query in `oracle-setup/05_test_queries.sql`.

---

## Test Query 1: Simple Relational Query

**Query:**
```sql
SELECT patient_id, customer_name, age, diagnosis, primary_physician
FROM patients
WHERE age > 65 AND diagnosis = 'Type 2 Diabetes'
ORDER BY age DESC;
```

**Expected Output:**
```
PATIENT_ID CUSTOMER_NAME              AGE DIAGNOSIS            PRIMARY_PHYSICIAN
---------- ------------------------- ---- -------------------- -------------------------
      1009 James Wilson                83 Type 2 Diabetes      Dr. James Chen
      1005 David Thompson              81 Type 2 Diabetes      Dr. Sarah Mitchell
      1004 Jennifer Williams           78 Type 2 Diabetes      Dr. Michael Brown
      1008 Patricia Davis              75 Type 2 Diabetes      Dr. Sarah Mitchell
      1001 John Anderson               72 Type 2 Diabetes      Dr. Sarah Mitchell
      1010 Mary Brown                  71 Type 2 Diabetes      Dr. Michael Brown
      1007 Michael Johnson             69 Type 2 Diabetes      Dr. Michael Brown
      1002 Maria Garcia                68 Type 2 Diabetes      Dr. James Chen

8 rows selected.
```

**Notes:**
- 8 elderly patients with Type 2 Diabetes
- Sorted by age descending
- 2 patients (1003, 1006) excluded: age < 65 or Type 1 Diabetes

---

## Test Query 2: Simple Graph Query

**Query:**
```sql
SELECT DISTINCT d.filename, e.entity_name, c.name AS condition_name
FROM GRAPH_TABLE (
    medical_literature_kg
    MATCH (d:Paper)-[:MENTIONS]->(e:Treatment)-[:TREATS]->(c:Condition)
    WHERE c.name = 'Type 2 Diabetes'
    COLUMNS (d.filename, e.entity_name, c.name)
)
ORDER BY e.entity_name;
```

**Expected Output:**
```
FILENAME                            ENTITY_NAME               CONDITION_NAME
----------------------------------- ------------------------- --------------------
diabetes_treatment_study.pdf        Basal Insulin             Type 2 Diabetes
diabetes_treatment_study.pdf        DPP-4 Inhibitors          Type 2 Diabetes
diabetes_treatment_study.pdf        GLP-1 Agonists            Type 2 Diabetes
diabetes_treatment_study.pdf        Metformin                 Type 2 Diabetes
diabetes_treatment_study.pdf        SGLT2 Inhibitors          Type 2 Diabetes
diabetes_treatment_study.pdf        Sulfonylureas             Type 2 Diabetes

6 rows selected.
```

**Notes:**
- One paper mentions 6 treatments for Type 2 Diabetes
- Insulin Therapy treats both Type 1 and Type 2, so appears separately
- Graph traversal: Paper → MENTIONS → Treatment → TREATS → Condition

---

## Test Query 3: HYBRID QUERY (Main Demo)

**Query:**
```sql
SELECT p.customer_name, p.age, p.diagnosis,
       d.filename, e.entity_name AS treatment_mentioned
FROM patients p
    JOIN GRAPH_TABLE (
        medical_literature_kg
        MATCH (d:Paper)-[:MENTIONS]->(e:Treatment)-[:TREATS]->(c:Condition)
        WHERE c.name = p.diagnosis
        COLUMNS (d.filename, e.entity_name)
    )
WHERE p.age > 65
ORDER BY p.age DESC, e.entity_name;
```

**Expected Output:**
```
CUSTOMER_NAME              AGE DIAGNOSIS            FILENAME                            TREATMENT_MENTIONED
------------------------- ---- -------------------- ----------------------------------- -------------------------
James Wilson                83 Type 2 Diabetes      diabetes_treatment_study.pdf        Basal Insulin
James Wilson                83 Type 2 Diabetes      diabetes_treatment_study.pdf        DPP-4 Inhibitors
James Wilson                83 Type 2 Diabetes      diabetes_treatment_study.pdf        GLP-1 Agonists
James Wilson                83 Type 2 Diabetes      diabetes_treatment_study.pdf        Metformin
James Wilson                83 Type 2 Diabetes      diabetes_treatment_study.pdf        SGLT2 Inhibitors
James Wilson                83 Type 2 Diabetes      diabetes_treatment_study.pdf        Sulfonylureas
David Thompson              81 Type 2 Diabetes      diabetes_treatment_study.pdf        Basal Insulin
David Thompson              81 Type 2 Diabetes      diabetes_treatment_study.pdf        DPP-4 Inhibitors
David Thompson              81 Type 2 Diabetes      diabetes_treatment_study.pdf        GLP-1 Agonists
David Thompson              81 Type 2 Diabetes      diabetes_treatment_study.pdf        Metformin
David Thompson              81 Type 2 Diabetes      diabetes_treatment_study.pdf        SGLT2 Inhibitors
David Thompson              81 Type 2 Diabetes      diabetes_treatment_study.pdf        Sulfonylureas
Jennifer Williams           78 Type 2 Diabetes      diabetes_treatment_study.pdf        Basal Insulin
Jennifer Williams           78 Type 2 Diabetes      diabetes_treatment_study.pdf        DPP-4 Inhibitors
Jennifer Williams           78 Type 2 Diabetes      diabetes_treatment_study.pdf        GLP-1 Agonists
Jennifer Williams           78 Type 2 Diabetes      diabetes_treatment_study.pdf        Metformin
Jennifer Williams           78 Type 2 Diabetes      diabetes_treatment_study.pdf        SGLT2 Inhibitors
Jennifer Williams           78 Type 2 Diabetes      diabetes_treatment_study.pdf        Sulfonylureas
Patricia Davis              75 Type 2 Diabetes      diabetes_treatment_study.pdf        Basal Insulin
Patricia Davis              75 Type 2 Diabetes      diabetes_treatment_study.pdf        DPP-4 Inhibitors
Patricia Davis              75 Type 2 Diabetes      diabetes_treatment_study.pdf        GLP-1 Agonists
Patricia Davis              75 Type 2 Diabetes      diabetes_treatment_study.pdf        Metformin
Patricia Davis              75 Type 2 Diabetes      diabetes_treatment_study.pdf        SGLT2 Inhibitors
Patricia Davis              75 Type 2 Diabetes      diabetes_treatment_study.pdf        Sulfonylureas
John Anderson               72 Type 2 Diabetes      diabetes_treatment_study.pdf        Basal Insulin
John Anderson               72 Type 2 Diabetes      diabetes_treatment_study.pdf        DPP-4 Inhibitors
John Anderson               72 Type 2 Diabetes      diabetes_treatment_study.pdf        GLP-1 Agonists
John Anderson               72 Type 2 Diabetes      diabetes_treatment_study.pdf        Metformin
John Anderson               72 Type 2 Diabetes      diabetes_treatment_study.pdf        SGLT2 Inhibitors
John Anderson               72 Type 2 Diabetes      diabetes_treatment_study.pdf        Sulfonylureas
Mary Brown                  71 Type 2 Diabetes      diabetes_treatment_study.pdf        Basal Insulin
Mary Brown                  71 Type 2 Diabetes      diabetes_treatment_study.pdf        DPP-4 Inhibitors
Mary Brown                  71 Type 2 Diabetes      diabetes_treatment_study.pdf        GLP-1 Agonists
Mary Brown                  71 Type 2 Diabetes      diabetes_treatment_study.pdf        Metformin
Mary Brown                  71 Type 2 Diabetes      diabetes_treatment_study.pdf        SGLT2 Inhibitors
Mary Brown                  71 Type 2 Diabetes      diabetes_treatment_study.pdf        Sulfonylureas
Michael Johnson             69 Type 2 Diabetes      diabetes_treatment_study.pdf        Basal Insulin
Michael Johnson             69 Type 2 Diabetes      diabetes_treatment_study.pdf        DPP-4 Inhibitors
Michael Johnson             69 Type 2 Diabetes      diabetes_treatment_study.pdf        GLP-1 Agonists
Michael Johnson             69 Type 2 Diabetes      diabetes_treatment_study.pdf        Metformin
Michael Johnson             69 Type 2 Diabetes      diabetes_treatment_study.pdf        SGLT2 Inhibitors
Michael Johnson             69 Type 2 Diabetes      diabetes_treatment_study.pdf        Sulfonylureas
Maria Garcia                68 Type 2 Diabetes      diabetes_treatment_study.pdf        Basal Insulin
Maria Garcia                68 Type 2 Diabetes      diabetes_treatment_study.pdf        DPP-4 Inhibitors
Maria Garcia                68 Type 2 Diabetes      diabetes_treatment_study.pdf        GLP-1 Agonists
Maria Garcia                68 Type 2 Diabetes      diabetes_treatment_study.pdf        Metformin
Maria Garcia                68 Type 2 Diabetes      diabetes_treatment_study.pdf        SGLT2 Inhibitors
Maria Garcia                68 Type 2 Diabetes      diabetes_treatment_study.pdf        Sulfonylureas

48 rows selected.
```

**Notes:**
- **8 patients × 6 treatments = 48 rows**
- Each elderly patient with Type 2 Diabetes matched with all 6 treatments
- Single query execution combining relational and graph data
- The `WHERE c.name = p.diagnosis` clause joins graph to relational

---

## Query 4: Aggregate Hybrid Query

**Query:**
```sql
SELECT p.diagnosis,
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
```

**Expected Output:**
```
DIAGNOSIS            TREATMENT_COUNT PATIENT_COUNT
-------------------- --------------- -------------
Type 2 Diabetes                    6             8

1 row selected.
```

**Notes:**
- Aggregation works across both relational and graph data
- Shows power of hybrid queries for analytics
- No Type 1 Diabetes patients meet age criteria (age > 65)

---

## Query 5: Specific Patient Query

**Query:**
```sql
SELECT p.customer_name, p.age, p.primary_physician,
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
```

**Expected Output:**
```
CUSTOMER_NAME         AGE PRIMARY_PHYSICIAN     RECOMMENDED_TREATMENT     RESEARCH_SOURCE
--------------------- ---- --------------------- ------------------------- -----------------------------------
John Anderson           72 Dr. Sarah Mitchell    Basal Insulin             diabetes_treatment_study.pdf
John Anderson           72 Dr. Sarah Mitchell    DPP-4 Inhibitors          diabetes_treatment_study.pdf
John Anderson           72 Dr. Sarah Mitchell    GLP-1 Agonists            diabetes_treatment_study.pdf
John Anderson           72 Dr. Sarah Mitchell    Metformin                 diabetes_treatment_study.pdf
John Anderson           72 Dr. Sarah Mitchell    SGLT2 Inhibitors          diabetes_treatment_study.pdf
John Anderson           72 Dr. Sarah Mitchell    Sulfonylureas             diabetes_treatment_study.pdf

6 rows selected.
```

**Notes:**
- Personalized treatment recommendations for one patient
- Shows how hybrid queries support application-level queries
- Combines patient demographics with research-backed treatments

---

## Query 6: Graph-Only Query

**Query:**
```sql
SELECT d.filename AS paper, e.entity_name AS treatment,
       c.name AS treats_condition
FROM GRAPH_TABLE (
    medical_literature_kg
    MATCH (d:Paper)-[:MENTIONS]->(e:Treatment)-[:TREATS]->(c:Condition)
    COLUMNS (d.filename, e.entity_name, c.name)
)
ORDER BY c.name, e.entity_name;
```

**Expected Output:**
```
PAPER                               TREATMENT                 TREATS_CONDITION
----------------------------------- ------------------------- --------------------
diabetes_treatment_study.pdf        Insulin Therapy           Type 1 Diabetes
diabetes_treatment_study.pdf        Basal Insulin             Type 2 Diabetes
diabetes_treatment_study.pdf        DPP-4 Inhibitors          Type 2 Diabetes
diabetes_treatment_study.pdf        GLP-1 Agonists            Type 2 Diabetes
diabetes_treatment_study.pdf        Insulin Therapy           Type 2 Diabetes
diabetes_treatment_study.pdf        Metformin                 Type 2 Diabetes
diabetes_treatment_study.pdf        SGLT2 Inhibitors          Type 2 Diabetes
diabetes_treatment_study.pdf        Sulfonylureas             Type 2 Diabetes

8 rows selected.
```

**Notes:**
- Pure graph traversal without relational join
- Shows all treatment pathways in the knowledge graph
- Note: Insulin Therapy treats both Type 1 and Type 2 Diabetes

---

## Verification Query

**Query:**
```sql
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
```

**Expected Output:**
```
TABLE_NAME       ROW_COUNT
---------------- ---------
Patients                10
Papers                   1
Treatments               7
Conditions               2
MENTIONS edges           7
TREATS edges             8

6 rows selected.
```

**Notes:**
- Quick verification that all data loaded correctly
- Run this first if hybrid query returns unexpected results

---

## Performance Notes

**Expected Query Execution Times:**
- Simple relational query: < 10ms
- Simple graph query: 20-50ms
- Hybrid query (main demo): **100-200ms**
- Aggregate hybrid query: 100-200ms

**Factors affecting performance:**
- Database resources (CPU, memory)
- Graph loaded into PGX memory
- Index usage on patients table
- Network latency (if remote database)

---

## Troubleshooting

### If you get 0 rows on hybrid query:

**Check data exists:**
```sql
SELECT COUNT(*) FROM patients WHERE age > 65;  -- Should be 8
SELECT COUNT(*) FROM treats_edges;              -- Should be 8
```

**Check graph created:**
```sql
SELECT * FROM user_property_graphs;
-- Should show: MEDICAL_LITERATURE_KG
```

**Check joins work:**
```sql
-- Test the graph condition independently
SELECT c.name FROM GRAPH_TABLE (
    medical_literature_kg
    MATCH (c:Condition)
    COLUMNS (c.name)
);
-- Should show: Type 1 Diabetes, Type 2 Diabetes
```

---

**These results demonstrate Oracle's converged architecture delivering seamless integration between relational and graph data models!**

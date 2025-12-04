# Oracle Hybrid Query POC - Demo Walkthrough

## 🎯 Presentation Guide

This guide provides a step-by-step walkthrough for demonstrating Oracle's hybrid query capability.

**Estimated Time:** 20-30 minutes
**Audience:** Technical decision makers, architects, developers
**Goal:** Prove Oracle's unique advantage for combining relational and graph data

---

## 📋 Pre-Demo Checklist

Before starting your demo:

- [ ] Oracle Database 23ai accessible and running
- [ ] All SQL scripts executed successfully (01-04)
- [ ] Data loaded and verified
- [ ] SQL*Plus or SQLcl connection tested
- [ ] Terminal/presentation screen ready
- [ ] `05_test_queries.sql` file open and ready

---

## 🎬 Demo Script

### Part 1: Set the Context (3 minutes)

**SAY:**
> "Today I'm demonstrating Oracle's hybrid query capability - the ability to combine relational and graph data in a single SQL statement. This is something unique to Oracle's converged architecture."

**SHOW:** The presentation slide from GraphRag_Final.pdf (slide 28 - Oracle Innovation #1)

**SAY:**
> "Our use case is a medical system where we have:
> - Relational data: Patient records in traditional tables
> - Graph data: Medical research papers with treatment relationships
>
> The question we want to answer: For our elderly diabetes patients, what treatments do the latest research papers recommend?"

---

### Part 2: Show the Traditional Approach (3 minutes)

**SAY:**
> "In a traditional architecture using separate systems - say Neo4j for the graph and PostgreSQL for relational - you'd need to:
>
> 1. Query the relational database for patients
> 2. Query the graph database for treatments
> 3. Join the results in application code
>
> This requires:
> - Two separate queries
> - Two round trips
> - Application-layer join logic
> - Eventual consistency challenges
> - 200-450ms latency"

**SHOW:** Diagram or whiteboard sketch:
```
App Layer
  ↓ Query 1 (50-100ms)
PostgreSQL [Patients] → Results Set A
  ↓ Query 2 (100-300ms)
Neo4j [Treatments Graph] → Results Set B
  ↓ App Join Logic
Final Result (200-450ms total)
```

---

### Part 3: Show the Data (5 minutes)

**SAY:**
> "Let me show you the data we're working with in Oracle."

**RUN:** Simple relational query
```sql
-- Show patient data
SELECT patient_id, customer_name, age, diagnosis
FROM patients
WHERE age > 65 AND diagnosis = 'Type 2 Diabetes'
ORDER BY age DESC;
```

**POINT OUT:**
- "We have 10 patients, 8 of them elderly with Type 2 Diabetes"
- "This is standard relational data - nothing special yet"

**RUN:** Simple graph query
```sql
-- Show graph structure
SELECT DISTINCT d.filename, e.entity_name, c.name AS condition
FROM GRAPH_TABLE (
    medical_literature_kg
    MATCH (d:Paper)-[:MENTIONS]->(e:Treatment)-[:TREATS]->(c:Condition)
    WHERE c.name = 'Type 2 Diabetes'
    COLUMNS (d.filename, e.entity_name, c.name)
)
ORDER BY e.entity_name;
```

**POINT OUT:**
- "This is our knowledge graph - one research paper mentioning 6 treatments for Type 2 Diabetes"
- "The graph pattern is: Paper → MENTIONS → Treatment → TREATS → Condition"
- "Notice the GRAPH_TABLE operator - this is Oracle's way of querying property graphs"

---

### Part 4: The Hybrid Query - The Big Reveal (7 minutes)

**SAY:**
> "Now here's where Oracle shines. Watch this..."

**TYPE OUT** (or show prepared) the hybrid query:
```sql
SELECT
    p.customer_name,
    p.age,
    p.diagnosis,
    d.filename,
    e.entity_name AS treatment_recommended
FROM patients p                    -- Relational table
    JOIN GRAPH_TABLE (             -- Graph traversal
        medical_literature_kg
        MATCH (d:Paper)-[:MENTIONS]->(e:Treatment)-[:TREATS]->(c:Condition)
        WHERE c.name = p.diagnosis
        COLUMNS (d.filename, e.entity_name)
    )
WHERE p.age > 65
ORDER BY p.age DESC, e.entity_name;
```

**PAUSE** - Let them see it

**SAY:**
> "Let me highlight what's happening here:
>
> Line 6: `FROM patients p` - Standard relational FROM clause
>
> Line 7: `JOIN GRAPH_TABLE` - This is the magic. We're joining relational data with a graph traversal
>
> Line 9-10: `MATCH (d:Paper)-[:MENTIONS]->(e:Treatment)-[:TREATS]->(c:Condition)` - This is graph pattern matching in SQL
>
> Line 11: `WHERE c.name = p.diagnosis` - The graph condition **references the relational table**. This is the cross-model join.
>
> This is ONE SQL statement. ONE round trip. ACID guarantees across both data types."

**RUN THE QUERY**

**SHOW RESULTS:**
- Each elderly patient matched with 6 treatments from research
- Single query execution
- Clean, joined results

---

### Part 5: The Performance Story (5 minutes)

**SAY:**
> "Let's talk about what we just eliminated:
>
> **What we DON'T need:**
> - ❌ Separate vector search query
> - ❌ Separate graph traversal query
> - ❌ Application-layer joins
> - ❌ Data duplication/ETL between systems
> - ❌ Eventual consistency management
>
> **What we GET:**
> - ✅ One SQL statement
> - ✅ Zero round-trips between operations
> - ✅ ACID transactions across all data
> - ✅ 100-200ms latency (vs 200-450ms)
> - ✅ Native Oracle security and access control"

**RUN:** Additional example showing complexity
```sql
-- Show aggregation across both models
SELECT
    p.diagnosis,
    COUNT(DISTINCT e.entity_name) AS treatment_options,
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

**POINT OUT:**
- "We can aggregate across both models"
- "All standard SQL operations work"
- "This is production-ready, enterprise-grade SQL"

---

### Part 6: The Docling Integration (5 minutes)

**SAY:**
> "Now, how did we build this knowledge graph? We used Docling - an open-source document processing framework."

**SHOW:** The sample PDF file
```bash
cat sample-data/diabetes_treatment_study.pdf | head -50
```

**SAY:**
> "This is our source document - a medical research paper. Docling extracts:
> - Document structure (sections, headings)
> - Entity spans (treatments, conditions)
> - Relationships (which treatments treat which conditions)"

**SHOW:** The processing pipeline
```bash
cd docling-processing
ls -la
```

**SAY:**
> "Our processing pipeline:
>
> 1. `process_documents.py` - Uses Docling to parse PDFs and Excel files
> 2. `extract_entities.py` - Extracts graph entities and relationships
> 3. Outputs CSV files ready for Oracle import
>
> The beauty is: Docling handles the complexity of document understanding, and Oracle handles the complexity of querying heterogeneous data."

---

### Part 7: Scaling and Production Considerations (3 minutes)

**SAY:**
> "This is a simple demo, but the architecture scales:
>
> **In Production:**
> - Load hundreds or thousands of research papers
> - Millions of patient records
> - Add vector search for semantic similarity
> - Real-time updates as new research publishes
>
> **Key Advantages:**
> - Everything runs in the same database
> - One security model
> - One backup/recovery process
> - One connection pool
> - One SQL language"

**SHOW:** (Optional) The full hybrid query with vectors from the presentation
```sql
-- The complete version (from slide 28)
SELECT c.customer_name, d.filename, e.entity_name, p.diagnosis
FROM patients p
  JOIN GRAPH_TABLE (
    medical_literature_kg
    MATCH (d:Paper)-[:MENTIONS]->(e:Treatment)-[:TREATS]->(c:Condition)
    WHERE c.name = p.diagnosis
    COLUMNS (d.filename, e.entity_name, d.embedding)
  )
WHERE VECTOR_DISTANCE(d.embedding, :query_vector, COSINE) < 0.3
  AND p.age > 65;
```

**SAY:**
> "When you add vectors for semantic search, it's still one query. Relational + Graph + Vector. All in Oracle."

---

### Part 8: Q&A and Next Steps (5 minutes)

**Common Questions to Prepare For:**

**Q: "Does this require special Oracle licensing?"**
**A:** "Property graphs are included in Oracle Database 23ai Enterprise Edition. No separate graph database license needed."

**Q: "Can this run on existing Oracle infrastructure?"**
**A:** "Yes - if you're on 23ai. This uses built-in capabilities, no add-ons required."

**Q: "What about performance with large graphs?"**
**A:** "Oracle's property graph implementation uses in-memory PGX (Parallel Graph AnalytiX) engine. It's designed for enterprise-scale graphs with billions of edges."

**Q: "How does this compare to Neo4j's pure graph performance?"**
**A:** "For pure graph workloads, Neo4j's Cypher may be more expressive. Oracle's advantage is when you need to combine graph with relational or vector data - that's where the converged architecture shines."

**Q: "Can we use our existing BI tools with this?"**
**A:** "Yes - it's standard SQL. Any tool that connects to Oracle can query this data."

---

## 🎯 Key Takeaways to Emphasize

At the end of the demo, reinforce these points:

1. **One Platform:** Relational + Graph + Vector in a single database
2. **One Query:** No multi-step application logic required
3. **One Transaction:** ACID guarantees across all data types
4. **Performance:** 50-100ms faster than multi-system approaches
5. **Simplicity:** Familiar SQL, existing Oracle infrastructure
6. **Production Ready:** Enterprise-grade security, backup, HA

---

## 📊 Metrics to Highlight

| Capability | Oracle 23ai | Neo4j + PostgreSQL |
|------------|-------------|-------------------|
| Queries required | **1** | 2 |
| Round trips | **0** | 2 |
| Query language | **SQL** | Cypher + SQL |
| Latency | **100-200ms** | 200-450ms |
| ACID across models | **✅ Yes** | ⚠️ Eventual |
| Integration complexity | **Native** | ETL required |

---

## 🛠️ Troubleshooting During Demo

**If query returns no rows:**
```sql
-- Quick diagnostic
SELECT COUNT(*) FROM patients WHERE age > 65;
SELECT COUNT(*) FROM treats_edges;
SELECT * FROM user_property_graphs;  -- Verify graph exists
```

**If performance seems slow:**
- Ensure graph is loaded into memory (PGX)
- Check indexes on patients table
- Verify database resources

**If GRAPH_TABLE syntax error:**
- Confirm Oracle version: `SELECT * FROM v$version;`
- Verify property graph created: `SELECT * FROM user_property_graphs;`

---

## 📝 Post-Demo Follow-Up

Send attendees:
- [ ] This demo code repository
- [ ] Link to Oracle Property Graph documentation
- [ ] GraphRag_Final.pdf presentation
- [ ] Oracle 23ai trial database link

---

**Good luck with your demo!** 🎉

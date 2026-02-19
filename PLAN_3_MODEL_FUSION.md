# Implementation Plan: 3-Model Fusion (Relational + Graph + Vector)

## Why This Matters

### The Problem with Current 2-Model Approach

The current system answers: *"What treatments exist for this patient's condition?"*

But it can't answer: *"What treatments are **semantically similar** to what worked before?"*

**Example limitation:** A patient had success with "GLP-1 Agonists". The current system can only find exact matches. It cannot find treatments with similar mechanisms, similar patient profiles, or similar research contexts—because similarity requires **semantic understanding**, not just string matching.

### Why Embeddings Transform the Result

Embeddings encode **meaning**, not just text. Two treatments can have:
- Different names ("Semaglutide" vs "Ozempic")
- Different descriptions
- But **similar embeddings** because they work the same way

| Query Type | Without Embeddings | With Embeddings |
|------------|-------------------|-----------------|
| "Find similar treatments" | Impossible (no similarity metric) | `VECTOR_DISTANCE < 0.3` |
| "Treatments like GLP-1s" | Exact string match only | Semantic similarity to GLP-1 embedding |
| "Papers about weight loss drugs" | Keyword search (misses synonyms) | Semantic search (catches "anti-obesity", "metabolic therapy") |

### The Power of 3-Model Fusion

**Single query now answers:**
> "For elderly diabetic patients, find treatments from research papers that are semantically similar to successful GLP-1 therapies, and rank by cost-effectiveness."

This requires ALL THREE models:
1. **Relational** → Filter patients by age, join clinical outcomes by cost
2. **Graph** → Traverse paper→treatment→condition relationships
3. **Vector** → Rank by semantic similarity to a reference treatment

**Competitors need 3 databases + application code. We need 1 query.**

---

## Implementation Plan

### Phase 1: Schema Changes

#### 1.1 Add Vector Columns to Node Tables

**File:** `oracle-setup/02_create_graph_tables.sql`

Add to `papers_nodes`:
```sql
content_embedding VECTOR(1536, FLOAT32)  -- Embedding of paper abstract/content
```

Add to `treatments_nodes`:
```sql
description_embedding VECTOR(1536, FLOAT32)  -- Embedding of treatment name + context
```

#### 1.2 Create Vector Indexes

**File:** `oracle-setup/02_create_graph_tables.sql` (append)

```sql
-- Vector similarity indexes for fast search
CREATE VECTOR INDEX idx_papers_vec ON papers_nodes(content_embedding)
  ORGANIZATION NEIGHBOR PARTITIONS
  DISTANCE COSINE
  WITH TARGET ACCURACY 95;

CREATE VECTOR INDEX idx_treatments_vec ON treatments_nodes(description_embedding)
  ORGANIZATION NEIGHBOR PARTITIONS
  DISTANCE COSINE
  WITH TARGET ACCURACY 95;
```

#### 1.3 Update Property Graph Definition

**File:** `oracle-setup/03_create_property_graph.sql`

Expose embeddings as graph properties:
```sql
treatments_nodes AS Treatment
    KEY (node_id)
    PROPERTIES (node_id, entity_name, treatment_type, description_embedding),
papers_nodes AS Paper
    KEY (node_id)
    PROPERTIES (node_id, filename, title, publication_date, content_embedding)
```

---

### Phase 2: Python Pipeline Changes

#### 2.1 Add Embedding Generation

**File:** `extractPDF/extract_pdf_with_llm.py`

Add embedding model initialization:
```python
from langchain_ollama import OllamaEmbeddings

# In __init__:
self.embedding_model = OllamaEmbeddings(model="nomic-embed-text")
```

Add embedding generation method:
```python
def generate_embedding(self, text: str) -> List[float]:
    """Generate embedding vector for text"""
    return self.embedding_model.embed_query(text)
```

Modify `process_pdf` to generate embeddings:
```python
# After LLM extraction, before loading:
paper_embedding = self.generate_embedding(parsed['text'][:2000])  # Abstract/intro

treatment_embeddings = {}
for t_name in entities['treatments']:
    # Embed treatment name + any context from the paper
    context = f"{t_name} treatment for diabetes"
    treatment_embeddings[t_name] = self.generate_embedding(context)
```

#### 2.2 Update Oracle Loader

**File:** `extractPDF/oracle_loader.py`

Modify `add_paper`:
```python
def add_paper(self, filename: str, title: str, publication_date: str = None,
              embedding: List[float] = None) -> int:
    sql = """
        INSERT INTO papers_nodes (filename, title, publication_date, content_embedding)
        VALUES (:1, :2, TO_DATE(:3, 'YYYY-MM-DD'), :4)
        RETURNING node_id INTO :5
    """
    # Convert embedding list to Oracle VECTOR format
    embedding_val = embedding if embedding else None
    out_id = self.cursor.var(int)
    self.cursor.execute(sql, [filename, title[:500], publication_date, embedding_val, out_id])
    return out_id.getvalue()[0]
```

Modify `add_treatment`:
```python
def add_treatment(self, name: str, treatment_type: str = "Pharmaceutical",
                  embedding: List[float] = None) -> int:
    # ... existing duplicate check ...

    sql = """
        INSERT INTO treatments_nodes (entity_name, treatment_type, description_embedding)
        VALUES (:1, :2, :3)
        RETURNING node_id INTO :4
    """
    out_id = self.cursor.var(int)
    self.cursor.execute(sql, [name, treatment_type, embedding, out_id])
    return out_id.getvalue()[0]
```

#### 2.3 Update Graph Schema (Optional)

**File:** `extractPDF/graph_schema.py`

Add embedding fields to Pydantic models:
```python
class Treatment(BaseModel):
    name: str
    type: Literal["Pharmaceutical", "Lifestyle", "Surgery", "Other"] = "Pharmaceutical"
    embedding: Optional[List[float]] = None
```

---

### Phase 3: Demo Queries

#### 3.1 Create 3-Model Demo Query File

**File:** `three_model_hybrid_query.sql` (new file)

```sql
-- ============================================================================
-- THREE-MODEL FUSION DEMO: Relational + Graph + Vector
-- ============================================================================
-- This query demonstrates Oracle 23ai's ability to combine:
--   1. RELATIONAL: Patient records, clinical outcomes (SQL JOINs)
--   2. GRAPH: Knowledge graph traversal (GRAPH_TABLE + MATCH)
--   3. VECTOR: Semantic similarity search (VECTOR_DISTANCE)
--
-- In a SINGLE SQL statement with UNIFIED optimization.
-- Competitors require 3 separate databases and application-level orchestration.
-- ============================================================================

-- First, create a reference embedding for "GLP-1 like treatments"
-- (In practice, this would come from a query parameter or application)
DEFINE query_text = 'GLP-1 receptor agonist diabetes treatment weight loss'

-- ============================================================================
-- QUERY 1: Basic 3-Model Join
-- Find treatments semantically similar to GLP-1s for elderly diabetic patients
-- ============================================================================
SELECT
    p.customer_name,
    p.age,
    p.diagnosis,
    graph_data.paper_title,
    graph_data.treatment_name,
    ROUND(graph_data.similarity_score, 3) AS semantic_similarity
FROM patients p
JOIN (
    SELECT
        paper.title AS paper_title,
        treat.entity_name AS treatment_name,
        cond.name AS condition_name,
        VECTOR_DISTANCE(
            treat.description_embedding,
            (SELECT description_embedding FROM treatments_nodes WHERE entity_name = 'GLP-1 Agonists'),
            COSINE
        ) AS similarity_score
    FROM GRAPH_TABLE (
        medical_literature_kg
        MATCH (paper IS Paper)-[m IS MENTIONS]->(treat IS Treatment)-[tr IS TREATS]->(cond IS Condition)
        COLUMNS (
            paper.title,
            treat.entity_name,
            treat.description_embedding,
            cond.name
        )
    )
) graph_data ON p.diagnosis = graph_data.condition_name
WHERE p.age > 65                          -- RELATIONAL filter
  AND graph_data.similarity_score < 0.5   -- VECTOR filter (lower = more similar)
ORDER BY graph_data.similarity_score ASC;

-- ============================================================================
-- QUERY 2: 3-Model with Clinical Outcomes (Full 4-Way Join)
-- Add cost-effectiveness from relational clinical_outcomes table
-- ============================================================================
SELECT
    p.customer_name,
    p.age,
    graph_data.treatment_name,
    co.effectiveness_score,
    co.monthly_cost,
    ROUND(graph_data.similarity_score, 3) AS semantic_similarity,
    RANK() OVER (
        PARTITION BY p.patient_id
        ORDER BY graph_data.similarity_score ASC, co.effectiveness_score DESC
    ) AS recommendation_rank
FROM patients p
JOIN (
    SELECT
        treat.entity_name AS treatment_name,
        cond.name AS condition_name,
        VECTOR_DISTANCE(
            treat.description_embedding,
            (SELECT description_embedding FROM treatments_nodes WHERE entity_name = 'GLP-1 Agonists'),
            COSINE
        ) AS similarity_score
    FROM GRAPH_TABLE (
        medical_literature_kg
        MATCH (paper IS Paper)-[m IS MENTIONS]->(treat IS Treatment)-[tr IS TREATS]->(cond IS Condition)
        COLUMNS (treat.entity_name, treat.description_embedding, cond.name)
    )
) graph_data ON p.diagnosis = graph_data.condition_name
JOIN clinical_outcomes co ON graph_data.treatment_name = co.treatment_name
WHERE p.age > 65                          -- RELATIONAL: age filter
  AND graph_data.similarity_score < 0.5   -- VECTOR: semantic similarity
  AND co.effectiveness_score >= 7.0       -- RELATIONAL: effectiveness threshold
  AND co.monthly_cost < 500               -- RELATIONAL: cost constraint
ORDER BY p.customer_name, recommendation_rank;

-- ============================================================================
-- QUERY 3: Paper Similarity Search
-- Find papers semantically similar to a research topic
-- ============================================================================
SELECT
    p.customer_name,
    graph_data.paper_title,
    graph_data.treatment_name,
    ROUND(graph_data.paper_similarity, 3) AS paper_relevance
FROM patients p
JOIN (
    SELECT
        paper.title AS paper_title,
        treat.entity_name AS treatment_name,
        cond.name AS condition_name,
        VECTOR_DISTANCE(
            paper.content_embedding,
            (SELECT content_embedding FROM papers_nodes WHERE filename = 'diabetes-treatment-study.pdf'),
            COSINE
        ) AS paper_similarity
    FROM GRAPH_TABLE (
        medical_literature_kg
        MATCH (paper IS Paper)-[m IS MENTIONS]->(treat IS Treatment)-[tr IS TREATS]->(cond IS Condition)
        COLUMNS (paper.title, paper.content_embedding, treat.entity_name, cond.name)
    )
) graph_data ON p.diagnosis = graph_data.condition_name
WHERE p.age > 65
ORDER BY graph_data.paper_similarity ASC
FETCH FIRST 20 ROWS ONLY;
```

---

### Phase 4: Testing & Verification

#### 4.1 Verify Schema Changes
```sql
-- Check vector columns exist
DESC papers_nodes;
DESC treatments_nodes;

-- Check vector indexes created
SELECT index_name, index_type FROM user_indexes WHERE index_type LIKE '%VECTOR%';
```

#### 4.2 Verify Embeddings Loaded
```sql
-- Check embeddings are populated (not null)
SELECT entity_name,
       CASE WHEN description_embedding IS NOT NULL THEN 'YES' ELSE 'NO' END AS has_embedding
FROM treatments_nodes;

SELECT filename,
       CASE WHEN content_embedding IS NOT NULL THEN 'YES' ELSE 'NO' END AS has_embedding
FROM papers_nodes;
```

#### 4.3 Test Vector Distance Function
```sql
-- Test raw vector distance between two treatments
SELECT
    t1.entity_name AS treatment_1,
    t2.entity_name AS treatment_2,
    ROUND(VECTOR_DISTANCE(t1.description_embedding, t2.description_embedding, COSINE), 4) AS similarity
FROM treatments_nodes t1, treatments_nodes t2
WHERE t1.entity_name = 'GLP-1 Agonists'
  AND t2.entity_name != t1.entity_name
ORDER BY similarity ASC;
```

#### 4.4 Run Full 3-Model Query
```bash
sqlplus system/Welcome12345@localhost:1521/FREEPDB1 @three_model_hybrid_query.sql
```

**Expected Results:**
- Query 1: Treatments ranked by semantic similarity to GLP-1s
- Query 2: Cost-effective treatments with similarity ranking
- Query 3: Papers similar to reference paper

---

## Files to Modify

| File | Change Type | Description |
|------|-------------|-------------|
| `oracle-setup/02_create_graph_tables.sql` | Modify | Add VECTOR columns + indexes |
| `oracle-setup/03_create_property_graph.sql` | Modify | Expose embedding properties |
| `extractPDF/extract_pdf_with_llm.py` | Modify | Add embedding generation |
| `extractPDF/oracle_loader.py` | Modify | Store embeddings in DB |
| `extractPDF/requirements.txt` | Modify | Ensure langchain-ollama included |
| `three_model_hybrid_query.sql` | Create | New demo queries |

---

## Prerequisites

1. **Ollama with embedding model:**
   ```bash
   ollama pull nomic-embed-text
   ```

2. **Oracle 23ai with VECTOR support** (already have this)

3. **Python dependencies** (already in requirements.txt):
   - `langchain-ollama`
   - `oracledb`

---

## Summary: The Patent-Worthy Innovation

**Before (Competitors):**
```
[PostgreSQL] → Patient query → results
[Neo4j] → Graph traversal → results
[Pinecone] → Vector search → results
[Application] → Merge 3 result sets → final answer
```
- 3 round trips
- 3 systems to maintain
- No unified optimization
- Application handles join logic

**After (Our Approach):**
```sql
SELECT ... FROM patients p
JOIN GRAPH_TABLE(...) graph_data ON ...
JOIN clinical_outcomes co ON ...
WHERE VECTOR_DISTANCE(...) < 0.3
  AND p.age > 65
  AND co.cost < 500;
```
- 1 query
- 1 database
- 1 execution plan
- Cost-based optimizer chooses: vector-first? graph-first? relational-first?

**The optimizer can dynamically choose:**
- Vector-first (if semantic filter is highly selective)
- Graph-first (if pattern traversal eliminates most paths)
- Relational-first (if age/cost filters are highly selective)

**No federated system can do this.** That's the patent.

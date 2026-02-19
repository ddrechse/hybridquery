# Oracle Hybrid Query POC: Unified Medical Intelligence 🏥🧠

**Solving the "Fragmentation Crisis" in Healthcare Data with Oracle 26ai.**

---

## 🌍 The Problem: Why This Matters
Modern healthcare is drowning in data, but starving for wisdom.
1.  **Patient Data** lives in Relational Databases (EHRs).
2.  **Medical Research** lives in Unstructured PDFs (millions of new papers/year).
3.  **Clinical Evidence** lives in Graphs (complex relationships between drugs/targets).

To answer a simple question like *"What is the safest, most effective treatment for my elderly diabetic patient based on the latest research?"*, a hospital currently needs:
*   A Vector Database (for the papers)
*   A Graph Database (for the relationships)
*   A Relational Database (for the patient records)
*   A massive "Glue Code" application to join them all.

**It is slow, expensive, and fragile.**

## 🚀 The Solution: Oracle 26ai "3-Model Fusion"
We demonstrate that **Oracle Database 26ai** can replace that entire complex stack with **ONE Converged Database**.

By treating **Vectors**, **Graphs**, and **Relational Tables** as first-class citizens in SQL, we can:
1.  **Read** raw medical PDFs using Generative AI (Llama 3.1).
2.  **Structure** them into a Knowledge Graph + Vector Embeddings.
3.  **Query** everything in real-time with standard SQL.

**The Result:** Evidence-Based Clinical Decision Support in < 200ms.

### 🏛️ The "Architecture of Trust"
Why combine three models? Because each solves a specific failure mode of AI:
1.  **Relational (The Safety Layer):** Enforces hard business rules and safety (e.g., *"Do not prescribe this to an 81-year-old"*).
2.  **Graph (The Evidence Layer):** Provides explainable paths and proof (e.g., *"Show me the paper that links this drug to this condition"*).
3.  **Vector (The Semantic Glue):** Bridges the gap between human language and rigid data (e.g., *"User asks for 'Heart Failure', Vector matches 'HFrEF'"*).

---

## 🕵️‍♂️ The Hidden Challenge: "The Triplet Trap"
**Why do so many GenAI Graph projects fail?**
Simple. You can use an LLM to build a graph, but **querying it is brittle**. 
*   If your graph has a node for `Type 2 Diabetes`...
*   and a user asks for `Metabolic Syndrome`...
*   **The query returns 0 results.** (Because the graph lacks the synonym).

**We solve this.**
In **Phase 3** of this demo, we reveal how **Vector Search** acting as a "Semantic Bridge" allows us to query the graph using *intent*, not just exact keywords. This turns a rigid graph into a flexible, thinking brain.
 
---



## 🎯 The Demo Scenarios

### Phase 1: The "Baseline" (Relational + Graph)
Demonstrates the current state of "Hybrid" querying without vector search.
*   **Question**: *"Find treatments mentioned in these specific papers for my elderly patients."*
*   **Tech**: Graph Traversal + SQL Join.
*   **Script**: `demo_relational_graph_only.sql`

### Phase 2: The "Fusion" (Relational + Graph + Vector)
Demonstrates the full power of AI-driven decision support.
*   **Question**: *"Find cost-effective treatments semantically similar to 'Modern Cardiovascular Treatment' for a specific patient, ensuring safety."*
*   **Tech**: **Vector Search** (Intent) + **Graph Traversal** (Evidence) + **Relational SQL** (Safety/Cost).
*   **Script**: `demo_phase2_vector_fusion.sql` (Includes the "Wow Factor" query)

### Phase 3: The "Graph Trap" Challenge
Demonstrates *why* pure graphs fail and how Vectors fix it (The "Architecture of Trust").
*   **Question**: *"Find treatments for 'Metabolic Syndrome' (a synonym not in the graph)."*
*   **Tech**: Vector Search bridges the semantic gap to find 'Diabetes' treatments.
*   **Script**: `demo_challenge_graph_vs_vector.sql`

---

## 🚀 ZERO-TO-DEMO GUIDE (Fresh Start)

Follow these steps to run the demo from scratch on a new environment.

### Prerequisites
1.  **Oracle Database 26ai** running locally (e.g., Docker container listening on port 1521).
    ```bash
    docker run -d -p 1521:1521 -e ORACLE_PASSWORD=Welcome12345 gvenzl/oracle-free:latest-faststart
    ```
2.  **Ollama** installed and running (`ollama serve`).
3.  **Python 3.10+** environment.
4.  **SQL Client:** `sqlplus` or `sqlcl` installed and on your PATH.

### Step 1: Install Python Dependencies
```bash
pip install -r extractPDF/requirements.txt
```

### Step 2: Install AI Models (Critical!)
You MUST run these commands to download the LLM and Embedding models before starting.
```bash
# 1. Pull the LLM for text extraction/generation
ollama pull llama3.1

# 2. Pull the Embedding Model for Vector Search
ollama pull nomic-embed-text
```

### Step 3: Initialize Database (Schema & Tablespaces)
Run these scripts to create the tables (including Vector columns) and load the patient data.

**Important:** Ensure you are connected as a privileged user (`SYSTEM` or `SYS`) initially to create tablespaces if needed.

```bash
# A. Create Vector Tablespace (Required for Vectors)
# This creates a tablespace with "Automatic Segment Space Management" (ASSM),
# which is strictly required for storing Vector Embeddings in Oracle.
sqlplus system/Welcome12345@localhost:1521/FREEPDB1 @oracle-setup/00_prepare_tablespace.sql

# B. Create Schema and Tablespaces
# 1. Relational: Creates PATIENTS and CLINICAL_OUTCOMES tables.
sqlplus system/Welcome12345@localhost:1521/FREEPDB1 @oracle-setup/01_create_relational_tables.sql

# 2. Graph & Vector: Creates Node/Edge tables and Vector Indexes (requires ASSM).
sqlplus system/Welcome12345@localhost:1521/FREEPDB1 @oracle-setup/02_create_graph_tables.sql

# 3. Property Graph DDL: Defines the Property Graph object "MedicalKnowledgeGraph" for MATCH queries.
sqlplus system/Welcome12345@localhost:1521/FREEPDB1 @oracle-setup/03_create_property_graph.sql

# C. Load Base Relational Data
# 1. Load Patients: Inserts dummy patient demographics.
sqlplus system/Welcome12345@localhost:1521/FREEPDB1 @oracle-setup/load_patients.sql 

# 2. Load Outcomes: Inserts historical clinical outcomes data.
sqlplus system/Welcome12345@localhost:1521/FREEPDB1 @load_clinical_outcomes.sql
```

### Step 3.5: The Knowledge Base (Medical Papers)
We are seeding our Knowledge Graph with three generated "Medical Papers" (located in `sample-data/`). These represent unstructured knowledge that the relational database doesn't know about:

1.  **Diabetes Treatment Study**: Comparing effectiveness of Metformin, Sulfonylureas, and DPP-4 inhibitors for Type 2 Diabetes.
2.  **Obesity Management Review**: Analysis of GLP-1 agonists (Liraglutide vs. Semaglutide) and their weight-loss impact.
3.  **Cardiovascular Outcomes Trials**: Studies on SGLT2 inhibitors (Dapagliflozin/Empagliflozin) and heart failure outcomes.

*The goal is to teach the database about these treatments so it can recommend them to relevant patients.*

### Step 4: Run AI Extraction Pipeline (The Magic)
This script reads the generated PDFs, extracts the knowledge graph (Entities/Relationships) via LLM, generates vector embeddings, and inserts everything directly into Oracle.

#### 🔧 Under the Hood: The AI Pipeline
1.  **Parse (Docling):** We use **Docling** to turn the PDF into clean Markdown, preserving tables and headers.
2.  **Extract (LLM):** We send the text to **Llama 3.1** (via Ollama) to identify Entities (Treatments, Conditions) and Relationships.
3.  **Vectorize (Nomic):** *Simultaneously*, we generate **Vector Embeddings** (768 dimensions) for every node description and paper content segment.

```bash
# Process all 3 PDFs
python extractPDF/extract_pdf_with_llm.py \
  sample-data/diabetes-treatment-study.pdf \
  --model llama3.1 \
  --db-user system --db-pass Welcome12345 --db-dsn localhost:1521/FREEPDB1

python extractPDF/extract_pdf_with_llm.py \
  sample-data/obesity-management-review.pdf \
  --model llama3.1 \
  --db-user system --db-pass Welcome12345 --db-dsn localhost:1521/FREEPDB1

python extractPDF/extract_pdf_with_llm.py \
  sample-data/cardiovascular-outcomes-trials.pdf \
  --model llama3.1 \
  --db-user system --db-pass Welcome12345 --db-dsn localhost:1521/FREEPDB1
```

### Step 5: Run the Demos

#### A. The "Relational Baseline" (The Missing Link)
Show that we have Patient Data and Outcome Data, but no way to link them without a Graph.
```bash
sqlplus system/Welcome12345@localhost:1521/FREEPDB1 @demo_relational_baseline.sql
```

#### B. The "Graph Inspection" Demo
Look under the hood at the Nodes (Treatments) and Edges (Relationships) the AI created.
```bash
sqlplus system/Welcome12345@localhost:1521/FREEPDB1 @demo_graph_inspection.sql
```

#### C. The "Relational + Graph" Demo
See how we find treatments explicitly linked in the graph (using modern `GRAPH_TABLE` syntax).
```bash
sqlplus system/Welcome12345@localhost:1521/FREEPDB1 @demo_relational_graph_only.sql
```

#### D. The "3-Model Fusion" Demo (The Main Event)
Run the full "Wow Factor" script. This executes 5 queries culminating in the **Clinical Decision Support Engine**.
```bash
sqlplus system/Welcome12345@localhost:1521/FREEPDB1 @demo_phase2_vector_fusion.sql
```

#### E. The "Graph Trap" Challenge (SQL)
Demonstrates why Graph alone is brittle and Hybrid is robust ("Metabolic Syndrome" example).
(This SQL script uses a **Pre-Calculated Vector** for client-side embedding simulation).
```bash
sqlplus system/Welcome12345@localhost:1521/FREEPDB1 @demo_challenge_graph_vs_vector.sql
```

## 📂 Project Structure
*   `extractPDF/extract_pdf_with_llm.py`: **The Engine.** Extracts entities/relationships using Llama 3.1 and generates embeddings using `nomic-embed-text`. Inserts directly into Oracle.
*   `oracle-setup/`: SQL scripts for schema definition (Relational tables, Graph tables with `VECTOR` columns, Property Graph DDL).
*   `sample-data/generate_sample_pdfs.py`: Python script to generate realistic medical research PDFs.
*   `demo_phase2_vector_fusion.sql`: **The Demo.** Contains the "Wow Factor" query and 3-model fusion logic.
*   `demo_challenge_graph_vs_vector.sql`: **The Challenge.** Side-by-side comparison of Pure Graph vs. Hybrid Fusion (Hardcoded Vector for pure SQL).

### Troubleshooting Notes for Fresh Installs

**1. ORA-43853 / ORA-51963 (Vector Tablespace Issue)**
*   **Issue:** `VECTOR type cannot be used in non-automatic segment space management tablespace`.
*   **Fix:** The script `02_create_graph_tables.sql` attempts to use `TABLESPACE users`. Ensure your `USERS` tablespace is ASSM or create a new one.

**2. ORA-22848 (Vector Comparison Key)**
*   **Issue:** `cannot use VECTOR type as comparison key`.
*   **Fix:** This happens if you try to `GROUP BY` a vector column. The fixed scripts use a CTE (Common Table Expression) to pre-calculate vector distances before aggregation.

**3. Model Not Found**
*   **Fix:** Run `ollama pull llama3.1` and `ollama pull nomic-embed-text` before starting.

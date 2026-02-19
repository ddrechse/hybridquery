# Oracle Hybrid Query Demo Guide: The "Architecture of Trust"

**Title:** Unified Medical Intelligence: 3-Model Fusion (Relational + Graph + Vector)
**Theme:** Solving the "Triplet Trap" with Hybrid AI

---

## Demo Flow (15 minutes)

### Part 1: The Problem (2 minutes)
**"The Triplet Trap"**
*   **The LinkedIn Critique:** "Naive LLM Graphs lack business logic and fail at scale."
*   **The Issue:** If you query a graph for "Metabolic Syndrome" but it only knows "Diabetes", it fails.
*   **The Solution:** **Oracle 3-Model Fusion**.
    *   **Relational:** Enforces Safety & Rules (The "Conceptual Model").
    *   **Vector:** Bridges Semantic Gaps (The "Glue").
    *   **Graph:** Provides Evidence (The "Proof").

---

### Part 2: Building the Data Foundation (5 minutes)

#### Step 0: The Relational Baseline (Structured Truth)
Before we add AI, we have a standard relational database with two core tables:
1.  **PATIENTS**: Who they are (Name, Age) and what they have (Diagnosis).
    *   *Example:* David Thompson (81), Type 2 Diabetes.
2.  **CLINICAL_OUTCOMES**: Hard facts about treatments (Cost, Risk, Effectiveness).
    *   *Example:* Metformin: Cheap ($4), High Effectiveness (8.5), Low Risk (1.0).

*This is our "Ground Truth". AI will add knowledge, but this data enforces safety.*

#### Step 1: The Source Data
*   Show `diabetes-treatment-study.pdf` (Unstructured Context).
*   Show `clinical_trial_outcomes.xlsx` (Structured Truth).

#### Step 2: The "Magic" Pipeline (PDF -> Graph + Vector)
Execute the extraction script:
```bash
python extractPDF/extract_pdf_with_llm.py sample-data/diabetes-treatment-study.pdf ...
```

**Explain the 3-Step Process happening under the hood:**
1.  **Parse:** We use **Docling** to turn the PDF into clean Markdown (preserving tables/headers).
2.  **Extract (LLM):** We send that text to **Llama 3.1** to identify Entites (Treatments, Conditions) and Relationships (TREATS, MENTIONS).
3.  **Vectorize:** *Simultaneously*, we generate **Vector Embeddings** (using `nomic-embed-text`) for every node description and paper content.

**Key Technical Win:**
"We don't just get a graph. We get a **Vectorized Graph**. Every node has a mathematical representation of its meaning, allowing us to do fuzzy matching later."

#### Step 3: Verify the Data in SQL
Show that the data is now structured and vectorized:
```sql
SELECT entity_name, VECTOR_DIMENSION_COUNT(description_embedding) as dims 
FROM treatments_nodes 
FETCH FIRST 5 ROWS ONLY;
```
*   **Result:** You see "Semaglutide" with a 768-dimension vector.
*   **Speaking Point:** "This vector is what allows us to find 'Semaglutide' even if the user searches for 'Weight loss shot'."

### Part 2.4: Phase 0 - The Relational Disconnect (2 minutes)

**Script:** `demo_relational_baseline.sql`

#### The Problem
Show that the Relational Database has the raw materials, but no bridge.
1.  **Query 1:** Shows "David Thompson" (Has Diabetes).
2.  **Query 2:** Shows "Metformin" (Effective Treatment).
3.  **The Gap:** "There is no `diagnosis_id` column in the `clinical_outcomes` table. The database doesn't know these are related."

*Transition: "This is why we need a Graph."*

### Part 2.45: Graph Inspection (The Evidence)
**Script:** `demo_graph_inspection.sql`

#### The Visualization
Let's peek under the hood. What did the AI actually build?
1.  **Nodes:** Show extracted Treatments (e.g., SGLT2 Inhibitors) and their descriptions.
2.  **Edges:** Show the "TREATS" relationship linking Treatments to Conditions.
*Point: "This isn't a black box. It's a queryable table structure."*

---

### Part 2.5: Phase 1 - Relational + Graph Baseline (3 minutes)

**Script:** `demo_relational_graph_only.sql`

#### The Concept
"We start with our Relational Foundation (David Thompson, 81). Now, let's layer on the **AI-Extracted Graph**."

#### The Query
Run the script to show treatments for David found via graph traversal.
*   **Result:** A list of treatments (e.g., Metformin, SGLT2 Inhibitors) linked to his diagnosis via medical papers.
*   **Speaking Point:** "This is powerful. We used the **Graph** to find treatments mentioned in literature for his condition. This is the 'Hybrid' baseline."

---

### Part 3: The "Graph Trap" Challenge (2 minutes)
**Script:** `demo_challenge_graph_vs_vector.sql`

#### Act 1: The Trap (Pure Graph Failure)
Run Query 1: Search for treatments for **"Metabolic Syndrome"**.
*   **Result:** **0 ROWS**.
*   **Speaking Point:** "The graph is rigid. It doesn't know the synonym. This is why pure graph projects fail."

#### Act 2: The Solution (Vector Bridge)
Run Query 2: Search for **"Metabolic Syndrome"** using Vector Fusion.
*   **Result:** **Success (Diabetes Treatments found)**.
*   **Speaking Point:** "Vector Search found that 'Metabolic Syndrome' is 85% similar to 'Type 2 Diabetes'. It bridged the gap dynamically."
*   **Note:** This query uses a pre-calculated vector for the demo, simulating the client-side embedding.

---

### Part 4: The "Wow" Moment (5 minutes)
**Script:** `demo_phase2_vector_fusion.sql`

#### The Scenario
"David Thompson" (81, Diabetic) needs a **Modern**, **Safe**, and **Effective** treatment.

#### The Query (Query 5)
Run the final query in the script. It combines:
1.  **Vector:** Find treatments conceptually similar to "SGLT2 Inhibitors" (Modern).
2.  **Relational:** `WHERE side_effect_risk < 3 AND age_limit >= 81` (Safe).
3.  **Graph:** `COUNT(papers)` (Proven/Effective).

**Result:**
*   Returns a ranked list of treatments.
*   **Speaking Point:** "We just replaced a complex RAG application with **ONE SQL QUERY**."

---

## Key Messages for Q&A

**Q: Why not just use a Vector DB?**
A: Vectors give you similarity, but they don't give you *facts*. You need the Relational data to enforce safety rules (e.g., "Do not give this to an 81-year-old").

**Q: Why not just use a Graph DB?**
A: Graphs are brittle. As we showed with "Metabolic Syndrome", if your ontology isn't perfect, the query fails. Vectors provide the flexibility.

**Q: What is the "Architecture of Trust"?**
A: It's grounding AI in your Enterprise Relational Data. The AI (Vector/Graph) provides suggestions, but the Relational DB provides the constraints.

---

## Preparation Checklist
1.  **Reset Environment:** Run the "Zero-to-Demo" steps in `README.md`.
2.  **Pre-load Data:** Ensure PDFs are processed (`extract_pdf_with_llm.py`).
3.  **Open SQL Client:** Connect to `system/Welcome12345`.
4.  **Have Scripts Ready:**
    *   `demo_challenge_graph_vs_vector.sql`
    *   `demo_phase2_vector_fusion.sql`

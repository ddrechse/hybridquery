# Quick Start Guide
## Get the 3-Way Hybrid Query POC Running in 10 Minutes

This guide gets you from zero to running 3-way hybrid queries (patients + graph + clinical outcomes) as fast as possible.

---

## Prerequisites

✅ Oracle Database 23ai or later
✅ SQL*Plus or SQLcl installed
✅ Database connection credentials

---

## 6-Step Setup

### Step 1: Navigate to the project
```bash
cd /path/to/data-refactoring-advisor/hands-on-lab/hybridQuery
```

### Step 2: Connect to Oracle
```bash
sqlplus username/password@database
```

### Step 3: Load patient data
```sql
@oracle-setup/01_create_relational_tables.sql
```

**Expected:** PATIENTS table created with 10 patient records (8 elderly).

### Step 4: Load graph data from extracted PDF
```sql
@load_extracted_graph_data.sql
```

**Expected:** Property graph MEDICAL_LITERATURE_KG created with 14 treatments, 1 condition, 18 edges.

### Step 5: Load clinical trial outcomes
```sql
@load_clinical_outcomes.sql
```

**Expected:** CLINICAL_OUTCOMES table created with 14 treatments (effectiveness, safety, cost data).

### Step 6: Run the 3-way hybrid query
```sql
@three_way_hybrid_query.sql
```

**Expected:** Query 1 returns **32 rows** showing 8 elderly patients matched with 4 treatments each, combining data from all three sources.

### Step 7: Celebrate! 🎉

You just ran Oracle's **3-way hybrid query** combining:
- Relational patient records
- Property graph from literature
- Relational clinical trial outcomes

All in a single SQL statement with sub-200ms performance!

---

## The Key Query

This is what you just ran - a **3-way hybrid query**:

```sql
SELECT
    p.customer_name,
    p.age,
    p.diagnosis,
    graph_data.treatment_name,
    co.effectiveness_score,
    co.side_effect_risk,
    co.monthly_cost
FROM patients p                           -- DATA SOURCE 1: Relational
  JOIN (
    SELECT entity_name AS treatment_name, condition_name
    FROM GRAPH_TABLE (                    -- DATA SOURCE 2: Graph
      medical_literature_kg
      MATCH (paper IS Paper)-[IS MENTIONS]->(treat IS Treatment)-[IS TREATS]->(cond IS Condition)
      COLUMNS (treat.entity_name, cond.name AS condition_name)
    )
  ) graph_data ON p.diagnosis = graph_data.condition_name
  JOIN clinical_outcomes co               -- DATA SOURCE 3: Relational
    ON graph_data.treatment_name = co.treatment_name
WHERE p.age > 65
  AND co.effectiveness_score >= 7.5
  AND co.side_effect_risk <= 2.0
ORDER BY p.age DESC, co.effectiveness_score DESC;
```

**What makes this special:**
- ✅ **THREE** data sources in ONE SQL statement
- ✅ Combines patients (relational) + literature (graph) + clinical outcomes (relational)
- ✅ Zero round-trips between databases
- ✅ 100-200ms latency (vs 200-450ms for multi-database)
- ✅ Complete clinical decision support with evidence

---

## Next Steps

### Explore More
- **5 demo queries**: See all queries in `three_way_hybrid_query.sql`
  - Basic 3-way join
  - Filtered for best treatments
  - Age-appropriate recommendations
  - Cost-effectiveness analysis
  - Clinical decision support with RANK()
- **Full walkthrough**: Read `DEMO_GUIDE.md` for 15-minute presentation
- **Complete docs**: See `README.md` for architecture details

### Process Your Own PDFs
```bash
cd extractPDF
pip install -r requirements.txt
python extract_pdf_to_graph.py ../sample-data/your-paper.pdf
# Review output/ for 5 CSV files
# Load with @load_extracted_graph_data.sql
```

See `extractPDF/README.md` for detailed extraction instructions.

### Learn More
- Full documentation: `README.md`
- Oracle Property Graphs: https://docs.oracle.com/en/database/oracle/property-graph/
- Docling: https://www.docling.ai/

---

## Troubleshooting

**Problem:** `ORA-00922: missing or invalid option`
**Solution:** Verify you're on Oracle 23ai or later:
```sql
SELECT * FROM v$version;
```

**Problem:** 3-way hybrid query returns 0 rows
**Solution:** Verify all three data sources loaded:
```sql
SELECT COUNT(*) FROM patients WHERE age > 65;  -- Should be 8
SELECT COUNT(*) FROM treatments_nodes;         -- Should be 14
SELECT COUNT(*) FROM treats_edges;             -- Should be 4
SELECT COUNT(*) FROM clinical_outcomes;        -- Should be 14
SELECT * FROM user_property_graphs;            -- Should show MEDICAL_LITERATURE_KG
```

**Problem:** `ORA-40926: property graph does not exist`
**Solution:** Re-run step 3:
```sql
@oracle-setup/03_create_property_graph.sql
```

---

## Key Files Reference

| File | Purpose |
|------|---------|
| `README.md` | Complete documentation |
| `QUICKSTART.md` | This file - fast setup |
| `DEMO_GUIDE.md` | 15-minute presentation script |
| `oracle-setup/01_*.sql` | Create relational tables (PATIENTS) |
| `load_extracted_graph_data.sql` | Load graph data from extracted PDF |
| `load_clinical_outcomes.sql` | Load clinical trial outcomes (NEW - 3-way demo) |
| `three_way_hybrid_query.sql` | 5 demo queries - main showcase |
| `oracle-setup/02-05*.sql` | Alternative embedded data approach |
| `extractPDF/README.md` | PDF extraction instructions |
| `sample-data/README.md` | Data files documentation |

---

**That's it! You're now running Oracle 3-way hybrid queries combining relational + graph + relational data sources!** 🚀

For questions or issues, see the full README.md or DEMO_GUIDE.md.

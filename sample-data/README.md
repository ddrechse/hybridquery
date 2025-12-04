# Sample Data Files

This directory contains sample medical data for the hybrid query POC.

---

## Files Included

### 1. sample_patients.csv ✅ Ready to Use
**Format:** CSV (comma-separated values)
**Records:** 10 patient records
**Usage:** Can be loaded directly into Oracle or used as reference

**Columns:**
- `patient_id` - Unique identifier
- `customer_name` - Patient name
- `age` - Patient age
- `diagnosis` - Medical diagnosis (Type 1 or Type 2 Diabetes)
- `admission_date` - Hospital admission date
- `primary_physician` - Assigned doctor

**Sample:**
```csv
patient_id,customer_name,age,diagnosis,admission_date,primary_physician
1001,John Anderson,72,Type 2 Diabetes,2024-01-15,Dr. Sarah Mitchell
```

---

### 2. treatment_outcomes.csv ✅ Ready to Use
**Format:** CSV (comma-separated values)
**Records:** 7 diabetes treatments
**Usage:** Reference data for treatment effectiveness

**Note:** The file `treatment_outcomes.xlsx` is a placeholder. Use the `.csv` version which contains the same data in a usable format.

**Columns:**
- `Treatment Name` - Name of treatment/medication
- `Condition Treated` - Which diabetes type
- `Success Rate` - Treatment effectiveness percentage
- `Study Year` - Year of study
- `Sample Size` - Number of patients in study
- `Side Effects` - Common side effects

**Sample:**
```csv
Treatment Name,Condition Treated,Success Rate,Study Year,Sample Size,Side Effects
Metformin,Type 2 Diabetes,85%,2023,1500,Mild GI upset
```

---

### 3. clinical_trial_outcomes.csv ✅ Ready to Use
**Format:** CSV (comma-separated values)
**Records:** 14 diabetes treatments with clinical trial outcomes
**Usage:** Load into Oracle via `load_clinical_outcomes.sql`

**Purpose:** This is the **third data source** in the 3-way hybrid query, providing treatment effectiveness, safety, and cost data to enable complete clinical decision support.

**Columns:**
- `treatment_name` - Primary key, treatment/medication name (e.g., "GLP-1 Agonists")
- `effectiveness_score` - Treatment effectiveness on 0-10 scale (e.g., 8.5 = highly effective)
- `side_effect_risk` - Safety risk on 0-5 scale (lower is safer, e.g., 2.0 = moderate risk)
- `monthly_cost` - Cost in USD per month (e.g., 450.00 = $450/month)
- `fda_approval_year` - Year FDA approved (e.g., 2005)
- `recommended_min_age` - Minimum age for treatment (e.g., 18)
- `recommended_max_age` - Maximum age for treatment (e.g., 85)

**Sample Data (first 3 treatments):**
```csv
treatment_name,effectiveness_score,side_effect_risk,monthly_cost,fda_approval_year,recommended_min_age,recommended_max_age
GLP-1 Agonists,8.5,2.0,450.00,2005,18,85
SGLT2 Inhibitors,8.0,1.5,380.00,2013,18,90
DPP-4 Inhibitors,7.2,1.2,320.00,2006,18,95
```

**Loading into Oracle:**
```bash
sqlplus username/password@database
@load_clinical_outcomes.sql
```

This creates the `CLINICAL_OUTCOMES` table with all 14 treatments.

---

### 4. clinical_trial_outcomes.xlsx ✅ Ready to Use
**Format:** Microsoft Excel (.xlsx)
**Records:** Same 14 diabetes treatments as CSV version
**Usage:** Can be opened in Excel for viewing/editing, or loaded via SQL

**Note:** For Oracle loading, the `.csv` version is recommended as it's easier to import. The Excel file is provided for convenience when viewing or modifying the data in Excel.

---

### 5. diabetes_treatment_study.pdf ✅ Real PDF
**Format:** PDF (binary) - Real medical research paper
**Content:** Medical research discussing diabetes treatments and clinical outcomes
**Usage:** Processed using `extractPDF/extract_pdf_to_graph.py` to extract knowledge graph

**Extraction Results:**
This PDF was processed with Docling to generate:
- 14 treatment nodes (GLP-1 Agonists, SGLT2 Inhibitors, DPP-4 Inhibitors, etc.)
- 1 condition node (Type 2 Diabetes)
- 14 MENTIONS edges (paper → treatments)
- 4 TREATS edges (treatments → Type 2 Diabetes)

**Output:** 5 CSV files in `extractPDF/output/` directory

**To Process Your Own PDFs:**
```bash
cd extractPDF
python extract_pdf_to_graph.py ../sample-data/your-paper.pdf
```

See `extractPDF/README.md` for complete extraction documentation.

---

## Loading Data into Oracle

### Option 1: Use Provided SQL Script (Recommended)
The data is already embedded in the SQL scripts:
```sql
@oracle-setup/04_load_sample_data.sql
```

### Option 2: Load from CSV Files
You can also load these CSV files using SQL*Loader or external tables.

**Using External Tables:**
```sql
-- Create external table for patients
CREATE TABLE patients_staging (
    patient_id NUMBER,
    customer_name VARCHAR2(100),
    age NUMBER,
    diagnosis VARCHAR2(200),
    admission_date DATE,
    primary_physician VARCHAR2(100)
)
ORGANIZATION EXTERNAL (
    TYPE ORACLE_LOADER
    DEFAULT DIRECTORY DATA_DIR
    ACCESS PARAMETERS (
        RECORDS DELIMITED BY NEWLINE
        FIELDS TERMINATED BY ','
        OPTIONALLY ENCLOSED BY '"'
        MISSING FIELD VALUES ARE NULL
        (patient_id, customer_name, age, diagnosis,
         admission_date DATE "YYYY-MM-DD", primary_physician)
    )
    LOCATION ('sample_patients.csv')
)
REJECT LIMIT UNLIMITED;

-- Load data
INSERT INTO patients SELECT * FROM patients_staging;
```

---

## Processing Documents with Docling

### Step 1: Install Docling
```bash
cd ../docling-processing
pip install -r requirements.txt
```

### Step 2: Process Documents
```bash
python process_documents.py
```

This will:
- Parse `diabetes_treatment_study.pdf` (even though it's text format)
- Extract structure and content
- Save processed output to `output/`

### Step 3: Extract Graph Entities
```bash
python extract_entities.py
```

This will:
- Analyze processed documents
- Extract entities (Papers, Treatments, Conditions)
- Identify relationships (MENTIONS, TREATS)
- Generate CSV files in `graph_data/` ready for Oracle import

---

## How This Data Was Created

### Knowledge Graph from PDF Extraction

The **diabetes-treatment-study.pdf** was processed using the `extractPDF/` pipeline:

1. **PDF Parsing**: Docling extracted structured content from the real PDF
2. **Entity Extraction**: `entity_patterns.py` identified treatments and conditions using regex
3. **Graph Building**: `graph_builder.py` generated 5 CSV files:
   - papers_nodes.csv (1 paper)
   - treatments_nodes.csv (14 treatments)
   - conditions_nodes.csv (1 condition)
   - mentions_edges.csv (14 edges: paper → treatments)
   - treats_edges.csv (4 edges: treatments → Type 2 Diabetes)

4. **Oracle Loading**: `load_extracted_graph_data.sql` loaded CSVs into property graph

**Result:** 14 treatments, 1 condition, 18 edges in MEDICAL_LITERATURE_KG

### Clinical Trial Outcomes

The **clinical_trial_outcomes.csv** was manually curated based on real clinical trial data:
- 14 treatments with effectiveness scores (0-10 scale)
- Safety risk scores (0-5 scale)
- Monthly costs (USD)
- FDA approval years
- Recommended age ranges

This enables the **3-way hybrid query** combining:
1. Patient records (relational)
2. Literature knowledge graph (property graph)
3. Clinical trial outcomes (relational)

---

## Processing Your Own Medical PDFs

Want to extract knowledge graphs from your own research papers? Follow these steps:

### Step 1: Place Your PDF

```bash
cp /path/to/your/medical_research.pdf sample-data/
```

### Step 2: Run Extraction

```bash
cd extractPDF
python extract_pdf_to_graph.py ../sample-data/your_medical_research.pdf
```

### Step 3: Review Output

Check `extractPDF/output/` for 5 generated CSV files with extracted entities and relationships.

### Step 4: Load into Oracle

```bash
docker exec -it oracle23ai sqlplus system/oracle@FREEPDB1
@load_extracted_graph_data.sql
```

**For detailed extraction instructions**, see [`../extractPDF/README.md`](../extractPDF/README.md)

---

## Data Summary

| File | Type | Records | Status |
|------|------|---------|--------|
| `sample_patients.csv` | CSV | 10 patients | ✅ Ready |
| `treatment_outcomes.csv` | CSV | 7 treatments | ✅ Ready (legacy) |
| `clinical_trial_outcomes.csv` | CSV | 14 treatments | ✅ Ready (3-way demo) |
| `clinical_trial_outcomes.xlsx` | Excel | 14 treatments | ✅ Ready |
| `diabetes-treatment-study.pdf` | PDF | 1 paper | ✅ Real PDF |

---

## Creating Realistic Sample Data

If you want to create more realistic sample data:

### Generate More Patients:
Use the CSV format and add more rows following the pattern:
```csv
1011,Patient Name,65,Type 2 Diabetes,2024-03-15,Dr. Name
```

### Add More Research Papers:
1. Find real medical research papers (open access from PubMed, etc.)
2. Place PDFs in this directory
3. Run `cd ../extractPDF && python extract_pdf_to_graph.py ../sample-data/your-paper.pdf`
4. Load extracted entities: `@load_extracted_graph_data.sql`
5. Property graph automatically includes new treatments and relationships

### Add More Clinical Outcomes:
1. Open `clinical_trial_outcomes.csv` or `.xlsx`
2. Add new treatments with their effectiveness/safety/cost data
3. Reload: `@load_clinical_outcomes.sql`
4. 3-way queries will include new treatments

### Generate Synthetic Data:
You can use tools like Mockaroo or Faker to generate large patient datasets:
```python
from faker import Faker
fake = Faker()

for i in range(100):
    print(f"{1000+i},{fake.name()},{fake.random_int(45,90)},Type 2 Diabetes,{fake.date_this_year()},Dr. {fake.last_name()}")
```

---

## Next Steps

1. ✅ **Quick Start**: Data files are ready - run `@load_extracted_graph_data.sql` and `@load_clinical_outcomes.sql`
2. 🔬 **PDF Extraction**: Process your own PDFs - see `../extractPDF/README.md`
3. 📊 **3-Way Demo**: Run complete demo queries - see `../three_way_hybrid_query.sql`
4. 📖 **Full Workflow**: Complete documentation - see `../README.md`
5. 🎭 **Presentation**: 15-minute demo script - see `../DEMO_GUIDE.md`

---

**Note:** The current sample data demonstrates the complete 3-way hybrid query capability:
- **10 patients** (8 elderly with Type 2 Diabetes)
- **14 treatments** extracted from real PDF
- **14 clinical outcomes** with effectiveness/safety/cost
- **Result**: 32-row query combining all three data sources in ONE SQL statement!

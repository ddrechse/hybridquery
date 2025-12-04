# PDF to Oracle Property Graph Extractor

Extract medical research papers into Oracle Property Graph format using Docling.

---

## 🎯 What This Does

This tool processes a **real PDF file** of a medical research paper and extracts:

1. **Paper metadata** (title, filename, publication date)
2. **Treatments** mentioned (GLP-1 Agonists, SGLT2 Inhibitors, etc.)
3. **Medical conditions** (Type 1/2 Diabetes)
4. **Relationships**:
   - Paper MENTIONS Treatment
   - Treatment TREATS Condition

**Output:** 5 CSV files ready to load into Oracle Database Property Graph tables.

---

## 📋 Prerequisites

- Python 3.8 or later
- Your diabetes_treatment_study.pdf file (real PDF created from Word)

---

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
cd hybridQuery/extractPDF
pip install -r requirements.txt
```

This installs:
- **Docling** - Advanced PDF parsing
- **spaCy** - Natural language processing
- **pandas** - Data manipulation

### Step 2: Run the Extractor

```bash
python extract_pdf_to_graph.py ../sample-data/diabetes_treatment_study.pdf
```

### Step 3: Check Output

```bash
ls -la output/
```

You should see:
```
papers_nodes.csv       - Paper metadata (1 row)
treatments_nodes.csv   - Treatments found (7+ rows)
conditions_nodes.csv   - Conditions found (2 rows)
mentions_edges.csv     - Paper→Treatment links
treats_edges.csv       - Treatment→Condition links
```

---

## 📄 Output Format

### papers_nodes.csv
```csv
node_id,filename,title,publication_date
1,diabetes_treatment_study.pdf,"Comparative Effectiveness of Second-Line Diabetes Treatments",2023-01-01
```

### treatments_nodes.csv
```csv
node_id,entity_name,treatment_type
100,GLP-1 Agonists,Pharmaceutical
101,SGLT2 Inhibitors,Pharmaceutical
102,DPP-4 Inhibitors,Pharmaceutical
103,Insulin Therapy,Pharmaceutical
104,Basal Insulin,Pharmaceutical
105,Metformin,Pharmaceutical
106,Sulfonylureas,Pharmaceutical
```

### conditions_nodes.csv
```csv
node_id,name,icd10_code
200,Type 1 Diabetes,E10
201,Type 2 Diabetes,E11
```

### mentions_edges.csv
```csv
edge_id,from_node_id,to_node_id
1000,1,100  # Paper mentions GLP-1 Agonists
1001,1,101  # Paper mentions SGLT2 Inhibitors
1002,1,102  # Paper mentions DPP-4 Inhibitors
...
```

### treats_edges.csv
```csv
edge_id,from_node_id,to_node_id
2000,100,201  # GLP-1 Agonists treat Type 2 Diabetes
2001,101,201  # SGLT2 Inhibitors treat Type 2 Diabetes
2002,102,201  # DPP-4 Inhibitors treat Type 2 Diabetes
...
```

---

## 🔧 Usage Options

### Basic Usage
```bash
python extract_pdf_to_graph.py path/to/paper.pdf
```

### With Publication Date
```bash
python extract_pdf_to_graph.py paper.pdf --date 2023-01-15
```

### Custom Output Directory
```bash
python extract_pdf_to_graph.py paper.pdf --output my_custom_dir
```

### Get Help
```bash
python extract_pdf_to_graph.py --help
```

---

## 🗄️ Loading into Oracle

### Option 1: Use External Tables (Recommended)

```sql
-- Create directory object
CREATE OR REPLACE DIRECTORY extractpdf_dir
AS '/path/to/hybridQuery/extractPDF/output';

-- Create external table for papers
CREATE TABLE papers_nodes_ext (
    node_id NUMBER,
    filename VARCHAR2(200),
    title VARCHAR2(500),
    publication_date DATE
)
ORGANIZATION EXTERNAL (
    TYPE ORACLE_LOADER
    DEFAULT DIRECTORY extractpdf_dir
    ACCESS PARAMETERS (
        RECORDS DELIMITED BY NEWLINE
        SKIP 1
        FIELDS TERMINATED BY ','
        OPTIONALLY ENCLOSED BY '"'
        MISSING FIELD VALUES ARE NULL
        (node_id, filename, title, publication_date DATE "YYYY-MM-DD")
    )
    LOCATION ('papers_nodes.csv')
)
REJECT LIMIT UNLIMITED;

-- Load into permanent table
INSERT INTO papers_nodes SELECT * FROM papers_nodes_ext;

-- Repeat for other tables:
-- treatments_nodes_ext → treatments_nodes
-- conditions_nodes_ext → conditions_nodes
-- mentions_edges_ext → mentions_edges
-- treats_edges_ext → treats_edges
```

### Option 2: Use SQL*Loader

```bash
# Create control file for each CSV
sqlldr userid=user/pass@db control=papers_nodes.ctl

# Example control file (papers_nodes.ctl):
LOAD DATA
INFILE 'output/papers_nodes.csv'
INTO TABLE papers_nodes
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
TRAILING NULLCOLS
(
    node_id,
    filename,
    title,
    publication_date DATE "YYYY-MM-DD"
)
```

### Option 3: Manual INSERT

For small datasets, you can manually copy the data:

```sql
-- Copy from papers_nodes.csv
INSERT INTO papers_nodes (node_id, filename, title, publication_date)
VALUES (1, 'diabetes_treatment_study.pdf',
        'Comparative Effectiveness of Second-Line Diabetes Treatments',
        DATE '2023-01-01');

-- Repeat for other rows...
```

---

## 🔍 How It Works

### Architecture

```
diabetes_treatment_study.pdf
    ↓
[Docling] Parse PDF structure
    ├─ Extract title
    ├─ Extract sections
    └─ Export as markdown
    ↓
[EntityExtractor] Find entities
    ├─ Regex patterns for treatments
    ├─ Regex patterns for conditions
    └─ Context-aware relationship detection
    ↓
[GraphBuilder] Build graph data
    ├─ Create Paper node (node_id=1)
    ├─ Create Treatment nodes (node_id=100+)
    ├─ Create Condition nodes (node_id=200+)
    ├─ Create MENTIONS edges
    └─ Create TREATS edges
    ↓
[CSV Export] Write 5 CSV files
```

### Entity Extraction Logic

The `entity_patterns.py` module uses regex patterns to find:

**Treatments:**
```python
# Exact matches for known medications
"GLP-1 Agonists", "SGLT2 Inhibitors", "DPP-4 Inhibitors",
"Insulin Therapy", "Basal Insulin", "Metformin", "Sulfonylureas"
```

**Conditions:**
```python
# Pattern matching for diabetes types
"Type 1 Diabetes", "Type 2 Diabetes", "Diabetes mellitus"
```

**Relationships:**
```python
# Patterns like:
"GLP-1 agonists treat Type 2 Diabetes"
"SGLT2 inhibitors for Type 2 Diabetes"
"Type 2 Diabetes treatment with Insulin Therapy"
```

---

## 📊 Expected Results

For the diabetes_treatment_study.pdf file, you should get:

- **1 paper node** (the PDF file)
- **6-7 treatment nodes** (GLP-1 Agonists, SGLT2 Inhibitors, DPP-4 Inhibitors, Insulin Therapy, Basal Insulin, Metformin, Sulfonylureas)
- **2 condition nodes** (Type 1 Diabetes, Type 2 Diabetes)
- **6-7 MENTIONS edges** (Paper → each Treatment)
- **8-10 TREATS edges** (Treatment → Condition)

---

## 🧪 Testing the Extractor

### Test Entity Extraction
```bash
python entity_patterns.py
```

This runs a self-test with sample text.

### Test Graph Builder
```bash
python graph_builder.py
```

This creates test CSV files to verify the builder works.

### Test Full Pipeline
```bash
python extract_pdf_to_graph.py ../sample-data/diabetes_treatment_study.pdf
```

Check `output/` directory for CSV files.

---

## 🐛 Troubleshooting

### Problem: Docling not found

```
ModuleNotFoundError: No module named 'docling'
```

**Solution:**
```bash
pip install docling
```

### Problem: No entities extracted

```
✓ Found 0 unique treatments
✓ Found 0 unique conditions
```

**Solution:**
- Check that your PDF contains medical terminology
- Verify PDF text is extractable (not scanned images)
- Try OCR if PDF is image-based

### Problem: CSV files empty

**Solution:**
- Check console output for extraction results
- Verify patterns match your document's terminology
- Adjust patterns in `entity_patterns.py` if needed

### Problem: Permission denied writing CSV

```
PermissionError: [Errno 13] Permission denied: 'output/papers_nodes.csv'
```

**Solution:**
```bash
chmod -R 755 output/
# or
rm -rf output/ && mkdir output
```

---

## 🔧 Customizing Entity Extraction

### Add New Treatments

Edit `entity_patterns.py`:

```python
self.known_treatments = [
    'Metformin',
    'GLP-1 Agonists',
    # Add your treatments here:
    'Liraglutide',
    'Empagliflozin',
    'Your New Treatment',
]
```

### Add New Relationship Patterns

Edit `entity_patterns.py`:

```python
self.treats_patterns = [
    # Existing patterns...

    # Add new pattern:
    re.compile(
        rf'\b({treatment_names})\s+is\s+effective\s+for\s+({condition_names})\b',
        re.IGNORECASE
    ),
]
```

---

## 📚 Project Files

| File | Purpose |
|------|---------|
| `extract_pdf_to_graph.py` | Main extraction script |
| `entity_patterns.py` | Regex patterns for medical entities |
| `graph_builder.py` | Builds CSV files for Oracle |
| `requirements.txt` | Python dependencies |
| `README.md` | This file |
| `output/` | Generated CSV files |

---

## 🎯 Integration with Oracle POC

### Complete Workflow

```bash
# 1. Extract from PDF
cd extractPDF
python extract_pdf_to_graph.py ../sample-data/diabetes_treatment_study.pdf

# 2. Load into Oracle
sqlplus user/pass@db
@../oracle-setup/02_create_graph_tables.sql

# 3. Load CSV data (use external tables or SQL*Loader)
# ... load from output/*.csv

# 4. Create property graph
@../oracle-setup/03_create_property_graph.sql

# 5. Run hybrid queries
@../oracle-setup/05_test_queries.sql
```

---

## 🚀 Next Steps

1. **Extract your PDF**: Run the extractor on your real PDF
2. **Review CSV files**: Check output/ for correct data
3. **Load into Oracle**: Use external tables or SQL*Loader
4. **Test queries**: Run hybrid queries combining patient + treatment data

---

## 💡 Pro Tips

- **Multiple PDFs**: Run the script multiple times on different PDFs. Graph builder will assign unique IDs.
- **Batch Processing**: Loop through a directory of PDFs:
  ```bash
  for pdf in ../sample-data/*.pdf; do
      python extract_pdf_to_graph.py "$pdf"
  done
  ```
- **Custom Patterns**: Modify `entity_patterns.py` to match your domain terminology
- **Validation**: Always check the CSV files before loading into Oracle

---

## 📖 Related Documentation

- Main POC: `../README.md`
- Oracle SQL Scripts: `../oracle-setup/`
- Demo Guide: `../demo/demo_walkthrough.md`
- Docling Documentation: https://www.docling.ai/

---

**Ready to extract your PDF? Run:** `python extract_pdf_to_graph.py ../sample-data/diabetes_treatment_study.pdf` 🎉

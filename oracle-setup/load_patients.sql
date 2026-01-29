-- ============================================================================
-- Load Patient Data Only
-- ============================================================================
-- Extracted from 04_load_sample_data.sql to allow separate loading of
-- relational data while keeping graph data dynamic (LLM-generated).

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

COMMIT;

PROMPT   → Loaded 10 patient records

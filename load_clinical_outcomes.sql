SET FEEDBACK OFF
SET ECHO OFF
SET VERIFY OFF

-- =====================================================================
-- Load Clinical Trial Outcomes Data
-- =====================================================================
-- Loads historical treatment effectiveness, safety, and cost data.
-- =====================================================================

PROMPT Loading Clinical Outcomes data...

-- Clean load
BEGIN
    EXECUTE IMMEDIATE 'TRUNCATE TABLE clinical_outcomes';
EXCEPTION
    WHEN OTHERS THEN
        NULL; -- Ignore if table empty or issues
END;
/

-- Insert clinical trial outcomes
INSERT INTO clinical_outcomes VALUES ('GLP-1 Agonists', 8.5, 2.0, 450.00, 2005, 18, 85);
INSERT INTO clinical_outcomes VALUES ('SGLT2 Inhibitors', 8.0, 1.5, 380.00, 2013, 18, 90);
INSERT INTO clinical_outcomes VALUES ('DPP-4 Inhibitors', 7.2, 1.2, 320.00, 2006, 18, 95);
INSERT INTO clinical_outcomes VALUES ('Insulin Therapy', 7.8, 2.5, 120.00, 1982, 0, 999);
INSERT INTO clinical_outcomes VALUES ('Basal Insulin', 7.5, 2.3, 95.00, 1990, 0, 999);
INSERT INTO clinical_outcomes VALUES ('Metformin', 7.5, 1.0, 25.00, 1995, 18, 80);
INSERT INTO clinical_outcomes VALUES ('Sulfonylureas', 6.8, 2.8, 35.00, 1984, 18, 75);
INSERT INTO clinical_outcomes VALUES ('Semaglutide', 9.0, 2.1, 500.00, 2017, 18, 85);
INSERT INTO clinical_outcomes VALUES ('Liraglutide', 8.3, 2.0, 475.00, 2010, 18, 85);
INSERT INTO clinical_outcomes VALUES ('Empagliflozin', 8.2, 1.4, 395.00, 2014, 18, 90);
INSERT INTO clinical_outcomes VALUES ('Dapagliflozin', 7.9, 1.6, 385.00, 2014, 18, 90);
INSERT INTO clinical_outcomes VALUES ('Canagliflozin', 7.8, 1.7, 390.00, 2013, 18, 90);
INSERT INTO clinical_outcomes VALUES ('Sitagliptin', 7.0, 1.1, 310.00, 2006, 18, 95);
INSERT INTO clinical_outcomes VALUES ('Linagliptin', 7.1, 1.2, 325.00, 2011, 18, 95);

COMMIT;

PROMPT   -> Loaded 14 clinical outcomes

SET FEEDBACK ON
SET ECHO OFF
SET VERIFY OFF

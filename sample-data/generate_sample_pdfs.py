from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
import os

# Ensure output directory exists
OUTPUT_DIR = "/Users/DDRECHSE/projects/hybridquery/sample-data/"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def create_comprehensive_pdf(filename, title, authors, content_sections):
    filepath = os.path.join(OUTPUT_DIR, filename)
    doc = SimpleDocTemplate(
        filepath, 
        pagesize=A4, 
        rightMargin=72, 
        leftMargin=72, 
        topMargin=72, 
        bottomMargin=18,
        title=title  # Add PDF metadata title
    )
    
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='MedicalTitle', parent=styles['Heading1'], fontSize=18, leading=22, alignment=1))
    styles.add(ParagraphStyle(name='MedicalAuthors', parent=styles['Normal'], fontSize=12, leading=14, alignment=1, fontName='Helvetica-Oblique'))
    styles.add(ParagraphStyle(name='SectionHeader', parent=styles['Heading2'], fontSize=12, leading=14, spaceBefore=12, spaceAfter=6))
    styles.add(ParagraphStyle(name='MedicalBody', parent=styles['Normal'], fontSize=11, leading=14, fontName='Times-Roman', spaceAfter=6))
    styles.add(ParagraphStyle(name='AbstractText', parent=styles['MedicalBody'], fontSize=10, leading=12, leftIndent=20, rightIndent=20))
    
    story = []
    
    # Header Note
    story.append(Paragraph("The New England Journal of Medicine (Synthetic Demo) | ORIGINAL ARTICLE", styles['Normal']))
    story.append(Spacer(1, 12))
    
    # Title & Authors
    story.append(Paragraph(title, styles['MedicalTitle']))
    story.append(Spacer(1, 12))
    story.append(Paragraph(authors, styles['MedicalAuthors']))
    story.append(Spacer(1, 24))
    
    # Abstract
    if "Abstract" in content_sections:
        story.append(Paragraph("ABSTRACT", styles['SectionHeader']))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.black))
        story.append(Spacer(1, 6))
        story.append(Paragraph(content_sections["Abstract"], styles['AbstractText']))
        story.append(Spacer(1, 6))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.black))
        story.append(Spacer(1, 12))
        del content_sections["Abstract"]
        
    # Main Body
    for section_title, section_text in content_sections.items():
        story.append(Paragraph(section_title.upper(), styles['SectionHeader']))
        # Handle multi-line text (split by newlines for Paragraphs)
        for line in section_text.split('\n\n'):
            story.append(Paragraph(line.strip(), styles['MedicalBody']))
        story.append(Spacer(1, 6))
        
    doc.build(story)
    print(f"Created comprehensive PDF (ReportLab): {filepath}")

# -------------------------------------------------------------------------
# PAPER 1: OBESITY MANAGEMENT (GLP-1 Focus)
# -------------------------------------------------------------------------
obesity_title = "Efficacy and Safety of Semaglutide versus Liraglutide for Weight Management in Adults with Overweight or Obesity: The STEP-8 Randomized Clinical Trial"
obesity_authors = "John D. Smith, M.D., Sarah L. Jones, Ph.D., Robert K. Lee, M.D., and the STEP-8 Investigators"

obesity_sections = {
    "Abstract": """BACKGROUND
Glucagon-like peptide-1 (GLP-1) analogues are effective for weight management. However, direct comparisons between once-weekly subcutaneous Semaglutide 2.4 mg and once-daily subcutaneous Liraglutide 3.0 mg are limited.

METHODS
We conducted a randomized, open-label, 68-week trial at 19 sites involving adults with a body-mass index (BMI) of 30 or greater, or 27 or greater with one or more weight-related comorbidities, and without diabetes. Participants were randomly assigned (3:1:3:1) to receive subcutaneous Semaglutide 2.4 mg once weekly, matching placebo, subcutaneous Liraglutide 3.0 mg once daily, or matching placebo. All received diet and physical activity counseling.

RESULTS
The mean weight change from baseline to week 68 was -15.8% with Semaglutide vs -6.4% with Liraglutide (difference, -9.4 percentage points; 95% CI, -12.0 to -6.8; P<0.001). Participants who received Semaglutide had greater improvements in cardiometabolic risk factors than those who received Liraglutide. Gastrointestinal adverse events were common with both treatments (84.1% Semaglutide vs 82.7% Liraglutide).

CONCLUSIONS
Among adults with overweight or obesity without diabetes, once-weekly subcutaneous Semaglutide resulted in significantly greater weight loss than once-daily subcutaneous Liraglutide.""",

    "Introduction": """Obesity is a complex, chronic disease associated with numerous complications, including Type 2 Diabetes, cardiovascular disease, obstructive sleep apnea, and certain cancers. Despite public health efforts, the prevalence continues to rise globally. Lifestyle interventions, including diet and exercise, remain the cornerstone of weight management but frequently result in insufficient long-term weight loss due to metabolic adaptation and hormonal upregulation of appetite.

Pharmacotherapy is recommended as an adjunct to lifestyle intervention for individuals with a BMI of 30 or higher, or 27 or higher with comorbidities. Glucagon-like peptide-1 (GLP-1) receptor agonists mimic the effects of endogenous GLP-1, a gut hormone that regulates appetite and food intake. Liraglutide 3.0 mg, a once-daily GLP-1 analogue, was approved for weight management in 2014 based on the SCALE program. Semaglutide 2.4 mg, a once-weekly GLP-1 analogue, has recently demonstrated superior efficacy in the STEP (Semaglutide Treatment Effect in People with obesity) clinical trial program. This head-to-head trial (STEP-8) was designed to compare their efficacy and safety directly.""",

    "Methods": """TRIAL DESIGN AND OVERSIGHT
This was a 68-week, randomized, open-label, active-controlled, parallel-group, phase 3b trial conducted at 19 sites in the United States. The trial was conducted in strict accordance with the Declaration of Helsinki and Good Clinical Practice guidelines. The protocol was approved by independent ethics committees at each site.

PARTICIPANTS
Eligible participants were adults (>=18 years) with a stable body weight and a BMI of >=30, or >=27 with at least one weight-related comorbidity (e.g., hypertension, dyslipidemia, obstructive sleep apnea, or cardiovascular disease). Patients with Type 1 or Type 2 Diabetes were excluded to isolate the weight-loss effect from glycemic control. Key exclusion criteria included a history of pancreatitis, major depressive disorder, or use of other weight-loss medications within 90 days of screening.

INTERVENTIONS AND PROCEDURES
Participants were randomized to Semaglutide 2.4 mg once weekly or Liraglutide 3.0 mg once daily. Doses were escalated over 16 weeks (Semaglutide) or 4 weeks (Liraglutide) to minimize gastrointestinal side effects. Both groups received standard lifestyle counseling, including a deficit of 500 kcal/day and 150 minutes of physical activity per week.

STATISTICAL ANALYSIS
The primary endpoint was the percentage change in body weight from baseline to week 68. The confirmatory secondary endpoint was achievement of weight loss of 10% or more, 15% or more, and 20% or more. Efficacy analyses were based on the treatment policy estimand using a mixed model for repeated measures. A sample size of 338 provided 90% power to detect a difference of 5 percentage points between groups.""",

    "Results": """WEIGHT LOSS OUTCOMES
A total of 338 participants underwent randomization (126 to Semaglutide, 127 to Liraglutide, and 85 to placebo groups combined). Baseline characteristics were similar across groups; the mean age was 49 years, mean body weight was 104.5 kg, and mean BMI was 37.5. 78.4% were female.

The mean change in body weight from baseline to week 68 was -15.8% (Standard Deviation [SD] 6.0) in the Semaglutide group compared with -6.4% (SD 5.0) in the Liraglutide group. The estimated treatment difference was -9.4 percentage points (95% CI, -12.0 to -6.8; P<0.001).

Treatment with Semaglutide lead to significantly higher rates of categorical weight loss:
- Weight loss >= 10%: 70.9% (Semaglutide) vs 25.6% (Liraglutide)
- Weight loss >= 15%: 55.6% (Semaglutide) vs 12.0% (Liraglutide)
- Weight loss >= 20%: 38.5% (Semaglutide) vs 6.0% (Liraglutide)

CARDIOMETABOLIC RISK FACTORS
Improvements in waist circumference, systolic and diastolic blood pressure, C-reactive protein, and lipid levels were greater with Semaglutide than with Liraglutide. For example, the reduction in waist circumference was 13.5 cm with Semaglutide vs 6.8 cm with Liraglutide (P<0.001). Systolic blood pressure decreased by 5.5 mm Hg with Semaglutide compared to 3.2 mm Hg with Liraglutide.""",

    "Safety and Adverse Events": """Adverse events were reported by 95.2% of participants in the Semaglutide group and 96.1% in the Liraglutide group. The most common adverse events were gastrointestinal disorders: nausea (60.3% vs 59.1%), vomiting (35.7% vs 31.5%), diarrhea (30.2% vs 24.4%), and constipation (23.8% vs 31.5%). Most events were mild to moderate in severity and transient, occurring primarily during the dose-escalation phase. 

Serious adverse events occurred in 7.9% of participants in the Semaglutide group and 11.0% in the Liraglutide group. Treatment discontinuation due to adverse events occurred in 13.5% of participants with Semaglutide and 27.6% with Liraglutide, suggesting better overall tolerability of the weekly regimen despite similar GI side effect rates.""",
    
    "Discussion": """In this head-to-head trial, once-weekly Semaglutide 2.4 mg was superior to once-daily Liraglutide 3.0 mg for weight reduction in adults with overweight or obesity without diabetes. The magnitude of weight loss observed with Semaglutide (approx. 16%) approaches that seen with bariatric surgery (typically 20-30%).

The mechanistic basis for the greater efficacy of Semaglutide may relate to its unique pharmacokinetic profile derived from albumin binding, allowing for sustained GLP-1 receptor activation, and potentially greater penetration into specific brain regions regulating appetite and satiety compared to Liraglutide.

While both drugs are effective, the magnitude of weight loss with Semaglutide sets a new benchmark for pharmacotherapy. Tirzepatide, a dual GIP/GLP-1 agonist, has shown even greater efficacy in recent trials (SURMOUNT-1), but was not included in this comparison.

LIMITATIONS
The trial was open-label, which may introduce bias. The duration was 68 weeks, and longer-term data are needed to assess durability of weight loss and long-term safety. The majority of participants were female and White, which may limit generalizability to other populations.""",

    "References": """1. Wilding JPH, et al. Once-Weekly Semaglutide in Adults with Overweight or Obesity. N Engl J Med 2021;384:989-1002.
2. Pi-Sunyer X, et al. A Randomized, Controlled Trial of 3.0 mg of Liraglutide in Weight Management. N Engl J Med 2015;373:11-22.
3. Jastreboff AM, et al. Tirzepatide Once Weekly for the Treatment of Obesity. N Engl J Med 2022;387:205-216."""
}


# -------------------------------------------------------------------------
# PAPER 2: CARDIOVASCULAR OUTCOMES (SGLT2 Focus)
# -------------------------------------------------------------------------
cardio_title = "Dapagliflozin in Patients with Heart Failure and Reduced Ejection Fraction: The DAPA-HF Trial Findings"
cardio_authors = "Michael J. McMurray, M.D., Solomon D. Rex, M.D., on behalf of the DAPA-HF Committees"

cardio_sections = {
    "Abstract": """BACKGROUND
Sodium-glucose cotransporter 2 (SGLT2) inhibitors reduce the risk of heart failure hospitalization in patients with Type 2 Diabetes. We investigated whether Dapagliflozin would provide similar cardiovascular benefits in patients with established heart failure and a reduced ejection fraction, regardless of the presence of diabetes.

METHODS
In this phase 3, placebo-controlled trial, we randomly assigned 4744 patients with New York Heart Association class II, III, or IV heart failure and an ejection fraction of 40% or less to receive either Dapagliflozin 10 mg once daily or placebo, in addition to recommended therapy. The primary outcome was a composite of worsening heart failure (hospitalization or an urgent visit resulting in intravenous therapy for heart failure) or cardiovascular death.

RESULTS
Over a median of 18.2 months, the primary outcome occurred in 386 of 2373 patients (16.3%) in the Dapagliflozin group and in 502 of 2371 patients (21.2%) in the placebo group (hazard ratio, 0.74; 95% CI, 0.65 to 0.85; P<0.001). A first worsening heart failure event occurred in 237 patients (10.0%) in the Dapagliflozin group and in 326 patients (13.7%) in the placebo group (HR 0.70; 95% CI, 0.59 to 0.83).

CONCLUSIONS
Among patients with heart failure and a reduced ejection fraction, the risk of worsening heart failure or death from cardiovascular causes was lower among those who received Dapagliflozin than among those who received placebo, regardless of the presence or absence of diabetes.""",

    "Introduction": """SGLT2 inhibitors, such as Empagliflozin, Canagliflozin, and Dapagliflozin, were originally developed as glucose-lowering agents for Type 2 Diabetes. Large cardiovascular outcome trials (CVOTs), such as EMPA-REG OUTCOME and DECLARE-TIMI 58, surprisingly demonstrated that these agents robustly reduced the risk of hospitalization for heart failure.

This observation led to the hypothesis that SGLT2 inhibitors might benefit patients with established Heart Failure (HF) through mechanisms independent of glucose lowering. This trial (DAPA-HF) was designed to test the efficacy and safety of Dapagliflozin specifically in patients with chronic heart failure with reduced ejection fraction (HFrEF), including those without diabetes.""",

    "Methods": """STUDY POPULATION
Eligible patients were 18 years of age or older, had New York Heart Association (NYHA) class II to IV heart failure, and had a left ventricular ejection fraction (LVEF) of <= 40%. Patients were required to have an elevated N-terminal pro-B-type natriuretic peptide (NT-proBNP) level (>=600 pg/ml). Key exclusion criteria included Type 1 Diabetes, systolic blood pressure < 95 mm Hg, and estimated glomerular filtration rate (eGFR) < 30 ml/min/1.73m^2.

PROCEDURES
Patients were randomly assigned to receive Dapagliflozin 10 mg once daily or matching placebo. All patients continued their standard heart failure therapies (standard of care), which included ACE inhibitors, ARBs, angiotensin receptor-neprilysin inhibitors (ARNI) like Sacubitril-Valsartan, beta-blockers, and mineralocorticoid receptor antagonists (MRAs).

STATISTICAL ANALYSIS
The primary efficacy outcome was analyzed with use of a Cox proportional-hazards model stratified according to diabetes status at baseline. Kaplan-Meier estimates of the cumulative incidence of the primary outcome were calculated.""",

    "Results": """PRIMARY OUTCOME
The primary composite outcome (worsening heart failure or cardiovascular death) occurred in 386 patients (16.3%) in the Dapagliflozin group and 502 patients (21.2%) in the placebo group (Hazard Ratio [HR] 0.74; 95% Confidence Interval [CI] 0.65-0.85; P<0.001). The number needed to treat to prevent one primary outcome event was 21.

The benefit was consistent across prespecified subgroups, including patients with diabetes (HR 0.75) and without diabetes (HR 0.73), confirming that the mechanism of action is independent of glycemic control.

SECONDARY OUTCOMES
Cardiovascular death occurred in 227 patients (9.6%) in the Dapagliflozin group and 273 (11.5%) in the placebo group (HR 0.82; 95% CI 0.69-0.98). Hospitalization for heart failure occurred in 231 (9.7%) vs 318 (13.4%) respectively (HR 0.70; 95% CI 0.59-0.83).

All-cause mortality was also lower in the Dapagliflozin group (276 deaths, 11.6%) than in the placebo group (329 deaths, 13.9%) (HR 0.83; 95% CI 0.71-0.97).

Kansas City Cardiomyopathy Questionnaire (KCCQ) scores, a measure of quality of life, improved significantly more in the Dapagliflozin group than in the placebo group.""",
    
    "Discussion": """These findings establish SGLT2 inhibitors as a new foundation or "pillar" of medical therapy for HFrEF, joining beta-blockers, RAAS inhibitors (ACEi/ARB/ARNI), and MRAs. The magnitude of benefit—a 26% reduction in the primary endpoint relative to excellent background therapy—is clinically substantial.

Mechanistically, the benefits of SGLT2 inhibitors in heart failure are complex and multifactorial. Proposed mechanisms include osmotic diuresis and natriuresis (reducing preload), reduction in arterial stiffness and vascular resistance (reducing afterload), improved myocardial energetics (shift towards ketone body utilization), and inhibition of the sodium-hydrogen exchanger in the myocardium.

The consistency of benefit in patients without diabetes is particularly important, as it expands the indication for these drugs to a much broader population of heart failure patients.

Similar benefits have been observed with Empagliflozin in the EMPEROR-Reduced trial, suggesting a class effect for SGLT2 inhibitors in HFrEF. However, Dapagliflozin was the first to demonstrate a significant reduction in cardiovascular death in this population.""",

    "Conclusion": """Dapagliflozin reduced the risk of worsening heart failure and death from cardiovascular causes in patients with heart failure and reduced ejection fraction. These benefits were observed in patients receiving excellent standard therapy and extended to patients both with and without Type 2 Diabetes.""",

    "References": """1. McMurray JJV, et al. Dapagliflozin in Patients with Heart Failure and Reduced Ejection Fraction. N Engl J Med 2019;381:1995-2008.
2. Packer M, et al. Cardiovascular and Renal Outcomes with Empagliflozin in Heart Failure. N Engl J Med 2020;383:1413-1424.
3. Zinman B, et al. Empagliflozin, Cardiovascular Outcomes, and Mortality in Type 2 Diabetes. N Engl J Med 2015;373:2117-2128."""
}

# -------------------------------------------------------------------------
# PAPER 3: DIABETES TREATMENT (First PDF - comprehensive diabetes therapies)
# -------------------------------------------------------------------------
diabetes_title = "Comparative Effectiveness of Metformin, Sulfonylureas, and DPP-4 Inhibitors as Second-Line Agents for Type 2 Diabetes: A Systematic Review and Network Meta-Analysis"
diabetes_authors = "Emily R. Chen, M.D., Ph.D., Michael A. Rodriguez, M.D., and the Diabetes Treatment Review Consortium"

diabetes_sections = {
    "Abstract": """BACKGROUND
Multiple oral agents are available as second-line therapies for Type 2 Diabetes when metformin monotherapy is insufficient. Direct comparative evidence is limited.

METHODS
We conducted a systematic review and network meta-analysis of randomized controlled trials comparing second-line therapies added to metformin. Outcomes included HbA1c reduction, weight change, and hypoglycemia risk.

RESULTS
GLP-1 Agonists and SGLT2 Inhibitors provided superior HbA1c reduction (-0.9% to -1.2%) compared to DPP-4 Inhibitors (-0.6%) and Sulfonylureas (-0.8%). GLP-1 Agonists lead to significant weight loss (-2.8 kg), while Sulfonylureas caused weight gain (+2.3 kg). SGLT2 Inhibitors were weight-neutral.

CONCLUSIONS
GLP-1 Agonists and SGLT2 Inhibitors offer superior glycemic control and favorable weight profiles compared to traditional second-line agents for Type 2 Diabetes.""",

    "Introduction": """Type 2 Diabetes Mellitus affects over 500 million individuals globally. Metformin remains the first-line pharmacotherapy due to its efficacy, safety profile, and low cost. However, progressive beta-cell dysfunction necessitates intensification of therapy in most patients within 3-5 years.

Second-line options include Sulfonylureas, DPP-4 Inhibitors, GLP-1 Receptor Agonists, SGLT2 Inhibitors, and Insulin Therapy. Clinical guidelines provide multiple options but limited head-to-head comparative data to guide selection.""",

    "Methods": """We searched MEDLINE, Embase, and CENTRAL for randomized trials published through December 2023. Eligible studies compared second-line agents in adults with Type 2 Diabetes inadequately controlled on metformin (HbA1c >= 7.0%).

Network meta-analysis was conducted using a Bayesian framework. Primary outcome was change in HbA1c at 24-52 weeks. Secondary outcomes included body weight, hypoglycemia, and treatment discontinuation.""",

    "Results": """A total of 127 trials (n=58,453 participants) were included.

HbA1c Reduction:
- GLP-1 Agonists (Semaglutide, Liraglutide): -1.2% (95% CrI: -1.4 to -1.0)
- SGLT2 Inhibitors (Dapagliflozin, Empagliflozin): -0.9% (95% CrI: -1.1 to -0.7)
- Sulfonylureas (Glipizide, Gliclazide): -0.8% (95% CrI: -1.0 to -0.6)
- DPP-4 Inhibitors (Sitagliptin, Linagliptin): -0.6% (95% CrI: -0.8 to -0.4)
- Insulin Therapy (Basal Insulin): -1.1% (95% CrI: -1.3 to -0.9)

Weight Change:
- GLP-1 Agonists caused the greatest weight loss (-2.8 kg)
- SGLT2 Inhibitors provided moderate weight loss (-1.8 kg)
- DPP-4 Inhibitors were weight-neutral
- Sulfonylureas and Insulin Therapy both caused weight gain (+2.3 kg and +3.1 kg respectively)

Hypoglycemia:
- Sulfonylureas had the highest risk (RR 3.8 vs placebo)
- Insulin Therapy also elevated risk (RR 2.9)
- GLP-1 Agonists, SGLT2 Inhibitors, and DPP-4 Inhibitors had minimal hypoglycemia risk""",

    "Discussion": """This network meta-analysis demonstrates that GLP-1 Receptor Agonists provide the most favorable overall profile for second-line Type 2 Diabetes therapy, with superior HbA1c reduction, substantial weight loss, and minimal hypoglycemia risk. SGLT2 Inhibitors offer similar benefits with added cardiovascular and renal protection demonstrated in outcomes trials.

Traditional agents like Sulfonylureas remain widely used due to low cost and familiarity, but their weight gain and hypoglycemia risk are clinically significant drawbacks. DPP-4 Inhibitors offer safety and tolerability but modest efficacy.

Individual patient factors should guide selection, including cost, patient preference, comorbidities, and weight goals.""",

    "References": """1. Davies MJ, et al. Management of Hyperglycemia in Type 2 Diabetes, 2022. Diabetes Care 2022;45:2753-2786.
2. Neuen BL, et al. SGLT2 inhibitors for the prevention of kidney failure in patients with type 2 diabetes: a systematic review and meta-analysis. Lancet Diabetes Endocrinol 2019;7:845-854.
3. Marso SP, et al. Liraglutide and Cardiovascular Outcomes in Type 2 Diabetes. N Engl J Med 2016;375:311-322."""
}

# Generate Updated PDFs
create_comprehensive_pdf("diabetes-treatment-study.pdf", diabetes_title, diabetes_authors, diabetes_sections)
create_comprehensive_pdf("obesity-management-review.pdf", obesity_title, obesity_authors, obesity_sections)
create_comprehensive_pdf("cardiovascular-outcomes-trials.pdf", cardio_title, cardio_authors, cardio_sections)


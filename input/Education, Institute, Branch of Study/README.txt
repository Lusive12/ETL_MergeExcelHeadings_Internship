EDUCATION, INSTITUTE & BRANCH OF STUDY
=======================================
SOURCE FILES (place here before running):
  IKP_IT0022.xlsx   <- SAP IT0022 export (education / qualifications)
  [other source files as required]

OUTPUT (produced by the automation):
  IKP_IT0022_HighestOrder_IgnoreTraining_WithBranchText.xlsx
    -> Used by the Final Assembler:
       col AS = Education
       col X  = Institute
       col AW = Branch Study

RULE: Select highest-order qualification only. Ignore training records.
      Include branch/field of study text.
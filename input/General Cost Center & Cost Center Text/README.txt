GENERAL COST CENTER & COST CENTER TEXT
=======================================
SOURCE FILES (place here before running):
  IKP_IT0027.xlsx   <- SAP IT0027 export (contains Cost Center columns)
  IKP_CSKT.xlsx     <- Cost Center master lookup (Cost Center, Valid To, Description)

OUTPUT (produced by the automation — do not edit manually):
  IKP_IT0027_All_CostCenter_With_Description_v2.xlsx
    -> Used by the Final Assembler:
       col Z  = General Expense Cost Center
       col AA = General Expense Cost Center Desc

RULE: For each Cost Center column in IT0027, look up Description from CSKT
      using the row with the latest Valid To date.
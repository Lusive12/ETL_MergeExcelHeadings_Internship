CONTRACT TYPE & CONTRACT END DATE
==================================
SOURCE FILES (place here before running):
  IKP_PA0016.xlsx   <- SAP PA0016 export (contract information)
  [other source files as required]

OUTPUT (produced by the automation):
  IKP_PA0016_With_ContractType_Description.xlsx
    -> Used by the Final Assembler:
       col AT = Contract Type
       col AM = Contract End Date

Note: Primary key join is done via Personnel Number -> IKP_PQAH.xlsx.
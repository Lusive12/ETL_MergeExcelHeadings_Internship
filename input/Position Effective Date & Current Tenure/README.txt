POSITION EFFECTIVE DATE & CURRENT TENURE
=========================================
SOURCE FILES (place here before running):
  IKP_HRP1001.xlsx   <- SAP HRP1001 export (Object ID, ID of related object, Start date)

  NOTE: IKP_PQAH.xlsx is read from the INPUT root folder (shared).

OUTPUT (produced by the automation):
  IKP_PQAH_With_EarliestStartDate_CurrentTenure_Years.xlsx
    -> Used by the Final Assembler:
       col Y = Position Effective Date (Earliest Start Date)
       col Z = Current Tenure (Years)

RULE: Build composite key: Personnel No. + Position.
      Match to HRP1001 (strip leading zeros from ID of related object).
      Select MIN(Start date). Tenure = (today - Start date) / 365.25, rounded 2dp.
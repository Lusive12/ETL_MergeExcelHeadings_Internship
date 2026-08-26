JOIN DATE & YEAR OF SERVICE
=============================
SOURCE FILES (place here before running):
  IKP_PA0041.xlsx   <- SAP PA0041 export (Date type / Date for date type columns)

  NOTE: IKP_PQAH.xlsx is read from the INPUT root folder (shared).

OUTPUT (produced by the automation):
  IKP_PQAH_With_JoinDate_YearsOfService_Normalized.xlsx
    -> Used by the Final Assembler:
       col Y = Join Date    (format: DD-Mon-YYYY e.g. 27-Sep-2020)
       col Z = Year of Service

RULE: Filter Date type = '01'. Select the EARLIEST date per employee.
      Year of Service = (today - Join Date) / 365.25, rounded to 2dp.
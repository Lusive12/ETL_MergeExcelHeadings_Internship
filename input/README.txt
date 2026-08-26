INPUT FOLDER — HR Data Automation Suite
========================================
Place the following SHARED files directly in this folder:

  IKP_PQAH.xlsx          <- Main source file (Personnel No. = primary key for ALL modules)
  IKP_Headings.xlsx      <- Output column template (row 1 = column names in exact order)
  IKP_Direct Spv.xlsx    <- Superior NIK (col D) and Superior Name (col C) lookup
  IKP_PA0105.xlsx        <- Email address source (col Y)
  IKP_Job Layer.xlsx     <- Layer lookup (col B)

Each subfolder contains files for its specific automation module.
See the README inside each subfolder for details.

DO NOT rename these files. Names must match exactly.
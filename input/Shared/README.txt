SHARED FILES — Required by all modules and the Final Assembler
==============================================================
Place these files here before every run:

  IKP_PQAH.xlsx          <- Main employee source file (primary key: Personnel No.)
                            Contains: Lvl, CoCd, Company Name, ESgrp, Name of EE Subgroup,
                            PArea, Personnel Area Text, Subarea, P.Subarea Text,
                            Position, Position Name, Org. Unit, Name of Organizational Unit,
                            Job, Job Title, Gender, Birth Date, Age, Nationality,
                            Birthplace, Religion, Marital Status, and more.

  IKP_Headings.xlsx       <- Output column template.
                            Row 1 only — column names in the exact required order.
                            The Final Assembler uses this to build the output report.

  IKP_Direct Spv.xlsx     <- Supervisor lookup table.
                            col C = Superior Name
                            col D = Superior NIK
                            Join key: Personnel No. from PQAH col A.

  IKP_PA0105.xlsx         <- Email address source.
                            col Y = Email
                            Join key: Personnel No.

  IKP_Job Layer.xlsx      <- Layer lookup table.
                            col B = Layer text
                            Join key: PQAH col P (Position/Job).

DO NOT rename these files.
Steps to produce this directory:

1. form results are put in directory.
2. small edits to fix wrong entries.
3. run `../../tools/prep/extract_data_from_submission.py -d ../divisions.json 2022 "SMT-COMP 2022 System Registration.csv" solvers_divisions.csv`
4. fix problems, check availability of solvers, contact solver authors.
5. run `./make_starexec_solvers_xml.sh`
6. upload solvers.zip to starexec, check for problems.
7. checkout github pages to correct directory, create empty `_participants_2021`
8. run `./update_web_pages.sh`
9. check for problems.
10. publish.

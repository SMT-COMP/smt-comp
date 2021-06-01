Steps to produce this directory:

1. form results are put in directory.
2. run `../../tools/prep/extract_data_from_submission.py 2021 "SMT-COMP 2021 System Registration.csv" solvers_divisions_final.csv`
3. fix problems, check availability of solvers, contact solver authors.
4. run `./make_starexec_solvers_sml.sh`
5. upload solvers.zip to starexec, check for problems.
6. checkout github pages to correct directory, create empty `_participants_2021`
7. run `./update_web_pages.sh`
8. check for problems.
9. publish.

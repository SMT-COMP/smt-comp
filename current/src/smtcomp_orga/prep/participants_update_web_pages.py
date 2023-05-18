import os

from smtcomp_orga.prep import extract_data_from_solvers_divisions
from smtcomp_orga.prep import make_participants_md

YEAR = "2023"
NYSE_DATE = "2023-05-30"
NYSE_VALUE = ""  # NYSE opening value, e.g., 12345.6789
LOGICS = "data/divisions.json"
DIVISIONS = "data/new-divisions.json"
WEBSITE = "../../smt-comp.github.io/"
SOLVERS = "data/registration/solvers_divisions_all.csv"


def main():
    outdir_participants=os.path.join(WEBSITE,"_participants_" + YEAR)
    os.makedirs(outdir_participants, exist_ok=True)
    extract_data_from_solvers_divisions.run(
        divisions=LOGICS, solver_divisions=SOLVERS,
        md_path=outdir_participants, year=YEAR
    )
    make_participants_md.run(
        divisions=DIVISIONS,
        nyse_date=NYSE_DATE,
        nyse_value=NYSE_VALUE,
        md_path=os.path.join(WEBSITE,YEAR),
        year=YEAR
    )

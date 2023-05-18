# Track options
OPT_TRACK_SQ = "sq"
OPT_TRACK_INC = "inc"
OPT_TRACK_CHALL_SQ = "chall_sq"
OPT_TRACK_CHALL_INC = "chall_inc"
OPT_TRACK_UC = "uc"
OPT_TRACK_MV = "mv"
OPT_TRACK_PE = "pe"
OPT_TRACK_CLOUD = "ct"
OPT_TRACK_PARALLEL = "pt"

OPT_tracks = [OPT_TRACK_SQ, OPT_TRACK_INC, OPT_TRACK_UC, OPT_TRACK_MV, OPT_TRACK_PE]


# Columns of solvers csv
COL_SOLVER_ID_PRELIM = "Preliminary Solver ID"
COL_SOLVER_ID = "Solver ID"
COL_SOLVER_NAME = "Solver Name"
COL_VARIANT_OF_ID = "Variant Of"
COL_COMPETING = "Competing"
COL_SOLVER_ID_SQ_2019 = "Wrapped Solver ID Single Query"
COL_SOLVER_ID_INC_2019 = "Wrapped Solver ID Incremental"
COL_SOLVER_ID_UC_2019 = "Wrapped Solver ID Unsat Core"
COL_SOLVER_ID_MV_2019 = "Wrapped Solver ID Model Validation"

COL_CONFIG_ID_SQ = "Config ID Single Query"
COL_CONFIG_ID_MV = "Config ID Model Validation"
COL_CONFIG_ID_UC = "Config ID Unsat Core"
COL_CONFIG_ID_INC = "Config ID Incremental"
COL_CONFIG_ID_PE = "Config ID Proof Exhibition"

# Track Columns
COL_SINGLE_QUERY_TRACK = 'Single Query Track'
COL_INCREMENTAL_TRACK = 'Incremental Track'
COL_CHALLENGE_TRACK_SINGLE_QUERY = 'Challenge Track (single query)'
COL_CHALLENGE_TRACK_INCREMENTAL = 'Challenge Track (incremental)'
COL_MODEL_VALIDATION_TRACK = 'Model Validation Track'
COL_UNSAT_CORE_TRACK = 'Unsat Core Track'
COL_PROOF_EXHIBITION_TRACK = 'Proof Exhibition Track'
# Other Columns
COL_IS_COMPETING = 'Competing'


COL_config_of_track = {
    OPT_TRACK_SQ: COL_CONFIG_ID_SQ,
    OPT_TRACK_INC: COL_CONFIG_ID_INC,
    OPT_TRACK_UC: COL_CONFIG_ID_UC,
    OPT_TRACK_MV: COL_CONFIG_ID_MV,
    OPT_TRACK_PE: COL_CONFIG_ID_PE,
}

COL_logic_of_track = {
    OPT_TRACK_SQ: COL_SINGLE_QUERY_TRACK,
    OPT_TRACK_INC: COL_INCREMENTAL_TRACK,
    OPT_TRACK_UC: COL_UNSAT_CORE_TRACK,
    OPT_TRACK_MV: COL_MODEL_VALIDATION_TRACK,
    OPT_TRACK_PE: COL_PROOF_EXHIBITION_TRACK,
}

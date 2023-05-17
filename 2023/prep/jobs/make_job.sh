#!/bin/bash

YEAR=2022
SCRIPTDIR=`dirname $(readlink -f "$0")`

PREPARE="$SCRIPTDIR/../../../tools/prep/prepare_space_xml.py"
SOLVERS_CSV="$SCRIPTDIR/../../registration/solvers_divisions_final.csv"

INCLUDE_NONCOMPETITIVE=""
PREPARE_JOB_ARGS=${PREPARE_JOB_ARGS:-}

### Input space xml files
IN_SPACE_NON_INC="../non-incremental.xml"
IN_SPACE_INC="../incremental.xml"

SQ="single_query"
UC="unsat_core"
MV="model_validation"
INC="incremental"
PE="proof_exhibition"

# output usage if called without parameters
if [ $# -eq 0 ]; then
    set -- -h
fi

TESTING=0
EXTRA=""
while [ $# -gt 0 ]
do
    case $1 in
  -h|--help)
      echo -n "usage: $(basename $0) [<option>]"
      echo
      echo "Generate a StarExec Competition Job."
      echo
      echo "  options:"
      echo "    -h, --help    Print this message and exit"
      echo "    --include-nc  Run also non-competitive divisions"
      echo "    --test-run    Create a Job for the test run"
      echo "    --sq          Single Query track"
      echo "    --inc         Incremental track"
      echo "    --uc          Unsat Core track"
      echo "    --mv          Model Validation track"
      echo "    --pe          Proof Exhibition track"
      echo "    --solvers <file> An optional alternative solvers csv file"
      echo "    --extra <id>  Some id to distinguish job"
      echo
      exit
      ;;
  --test-run)
      TESTING=1
      ;;
  --sq)
      TRACK=SQ
      ;;
  --inc)
      TRACK=INC
      ;;
  --uc)
      TRACK=UC
      ;;
  --mv)
      TRACK=MV
      ;;
  --pe)
      TRACK=PE
      ;;
  --solvers)
      shift
      SOLVERS_CSV=$1
      ;;
  --include-nc)
      INCLUDE_NONCOMPETITIVE="--include-non-competitive"
      ;;
  --extra)
      shift
      EXTRA=$1
      ;;
  *)
            echo "ERROR: invalid option '$1'"
            exit 1
      ;;
    esac
    shift
done


if [ "$TESTING" = "1" ]; then
    SEED=`cat $SCRIPTDIR/../../../$(expr $YEAR - 1)/COMPETITION_SEED`
    TIMEOUT="120"    # 2 minutes for testing
    KIND=testing
    PRE_SQ=763
    PRE_INC=760
    PRE_UC=764
    PRE_MV=761
    PRE_PE=762
    POST_SQ=768
    POST_INC=765
    POST_UC=769
    POST_MV=766
    POST_PE=767
    QUEUE=1   # smtcomp.q
else
    SEED=`cat $SCRIPTDIR/../../COMPETITION_SEED`
    TIMEOUT="1200"    # 20 minutes
    KIND=final
    PRE_SQ=763
    PRE_INC=760
    PRE_UC=764
    PRE_MV=761
    PRE_PE=762
    POST_SQ=768
    POST_INC=765
    POST_UC=769
    POST_MV=766
    POST_PE=767
    QUEUE=1 # smtcomp.q
    # QUEUE=181493 # new.q
fi

mkdir -p $KIND

PRETR=PRE_${TRACK}
POSTTR=POST_${TRACK}

MEMLIMIT="60.0"

SELECTION="$SCRIPTDIR/../selection/$KIND/benchmark_selection_${!TRACK}"
PRE=${!PRETR}
POST=${!POSTTR}
OUTFILE=${!TRACK}
JOBNAME="SMT-COMP $YEAR $(echo ${!TRACK} | tr '_' ' ') $KIND"
if [ -n "$EXTRA" ]; then
    JOBNAME="$JOBNAME $EXTRA"
    OUTFILE=${!TRACK}_${EXTRA}
fi
if [ "$TRACK" = "INC" ]; then
    IN_SPACE=$IN_SPACE_INC
else
    IN_SPACE=$IN_SPACE_NON_INC
fi

python3 $SCRIPTDIR/../../../tools/prep/prepare_job_xml.py \
  -t ${!TRACK} --name "$JOBNAME" --queue $QUEUE --pre $PRE --post $POST \
  --wall $TIMEOUT --seed $SEED --memlimit $MEMLIMIT \
  -s $SELECTION $IN_SPACE $SOLVERS_CSV $KIND/$OUTFILE.xml \
  $PREPARE_JOB_ARGS $INCLUDE_NONCOMPETITIVE

(cd $KIND; zip $OUTFILE.zip $OUTFILE.xml)

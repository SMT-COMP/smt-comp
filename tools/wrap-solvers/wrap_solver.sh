#!/bin/bash

# ./wrap_solver.sh <wrapped name> <wrapper directory> <solver id> <space id>


SCRIPTDIR=`dirname $(readlink -f "$0")`
source "$SCRIPTDIR/login.sh"

WRAP=yes
DOWNLOAD=yes
UPLOAD=yes
FORCE_WRAP=no
ZIP_ONLY=no

while [ $# -gt 0 ]
do
  case $1 in
    -h|--help)
      echo -n "usage: $(basename $0) [<option>] <wrapped name> <wrapper directory> <solver id> <space id> <solver-dir>"
      echo
      echo "  options:"
      echo "    -h, --help    print this message and exit"
      echo "    -W            wrap solver"
      echo "    -d            download solver only"
      echo "    -w            wrap solver only"
      echo "    -u            upload solver only"
      echo "    -z            only zip solver from existing wrapped dir when wrapping"
      echo
      exit
      ;;
    -W)
      FORCE_WRAP=yes
      ;;
    -d)
      UPLOAD=no
      WRAP=no
      ;;
    -w)
      DOWNLOAD=no
      UPLOAD=no
      ;;
    -u)
      DOWNLOAD=no
      WRAP=no
      ;;
    -z)
      ZIP_ONLY=yes
      ;;
    -*)
        echo "ERROR: invalid option '$1'"
        exit 1
      ;;
    *)
      break
  esac
  shift
done

WRAPPED_NAME=$1
WRAPPER_DIR=$2
SOLVER_ID=$3
SPACE_ID=$4
SOLVER_DIR=$5
WRAPPED_SOLVER_DIR=$5-wrapped

[ $FORCE_WRAP == "yes" ] && WRAP=yes
uploadSolver()
{
  SOLVER=$1
  SOLVER_NAME=$2

  COMMAND="pushsolver f=${SOLVER} n=${SOLVER_NAME} id=${SPACE_ID} downloadable="
  java -jar ${SCRIPTDIR}/StarexecCommand.jar <<EOF
login u=${USERNAME} p=${PASSWORD}
${COMMAND}
EOF
}

getSolverInfo()
{
  ID=$1

  COMMAND="viewsolver id=${ID}"
  java -jar StarexecCommand.jar <<EOF
login u=${USERNAME} p=${PASSWORD}
${COMMAND}
EOF
}

downloadSolver()
{
  ID=$1
  OUT=$2

  COMMAND="getsolver id=${ID} out=${OUT}"
  java -jar StarexecCommand.jar <<EOF
login u=${USERNAME} p=${PASSWORD}
${COMMAND}
EOF
}

# Create directories
mkdir -p "${SOLVER_DIR}"
mkdir -p "${WRAPPED_SOLVER_DIR}"

# Download info
INFO=$(getSolverInfo "${SOLVER_ID}")
NAME=$(echo "$INFO" | sed -n -e 's/.*name= \"\([^\"]*\).*/\1/p')
echo $INFO

# Download solver
SOLVER="${SOLVER_DIR}/${NAME}.zip"
if [ $DOWNLOAD == "yes" ]
then
  echo ">> download solver"
  downloadSolver "${SOLVER_ID}" "${SOLVER}"
  if [ ! -f "${SOLVER}" ]; then
    exit 1
  fi
fi

[ $WRAP == "no" ] && [ $UPLOAD == "no" ] && exit

# Wrap solver
if [ $WRAP == "yes" ]
then
  echo ">> wrap solver"

  if [ $ZIP_ONLY == "no" ]
  then
    pushd "${SOLVER_DIR}"
    unzip -o "${NAME}.zip"
    popd
  fi

  NEW_SOLVER_DIR="${WRAPPED_SOLVER_DIR}/${NAME}-${WRAPPED_NAME}"

  if [ $ZIP_ONLY == "no" ]
  then
    cp -r "${SOLVER_DIR}/${NAME}" "${NEW_SOLVER_DIR}"
    mv "${NEW_SOLVER_DIR}/bin/starexec_run_default" "${NEW_SOLVER_DIR}/bin/original_starexec_run_default"
    if [ $? -ne 0 ]
    then
        echo "ERROR: not default config"
        exit 1
    fi
    cp -r ${WRAPPER_DIR}/* "${NEW_SOLVER_DIR}/bin"
  fi

  pushd "${NEW_SOLVER_DIR}"
  zip -r "../${NAME}-${WRAPPED_NAME}.zip" *
  popd
fi

[ $UPLOAD == "no" ] && exit

# Upload solver
echo ">> upload solver"
uploadSolver "${WRAPPED_SOLVER_DIR}/${NAME}-${WRAPPED_NAME}.zip" "${NAME}-${WRAPPED_NAME}"

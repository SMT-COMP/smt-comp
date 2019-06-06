#!/bin/bash

# ./wrap_solver.sh <wrapped name> <wrapper directory> <solver id> <space id>

source login.sh

WRAPPED_NAME=$1
WRAPPER_DIR=$2
SOLVER_ID=$3
SPACE_ID=$4
SOLVER_DIR=$5
WRAPPED_SOLVER_DIR=$5-wrapped

uploadSolver()
{
  SOLVER=$1
  SOLVER_NAME=$2

  COMMAND="pushsolver f=${SOLVER} n=${SOLVER_NAME} id=${SPACE_ID} downloadable="
  java -jar StarexecCommand.jar <<EOF
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

INFO=$(getSolverInfo "${SOLVER_ID}")
NAME=$(echo "$INFO" | sed -n -e 's/.*name= \"\([^\"]*\).*/\1/p')

SOLVER="${SOLVER_DIR}/${NAME}.zip"
downloadSolver "${SOLVER_ID}" "${SOLVER}"

if [ ! -f "${SOLVER}" ]; then
  exit 1
fi

pushd "${SOLVER_DIR}"
unzip -o "${NAME}.zip"
popd

NEW_SOLVER_DIR="${WRAPPED_SOLVER_DIR}/${NAME}-${WRAPPED_NAME}"
cp -r "${SOLVER_DIR}/${NAME}" "${NEW_SOLVER_DIR}"
mv "${NEW_SOLVER_DIR}/bin/starexec_run_default" "${NEW_SOLVER_DIR}/bin/original_starexec_run_default"
cp -r ${WRAPPER_DIR}/* "${NEW_SOLVER_DIR}/bin"

pushd "${NEW_SOLVER_DIR}"
zip -r "../${NAME}-${WRAPPED_NAME}.zip" *
popd

uploadSolver "${WRAPPED_SOLVER_DIR}/${NAME}-${WRAPPED_NAME}.zip" "${NAME}-${WRAPPED_NAME}"


#!/bin/bash

# ./wrap_solver.sh <wrapped name> <wrapper directory> <solver id> <space id>


SCRIPTDIR=`dirname $(readlink -f "$0")`
source "$SCRIPTDIR/login.sh"

if [ $# -eq 5 ]
then
  WRAP=yes
  DOWNLOAD=yes
  UNZIP=yes
  UPLOAD=yes
  ZIP=yes
else
  WRAP=no
  DOWNLOAD=no
  UNZIP=no
  UPLOAD=no
  ZIP=no
fi

while [ $# -gt 0 ]
do
  case $1 in
    -h|--help)
      echo -n "usage: $(basename $0) [<option>] <wrapped name> <wrapper directory> <solver id> <space id> <solver-dir>"
      echo ""
      echo "Download, wrap and upload solver from and to StarExec."
      echo "If no options are given, all actions are performed."
      echo
      echo "  options:"
      echo "    -h, --help    print this message and exit"
      echo "    -d            download only"
      echo "    -x            unzip only"
      echo "    -w            wrap solver only"
      echo "    -u            upload solver only"
      echo "    -z            only zip solver from existing wrapped dir when wrapping"
      echo
      exit
      ;;
    -d)
      DOWNLOAD=yes
      ;;
    -x)
      UNZIP=yes
      ;;
    -w)
      WRAP=yes
      ;;
    -u)
      UPLOAD=yes
      ;;
    -z)
      ZIP=yes
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

[ $WRAP == "yes" ] && ZIP=yes

WRAPPED_NAME=$1
WRAPPER_DIR=$2
SOLVER_ID=$3
SPACE_ID=$4
SOLVER_DIR=$5
WRAPPED_SOLVER_DIR=$5-wrapped

upload_solver()
{
  echo ">> upload solver"

  SOLVER=$1
  SOLVER_NAME=$2
#  COMMAND="pushsolver f=${SOLVER} n=${SOLVER_NAME} id=${SPACE_ID} downloadable="
#  java -jar ${SCRIPTDIR}/StarexecCommand.jar <<EOF
#login u=${USERNAME} p=${PASSWORD}
#${COMMAND}
#EOF
  mkdir -p upload
  cp "${SOLVER}" upload
}

get_solver_info()
{
  echo ">> get solver info"

  ID=$1
#  COMMAND="viewsolver id=${ID}"
#  java -jar ${SCRIPTDIR}/StarexecCommand.jar <<EOF
#login u=${USERNAME} p=${PASSWORD}
#${COMMAND}
#EOF
  curl -s 'https://www.starexec.org/starexec/secure/details/solver.jsp?id='${ID} | \
	perl -ne '/<td>name<\/td>/ and do {$name=1; next }; 
                  $name && /<td>(.*)<\/td>/ and do { print "name= \"$1\"\n"; exit }'
}

download_solver()
{
  echo ">> download solver"

  ID=$1
  OUT=$2
#  COMMAND="getsolver id=${ID} out=${OUT}"
#  java -jar ${SCRIPTDIR}/StarexecCommand.jar <<EOF
#login u=${USERNAME} p=${PASSWORD}
#${COMMAND}
#EOF
  cp download/${ID}.zip "${OUT}"
}

unzip_solver()
{
  echo ">> unzip solver"
  SOLVER_DIR=$1
  pushd "${SOLVER_DIR}"
  unzip -o "${NAME}.zip"
  popd
}

wrap_solver()
{
  echo ">> wrap solver"
  SOLVER_DIR=$1
  NEW_SOLVER_DIR=$2
  cp -r "${SOLVER_DIR}/${NAME}" "${NEW_SOLVER_DIR}"
  echo "${NEW_SOLVER_DIR}/bin/starexec_run_default"
  mv "${NEW_SOLVER_DIR}/bin/starexec_run_default" "${NEW_SOLVER_DIR}/bin/original_starexec_run_default"
  res=$?
  cp -r ${WRAPPER_DIR}/* "${NEW_SOLVER_DIR}/bin"
  if [ $res -ne 0 ]
  then
      echo "ERROR: no default config"
      exit 1
  fi
}

zip_solver()
{
  echo ">> zip solver"
  NEW_SOLVER_DIR=$1
  pushd "${NEW_SOLVER_DIR}"
  zip -r "../${NAME}-${WRAPPED_NAME}.zip" *
  popd
}

# Create directories
mkdir -p "${SOLVER_DIR}"
mkdir -p "${WRAPPED_SOLVER_DIR}"

# Download info
INFO=$(get_solver_info "${SOLVER_ID}")
NAME=$(echo "$INFO" | sed -n -e 's/.*name= \"\([^\"]*\).*/\1/p')
echo $INFO

# Download solver
if [ $DOWNLOAD == "yes" ]
then
  SOLVER="${SOLVER_DIR}/${NAME}.zip"
  download_solver "${SOLVER_ID}" "${SOLVER}"
  if [ ! -f "${SOLVER}" ]; then
    exit 1
  fi
fi

[ $UNZIP == "yes" ] && \
  unzip_solver "${SOLVER_DIR}"

NEW_SOLVER_DIR="${WRAPPED_SOLVER_DIR}/${NAME}-${WRAPPED_NAME}"

[ $WRAP == "yes" ] && \
  wrap_solver "${SOLVER_DIR}" "${NEW_SOLVER_DIR}"

[ $ZIP == "yes" ] && \
  zip_solver "${NEW_SOLVER_DIR}"

[ $UPLOAD == "yes" ] && \
  upload_solver "${WRAPPED_SOLVER_DIR}/${NAME}-${WRAPPED_NAME}.zip" "${NAME}-${WRAPPED_NAME}"

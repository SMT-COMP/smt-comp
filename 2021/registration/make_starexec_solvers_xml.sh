#!/bin/sh

# Create solvers.zip file to link solvers into a fresh space.
#
# Create a new space in starexec, move to that space, open Sub spaces,
# choose "Upload Sub Spaces" and upload the solvers.zip file.

if true; then  # set to false for final
    SOLVER_ID="Preliminary Solver ID"
    SPACE_NAME="Preliminary Solvers - Linked"
else
    SOLVER_ID="Solver ID"
    SPACE_NAME="Final Solvers - Linked"
fi

(
    cat <<EOF
<ns0:Spaces xmlns:ns0="https://www.starexec.org/starexec/public/batchSpaceSchema.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="https://www.starexec.org/starexec/public/batchSpaceSchema.xsd batchSpaceSchema.xsd">
<Space id="123456" name="$SPACE_NAME">
<SpaceAttributes>
<description value="no description" />
<sticky-leaders value="true" />
<inherit-users value="true" />
<locked value="false" />
<add-benchmark-perm value="false" />
<add-job-perm value="false" />
<add-solver-perm value="false" />
<add-space-perm value="false" />
<add-user-perm value="false" />
<rem-benchmark-perm value="false" />
<rem-job-perm value="false" />
<rem-solver-perm value="false" />
<rem-space-perm value="false" />
<rem-user-perm value="false" />
</SpaceAttributes>
EOF

csvcut -c "$SOLVER_ID","Solver Name" solvers_divisions_final.csv | tail -n +2 | grep -v ^-1 | sed -E 's/(.*),(.*)/<Solver id="\1" name="\2"\/>/'

cat <<EOF
</Space>
</ns0:Spaces>
EOF
) > solvers.xml
zip solvers.zip solvers.xml

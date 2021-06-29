SOLVERS_CSV="../../registration/solvers_divisions_noncompeting.csv"
SELECTION=final
export SOLVERS_CSV SELECTION
DIR=noncompeting

mkdir -p $DIR

./make_spaces.sh --include-nc --mv $DIR/mv.xml --uc $DIR/uc.xml --inc $DIR/inc.xml --sq $DIR/sq.xml

cd $DIR
for i in sq inc mv uc; do
   tar czf $i.tar.gz $i.xml
done

SOLVERS_DIVISIONS="../../registration/solvers_divisions_latefix.csv"
SELECTION=final
DIR=latefix
export SELECTION

mkdir -p $DIR

./make_spaces.sh --solvdiv $SOLVERS_DIVISIONS --include-nc --mv $DIR/mv.xml --uc $DIR/uc.xml --inc $DIR/inc.xml --sq $DIR/sq.xml

cd $DIR
for i in sq inc mv uc; do
   tar czf $i.tar.gz $i.xml
done

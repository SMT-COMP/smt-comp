SELECTION=final
BESTOF_OUT=bestof-2020

export SELECTION
SOLVERS_DIVISIONS_BESTOF="../../previous-best/solvers_divisions_bestof_2020.csv"

mkdir -p $BESTOF_OUT

./make_spaces.sh --solvdiv $SOLVERS_DIVISIONS_BESTOF --include-nc --mv $BESTOF_OUT/mv.xml --uc $BESTOF_OUT/uc.xml --inc $BESTOF_OUT/inc.xml --sq $BESTOF_OUT/sq.xml

cd $BESTOF_OUT
for i in sq inc mv uc; do
   tar czf $i.tar.gz $i.xml
done

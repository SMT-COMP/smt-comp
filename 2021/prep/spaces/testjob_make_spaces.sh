mkdir -p testing

./make_spaces.sh --mv testing/mv.xml --uc testing/uc.xml --inc testing/inc.xml --sq testing/sq.xml

cd testing
for i in sq inc mv uc; do
   tar czf $i.tar.gz $i.xml
done

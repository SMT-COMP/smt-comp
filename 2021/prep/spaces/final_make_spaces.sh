mkdir -p final

./make_spaces.sh --include-nc --mv final/mv.xml --uc final/uc.xml --inc final/inc.xml --sq final/sq.xml

cd final
for i in sq inc mv uc; do
   tar czf $i.tar.gz $i.xml
done

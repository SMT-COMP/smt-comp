ID=53368

cat raw-results-sq.csv |cut -d, -f 3,12 | grep -v -e starexec-unknown -e '--' | sort |uniq | cut -d, -f1 |uniq -c |grep -v ' 1 '  | cut -c 9- > disagreeing-${ID}.txt

COMMA=""
while read bench; do
    PATTERN="$PATTERN$COMMA$bench"
    COMMA="|"
done < disagreeing-${ID}.txt
cat raw-results-sq.csv | grep -E ",($PATTERN)," | LANG=C sort -t, -k 2

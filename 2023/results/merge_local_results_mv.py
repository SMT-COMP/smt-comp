#!/usr/bin/python3

## Merge local result with fixed dolmen

import csv
import sys
import gzip

def main():
    local_result = sys.argv[1] #gzipped file
    raw_result = sys.argv[2]
    new_result = sys.argv[3]
    
    not_proved_locally={}
    
    with gzip.open(local_result, newline='',mode='rt') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            not_proved_locally[(row[0],row[1],row[2])]=True

    with open(raw_result, newline='') as inputcsvfile:
        reader = csv.DictReader(inputcsvfile)

        with open(new_result, 'w', newline='') as outputcsvfile:
            writer = csv.DictWriter(outputcsvfile, fieldnames=reader.fieldnames)

            writer.writeheader()

            for row in reader:
                key=(row["benchmark"],row["solver"],row["configuration"])
                if not key in not_proved_locally:
                    row["result"]="sat"
                    row["dolmenexit"]="0"
                    row["model_validator_error"]="-"
                    row["model_validator_status"]="VALID"
                
                writer.writerow(row)
    
    
main()


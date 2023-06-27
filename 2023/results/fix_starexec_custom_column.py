#!/usr/bin/env python3

## Some cell are in column with header "foo=bar" and value "baz" which should
## be in column "foo" with value "barbaz"
## starexec cut the last = instead of the first

import csv
import sys

csv.field_size_limit(sys.maxsize)

def main():
    with open(sys.argv[1], newline='') as csvin:
        csvin = csv.reader(csvin)
        header=next(csvin)
        clean_header=[]
        conv=[]
        for head in header:
            split=head.split(sep="=",maxsplit=1)
            if split[0] not in clean_header:
                clean_header.append(split[0])
            conv.append(split[0])
            # print(head)
            # print(split[0])
            # print(spurious)

        with open(sys.argv[2], 'w', newline='') as csvout:
            csvout = csv.DictWriter(csvout,quoting=csv.QUOTE_MINIMAL,fieldnames=clean_header)
            csvout.writeheader()
            for row in csvin:
                new_row={}
                for col,head in zip(row,conv):
                    new_row[head]=col
                csvout.writerow(new_row)
                
main()
        

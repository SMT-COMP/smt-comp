#!/usr/bin/env python3

import json
import sys
import random

if __name__ == '__main__':
    if len(sys.argv) != 5:
        print("Usage: %s <selection-numbers> "\
                "<hard-instance-list> "\
                "<unsolved-instance-list> <seed>" %\
                sys.argv[0])
        sys.exit(1)

    seed = int(sys.argv[4])
    selectionNumbers = json.loads(open(sys.argv[1]).read())

    instFiles = {'hard': sys.argv[2], 'unsolved': sys.argv[3]}

    for t in ('hard', 'unsolved'):

        instanceList = map(lambda x: [x.split("/")[2], x.strip()],\
            open(instFiles[t]).readlines())
        instances = dict()

        for (logic, name) in instanceList:
            if logic not in instances:
                instances[logic] = []
            instances[logic].append(name)

        for logic in selectionNumbers:
            if logic in instances:
                shuffledInstances = sorted(instances[logic])
                random.seed(seed)
                random.shuffle(shuffledInstances)
                numToPick = int(selectionNumbers[logic]['picked_%s' % t])
                selectedInstances = shuffledInstances[:numToPick]
                selectedInstances.sort()
                print("\n".join(selectedInstances))


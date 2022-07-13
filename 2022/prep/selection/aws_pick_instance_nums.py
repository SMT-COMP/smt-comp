#!/usr/bin/env python3
import sys
import json

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: %s <hard> <unsolved> <min-benchmarks>" % sys.argv[0])
        sys.exit(1)

    hard = dict(map(lambda x: [x[0], int(x[1])], \
            map(lambda x: list(reversed(x.split(" "))), \
            map(lambda x: x.strip(), \
            open(sys.argv[1]).readlines()))))
    unsolved = dict(map(lambda x: [x[0], int(x[1])], \
            map(lambda x: list(reversed(x.split(" "))), \
            map(lambda x: x.strip(), \
            open(sys.argv[2]).readlines()))))

    minBenchmarks = int(sys.argv[3])

    allBenchmarks = sum(map(lambda x: hard[x], hard.keys())) + \
        sum(map(lambda x: unsolved[x], unsolved.keys()))

    if (minBenchmarks > allBenchmarks):
        print("Insufficient total benchmarks: %d < %d" % \
                (allBenchmarks, minBenchmarks))
        sys.exit(1)

    # All interested logics
    logics = set(hard.keys())
    logics.update(unsolved.keys())

    if (allBenchmarks <= minBenchmarks + len(logics)-1):
        print("There might not be enough benchmarks for a" \
              "non-discriminating assignment")


    class Partition:
        available = 0
        picked = 0
        picked_hard = 0
        picked_unsolved = 0

    partitions = dict()

    for logic in logics:
        if logic not in hard:
            hard[logic] = 0
        if logic not in unsolved:
            unsolved[logic] = 0
        p = Partition()
        partitions[logic] = p
        hard_available = hard[logic]
        unsolved_available = unsolved[logic]
        p.available = hard_available + unsolved_available
        p.picked = 0

    quota = minBenchmarks

    while quota > 0:
        # Compute the number of instances to assign on this round
        minAvailability = min(map(lambda x: partitions[x].available, \
                              logics))
        quotaPerLogic = int(float(quota)/len(logics)+1)
        quotaPerRound = min(minAvailability, quotaPerLogic)

        exhaustedLogics = []
        for logic in logics:
            p = partitions[logic]
            p.picked += quotaPerRound
            p.available -= quotaPerRound
            assert p.picked + p.available == hard[logic] + unsolved[logic]
            if p.available == 0:
                exhaustedLogics.append(logic)
        quota -= len(logics) * quotaPerRound

        for l in exhaustedLogics:
            logics.remove(l)

    for logic in partitions.keys():
        p = partitions[logic]
        assert p.picked <= hard[logic] + unsolved[logic]
        minTypeNum = hard[logic] if hard[logic] <= unsolved[logic] else unsolved[logic]

        if minTypeNum < p.picked/2:
            if hard[logic] == minTypeNum:
                p.picked_hard = minTypeNum
                p.picked_unsolved = p.picked - p.picked_hard
            else:
                assert unsolved[logic] == minTypeNum
                p.picked_unsolved = minTypeNum
                p.picked_hard = p.picked - p.picked_unsolved
        else:
            p.picked_unsolved = int(partitions[logic].picked/2)
            p.picked_hard = p.picked - p.picked_unsolved

    print(json.dumps(dict([[x, partitions[x].__dict__] for x in partitions]), \
                sort_keys=True, indent=4))

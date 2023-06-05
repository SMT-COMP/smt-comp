#!/usr/bin/env python3

from argparse import ArgumentParser
from collections import Counter
import sys,random,json

def sample(l,n):
    return random.sample(l,min(len(l),n))

if __name__ == '__main__':
    parser = ArgumentParser(
            description = "Compute the number of benchmark for aws for each logic")
    parser.add_argument ("hard",
            help="the number of hard benchmark by logic")
    parser.add_argument ("unsolved",
            help="the number of unsolved benchmark by logic")
    parser.add_argument ("-d", "--divisions", required=True,
            help="a json file with the tracks and divisions (required)")
    parser.add_argument ("minbenchmarks",
            help="the number of benchmarks (maximum)")
    parser.add_argument('--oldway', action='store_true',
            help="use 2021 way of counting")
    parser.add_argument("-t", "--track", required=True,
            help="solver track, either `cloud' or `parallel'")
    parser.add_argument("--seed", required=True,
            help="seed used for randomness")


    args = parser.parse_args()

    hard = dict(map(lambda x: [x[0], int(x[1])], \
            map(lambda x: list(reversed(x.split(" "))), \
            map(lambda x: x.strip(), \
            open(args.hard).readlines()))))
    unsolved = dict(map(lambda x: [x[0], int(x[1])], \
            map(lambda x: list(reversed(x.split(" "))), \
            map(lambda x: x.strip(), \
            open(args.unsolved).readlines()))))

    tracks=json.load(open(args.divisions))

    minBenchmarks = int(args.minbenchmarks)

    random.seed(a=args.seed)

    allBenchmarks = sum(map(lambda x: hard[x], hard.keys())) + \
        sum(map(lambda x: unsolved[x], unsolved.keys()))

    tracknames = {'cloud': "track_cloud",\
            'parallel': "track_parallel"}
    track = tracknames[args.track]

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

    if args.oldway:
        sys.stderr.write("Old way pre-2021 of picking instances\n")
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
    else:
        sys.stderr.write("New way post 2022 of picking instances\n")
        pickable_all=[]
        for division in tracks[track]:
            pickable=[]
            for logic in tracks[track][division]:
                if logic in partitions:
                    pickable+=[logic]*min(minBenchmarks,partitions[logic].available)
            pickable_all+=sample(pickable,minBenchmarks)
        pickable_all=sample(pickable_all,minBenchmarks)
        pickable_all=Counter(pickable_all)
        for logic in pickable_all:
            partitions[logic].picked+=pickable_all[logic]
            partitions[logic].available-=pickable_all[logic]

    for logic in partitions:
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

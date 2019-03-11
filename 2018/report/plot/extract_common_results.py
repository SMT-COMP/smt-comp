#! /usr/bin/env python3

import os
import sys
from argparse import ArgumentParser

winners_2018_main  = {
        "ABVFP" : "master-2018-06-10-b19c840-competition-default",
        "ALIA" : "master-2018-06-10-b19c840-competition-default",
        "AUFBVDTLIA" : "master-2018-06-10-b19c840-competition-default",
        "AUFDTLIA" : "master-2018-06-10-b19c840-competition-default",
        "AUFLIA" : "master-2018-06-10-b19c840-competition-default",
        "AUFLIRA" : "master-2018-06-10-b19c840-competition-default",
        "AUFNIRA" : "master-2018-06-10-b19c840-competition-default",
        "BV" : "master-2018-06-10-b19c840-competition-default",
        "BVFP" : "master-2018-06-10-b19c840-competition-default",
        "FP" : "master-2018-06-10-b19c840-competition-default",
        "LIA" : "master-2018-06-10-b19c840-competition-default",
        "LRA" : "master-2018-06-10-b19c840-competition-default",
        "NIA" : "master-2018-06-10-b19c840-competition-default",
        "NRA" : "vampire-4.3-smt",
        "QF_ABV" : "Boolector",
        "QF_ABVFP" : "master-2018-06-10-b19c840-competition-default",
        "QF_ALIA" : "Yices 2.6.0",
        "QF_ANIA" : "master-2018-06-10-b19c840-competition-default",
        "QF_AUFBV" : "master-2018-06-10-b19c840-competition-default",
        "QF_AUFLIA" : "Yices 2.6.0",
        "QF_AUFNIA" : "master-2018-06-10-b19c840-competition-default",
        "QF_AX" : "Yices 2.6.0",
        "QF_BV" : "Boolector",
        "QF_BVFP" : "master-2018-06-10-b19c840-competition-default",
        "QF_DT" : "master-2018-06-10-b19c840-competition-default",
        "QF_FP" : "COLIBRI 10_06_18 v2038",
        "QF_IDL" : "Yices 2.6.0",
        "QF_LIA" : "SPASS-SATT",
        "QF_LIRA" : "Yices 2.6.0",
        "QF_LRA" : "master-2018-06-10-b19c840-competition-default",
        "QF_NIA" : "master-2018-06-10-b19c840-competition-default",
        "QF_NIRA" : "SMTRAT-Rat-final",
        "QF_NRA" : "Yices 2.6.0",
        "QF_RDL" : "Yices 2.6.0",
        "QF_SLIA" : "master-2018-06-10-b19c840-competition-default",
        "QF_UF" : "Yices 2.6.0",
        "QF_UFBV" : "Boolector",
        "QF_UFIDL" : "Yices 2.6.0",
        "QF_UFLIA" : "Yices 2.6.0",
        "QF_UFLRA" : "Yices 2.6.0",
        "QF_UFNIA" : "Yices 2.6.0",
        "QF_UFNRA" : "Yices 2.6.0",
        "UF" : "master-2018-06-10-b19c840-competition-default",
        "UFBV" : "master-2018-06-10-b19c840-competition-default",
        "UFDT" : "master-2018-06-10-b19c840-competition-default",
        "UFDTLIA" : "master-2018-06-10-b19c840-competition-default",
        "UFIDL" : "master-2018-06-10-b19c840-competition-default",
        "UFLIA" : "master-2018-06-10-b19c840-competition-default",
        "UFLRA" : "master-2018-06-10-b19c840-competition-default",
        "UFNIA" : "vampire-4.3-smt",
}

winners_2017_main = {
        "ALIA" : "CVC4-smtcomp2017-main",
        "AUFBVDTLIA" : "CVC4-smtcomp2017-main",
        "AUFDTLIA" : "CVC4-smtcomp2017-main",
        "AUFLIA" : "CVC4-smtcomp2017-main",
        "AUFLIRA" : "vampire4.2-smt",
        "AUFNIRA" : "vampire4.2-smt",
        "BV" : "Q3B",
        "LIA" : "CVC4-smtcomp2017-main",
        "LRA" : "CVC4-smtcomp2017-main",
        "NIA" : "CVC4-smtcomp2017-main",
        "NRA" : "Redlog",
        "QF_ABV" : "Boolector SMT17 final",
        "QF_ALIA" : "Yices2-Main",
        "QF_ANIA" : "CVC4-smtcomp2017-main",
        "QF_AUFBV" : "Yices2-Main",
        "QF_AUFLIA" : "SMTInterpol",
        "QF_AUFNIA" : "CVC4-smtcomp2017-main",
        "QF_AX" : "Yices2-Main",
        "QF_BV" : "Boolector+CaDiCaL SMT17 final",
        "QF_BVFP" : "COLIBRI 18_06_2017 105a81",
        "QF_DT" : "CVC4-smtcomp2017-main",
        "QF_FP" : "COLIBRI 18_06_2017 105a81",
        "QF_IDL" : "Yices2-Main",
        "QF_LIA" : "CVC4-smtcomp2017-main",
        "QF_LIRA" : "Yices2-Main",
        "QF_LRA" : "CVC4-smtcomp2017-main",
        "QF_NIA" : "CVC4-smtcomp2017-main",
        "QF_NIRA" : "SMTRAT-comp2017_2",
        "QF_NRA" : "Yices2-Main",
        "QF_RDL" : "Yices2-Main",
        "QF_UF" : "Yices2-Main",
        "QF_UFBV" : "Boolector SMT17 final",
        "QF_UFIDL" : "Yices2-Main",
        "QF_UFLIA" : "Yices2-Main",
        "QF_UFLRA" : "Yices2-Main",
        "QF_UFNIA" : "Yices2-Main",
        "QF_UFNRA" : "Yices2-Main",
        "UF" : "vampire4.2-smt",
        "UFBV" : "CVC4-smtcomp2017-main",
        "UFDT" : "CVC4-smtcomp2017-main",
        "UFDTLIA" : "vampire4.2-smt",
        "UFIDL" : "CVC4-smtcomp2017-main",
        "UFLIA" : "CVC4-smtcomp2017-main",
        "UFLRA" : "CVC4-smtcomp2017-main",
        "UFNIA" : "vampire4.2-smt",
}

winners_2016_main = {
        "ALIA" : "CVC4-master-2016-05-27-cfef263-main",
        "AUFLIA" : "CVC4-master-2016-05-27-cfef263-main",
        "AUFLIRA" : "vampire_smt_4.1",
        "AUFNIRA" : "vampire_smt_4.1_parallel",
        "BV" : "Q3B",
        "LIA" : "CVC4-master-2016-05-27-cfef263-main",
        "LRA" : "CVC4-master-2016-05-27-cfef263-main",
        "NIA" : "z3-4.4.1",
        "NRA" : "vampire_smt_4.1_parallel",
        "QF_ABV" : "Boolector",
        "QF_ALIA" : "Yices-2.4.2",
        "QF_ANIA" : "CVC4-master-2016-05-27-cfef263-main",
        "QF_AUFBV" : "CVC4-master-2016-05-27-cfef263-main",
        "QF_AUFLIA" : "Yices-2.4.2",
        "QF_AUFNIA" : "CVC4-master-2016-05-27-cfef263-main",
        "QF_AX" : "Yices-2.4.2",
        "QF_BV" : "Boolector preprop",
        "QF_BVFP" : "mathsat-5.3.11-linux-x86_64-Main",
        "QF_FP" : "mathsat-5.3.11-linux-x86_64-Main",
        "QF_IDL" : "Yices-2.4.2",
        "QF_LIA" : "CVC4-master-2016-05-27-cfef263-main",
        "QF_LIRA" : "Yices-2.4.2",
        "QF_LRA" : "CVC4-master-2016-05-27-cfef263-main",
        "QF_NIA" : "Yices-2.4.2",
        "QF_NIRA" : "CVC4-master-2016-05-27-cfef263-main",
        "QF_NRA" : "Yices-2.4.2",
        "QF_RDL" : "Yices-2.4.2",
        "QF_UF" : "Yices-2.4.2",
        "QF_UFBV" : "Boolector",
        "QF_UFIDL" : "Yices-2.4.2",
        "QF_UFLIA" : "Yices-2.4.2",
        "QF_UFLRA" : "Yices-2.4.2",
        "QF_UFNIA" : "Yices-2.4.2",
        "QF_UFNRA" : "Yices-2.4.2",
        "UF" : "CVC4-master-2016-05-27-cfef263-main",
        "UFBV" : "CVC4-master-2016-05-27-cfef263-main",
        "UFIDL" : "CVC4-master-2016-05-27-cfef263-main",
        "UFLIA" : "CVC4-master-2016-05-27-cfef263-main",
        "UFLRA" : "vampire_smt_4.1",
        "UFNIA" : "vampire_smt_4.1_parallel",
}

winners_2015_main = {
        "ALIA" : "CVC4-experimental-2015-06-15-ff5745a-main",
        "AUFLIA" : "CVC4-experimental-2015-06-15-ff5745a-main",
        "AUFLIRA" : "CVC4-experimental-2015-06-15-ff5745a-main",
        "AUFNIRA" : "CVC4-master-2015-06-15-9b32405-main",
        "BV" : "CVC4-master-2015-06-15-9b32405-main",
        "LIA" : "CVC4-experimental-2015-06-15-ff5745a-main",
        "LRA" : "CVC4-experimental-2015-06-15-ff5745a-main",
        "NIA" : "CVC4-master-2015-06-15-9b32405-main",
        "NRA" : "CVC4-experimental-2015-06-15-ff5745a-main",
        "QF_ABV" : "Boolector SMT15 QF_AUFBV final",
        "QF_ALIA" : "SMTInterpol v2.1-206-g86e9531",
        "QF_ANIA" : "CVC4-experimental-2015-06-15-ff5745a-main",
        "QF_AUFBV" : "CVC4-master-2015-06-15-9b32405-main",
        "QF_AUFLIA" : "Yices",
        "QF_AUFNIA" : "CVC4-master-2015-06-15-9b32405-main",
        "QF_AX" : "Yices",
        "QF_BV" : "Boolector SMT15 QF_BV final",
        "QF_BVFP" : "Z3-unstable",
        "QF_FP" : "Z3-unstable",
        "QF_IDL" : "Yices",
        "QF_LIA" : "CVC4-experimental-2015-06-15-ff5745a-main",
        "QF_LIRA" : "Yices",
        "QF_LRA" : "CVC4-master-2015-06-15-9b32405-main",
        "QF_NIA" : "AProVE NIA 2014",
        "QF_NIRA" : "CVC4-experimental-2015-06-15-ff5745a-main",
        "QF_NRA" : "Yices2-NL",
        "QF_RDL" : "Yices",
        "QF_UF" : "Yices",
        "QF_UFBV" : "Boolector SMT15 QF_AUFBV final",
        "QF_UFIDL" : "Yices",
        "QF_UFLIA" : "Yices",
        "QF_UFLRA" : "Yices",
        "QF_UFNIA" : "CVC4-experimental-2015-06-15-ff5745a-main",
        "QF_UFNRA" : "CVC3",
        "UF" : "CVC4-experimental-2015-06-15-ff5745a-main",
        "UFBV" : "CVC4-master-2015-06-15-9b32405-main",
        "UFIDL" : "CVC4-master-2015-06-15-9b32405-main",
        "UFLIA" : "CVC4-master-2015-06-15-9b32405-main",
        "UFLRA" : "CVC3",
        "UFNIA" : "CVC4-master-2015-06-15-9b32405-main",
}

solvers_2018_main = {
        "Alt-Ergo-SMTComp-2018" : "Alt-Ergo-SMTComp-2018",
        "AProVE NIA 2014" : "AProVE",
        "Boolector" : "Boolector",
        "COLIBRI 10_06_18 v2038" : "COLIBRI",
        "Ctrl-Ergo-SMTComp-2018" : "Ctrl-Ergo",
        "CVC4-experimental-idl-2" : "CVC4-experimental-idl-2",
        "master-2018-06-10-b19c840-competition-default" : "CVC4",
        "mathsat-5.5.2-linux-x86_64-Main" : "MathSAT 5.5.2",
        "Minkeyrink MT" : " MinkeyRink 2018.1 MT",
        "Minkeyrink ST" : " MinkeyRink 2018.1 ST",
        "opensmt2" : "opensmt2",
        "Q3B" : "Q3B",
        "SMTInterpol-2.5-19-g0d39cdee" : "SMTInterpol",
        "SMTRAT-Rat-final" : "SMT-RAT",
        "SMTRAT-MCSAT-final" : "SMT-RAT-MCSAT",
        "SPASS-SATT" : "SPASS-SATT",
        "STP-CMS-mt-2018" : "STP-CMS-mt",
        "STP-CMS-st-2018" : "STP-CMS-st",
        "STP-Riss-st-2018" : "STP-Riss-st",
        "vampire-4.3-smt" : "Vampire 4.3",
        "veriT" : "veriT",
        "veriT+raSAT+Reduce" : "veriT+raSAT+Reduce",
        "Yices 2.6.0" : "Yices 2.6.0",
        "z3-4.7.1" : "Z3 (4.7.1)",
}

solvers_2017_main = {
        "AProVE NIA 2014" : "AProVE",
        "Boolector SMT17 final" : "Boolector",
        "Boolector+CaDiCaL SMT17 final" : "Boolector+CaDiCaL",
        "COLIBRI 18_06_2017 105a81" : "COLIBRI",
        "CVC4-smtcomp2017-main" : "CVC4",
        "mathsat-5.4.1-linux-x86_64-Main" : "MathSAT 5.4.1",
        "MinkeyRink 2017.3a" : "MinkeyRink",
        "opensmt2-2017-06-04" : "opensmt2",
        "Q3B" : "Q3B",
        "Redlog" : "Redlog",
        "SMTRAT-comp2017_2" : "SMT-RAT",
        "SMTInterpol" : "SMTInterpol",
        "stp_mt" : "STP-mt",
        "stp_st" : "STP-st",
        "vampire4.2-smt" : "Vampire",
        "veriT-2017-06-17" : "veriT",
        "veriT+Redlog_20170618" : "veriT+Redlog",
        "veriT+raSAT+Redlog" : "veriT+raSAT+Redlog",
        "xsat-smt-comp-2017" : "XSat",
        "Yices2-Main" : "Yices2",
        "z3-4.5.0" : "Z3 (4.5.0)",
}

solvers_2016_main = {
        "ABC_default" : "ABC_default",
        "ABC_glucose" : "ABC_glucose",
        "AProVE NIA 2014" : "AProVE",
        "Boolector" : "Boolector",
        "Boolector preprop" : "Boolector (preprop)",
        "CVC4-master-2016-05-27-cfef263-main" : "CVC4 (Main track)",
        "MapleSTP" : "MapleSTP",
        "MapleSTP-mt" : "MapleSTP-mt",
        "mathsat-5.3.11-linux-x86_64-Main" : "MathSAT 5",
        "Minkeyrink  2016" : "Minkeyrink",
        "OpenSMT2-2016-05-12" : "OpenSMT2",
        "ProB" : "ProB",
        "Q3B" : "Q3B",
        "raSAT 0.3" : "raSAT 0.3",
        "raSAT 0.4 exp - final" : "raSAT 0.4",
        "SMT-RAT" : "SMT-RAT",
        "smtinterpol-2.1-258-g92ab3df" : "SMTInterpol",
        "stp-cms-exp-2016" : "STP-cms-exp-2016",
        "stp-cms-mt-2016" : "STP-cms-mt-2016",
        "stp-cms-st-2016" : "STP-cms-st-2016",
        "stp-minisat-st-2016" : "STP-minisat-st-2016",
        "toysmt" : "toysmt",
        "vampire_smt_4.1" : "Vampire",
        "vampire_smt_4.1_parallel" : "Vampire (parallel)",
        "veriT-dev" : "veriT",
        "Yices-2.4.2" : "Yices-2.4.2",
        "z3-4.4.1" : "Z3 (4.4.1)",
}

solvers_2015_main = {
        "AProVE NIA 2014" : "AProVE",
        "Boolector SMT15 QF_AUFBV final" : "Boolector (QF_AUFBV)",
        "Boolector SMT15 QF_BV final" : "Boolector (QF_BV)",
        "CVC3" : "CVC3",
        "CVC4-master-2015-06-15-9b32405-main" : "CVC4",
        "CVC4-experimental-2015-06-15-ff5745a-main" : "CVC4 Experimental",
        "MathSat 5.3.6 main" : "MathSAT 5",
        "OpenSMT2" : "OpenSMT2",
        "OpenSMT2-parallel" : "OpenSMT2-parallel",
        "raSAT" : "raSAT",
        "SMT-RAT-final" : "SMT-RAT",
        "SMT-RAT-NIA-Parallel-final" : "SMT-RAT-PARL",
        "SMTInterpol v2.1-206-g86e9531" : "SMTInterpol",
        "stp-cryptominisat4" : "STP-CryptoMiniSat4",
        "stp-cmsat4-v15" : "STP-CryptoMiniSat4-v15",
        "stp-cmsat4-mt-v15" : "STP-CryptoMiniSat4-mt-v15",
        "stp-minisat-v15" : "STP-MiniSat-v15",
        "veriT" : "veriT",
        "Yices" : "Yices2",
        "Yices2-NL" : "Yices2-NL",
        "z3 4.4.0" : "Z3 (4.4.0)",
        "Z3-unstable" : "Z3 (unstable)",
        "z3-ijcar14" : "Z3 (IJCAR'14)",
}

results = {}
benchmarks = {}
common_benchmarks = {}
vbs = {}

if __name__ == "__main__":
    try:
        aparser = ArgumentParser()
        aparser.add_argument \
              (
                "files",
                metavar="file[,file,...]",
                help="Results files"
              )
        aparser.add_argument \
              (
                "years",
                metavar="year[,year,...]",
                help="years to output files"
              )
        aparser.add_argument \
            (
                "-w",
                dest="winners_only", default=False, action="store_true",
                help="Generate output files for winners only"
            )
        aparser.add_argument \
            (
                "-v",
                dest="vbs_only", default=False, action="store_true",
                help="Generate output files for vbs only"
            )
        args = aparser.parse_args()

        path = "{}/results-files".format(os.getcwd())
        if not os.path.exists(path): os.mkdir(path)

        args.files = args.files.split(sep=',')
        args.years = args.years.split(sep=',')
        common_benchmarks = {}
        common_benchmarks_all = set()
        benchmarks_all = {}
        for f in args.files:
            if f not in results: results[f] = {}
            if f not in vbs: vbs[f] = {}
            with open(f, 'r') as infile:
                lines = infile.readlines()
                i = 0
                for line in lines:
                    i += 1
                    line = line.strip()
                    cols = line.split(sep=',')
                    if "pair id" in cols[0]: continue
                    benchmark = cols[1]
                    benchmark_split = benchmark.split(sep='/')
                    logic = None
                    benchmark_name = None
                    for i in range(0, len(benchmark_split)):
                        if benchmark_split[i].isupper():
                            logic = benchmark_split[i]
                            benchmark_name = '/'.join(benchmark_split[i:])
                            break
                    if not logic:
                        raise ValueError(
                                "invalid logic string'{}'".format(cols[1]))
                    assert (benchmark_name)
                    if logic not in results[f]:
                        results[f][logic] = {}
                    #if logic not in vbs[f]:
                    #    vbs[f][logic] = {}
                    if logic not in benchmarks:
                        benchmarks[logic] = {}
                    if f not in benchmarks[logic]:
                        benchmarks[logic][f] = set()
                    if f not in benchmarks_all:
                        benchmarks_all[f] = set()
                    solver = cols[3]
                    if solver not in results[f][logic]:
                        results[f][logic][solver] = {}
                    if benchmark in results[f][logic][solver]:
                        raise ValueError(
                                "duplicate benchmark '{}' " \
                                "for solver '{}'".format(benchmark, solver))
                    assert (logic in results[f])
                    assert (solver in results[f][logic])
                    assert (logic in benchmarks)
                    assert (f in benchmarks[logic])
                    assert (f in vbs)
                    #assert (logic in vbs[f])
                    results[f][logic][solver][benchmark_name] = cols[9]
                    benchmarks[logic][f].add(benchmark_name)
                    #if benchmark_name not in vbs[f][logic] \
                    #   or vbs[f][logic][benchmark_name][1] < cols[9]:
                    #       vbs[f][logic][benchmark_name] = [solver, cols[9]]
                    if benchmark_name not in vbs[f] \
                       or vbs[f][benchmark_name][1] < cols[9]:
                           vbs[f][benchmark_name] = [solver, cols[9]]
                    benchmarks_all[f].add(benchmark_name)

        for f in vbs:
            print("@ " + str(f) + " " + str(len(vbs[f])))
        i = 0
        for f in benchmarks_all:
            print("@@ " + str(f) + " " + str(len(benchmarks_all[f])))
            if i == 0:
                common_benchmarks_all = benchmarks_all[f]
            else:
                common_benchmarks_all = common_benchmarks_all.intersection(benchmarks_all[f])
            i += 1

        print("common " + str(len(common_benchmarks_all)))
        #leny = {}
        #lenz = {}
        ##for l in benchmarks:
        ##    i = 0
        ##    for f in benchmarks[l]:
        ##        if f not in leny:
        ##            leny[f] = 0
        ##        leny[f] += len(benchmarks[l][f])
        ##        if i == 0:
        ##            common_benchmarks[l] = benchmarks[l][f]
        ##            lenz[f] = benchmarks[l][f]
        ##        else:
        ##            common_benchmarks[l] = \
        ##                    common_benchmarks[l].intersection(benchmarks[l][f])
        ##            assert(f in lenz)
        ##            #if f not in lenz:
        ##            #    lenz[f] = benchmarks[l][f]
        ##            #else:
        ##            lenz[f].update(benchmarks[l][f])
        ##        i += 1
        #for l in benchmarks:
        #    i = 0
        #    for f in benchmarks[l]:
        #        if f not in leny:
        #            leny[f] = 0
        #        leny[f] += len(benchmarks[l][f])
        #        assert(len(benchmarks[l][f]))
        #        if f not in lenz or lenz[f] == None:
        #            lenz[f] = benchmarks[l][f]
        #        else:
        #            assert(lenz[f])
        #            lenz[f] = lenz[f].update(benchmarks[l][f])
        #        if i == 0:
        #            common_benchmarks[l] = benchmarks[l][f]
        #        else:
        #            common_benchmarks[l] = \
        #                    common_benchmarks[l].intersection(benchmarks[l][f])
        #        i += 1


        #print(leny)
        #common_benchmarks_all = {}
        #i = 0
        #for f in lenz:
        #    print("# " + str(f) + " " + str(len(lenz[f])))
        #    if i == 0:
        #        common_benchmarks_all = lenz[f]
        #    else:
        #        common_benchmarks_all.intersection(lenz[f])
        #    i += 1
        #print("### " + str(len(common_benchmarks_all)))
        #asdf = {}
        #i = 0
        #for l in common_benchmarks:
        #    if i == 0:
        #        asdf = common_benchmarks[l]
        #    else:
        #        asdf.update(common_benchmarks[l])
        #    i += 1
        #print("##- " + str(len(asdf)))


            

        with open("makefile", 'w') as makefile:
            makefile.write("all:\n")
            makefile.write("\tmkdir -p pdf\n")
            tmp = {}
            tmp_vbs = {}
            for i in range(0,len(args.files)):
                f = args.files[i]
                p = args.years[i]
                winners = winners_2018_main if p == "2018" \
                        else (winners_2017_main if p == "2017" \
                        else (winners_2016_main if p == "2016" \
                        else winners_2015_main))
                solvers = solvers_2018_main if p == "2018" \
                        else (solvers_2017_main if p == "2017" \
                        else (solvers_2016_main if p == "2016" \
                        else solvers_2015_main))

                outfile_name = "{}/{}-Main_Track-VBS.csv".format(path, p)
                tmp_vbs["VBS-{}".format(p)] = outfile_name
                with open(outfile_name, 'w') as outfile:
                    outfile.write(
                            "# 1 solver, 2 benchmark, 3 time (wallclock)\n")
                    #lenx = 0
                    #for l in results[f]:
                    #    for b in common_benchmarks[l]:
                    #        if len(common_benchmarks[l]) > 0:
                    #            outfile.write(
                    #                "{},{},{}\n".format(
                    #                    vbs[f][l][b][0],
                    #                    b,
                    #                    vbs[f][l][b][1]))
                    #            lenx += 1
                    #print(lenx)
                    for b in common_benchmarks_all:
                        outfile.write(
                                "{},{},{}\n".format(
                                vbs[f][b][0],
                                b,
                                vbs[f][b][1]))
                if not args.vbs_only:
                    for l in results[f]:
                        if len(common_benchmarks[l]) > 0:
                            if not l in tmp: tmp[l] = {}
                            assert (l in benchmarks)
                            r = results[f][l] \
                                    if not args.winners_only else [winners[l]]
                            for s in r:
                                s_name = s if not args.winners_only \
                                           else solvers[s]
                                outfile_name = \
                                        "{}/{}-{}-Main_Track-{}.csv".format(
                                                path, p, l, s_name)
                                tmp[l]["{}-{}".format(p,s_name)] = outfile_name
                                with open(outfile_name, 'w') as outfile:
                                    outfile.write(
                                        "# 1 solver, "\
                                        "2 benchmark, "\
                                        "3 time (wallclock)\n")
                                    for b in common_benchmarks[l]:
                                        assert (b in results[f][l][s])
                                        assert (s in solvers)
                                        outfile.write(
                                            "{},{},{}\n".format(
                                                s_name,
                                                b,
                                                results[f][l][s][b]))
            makefile.write(
                    '\tRscript cactus_plot.r "VBS" "{}" "{}"\n'.format(
                        '" "'.join(tmp_vbs.values()),
                        '" "'.join(tmp_vbs.keys())))
            if not args.vbs_only:
                for l in tmp:
                    makefile.write(
                            '\tRscript cactus_plot.r "{}" "{}" "{}"\n'.format(
                                l,
                                '" "'.join(tmp[l].values()),
                                '" "'.join(tmp[l].keys())))
            makefile.write("clean:\n")
            makefile.write("\trm -r pdf\n")
            makefile.write("\trm -r makefile\n")
    except BrokenPipeError:
        pass

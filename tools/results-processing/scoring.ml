open Format

type raw_score = {
  raw_bench : string;
  error : int;
  correct : int;
  wall : float; 
  cpu : float;
  pending : int;
}

type weighted_raw_score = {
  mutable w_error : float;
  mutable w_correct : float;
  mutable w_wall : float; 
  mutable w_cpu : float;
  mutable w_pending : int;
}


type perf = {
  seq_perf : weighted_raw_score ; 
  parall_perf : weighted_raw_score;
  solved : int;
  solved_seq : int;
  not_solved : int;
  not_solved_seq : int;
  remaining : int;
}

type result = Sat | Unsat | Unknown 

type division = {
  mutable name : string;
  mutable nb_pairs : int;
  mutable nb_benchs : int;
  mutable complete : bool;
  mutable nb_pendings : int;
  mutable winner_seq : string;
  mutable winner_parall : string;
  provers : (string, raw_score list) Hashtbl.t;
  mutable order_seq : string list;
  mutable order_parall : string list;
  benchs :  (string, result) Hashtbl.t;
  families : (string, int) Hashtbl.t;
  clash : (string,unit) Hashtbl.t;
  mutable table : (string * perf) list;
  mutable competitive_seq : bool;
  mutable competitive_parall : bool;
}

type status = Complete | Pending | Timeout | Memout

type csv_line = {
  mutable pair_id : string ;
  mutable benchmark : string ;
  mutable benchmark_id : string ;
  mutable solver : string ;
  mutable solver_id : string;
  mutable configuration : string ;
  mutable configuration_id : string ;
  mutable status : status;
  mutable cpu_time : float ;
  mutable wallclock_time : float;
  mutable memory_usage : float ;
  mutable result : result;
  mutable expected : result;
}

let solver_short_names = 
  [
"Alt-Ergo-SMTComp-2018","Alt-Ergo";
"AProVE NIA 2014","AProVE";
"Boolector","Boolector";
"COLIBRI 10_06_18 v2038","COLIBRI";
"Ctrl-Ergo-SMTComp-2018","Ctrl-Ergo";
"CVC4-experimental-idl-2","CVC4-experimental-idl-2";
"master-2018-06-10-b19c840-competition-default","CVC4";
"mathsat-5.5.2-linux-x86_64-Main","MathSAT";
"Minkeyrink MT","Minkeyrink-MT";
"Minkeyrink ST","Minkeyrink-ST";
"opensmt2","opensmt2";
"Q3B","Q3B";
"SMTInterpol-2.5-19-g0d39cdee","SMTInterpol";
"SMTRAT-MCSAT-final","SMTRAT-MCSAT";
"SMTRAT-Rat-final","SMTRAT-Rat";
"SPASS-SATT","SPASS-SATT";
"STP-CMS-mt-2018","STP-CMS-mt-2018";
"STP-CMS-st-2018","STP-CMS-st-2018";
"STP-Riss-st-2018","STP-Riss-st-2018";
"vampire-4.3-smt","vampire 4.3 (test)";
"veriT","veriT";
"veriT+raSAT+Reduce","veriT+raSAT+Reduce";
"Yices 2.6.0","Yices 2.6.0";
"z3-4.7.1","z3-4.7.1";
    "No winner", "No (competing) winner"
  ]

let short_name s = 
  try
    List.assoc s solver_short_names
  with Not_found -> 
    eprintf "error : not found %s@." s;
    assert false

let jobs_dir = "jobs"
let results_dir = "results"

let date = 
  let d = Sys.argv.(1) in
  Unix.gmtime (float_of_string d)

let wall = float_of_string Sys.argv.(2)

let non_competitive_solver s = 
  s = "z3-4.7.1" || 
  s = "mathsat-5.5.2-linux-x86_64-Main" 

let competitive_solvers_only l = 
  List.filter (fun (s,_) -> not (non_competitive_solver s)) l


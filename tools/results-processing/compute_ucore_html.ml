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
  parall_perf : weighted_raw_score ; 
  not_solved : int;
  remaining : int;
}

type division = {
  mutable name : string;
  mutable nb_pairs : int;
  mutable complete : bool;
  mutable nb_pendings : int;
  mutable winner_seq : string;
  mutable winner_par : string;
  provers : (string, raw_score list) Hashtbl.t;
  mutable order_seq : string list;
  mutable order_par : string list;
  benchs :  (string, unit) Hashtbl.t;
  mutable table : (string * perf) list;
  families : (string, int) Hashtbl.t;
  mutable competitive_seq : bool;
  mutable competitive_par : bool;
}

type result = Sat | Unsat | Unknown

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
  mutable unsat_core_validated : bool;
  mutable result_is_erroneous : bool;
  mutable parsable_unsat_core : bool;
  mutable size_unsat_core : int;
  mutable number_of_assert_commands : int;
  mutable check_sat_result_is_erroneous : bool;
  mutable reduction : int
}

let jobs_dir = "jobs-ucore"
let results_dir = "results-ucore"

let date = 
  let d = Sys.argv.(1) in
  Unix.gmtime (float_of_string d)

let wall = float_of_string Sys.argv.(2)

let result_of_string s = 
  match s with
    | "sat" -> Sat 
    | "unsat" -> Unsat 
    | "starexec-unknown" | "--" -> Unknown
    | _ -> 
      eprintf "error : cannot convert result %s@." s;
      exit 1

let family_of c = 
  let b = Str.split (Str.regexp "/") c in
  let rec concat = function
    | [] -> assert false
    | [x] -> ""
    | x :: s -> x^"/"^(concat s)
  in 
  concat b

let division_and_family_of c = 
  let b = Str.split (Str.regexp "/") c in
  match b with
    | _ :: d :: bch ->
      let rec concat = function
	| [] -> assert false
	| [x] -> ""
	| x :: s -> x^"/"^(concat s)
      in 
      d, concat (d::bch)
	
    | _ -> 
      eprintf "ici : %s@." c;
      assert false

let empty_csv_line () = 
  {
    pair_id = "" ;
    benchmark = "" ;
    benchmark_id = "" ;
    solver = "" ;
    solver_id = "" ;
    configuration = "" ;
    configuration_id = "" ;
    status = Pending ;
    cpu_time = 0. ;
    wallclock_time = 0. ;
    memory_usage = 0. ;
    result = Unknown;
    expected = Unknown;
    unsat_core_validated = false;
    result_is_erroneous = false;
    parsable_unsat_core = false;
    size_unsat_core = 0;
    number_of_assert_commands = 0;
    check_sat_result_is_erroneous = false;
    reduction = 0;
  }

let status_of_string s = 
  match s with
    | "complete" -> Complete 
    | "pending submission" -> Pending 
    | "timeout (cpu)" | "timeout (wallclock)" -> Timeout
    | "memout" -> Memout
    | _ -> 
      eprintf "error : cannot convert status %s@." s;
      exit 1

let col_names = [ 
"pair id";
"benchmark";
"benchmark id";
"solver";
"solver id";
"configuration";
"configuration id";
"status";
"cpu time";
"wallclock time";
"memory usage";
"result";
"expected";
"validation-check-sat-time_cvc4";
"validation-solvers";
"validation-check-sat-result_z3";
"ucpp-version";
"validation-check-sat-time_z3";
"validation-check-sat-result_mathsat";
"unsat-core-rejections";
"unsat-core-validated";
"validation-check-sat-time_vampire";
"unsat-core-confirmations";
"result-is-erroneous";
"parsable-unsat-core";
"validation-check-sat-result_cvc4";
"size-unsat-core";
"validation-check-sat-time_mathsat";
"number-of-assert-commands";
"check-sat-result-is-erroneous";
"reduction";
"validation-check-sat-result_vampire"
]

let split_csv s = Str.split (Str.regexp ",") s

let split_csv_line s = 
  let l = split_csv s in
  let c = empty_csv_line () in
  try
    List.iter2 
      (fun label v ->
	match label with
	  | "pair id" -> c.pair_id <- v
	  | "benchmark" -> c.benchmark <- v
	  | "benchmark id" -> c.benchmark_id <- v
	  | "solver" -> c.solver <- v
	  | "solver id" -> c.solver_id <- v
	  | "configuration" -> c.configuration <- v
	  | "configuration id" -> c.configuration_id <- v
	  | "status" -> c.status <- status_of_string v
	  | "cpu time" -> c.cpu_time <- float_of_string v
	  | "wallclock time" -> c.wallclock_time <- float_of_string v
	  | "memory usage" -> c.memory_usage <- float_of_string v
	  | "result" -> c.result <- result_of_string v
	  | "expected" -> c.expected <- result_of_string v
	  | "REVISED_result-is-erroneous" -> c.result_is_erroneous<- ((int_of_string v)=1)
	  | "parsable-unsat-core" -> if v <> "-" then c.parsable_unsat_core <- bool_of_string v
	  | "size-unsat-core" -> 
	    if v <> "-" then  c.size_unsat_core <- int_of_string v
	  | "number-of-assert-commands" -> 
	    c.number_of_assert_commands <- int_of_string v
	  | "REVISED_reduction" -> c.reduction <- int_of_string v
	  | _ -> () 
      ) 
      col_names l;
    c
  with Invalid_argument _ -> 
    eprintf " error : cvs line << %s >> does not have the good structure@." s;
    exit 1

let input_line ch = String.trim (input_line ch)

let divs = Hashtbl.create 107 

let init_divs cin = 
  let visited = Hashtbl.create 1007 in
  let find_division d_name = 
    try Hashtbl.find divs d_name
    with Not_found -> 
      let d = {
	name = d_name;
	nb_pairs = 0;
	complete = true;
	nb_pendings = 0;
	order_seq = [];
	order_par = [];
	winner_seq = "";
	winner_par = "";
	provers = Hashtbl.create 7;
	benchs = Hashtbl.create 1007;
	table = [];
	families = Hashtbl.create 17;
        competitive_seq = true;
        competitive_par = true;
      }
      in Hashtbl.add divs d_name d; d
  in
  (try
     while true do 
       let tmp =  input_line cin in
       let c = split_csv_line tmp in
       if not (Hashtbl.mem visited c.benchmark) then
       	 begin
       	   Hashtbl.add visited c.benchmark ();
       	   let d_name, f_name = division_and_family_of c.benchmark in
       	   let d = find_division d_name in
       	   let n = try Hashtbl.find d.families f_name with Not_found -> 0 in
       	   Hashtbl.replace d.families f_name (n + 1);
       	 end
     done 
   with End_of_file -> ())


let solver_short_names = 
  [
"master-2018-06-10-b19c840-proofs-unsat_cores", "CVC4";
"SMTInterpol-2.5-19-g0d39cdee", "SMTInterpol";
"mathsat-5.5.2-linux-x86_64-Unsat-Core", "mathsat-5.5.2";
"Yices 2.6.0","Yices 2.6.0";
"z3-4.7.1", "z3-4.7.1";
    "No winner", "No (competitive) winner"
  ]

let test_filter s = 
  s = "mathsat-5.4.1-linux-x86_64-Unsat-Core" ||
  s = "z3-4.7.1" 

let filter_solvers l = 
  List.filter (fun (s,_) -> not (test_filter s)) l

module Html = struct

  let day_of = function 
    | 0 -> "Sun"  | 1 -> "Mon" | 2 -> "Tue" | 3 -> "Wed"
    | 4 -> "Thu"  | 5 -> "Fri" | 6 -> "Sat"
    | _ -> assert false

  let month_of = function 
    | 0 -> "Jan"  | 1 -> "Feb" | 2 -> "Mar" | 3 -> "Apr"
    | 4 -> "May"  | 5 -> "Jun" | 6 -> "Jul" | 7 -> "Aug"
    | 8 -> "Sep"  | 9 -> "Oct" | 10 -> "Nov" | 11 -> "Dec"
    | _ -> assert false

    
  let print_date fmt d = 
    fprintf fmt "%s %s %d %02d:%02d:%02d GMT" 
      (day_of d.Unix.tm_wday) 
      (month_of d.Unix.tm_mon)
      d.Unix.tm_mday
      d.Unix.tm_hour
      d.Unix.tm_min
      d.Unix.tm_sec

  let print_header fmt name = 
    fprintf fmt "<!--#set var=\"title\" value=\" %s (Unsat Core Track)\"-->" name;
    fprintf fmt "<!--#include file=\"smt-comp-prelude.shtml\" -->";
    fprintf fmt "<p>Competition results for the %s division as of %a" 
     name print_date date

  let print_summary_header fmt () = 
    fprintf fmt "<!--#set var=\"title\" value=\"Summary\"-->";
    fprintf fmt "<!--#include file=\"smt-comp-prelude.shtml\" -->";
    fprintf fmt "<H1>Unsat Core Track</H1>";
    fprintf fmt "<p>Competition results as of %a" print_date date;
    fprintf fmt 
      "<style> table{ table-layout:fixed; border-collapse:collapse; 
                      border-spacing:0; border:1px solid black; } 
                      td { padding:0.25em; border: 1px solid black } </style>";
    
    fprintf fmt "<p><table>
                 <tr>
                 <td>Logic</td>
                 <td>Solvers</td>
                 <td>Benchmarks</td>
                 <td>Order</td>
                 </tr>
                 "

  let print_competition_header fmt () = 
    fprintf fmt 
      "<!--#set var=\"title\" value=\"Competition-Wide Scoring for the Unsat Core Track\"-->";
    fprintf fmt "<!--#include file=\"smt-comp-prelude.shtml\" -->";
    fprintf fmt "<p>Competition results as of %a" print_date date;
    fprintf fmt "<p>"


  let print_summary_footer fmt () = 
    fprintf fmt "</table><p>";
    fprintf fmt "<p> <span id=\"fn\"> n. Non-competing. </span></p>";
    fprintf fmt "<!--#include virtual=\"smt-comp-postlude.shtml\" -->"

  let print_competition_footer fmt () = 
    fprintf fmt "<!--#include virtual=\"smt-comp-postlude.shtml\" -->"

let print_header_results fmt d =
  fprintf fmt "<p><B>Benchmarks in this division : %d</B> @." (Hashtbl.length d.benchs);
  if d.complete then
    begin
      if d.winner_seq = "No winner" then
        fprintf fmt "<h3> Non-Competitive division </h3>"
      else
        begin
          fprintf fmt "<h3>Winners: </h3>";
          fprintf fmt "<table>";
          fprintf fmt "<tr>
                           <td>Sequential Performances</td>
                           <td>Parallel Performances</td>
                           </tr>";
          try
          fprintf fmt
            "<tr><td>%s</td><td>%s</td>"
            (List.assoc d.winner_seq solver_short_names)
            (List.assoc d.winner_par solver_short_names);
          with Not_found -> printf "Missing %s\n" d.winner_seq; printf "Missing %s\n"  d.winner_par; raise Not_found;

          fprintf fmt "</table><p><p>";

          fprintf fmt "<h3>Result table<sup><a href=\"#fn1\">1</a></sup></h3>@.";
        end
    end

  let print_footer fmt () = 
    fprintf fmt "<p> <span id=\"fn\"> n. Non-competing. </span></p>";
    fprintf fmt "<p> <span id=\"fn1\"> 1. Scores are computed according to Section 7 of the rules. </span></p>";
    fprintf fmt "<!--#include virtual=\"smt-comp-postlude.shtml\" -->"


  let non_competitive_solver s = 
    s = "mathsat-5.5.2-linux-x86_64-Unsat-Core" ||
    s = "z3-4.7.1"

  let print_solver fmt s = 
    try
    let b = non_competitive_solver s in
    let s = List.assoc s solver_short_names in
    if b then fprintf fmt "%s<SUP><a href=\"#fn\">n</a></SUP>" s 
    else fprintf fmt "%s" s
    with Not_found -> printf "Missing %s\n" s; raise Not_found

  let compare_solver_names (n1, _) (n2, _) =
    compare n1 n2

let print_prover_line fmt d =
  fprintf fmt
    "<style> 
       table{ table-layout:fixed; border-collapse:collapse; 
              border-spacing:0; border:1px solid black; } 
             td { padding:0.5em; border: 1px solid black } </style>@.";
  fprintf fmt "<table>\n";
  fprintf fmt
    "<tr><td rowspan=\"2\">Solver</td>
             <td colspan=\"3\" align=center>Sequential performance</td>
             <td colspan=\"4\" align=center>Parallel performance</td>
         </tr>
         <tr>
             <td>Error Score</td>
             <td>Reduction Score</td>
             <td>avg. CPU time</td>

             <td>Errors</td>
             <td>Reduction Score</td>
             <td>avg. CPU time</td>
             <td>avg. WALL time</td>

         </tr>";
  List.iter
    (fun (p, i) ->
      fprintf fmt "<tr>\n";
      fprintf fmt "<td>%a</td>\n" print_solver p;

      fprintf fmt "<td>%.3f</td>" i.seq_perf.w_error;
      fprintf fmt "<td>%.3f</td>" i.seq_perf.w_correct;
      fprintf fmt "<td>%.3f</td>" i.seq_perf.w_cpu;

      fprintf fmt "<td>%.3f</td>" i.parall_perf.w_error;
      fprintf fmt "<td>%.3f</td>" i.parall_perf.w_correct;
      fprintf fmt "<td>%.3f</td>" i.parall_perf.w_cpu;
      fprintf fmt "<td>%.3f</td>" i.parall_perf.w_wall;

      fprintf fmt "</tr>"
    )
    (List.sort compare_solver_names d.table);
  fprintf fmt "</table>\n"
	
  let print_division d = 
    let res_name = results_dir^"/results-"^d.name^"-ucore.shtml" in
    try
      let chan = open_out res_name in
      let fmt = formatter_of_out_channel chan in
      print_header fmt d.name;
      print_header_results fmt d;
      print_prover_line fmt d;
      print_footer fmt ();
      fprintf fmt "@.";
      close_out chan
    with Sys_error m -> 
      eprintf "error : cannot open %s\n %s\n@." res_name m;
      exit 1

  let print_division_not_started name = 
    let res_name = results_dir^"/results-"^name^"-ucore.shtml" in
    try
      let chan = open_out res_name in
      let fmt = formatter_of_out_channel chan in
      print_header fmt name;
      fprintf fmt 
	"<H1> The competition for the division %s has not started yet </H1> " 
	name;
      print_footer fmt ();
      fprintf fmt "@.";
      close_out chan
    with Sys_error m -> 
      eprintf "error : cannot open %s\n %s\n@." res_name m;
      exit 1


  let print_solver fmt s = 
    let b = non_competitive_solver s in
    let s = List.assoc s solver_short_names in
    if b then fprintf fmt "%s<SUP><a href=\"#fn\">n</a></SUP>" s 
    else fprintf fmt "%s" s

  let print_solver_list fmt l = 
    let rec print = function
      | [] -> ()
      | [s] -> fprintf fmt "%a" print_solver s
      | s :: l -> fprintf fmt "%a; " print_solver s; print l
    in 
    print l

  let print_summary_division fmt d =
    if d.winner_seq = "" then
      fprintf fmt "<tr bgcolor=#E4E4E4>"
    else fprintf fmt "<tr>";
    fprintf fmt "<td rowspan=4><a href=\"results-%s-ucore.shtml\">%s</a></td>"
      d.name d.name;
    fprintf fmt "<td rowspan=4>%d</td>" (Hashtbl.length d.provers);
    fprintf fmt "<td rowspan=4>%d</td>" (Hashtbl.length d.benchs);
    fprintf fmt "<td>%a</td>" print_solver_list d.order_seq;
    fprintf fmt "</tr>";
    if d.winner_seq="" then
      fprintf fmt "<tr bgcolor=#E4E4E4>"
    else fprintf fmt "<tr>";
    fprintf fmt "<td>%a</td>" print_solver_list d.order_par;
    fprintf fmt "</tr>";
  
    if d.winner_seq="" then
      fprintf fmt "<tr bgcolor=#E4E4E4>"
    else fprintf fmt "<tr>";
    fprintf fmt "</tr>";

    if d.winner_seq="" then
      fprintf fmt "<tr bgcolor=#E4E4E4>"
    else fprintf fmt "<tr>";
    fprintf fmt "</tr>"

end

let check_header job ch = 
  try
    let s = input_line ch in
    let l = (split_csv s) in
    List.for_all2 (fun c1 c2 -> c1 = c2)  l col_names
  with 
    | Invalid_argument _ -> false
    | End_of_file -> 
      eprintf "error: cannnot read %s" job;
      exit 1
  

let raw_score c = 
  let error, correct, pending, cpu, wall = 
    match c.status with
      | Pending -> 0, 0, 1, c.cpu_time, c.wallclock_time

      | Complete when c.result <> Unknown -> 
	if c.result = Sat ||  c.result_is_erroneous ||  not c.parsable_unsat_core then
	  1, 0, 0, c.cpu_time, c.wallclock_time
	else 
	  0, c.reduction, 0, c.cpu_time, c.wallclock_time

      | _ -> 0, 0, 0, c.cpu_time, c.wallclock_time

  in
  { error = error; correct = correct; 
    wall = wall; cpu = cpu;
    pending = pending;
    raw_bench = c.benchmark;
  }

let all_divisions = 
  let t = Hashtbl.create 17 in
  List.iter (fun d -> Hashtbl.add t d () )
[
"ALIA"; "AUFLIRA"; "AUFNIRA"; "BV"; "LRA"; "QF_ABV"; "NRA"; "QF_ALIA"; "QF_AUFLIA"; "QF_BV"; 
"QF_AX"; "QF_BVFP"; "QF_FP"; "QF_IDL"; "QF_LIA"; "QF_LIRA"; "QF_LRA"; "QF_NIA"; "QF_NRA"; "QF_UF"; 
"QF_RDL"; "QF_UFIDL"; "QF_UFBV"; "UF"; "UFBV"; "UFLIA"; "UFNIA"
];
  t

let update_division d c = 

  Hashtbl.remove all_divisions d.name;

  if not (Hashtbl.mem d.benchs c.benchmark) then
    begin
      Hashtbl.add d.benchs c.benchmark ();
    end;

  d.nb_pairs <- d.nb_pairs + 1;

  d.nb_pendings <- d.nb_pendings + (if c.status = Pending then 1 else 0);

  d.complete <- d.complete && (c.status <> Pending);

  let raw = raw_score c in
  let l = try Hashtbl.find d.provers c.solver with Not_found -> [] in
  Hashtbl.replace d.provers c.solver (raw::l)
    
let run_divisions chan_job = 
  try
    while true do 
      let c = split_csv_line (input_line chan_job) in
      begin
	match Str.split (Str.regexp "/") c.benchmark with  
	  | _ :: n :: s -> 
	    c.benchmark <- List.fold_right (fun x b -> x ^ "/" ^ b) (n :: s) "";
	    update_division (Hashtbl.find divs n) c;
	  | _ -> assert false
      end
    done
  with End_of_file -> ()

let seq_score sc = 
  if sc.cpu > wall then
    { sc with error = 0; correct = 0; cpu = min sc.cpu wall }
  else
    { sc with cpu = min sc.cpu wall }

let alpha_b d b = 
  let fb = family_of b in
  let tmp = Hashtbl.find d.families fb in
  let fb = float tmp in
  (1. +. log fb) /. fb

let compute_prover_perfs d rsc_l = 
  let nb_benchs = Hashtbl.length d.benchs in
  let sum_alpha_b = 
    Hashtbl.fold (fun b _ acc -> acc +. alpha_b d b) d.benchs 0. in

  let sp = { w_error = 0.; w_correct = 0.; w_wall = 0.; w_cpu = 0.; w_pending = 0 } in
  let pp = { w_error = 0.; w_correct = 0.; w_wall = 0.; w_cpu = 0.; w_pending = 0 } in

  let remaining = ref 0 in
  let not_solved = ref nb_benchs in
  let fnb = float nb_benchs in
  List.iter 
    (fun sc -> 
      let alpha'_b = (alpha_b d sc.raw_bench) /. sum_alpha_b in
      let seq_sc = seq_score sc in
      sp.w_error <- (sp.w_error +. alpha'_b *. (float seq_sc.error));
      sp.w_correct <- (sp.w_correct +. alpha'_b *. (float seq_sc.correct));
      sp.w_wall <- (sp.w_wall +. alpha'_b *. seq_sc.wall);
      sp.w_cpu <- (sp.w_cpu +. alpha'_b *. seq_sc.cpu);
      sp.w_pending <- sp.w_pending + seq_sc.pending;

      pp.w_error <- (pp.w_error +. alpha'_b *. (float sc.error));
      pp.w_correct <- (pp.w_correct +. alpha'_b *. (float sc.correct));
      pp.w_wall <- (pp.w_wall +. alpha'_b *. sc.wall);
      pp.w_cpu <- (pp.w_cpu +. alpha'_b *. sc.cpu);
      pp.w_pending <- pp.w_pending + sc.pending;

      remaining := sp.w_pending;
      not_solved := !not_solved - sc.error - sc.correct
    )
  rsc_l;
  sp.w_error <- fnb *. sp.w_error;
  sp.w_correct <- fnb *. sp.w_correct;
  sp.w_wall <- sp.w_wall;
  sp.w_cpu <- sp.w_cpu;
  pp.w_error <- fnb *. pp.w_error;
  pp.w_correct <- fnb *. pp.w_correct;
  pp.w_wall <- pp.w_wall;
  pp.w_cpu <- pp.w_cpu;
  { 
    seq_perf = sp; 
    parall_perf = pp;
    not_solved = !not_solved ;
    remaining = !remaining ;  
  }
    
let roundf x = snd (modf (x +. copysign 0.5 x))
let hackfp fp = int_of_float (roundf (100.0 *. fp))

let compare_perf p1 p2 =
  if hackfp p1.w_error > hackfp p2.w_error then 1
  else if hackfp p1.w_error < hackfp p2.w_error  then -1
  else
    if hackfp p1.w_correct > hackfp p2.w_correct then -1
    else if hackfp p1.w_correct < hackfp p2.w_correct then 1
    else 0


let compare_parall (_, {parall_perf = p1}) (_, {parall_perf = p2}) =
  let c = compare_perf p1 p2 in
  if c != 0 then c
  else
      if p1.w_wall < p2.w_wall then -1
      else if p1.w_wall > p2.w_wall then 1
      else
        if p1.w_cpu < p2.w_cpu then -1
        else if p1.w_cpu > p2.w_cpu then 1
        else 0

let compare_seq (_, {seq_perf = p1}) (_, {seq_perf = p2}) =
  let c = compare_perf p1 p2 in
  if c != 0 then c
  else
      if p1.w_cpu < p2.w_cpu then -1
      else if p1.w_cpu > p2.w_cpu then 1
      else 0

  
let families = 
  let t = Hashtbl.create 20 in
  List.iter (fun (s,f) -> Hashtbl.add t s f)
    ["CVC3 application track", 1 ; 
     "CVC4-master-2015-06-15-9b32405-application", 1; 
     "CVC4-experimental-2015-06-15-ff5745a-application", 1;
     "z3 4.4.0", 2; 
     "stp-cryptominisat4", 4;
     "stp-cmsat4-v15", 4;
     "stp-cmsat4-mt-v15", 4;
     "stp-minisat-v15", 7;
     "SMTInterpol v2.1-206-g86e9531", 6;
     "MathSat 5.3.6 application", 9;
     "Yices", 11;
     "Boolector SMT15 QF_BV application track final", 12;
     "Boolector SMT15 fixed QF_BV application track", 12;
    ];
  t

let non_competitive_solver s =
  s = "mathsat-5.5.2-linux-x86_64-Unsat-Core" ||
  s = "z3-4.7.1"

let competitive_solvers_only l =
  List.filter (fun (s,_) -> not (non_competitive_solver s)) l

let confirm_winner s l = 
  let fs = Hashtbl.find families s in
  List.exists (fun (s',_) -> Hashtbl.find families s' <> fs) l

let compute_division_perfs d = 
  Hashtbl.iter 
    (fun p rsc_l -> 
      d.table <- (p, compute_prover_perfs d rsc_l) :: d.table) 
    d.provers;

  d.order_seq <- List.map fst (List.sort compare_seq d.table);
  d.order_par <- List.map fst (List.sort compare_parall d.table);

  let table = competitive_solvers_only d.table in
  let stable_seq = List.sort compare_seq table in
  let stable_par = List.sort compare_parall table in
  let w_seq =
    if List.length stable_seq < 2 then (d.competitive_seq <- false; "No winner")
    else fst (List.hd stable_seq) in
  let w_par =
    if List.length stable_seq < 2 then
      (d.competitive_par <- false; "No winner" )
    else fst (List.hd stable_par) in
  (*print_string (d.name^" "^w_seq^"\n");*)
  d.winner_seq <- w_seq (*if confirm_winner w_seq table then w_seq else ""*);
  d.winner_par <- w_par (*if confirm_winner w_par table then w_par else ""*)
  
  
let process_job job = 
  printf "Job : %s@." job;
  let job = jobs_dir^"/"^job in
  try
    let chan_job = open_in job in
    if not (check_header job chan_job) then
      eprintf "error : header is not valid -- I skip this job\n@."
    else
      begin
	init_divs chan_job;
	seek_in chan_job 0; ignore (check_header job chan_job);
	run_divisions chan_job;
	Hashtbl.iter (fun _ d -> compute_division_perfs d) divs;
	Hashtbl.iter (fun _ d -> Html.print_division d) divs;
	printf "@. HTML generated : OK\n@.";
	close_in chan_job
      end
  with Sys_error m -> 
    eprintf "error : cannot open %s \n %s\n@." job m;
    exit 1

let summary () = 
  let summary_name = results_dir^"/results-ucore-summary.shtml" in
    try
      let chan = open_out summary_name in
      let fmt = formatter_of_out_channel chan in
      Html.print_summary_header fmt ();
      Hashtbl.iter (fun _ d -> Html.print_summary_division fmt d) divs;
      Html.print_summary_footer fmt ();
      fprintf fmt "@.";
      printf "@. Summary UCORE : OK\n@.";
      close_out chan
    with Sys_error m -> 
      eprintf "error : cannot open %s\n %s\n@." summary_name m;
      exit 1

let () = 
  let jobs = Sys.readdir jobs_dir in
  Array.iter process_job jobs;
  Hashtbl.iter (fun n _ -> Html.print_division_not_started n) all_divisions; 
  summary ()


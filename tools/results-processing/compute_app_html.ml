open Format

type raw_score = {
  error : int;
  correct : int;
  wall : float; 
  cpu : float;
  pending : int;
}

type perf = {
  seq_perf : raw_score ; 
  parall_perf : raw_score;
  not_solved : int;
  remaining : int;
}

type division = {
  mutable name : string;
  mutable nb_pairs : int;
  mutable complete : bool;
  mutable nb_pendings : int;
  mutable winner_parall : string;
  provers : (string, raw_score list) Hashtbl.t;
  mutable order_seq : string list;
  mutable order_parall : string list;
  benchs :  (string, unit) Hashtbl.t;
  mutable table : (string * perf) list;
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
  mutable wrong_answers : int;
  mutable correct_answers : int;
}

let jobs_dir = "jobs-app"
let results_dir = "results-app"

let date = 
  let d = Sys.argv.(1) in
  Unix.gmtime (float_of_string d)

let wall = float_of_string Sys.argv.(2)

let init_division () = {
  name = "";
  nb_pairs = 0;
  complete = true;
  nb_pendings = 0;
  winner_parall = "";
  order_seq = [];
  order_parall = [];
  provers = Hashtbl.create 7;
  benchs = Hashtbl.create 1007;
  table = []
}

let divs = 
  let t = Hashtbl.create 17 in
  List.iter 
    (fun n -> 
      let d = init_division () in
      d.name <- n;
      Hashtbl.add t n d )
    [ "ALIA"; "ANIA"; "AUFNIRA"; "BV"; "LIA"; "QF_ABV"; "QF_ALIA"; "QF_ANIA"; "QF_AUFBV"; "QF_AUFLIA"; "QF_BV";
      "QF_BVFP"; "QF_FP";
      "QF_LIA"; "QF_LRA"; "QF_NIA"; "QF_UFBV"; "QF_UFLIA"; "QF_UFLRA"; "QF_UFNIA";
      "UFLRA" ];
  t

let solver_short_names =
  [
    "Boolector","Boolector";
    "CVC4", "CVC4";
    "MathSAT", "mathsat-5.5.2";
    "SMTInterpol", "SMTInterpol";
    "Yices", "Yices2";
    "Z3", "z3-4.7.1";
    "No winner", "No (competing) winner"
  ]

let split_csv s = Str.split (Str.regexp ",") s

let test_filter s = 
    s = "MathSAT" ||
    s = "Z3" 

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
    fprintf fmt "<!--#set var=\"title\" value=\" %s (Application Track)\"-->" name;
    fprintf fmt "<!--#include file=\"smt-comp-prelude.shtml\" -->";
    fprintf fmt "<p>Competition results for the %s division as of %a" 
     name print_date date

  let print_summary_header fmt () = 
    fprintf fmt "<!--#set var=\"title\" value=\"Summary\"-->";
    fprintf fmt "<!--#include file=\"smt-comp-prelude.shtml\" -->";
    fprintf fmt "<H1>Application Track</H1>";
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
                 <td>Order (parallel performance)</td>
                 </tr>
                 "

  let print_competition_header fmt () = 
    fprintf fmt 
      "<!--#set var=\"title\" value=\"Competition-Wide Scoring for the Application Track\"-->";
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
    try
    fprintf fmt "<p><B>Benchmarks in this division : %d</B> @." 
      (Hashtbl.length d.benchs);
    if d.complete then
      begin
	if d.winner_parall = "" then
	  fprintf fmt "<h3> Non-Competitive division </h3>"
	else
	  fprintf fmt 
	    "<h3> Winner : %s </h3>" 
	      (List.assoc d.winner_parall  solver_short_names);
	
	fprintf fmt "<h3>Result table<sup><a href=\"#fn1\">1</a></sup></h3>@."
      end
       with Not_found -> printf "Missing %s\n" (d.winner_parall);  raise Not_found

  let print_footer fmt () = 
    fprintf fmt "<p> <span id=\"fn\"> n. Non-competing. </span></p>";
    fprintf fmt "<p> <span id=\"fn1\"> 1. Scores are computed according to Section 7 of the rules. </span></p>";
    fprintf fmt "<!--#include virtual=\"smt-comp-postlude.shtml\" -->"


  let non_competitive_solver s = 
    s = "MathSAT" || 
    s = "Z3"

  let print_solver fmt s = 
    let b = non_competitive_solver s in
    let s = List.assoc s solver_short_names in
    if b then fprintf fmt "%s<SUP><a href=\"#fn\">n</a></SUP>" s 
    else fprintf fmt "%s" s

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
             <td colspan=\"4\" align=center>Parallel performance</td>
         </tr>
         <tr>
             <td>Error Score</td>
             <td>Correctly Solved Score</td>
             <td>avg. CPU time</td>
             <td>avg. WALL time</td>
         </tr>";
      List.iter 
	(fun (p, i) ->
	  fprintf fmt "<tr>\n";
	  fprintf fmt "<td>%a</td>\n" print_solver p;
	  fprintf fmt "<td>%d</td>" i.parall_perf.error;
	  fprintf fmt "<td>%d</td>" i.parall_perf.correct;
	  fprintf fmt "<td>%.2f</td>" i.parall_perf.cpu;
	  fprintf fmt "<td>%.2f</td>" i.parall_perf.wall;
	  fprintf fmt "</tr>"
	)
	(List.sort compare_solver_names d.table);
      fprintf fmt "</table>\n"
	
  let print_division d = 
    let res_name = results_dir^"/results-"^d.name^"-app.shtml" in
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
    let res_name = results_dir^"/results-"^name^"-app.shtml" in
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

  let print_solver_list fmt l = 
    let rec print = function
      | [] -> ()
      | [s] -> fprintf fmt "%a" print_solver s
      | s :: l -> fprintf fmt "%a; " print_solver s; print l
    in 
    print l

  let print_summary_division fmt d = 
    fprintf fmt "<tr>";
    fprintf fmt "<td rowspan=2><a href=\"results-%s-app.shtml\">%s</a></td>" 
      d.name d.name;
    fprintf fmt "<td rowspan=2>%d</td>" (Hashtbl.length d.provers);
    fprintf fmt "<td rowspan=2>%d</td>" (Hashtbl.length d.benchs);
    fprintf fmt "<td>%a</td>" print_solver_list d.order_parall;
    fprintf fmt "</tr>";
    fprintf fmt "<tr>";
    fprintf fmt "</tr>"

    
  let print_competition_wide_scoring fmt () = 
    let t_seq = Hashtbl.create 17 in
    let t_parall = Hashtbl.create 17 in

    Hashtbl.iter (fun _ d -> 
      let n = float (Hashtbl.length d.benchs) in
      if d.winner_parall <> "" then
	List.iter (fun (s, {seq_perf = sp; parall_perf=pp } ) -> 
	  let seq = 
	    if sp.error = 0 then 
	      let v = (float sp.correct) /. n in
	      v *. v
	    else -. 4.0 
	  in 
	  let parall = 
	    if pp.error = 0 then 
	      let v = (float pp.correct) /. n in
	      v *. v
	    else -. 4.0
	  in 
	  let old_seq = try Hashtbl.find t_seq s with Not_found -> 0. in
	  let old_parall = try Hashtbl.find t_parall s with Not_found -> 0. in
	  
	  let new_seq = (seq *. (log n) +. old_seq) in
	  let new_parall = (parall *. (log n) +. old_parall) in
	  
	  Hashtbl.replace t_seq s new_seq;
	  Hashtbl.replace t_parall s new_parall;
	) d.table
    ) divs;

    let l_seq = 
      let v = ref [] in Hashtbl.iter (fun x y -> v := (x,y) :: !v) t_seq; !v in
    let l_parall = 
      let v = ref [] in 
      Hashtbl.iter (fun x y -> v := (x,y) :: !v) t_parall; !v in

    let l_seq = List.sort (fun (_, a) (_, b) -> compare b a) l_seq in
    (*let l_seq = filter_solvers l_seq in*)

    let l_parall = List.sort (fun (_, a) (_, b) -> compare b a) l_parall in
    (*let l_parall = filter_solvers l_parall in*)

    fprintf fmt
      "<style> 
       table{ table-layout:fixed; border-collapse:collapse; 
              border-spacing:0; border:1px solid black; } 
             td { padding:0.5em; border: 1px solid black } </style>@.";

    fprintf fmt "<table>";
    fprintf fmt "<tr><td align=center><B>Sequential Performances</B></td><td align=center><B>Parallel Performances</B></td></tr>";
    fprintf fmt "<tr><td><table>\n";
    fprintf fmt 
      " <tr> <td>Rank</td> <td>Solver</td><td>Score</td></tr>";
    let cpt = ref 1 in
    List.iter 
      (fun (a, sa) ->  
	if test_filter a then
	  fprintf fmt "<tr><td> - </td><td>%s</td><td>%.2f</td></tr>"
	    (List.assoc a solver_short_names) sa
	else
	  begin
	    fprintf fmt "<tr><td>%d</td><td>%s</td><td>%.2f</td></tr>"
	      !cpt (List.assoc a solver_short_names) sa;
	    incr cpt
	  end) l_seq;
    fprintf fmt "</table></td>";

    
(*    fprintf fmt "<p><H1>Parallel Performances</H1>";*)
    fprintf fmt "<td><table>\n";
    fprintf fmt 
      " <tr> <td>Rank</td> <td>Solver</td><td>Score</td></tr>";
    let cpt = ref 1 in
    List.iter 
      (fun (a, sa) ->  
	if test_filter a then
	  fprintf fmt "<tr><td> - </td><td>%s</td><td>%.2f</td></tr>"
	    (List.assoc a solver_short_names) sa
	else
	  begin
	    fprintf fmt "<tr><td>%d</td><td>%s</td><td>%.2f</td></tr>"
	      !cpt (List.assoc a solver_short_names) sa;
	    incr cpt
	  end) l_parall;
    fprintf fmt "</table></td></table>"


end

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
  "pair id"; "benchmark"; "benchmark id"; "solver"; "solver id";
  "configuration"; "configuration id"; "status"; "cpu time"; "wallclock time";
  "memory usage"; "result"; "wrong-answers"; "correct-answers"]

let input_line ch = String.trim (input_line ch)

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
    wrong_answers = 0 ;
    correct_answers = 0 ;
  }
  
let split_csv_line s = 
  let l = split_csv s in
  let c = empty_csv_line () in
  let cols = col_names in
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
	  | "result" -> ()
	  | "wrong-answers" -> c.wrong_answers <- int_of_string v
	  | "correct-answers" -> c.correct_answers <- int_of_string v
	  | _ -> assert false
      ) 
      cols l;
    c
  with Invalid_argument _ -> 
    eprintf "error : cvs line << %s >> does not have the good structure@." s;
    exit 1

let raw_score c = 
  let error, correct, pending, cpu, wall = 
    match c.status with
      | Pending -> 0, 0, 1, c.cpu_time, c.wallclock_time
      (*| Timeout | Memout  -> 0, 0, 0, c.cpu_time, c.wallclock_time*)
      | Complete | Timeout | Memout-> 
	let e, n = if c.wrong_answers > 0 then 1, 0 else 0, c.correct_answers in
	e, n, 0, c.cpu_time, c.wallclock_time
  in
  { error = error; correct = correct; 
    wall = wall; cpu = cpu;
    pending = pending;
  }

let all_divisions = 
  let t = Hashtbl.create 17 in
  List.iter (fun d -> Hashtbl.add t d () )
    [ "ALIA"; "ANIA"; "AUFNIRA"; "BV"; "LIA"; "QF_ABV"; "QF_ALIA"; "QF_ANIA"; "QF_AUFBV"; "QF_AUFLIA"; "QF_BV"; 
      "QF_BVFP"; "QF_FP"; 
      "QF_LIA"; "QF_LRA"; "QF_NIA"; "QF_UFBV"; "QF_UFLIA"; "QF_UFLRA"; "QF_UFNIA";
      "UFLRA" ];
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
	    c.benchmark <- List.fold_right (fun x b -> x ^ b) (n :: s) "";
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

let compute_prover_perfs nb_benchs rsc_l = 
  let seq_perf = 
    ref { error = 0; correct = 0; wall = 0.; cpu = 0.; pending = 0 } in

  let parall_perf = 
    ref { error = 0; correct = 0; wall = 0.; cpu = 0.; pending = 0 } in

  let remaining = ref 0 in
  let not_solved = ref nb_benchs in
  List.iter 
    (fun sc -> 
      let seq_sc = seq_score sc in
      seq_perf := { error = !seq_perf.error + seq_sc.error;
		    correct = !seq_perf.correct + seq_sc.correct;
		    wall = !seq_perf.wall +. seq_sc.wall;
		    cpu = !seq_perf.cpu +. seq_sc.cpu;
		    pending = !seq_perf.pending + seq_sc.pending };

      parall_perf := { error = !parall_perf.error + sc.error;
		       correct = !parall_perf.correct + sc.correct;
		       wall = !parall_perf.wall +. sc.wall;
		       cpu = !parall_perf.cpu +. sc.cpu;
		       pending = !parall_perf.pending + sc.pending };

      remaining := !parall_perf.pending;
      not_solved := !not_solved - sc.error - sc.correct
    )
  rsc_l;
  { 
    seq_perf = !seq_perf; 
    parall_perf = !parall_perf;
    not_solved = !not_solved ;
    remaining = !remaining ;  
  }
    
let compare_parall (_, {parall_perf = p1}) (_, {parall_perf = p2}) =
  let c = compare p1.error p2.error in
  if c < 0 then -1
  else if c > 0 then 1
  else 
    let c = compare p1.correct p2.correct in
    if c > 0 then -1
    else if c < 0 then 1
    else 
      let c = compare p1.wall p2.wall in
      if c < 0 then -1
      else if c > 0 then 1
      else 
	let c = compare p1.cpu p2.cpu in
	if c < 0 then -1
	else if c > 0 then 1
	else c

let compare_seq (_, {seq_perf = p1}) (_, {seq_perf = p2}) =
  let c = compare p1.error p2.error in
  if c < 0 then -1
  else if c > 0 then 1
  else 
    let c = compare p1.correct p2.correct in
    if c > 0 then -1
    else if c < 0 then 1
    else 
      let c = compare p1.cpu p2.cpu in
      if c < 0 then -1
      else if c > 0 then 1
      else c
  
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

let confirm_winner s l = 
  let fs = Hashtbl.find families s in
  List.exists (fun (s',_) -> Hashtbl.find families s' <> fs) l

let compute_division_perfs d = 
  let nb_benchs = Hashtbl.length d.benchs in
  Hashtbl.iter 
    (fun p rsc_l -> 
      d.table <- (p, compute_prover_perfs nb_benchs rsc_l) :: d.table) 
    d.provers;
  
  d.order_seq <- List.map fst (List.sort compare_seq d.table);
  d.order_parall <- List.map fst (List.sort compare_parall d.table);
  
  let table = filter_solvers d.table in
  let w_par = 
    match List.sort compare_parall table with 
      | []
      | _::[] -> "No winner" 
      | (x, _) :: _ -> x 
  in
  d.winner_parall <- w_par 
  
let process_job job = 
  printf "Job : %s@." job;
  let job = jobs_dir^"/"^job in
  try
    let chan_job = open_in job in
    if not (check_header job chan_job) then
      eprintf "error : header is not valid -- I skip this job\n@."
    else
      begin
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
  let summary_name = results_dir^"/results-app-summary.shtml" in
    try
      let chan = open_out summary_name in
      let fmt = formatter_of_out_channel chan in
      Html.print_summary_header fmt ();
      Hashtbl.iter (fun _ d -> Html.print_summary_division fmt d) divs;
      Html.print_summary_footer fmt ();
      fprintf fmt "@.";
      printf "@. Summary : OK\n@.";
      close_out chan
    with Sys_error m -> 
      eprintf "error : cannot open %s\n %s\n@." summary_name m;
      exit 1

let competition_wide_scoring () = 
  let compet_name = results_dir^"/results-competition-app.shtml" in
  try
    let chan = open_out compet_name in
    let fmt = formatter_of_out_channel chan in
      Html.print_competition_header fmt ();
      Html.print_competition_wide_scoring fmt ();
      Html.print_competition_footer fmt ();
    printf "@. Competition Wide Scoring : OK\n@.";
    close_out chan
  with Sys_error m -> 
    eprintf "error : cannot open %s\n %s\n@." compet_name m;
    exit 1

let () = 
  let jobs = Sys.readdir jobs_dir in
  Array.iter process_job jobs;
  (*let job = (Sys.readdir jobs_dir).(0) in
  process_job job;*)
  Hashtbl.iter (fun n _ -> Html.print_division_not_started n) all_divisions;
  summary ()
(*  competition_wide_scoring ()*)

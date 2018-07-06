open Format
open Scoring
open Html

let division_list = ref []

let non_competing_division d = 
    d = "QF_SLIA"

 
let split_csv s = Str.split (Str.regexp ",") s
  
let status_of_string s = 
  match s with
    | "complete" -> Complete 
    | "pending submission" -> Pending 
    | "run script error" -> Pending 
    | "enqueued" -> Pending
    | "timeout (cpu)" | "timeout (wallclock)" -> Timeout
    | "memout" -> Memout
    | _ -> 
      eprintf "error : cannot convert status %s@." s;
      exit 1

let result_of_string s = 
  match s with
    | "sat" -> Sat 
    | "unsat" -> Unsat 
    | "starexec-unknown" | "--" -> Unknown
    | _ -> 
      eprintf "error : cannot convert result %s@." s;
      exit 1

let col_names = [ 
  "pair id"; "benchmark"; "benchmark id"; "solver"; "solver id";
  "configuration"; "configuration id"; "status"; "cpu time"; "wallclock time";
  "memory usage"; "result"; "expected" ]

let col_names_incomplete = [ 
  "pair id"; "benchmark"; "benchmark id"; "solver"; "solver id";
  "configuration"; "configuration id"; "status"; "cpu time"; "wallclock time";
  "memory usage"; "result" ]


let input_line ch = String.trim (input_line ch)

let check_header job ch = 
  try
    let s = input_line ch in
    let l = (split_csv s) in
    if List.length l = List.length col_names - 1 then 
      List.for_all2 (fun c1 c2 -> c1 = c2)  l col_names_incomplete
    else 
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
    result = Unknown ;
    expected = Unknown ;
  }
  
let split_csv_line s = 
  let l = split_csv s in
  let c = empty_csv_line () in
  let cols = 
    if List.length l = List.length col_names - 1 then col_names_incomplete
    else col_names
  in
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
	  | _ -> printf "ERROR here"; assert false
      ) 
      cols l;
    c
  with Invalid_argument _ -> 
    eprintf "error : cvs line << %s >> does not have the good structure@." s;
    exit 1

let raw_score c = 
  let error, correct, pending, cpu, wall = 
    match c.status, c.result with
      | Pending, _ -> 0, 0, 1, c.cpu_time, c.wallclock_time

      | _, r when (r <> Unknown && (r = c.expected || c.expected = Unknown)) -> 
	0, 1, 0, c.cpu_time, c.wallclock_time

      | _, cr when (cr <> Unknown)  ->
	1, 0, 0, c.cpu_time, c.wallclock_time

      | _ -> 0, 0, 0, c.cpu_time, c.wallclock_time

  in
  { error = error; correct = correct; 
    wall = wall; cpu = cpu;
    pending = pending; 
    raw_bench = c.benchmark}

let all_divisions = 
  let t = Hashtbl.create 17 in
  List.iter (fun d -> Hashtbl.add t d () )
    [ "ABVFP"; "ALIA"; "AUFBVDTLIA"; "AUFDTLIA";"AUFLIA"; "AUFLIRA"; "AUFNIRA"; "BV"; "BVFP"; "FP"; "LIA"; "LRA"; "NIA"; "NRA";
      "QF_ABV"; "QF_ABVFP"; "QF_ALIA"; "QF_ANIA"; "QF_AUFBV"; "QF_AUFLIA"; "QF_AUFNIA";
      "QF_AX"; "QF_BV"; "QF_BVFP"; "QF_DT"; "QF_FP"; "QF_IDL"; "QF_LIA"; "QF_LIRA";
      "QF_LRA"; "QF_NIA"; "QF_NIRA"; "QF_NRA"; "QF_RDL"; "QF_SLIA"; "QF_UF"; "QF_UFBV";
      "QF_UFIDL"; "QF_UFLIA"; "QF_UFLRA"; "QF_UFNIA"; "QF_UFNRA"; "UF"; "UFBV"; "UFDT"; "UFDTLIA";
      "UFIDL"; "UFLIA"; "UFLRA"; "UFNIA" ];
  t

let family_of c = 
  let b = Str.split (Str.regexp "/") c in
  let rec concat = function
    | [] -> printf "ERROR in family_of"; assert false
    | [x] -> ""
    | x :: s -> x^"/"^(concat s)
  in 
  concat b

let get_unsound cin =
  let unsound = Hashtbl.create 1007 in
  (try
    while true do
      let c = split_csv_line (input_line cin) in 
      if (not (Hashtbl.mem unsound c.solver)) && 
         c.expected <> Unknown && c.result <> Unknown && c.expected <> c.result then
        begin
          print_string (c.solver^" is unsound\n");
          Hashtbl.add unsound c.solver ()
        end
    done
  with End_of_file -> ());
  unsound

let init_division cin unsound = 
  let visited = Hashtbl.create 1007 in
  let families = Hashtbl.create 1007 in
  let unknown = Hashtbl.create 1007 in
  let clash = Hashtbl.create 1007 in
  (try
     while true do 
       let c = split_csv_line (input_line cin) in
       if not (Hashtbl.mem unsound c.solver) then
       let clashed = ref (Hashtbl.mem clash c.benchmark) in
       if not !clashed && c.expected = Unknown && c.result <> Unknown then
        if not (Hashtbl.mem unknown c.benchmark) then
          Hashtbl.add unknown c.benchmark c.result
        else
          if c.result <> (Hashtbl.find unknown c.benchmark) then
          begin
            print_string ("Clash in "^c.benchmark^"\n");
            Hashtbl.add clash c.benchmark ();
            clashed := true;
            if (Hashtbl.mem visited c.benchmark) then
              let f = family_of c.benchmark in
              let n = Hashtbl.find families f in
              Hashtbl.replace families f (n-1);  
          end;
       if not !clashed && not (Hashtbl.mem visited c.benchmark) then
	 begin
	   Hashtbl.add visited c.benchmark ();
	   let f = family_of c.benchmark in
	   let n = try Hashtbl.find families f with Not_found -> 0 in
	   Hashtbl.replace families f (n + 1);
	 end
     done 
   with End_of_file -> ());
    print_string ((string_of_int (Hashtbl.length clash))^" clashes\n"); 
    {
      name = "";
      nb_pairs = 0;
      nb_benchs = 0;
      complete = true;
      nb_pendings = 0;
      winner_seq = "";
      winner_parall = "";
      order_seq = [];
      order_parall = [];
      provers = Hashtbl.create 7;
      benchs = Hashtbl.create 1007;
      families = families;
      clash = clash;
      table = [];
      competitive_seq = true;
      competitive_parall = true;
    }


let update_division d c = 

  let name = List.hd (Str.split (Str.regexp "/") c.benchmark) in
  if d.name = "" then 
    begin
      d.name <- name;
      print_string ("Processing "^d.name^"\n");
    end;
  if d.name <> name then print_string (name^" and "^d.name);
  assert (d.name = name);

  Hashtbl.remove all_divisions d.name;

  if not (Hashtbl.mem d.benchs c.benchmark) then
    begin
      Hashtbl.add d.benchs c.benchmark c.expected;
      d.nb_benchs <- d.nb_benchs + 1;
    end;
  assert (c.expected = Hashtbl.find d.benchs c.benchmark);

  d.nb_pairs <- d.nb_pairs + 1;

  d.nb_pendings <- d.nb_pendings + (if c.status = Pending then 1 else 0);

  d.complete <- d.complete && (c.status <> Pending);

  let raw = raw_score c in
  let l = try Hashtbl.find d.provers c.solver with Not_found -> [] in
  Hashtbl.replace d.provers c.solver (raw::l)

let run_division job chan_job = 
  let unsound = get_unsound chan_job in
  seek_in chan_job 0;
  ignore (check_header job chan_job);
  let d = init_division chan_job unsound in
  seek_in chan_job 0;
  ignore (check_header job chan_job);
  (try
     while true do 
       let cvs_line = split_csv_line (input_line chan_job) in
       if not (Hashtbl.mem d.clash cvs_line.benchmark) then 
         update_division d cvs_line
     done 
   with End_of_file -> ());
  d

let seq_score sc = 
  if sc.cpu > wall then
    { sc with error = 0; correct = 0; cpu = min sc.cpu wall }
  else
    { sc with cpu = min sc.cpu wall }

let alpha_b d b = 
  let fb = (float (Hashtbl.find d.families (family_of b))) in
  (1. +. log fb) /. fb

let compute_prover_perfs d rsc_l = 
  let nb_benchs = Hashtbl.length d.benchs in
  let sum_alpha_b = 
    Hashtbl.fold (fun b _ acc -> acc +. alpha_b d b) d.benchs 0. in

  let sp = 
    { w_error = 0.; w_correct = 0.; w_wall = 0.; w_cpu = 0.; w_pending = 0 } 
  in
  let pp = 
    { w_error = 0.; w_correct = 0.; w_wall = 0.; w_cpu = 0.; w_pending = 0 } 
  in
  let remaining = ref 0 in
  let not_solved = ref nb_benchs in
  let not_solved_seq = ref nb_benchs in
  let solved = ref 0 in
  let solved_seq = ref 0 in
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

      remaining := pp.w_pending;
      solved := !solved + sc.correct;
      solved_seq := !solved + seq_sc.correct;
      not_solved := !not_solved - sc.correct;
      not_solved_seq := !not_solved_seq - seq_sc.correct
    )
  rsc_l;
  (* Tjark's fix *)
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
    not_solved_seq = !not_solved_seq ;
    solved = !solved ;
    solved_seq = !solved_seq ;
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
(*
  let x = (print_string ((Printf.sprintf "%.15f" p1.w_correct) ^ " " ^ (Printf.sprintf "%.15f" p2.w_correct) ^ "\n")); 0 in 
  let y = (print_string ((string_of_int (hackfp p1.w_correct)) ^ " " ^ (string_of_int (hackfp p2.w_correct)) ^ "\n")); 0 in 
*)
  let c = compare_perf p1 p2 in
  if c != 0 then c 
  else
      if p1.w_cpu < p2.w_cpu then -1
      else if p1.w_cpu > p2.w_cpu then 1
      else 0
  
let families = 
  let t = Hashtbl.create 20 in
  List.iter (fun (s,f) -> Hashtbl.add t s f)
    ["CVC3", 1 ; 
     "CVC4-master-2015-06-15-9b32405-main", 1; 
     "CVC4-experimental-2015-06-15-ff5745a-main", 1;
     "Z3-unstable", 2; 
     "z3 4.4.0", 2; 
     "z3-ijcar14", 2;
     "AProVE NIA 2014", 3;
     "stp-cryptominisat4", 4;
     "stp-cmsat4-v15", 4;
     "stp-cmsat4-mt-v15", 4;
     "raSAT", 5;
     "SMTInterpol v2.1-206-g86e9531", 6;
     "stp-minisat-v15", 7;
     "veriT", 8;
     "MathSat 5.3.6 main", 9;
     "OpenSMT2-parallel", 10;
     "OpenSMT2", 10;
     "Yices", 11;
     "Yices2-NL", 11;
     "Boolector SMT15 QF_AUFBV final", 12;
     "Boolector SMT15 QF_BV final", 12;
     "SMT-RAT-final", 13;
     "SMT-RAT-NIA-Parallel-final", 13
    ];
  t

let confirm_winner s l = 
  let fs = Hashtbl.find families s in
  List.exists (fun (s',_) -> Hashtbl.find families s' <> fs) l

let compute_division_perfs d = 
  Hashtbl.iter 
    (fun p rsc_l -> 
      d.table <- (p, compute_prover_perfs d rsc_l) :: d.table) 
    d.provers;
  
  d.order_seq <- List.map fst (List.sort compare_seq d.table);
  d.order_parall <- List.map fst (List.sort compare_parall d.table);

  let table = competitive_solvers_only d.table in
  let stable_seq = List.sort compare_seq table in
  let stable_par = List.sort compare_parall table in
  let w_seq = 
    if List.length stable_seq < 2 || (non_competing_division d.name) 
    then (d.competitive_seq <- false; "No winner")
    else fst (List.hd stable_seq) in
  let w_par = 
    if List.length stable_seq < 2 || (non_competing_division d.name)
    then 
      (d.competitive_parall <- false; "No winner" )
    else fst (List.hd stable_par) in
  print_string (d.name^" "^w_seq^"\n");
  d.winner_seq <- w_seq (*if confirm_winner w_seq table then w_seq else ""*);
  d.winner_parall <- w_par (*if confirm_winner w_par table then w_par else ""*)

let process_job job = 
  printf "Job : %s@." job;
  let job = jobs_dir^"/"^job in
  try
    let chan_job = open_in job in
    if not (check_header job chan_job) then
      eprintf "error : header is not valid -- I skip this job\n@."
    else
      let d = run_division job chan_job in
      compute_division_perfs d;
      printf "Computed division perfs\n";
      Html.print_division d;
      printf "@. HTML generated : OK\n@.";
      division_list := d :: !division_list;
      close_in chan_job
  with Sys_error m -> 
    eprintf "error : cannot open %s \n %s\n@." job m;
    exit 1

let summary () = 
  let summary_name = results_dir^"/results-summary.shtml" in
    try
      let chan = open_out summary_name in
      let fmt = formatter_of_out_channel chan in
      Html.print_summary_header fmt ();
      let divs = List.sort compare !division_list in
      List.iter (Html.print_summary_division fmt) divs;
      Html.print_summary_footer fmt ();
      fprintf fmt "@.";
      printf "@. Summary : OK\n@.";
      close_out chan
    with Sys_error m -> 
      eprintf "error : cannot open %s\n %s\n@." summary_name m;
      exit 1

let competition_wide_scoring () = 
  let compet_name = results_dir^"/results-competition-main.shtml" in
  try
    let chan = open_out compet_name in
    let fmt = formatter_of_out_channel chan in
      Html.print_competition_header fmt ();
      Html.print_competition_wide_scoring fmt !division_list;
      Html.print_competition_footer fmt ();
    printf "@. Competition Wide Scoring : OK\n@.";
    close_out chan
  with Sys_error m -> 
    eprintf "error : cannot open %s\n %s\n@." compet_name m;
    exit 1
      
let () = 
  let jobs = Sys.readdir jobs_dir in
  Array.iter process_job jobs;
  Hashtbl.iter (fun n _ -> Html.print_division_not_started n) all_divisions;
  summary ();
  competition_wide_scoring ()

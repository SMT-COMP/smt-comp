open Format
open Scoring

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
  fprintf fmt "<!--#set var=\"title\" value=\" %s (Main Track)\"-->" name;
  fprintf fmt "<!--#include file=\"smt-comp-prelude.shtml\" -->";
  fprintf fmt "<p>Competition results for the %s division as of %a" 
    name print_date date

let print_summary_header fmt () = 
  fprintf fmt "<!--#set var=\"title\" value=\"Summary\"-->";
  fprintf fmt "<!--#include file=\"smt-comp-prelude.shtml\" -->";
  fprintf fmt "<H1>Main Track</H1>";
  fprintf fmt "<p>Competition results as of %a" print_date date;
  fprintf fmt 
    "<style> table{ table-layout:fixed; border-collapse:collapse; 
                      border-spacing:0; border:1px solid black; } 
                      td { padding:0.25em; border: 1px solid black } </style>";
  fprintf fmt "<p><table>
                 <tr>
                 <td rowspan=2>Logic</td>
                 <td rowspan=2>Solvers</td>
                 <td rowspan=2>Benchmarks</td>
                 <td rowspan=2># pairs Complete</td>
                 <td rowspan=2>%%\n Complete</td>
                 <td>Order (sequential performance)</td>
                 </tr>
                 <tr>
                 <td>Order (parallel performance)</td>
                 </tr>
                 "
let print_competition_header fmt () = 
  fprintf fmt 
    "<!--#set var=\"title\" value=\"Competition-Wide Scoring for the Main Track\"-->";
  fprintf fmt "<!--#include file=\"smt-comp-prelude.shtml\" -->";
  fprintf fmt "<p>Competition results as of %a" print_date date;
  fprintf fmt "<p>"

let print_summary_footer fmt () = 
  fprintf fmt "</table><p>";
  fprintf fmt "<p> <span id=\"fn\"> n. Non-competing. </span></p>";
  fprintf fmt "<!--#include virtual=\"smt-comp-postlude.shtml\" -->"

let print_competition_footer fmt () = 
  fprintf fmt "<p> <span id=\"fn\"> n. Non-competing. </span></p>";
  fprintf fmt "<!--#include virtual=\"smt-comp-postlude.shtml\" -->"

let print_header_results fmt d = 
  fprintf fmt "<p><B>Benchmarks in this division : %d</B> @." d.nb_benchs;
  if d.complete then
    begin
      if d.winner_seq = "No winner" then
	fprintf fmt "<h3> Non-Competitive division </h3>"
      else
	begin
    fprintf fmt "<h3>Winners: </h3>\n";
	  fprintf fmt "<table class=\"result\">\n";
    fprintf fmt "<tr>";
    fprintf fmt "<td>Sequential Performances</td>";
    fprintf fmt "<td>Parallel Performances</td>";
    fprintf fmt "</tr>\n";
	  fprintf fmt 
	    "<tr><td>%s</td><td>%s</td>" 
	    (short_name d.winner_seq)
	    (short_name d.winner_parall);
	  
	  fprintf fmt "</table><p><p>";
	  
	  fprintf fmt "<h3>Result table<sup><a href=\"#fn1\">1</a></sup></h3>@.";
	end
    end

let print_footer fmt () = 
  fprintf fmt "<p> <span id=\"fn\"> n. Non-competing. </span></p>";
  fprintf fmt "<p> <span id=\"fn1\"> 1. Scores are computed according to Section 7 of the rules. </span></p>";
  fprintf fmt "<!--#include virtual=\"smt-comp-postlude.shtml\" -->"

let print_solver fmt s = 
  let b = non_competitive_solver s in
  let s = List.assoc s solver_short_names in
  if b then fprintf fmt "%s<SUP><a href=\"#fn\">n</a></SUP>" s 
  else fprintf fmt "%s" s

let compare_solver_names (n1, _) (n2, _) =
  try
    compare 
      (List.assoc n1 solver_short_names) (List.assoc n2 solver_short_names)
  with Not_found -> 
    eprintf "error : compare_solver_names not found %s | %s@." n1 n2; raise Not_found 

let print_prover_line fmt d = 
  fprintf fmt "<h4>Sequential Performance</h4>\n\n";
  fprintf fmt "<table class=\"result sorted\">\n";
  fprintf fmt "<tr>\n";
  fprintf fmt "  <th>Solver</th>\n";
  fprintf fmt "  <th>Error Score</th>\n";
  fprintf fmt "  <th>Correctly Solved Score</th>\n";
  fprintf fmt "  <th>CPU time Score</th>\n";
  fprintf fmt "  <th>Solved</th>\n";
  fprintf fmt "  <th>Unsolved</th>\n";
  fprintf fmt "</tr>";
  List.iter 
    (fun (p, i) ->
      fprintf fmt "<tr>\n";
      fprintf fmt "  <td>%a</td>\n" print_solver p;

      fprintf fmt "  <td>%.3f</td>\n" i.seq_perf.w_error;
      fprintf fmt "  <td>%.3f</td>\n" i.seq_perf.w_correct;
      fprintf fmt "  <td>%.3f</td>\n" i.seq_perf.w_cpu;

      fprintf fmt "<td>%d</td>\n" i.solved_seq;
      fprintf fmt "<td>%d</td>\n" i.not_solved_seq;

      fprintf fmt "</tr>"
    )
    (List.sort compare_solver_names d.table);
  fprintf fmt "</table>\n";

  fprintf fmt "<h4>Parallel Performance</h4>\n\n";
  fprintf fmt "<table class=\"result sorted\">\n";
  fprintf fmt "<tr>\n";
  fprintf fmt "  <th>Solver</th>\n";
  fprintf fmt "  <th>Error Score</th>\n";
  fprintf fmt "  <th>Correctly Solved Score</th>\n";
  fprintf fmt "  <th>CPU time Score</th>\n";
  fprintf fmt "  <th>WALL time Score</th>\n";
  fprintf fmt "  <th>Solved</th>\n" ;
  fprintf fmt "  <th>Unsolved</th>\n" ;
  fprintf fmt "</tr>";
  List.iter 
    (fun (p, i) ->
      fprintf fmt "<tr>\n";
      fprintf fmt "  <td>%a</td>\n" print_solver p;
    
      fprintf fmt "<td>%.3f</td>" i.parall_perf.w_error;
      fprintf fmt "<td>%.3f</td>" i.parall_perf.w_correct;
      fprintf fmt "<td>%.3f</td>" i.parall_perf.w_cpu;
      fprintf fmt "<td>%.3f</td>" i.parall_perf.w_wall;

      fprintf fmt "<td>%d</td>" i.solved;
      fprintf fmt "<td>%d</td>" i.not_solved;

      fprintf fmt "</tr>"
    )
    (List.sort compare_solver_names d.table);
  fprintf fmt "</table>\n"

let print_division d  = 
  printf "HERE\n";
  let res_name = results_dir^"/results-"^d.name^".shtml" in
  try
    let chan = open_out res_name in
    let fmt = formatter_of_out_channel chan in
    print_header fmt d.name;
    print_header_results fmt d;
    print_prover_line fmt d;
    print_footer fmt ();
    fprintf fmt "@.";
    let swin = 
      match (List.nth_opt (List.filter (fun (s,t) -> s=d.winner_seq) d.table) 0) 
      with Some (x,y) -> y.seq_perf.w_correct | None -> 0.0 
    in
    print_string ("SEQ WINNER,"^d.name^","^d.winner_seq^"\n");(*","^string_of_float(swin)^"\n");*)
    let pwin =
      match (List.nth_opt (List.filter (fun (s,t) -> s=d.winner_parall) d.table) 0)
      with Some (x,y) -> y.parall_perf.w_correct | None -> 0.0
    in

    print_string ("PAR WINNER,"^d.name^","^d.winner_parall^"\n");(*","^string_of_float(pwin)^"\n");*)
    close_out chan;
  with Sys_error m -> 
    eprintf "error : cannot open %s\n %s\n@." res_name m;
    exit 1

let print_division_not_started name = 
  let res_name = results_dir^"/results-"^name^".shtml" in
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
  if d.winner_seq = "" then
    fprintf fmt "<tr bgcolor=#E4E4E4>"
  else fprintf fmt "<tr>";
  fprintf fmt "<td rowspan=4><a href=\"results-%s.shtml\">%s</a></td>" 
    d.name d.name;
  fprintf fmt "<td rowspan=4>%d</td>" (Hashtbl.length d.provers);
  fprintf fmt "<td rowspan=4>%d</td>" (Hashtbl.length d.benchs);
  fprintf fmt "<td rowspan=4>%d</td>" (d.nb_pairs - d.nb_pendings);
  let p = float (d.nb_pairs - d.nb_pendings) *. 100. /. (float d.nb_pairs) in
  fprintf fmt "<td rowspan=4>%d</td>" (int_of_float p); 
  fprintf fmt "<td>%a</td>" print_solver_list d.order_seq;
  fprintf fmt "</tr>";
  if d.winner_seq="" then
    fprintf fmt "<tr bgcolor=#E4E4E4>"
  else fprintf fmt "<tr>";
  fprintf fmt "<td>%a</td>" print_solver_list d.order_parall;
  fprintf fmt "</tr>";

  if d.winner_seq="" then
    fprintf fmt "<tr bgcolor=#E4E4E4>"
  else fprintf fmt "<tr>";
  fprintf fmt "</tr>";

  if d.winner_seq="" then
    fprintf fmt "<tr bgcolor=#E4E4E4>"
  else fprintf fmt "<tr>";
  fprintf fmt "</tr>"

let print_competition_wide_scoring fmt divs = 
  let t_seq = Hashtbl.create 17 in
  let t_parall = Hashtbl.create 17 in
  List.iter (fun d -> 
    let n = float (Hashtbl.length d.benchs) in
    if d.competitive_seq then
      List.iter 
	(fun (s, {seq_perf = sp; parall_perf=pp } ) -> 
	  let seq = 
	    if sp.w_error = 0. then 
	      let v = sp.w_correct /. n in
	      v *. v
	    else -4.
	  in 
	  let parall = 
	    if pp.w_error = 0. then 
	      let v = pp.w_correct /. n in
	      v *. v
	    else -4.  
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
  (*let l_seq = competitive_solvers_only l_seq in*)

  let l_parall = List.sort (fun (_, a) (_, b) -> compare b a) l_parall in
  (*let l_parall = competitive_solvers_only l_parall in*)

  fprintf fmt
    "<style> 
       table{ table-layout:fixed; border-collapse:collapse; 
              border-spacing:0; border:1px solid black; } 
             td { padding:0.5em; border: 1px solid black } </style>@.";

  fprintf fmt "<table>";
  fprintf fmt "<tr><td align=center><B>Sequential Performances</B></td><td align=center><B>Parallel Performances</B></td>
</tr>";
  fprintf fmt "<tr><td><table>\n";
  fprintf fmt 
    " <tr> <td>Rank</td> <td>Solver</td><td>Score</td></tr>";
  let cpt = ref 1 in
  List.iter 
    (fun (a, sa) ->  
      if non_competitive_solver a then
	fprintf fmt "<tr><td> - </td><td>%s<SUP><a href=\"#fn\">n</a></SUP></td><td>%.2f</td></tr>"
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
      if non_competitive_solver a then
	fprintf fmt "<tr><td> - </td><td>%s<SUP><a href=\"#fn\">n</a></SUP></td><td>%.2f</td></tr>"
	  (List.assoc a solver_short_names) sa
      else
	begin
	  fprintf fmt "<tr><td>%d</td><td>%s</td><td>%.2f</td></tr>"
	    !cpt (List.assoc a solver_short_names) sa;
	  incr cpt
	end) l_parall;
  fprintf fmt "</table></td>";
  fprintf fmt "</table>"

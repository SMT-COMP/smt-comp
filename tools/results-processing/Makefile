OCAMLC  = ocamlc
OCAMLOPT= ocamlopt
OCAMLDEP= ocamldep

OBJ     = scoring html competition
CMO     := $(addsuffix .cmo, $(OBJ))
CMX     := $(addsuffix .cmx, $(OBJ))

EXE = competition

all: $(EXE).byte $(EXE)

# Generic rules
###############

.SUFFIXES: .ml .mli .mll .cmo .cmi .cmx .html .o .tex .dvi .ps

.mli.cmi:
	$(OCAMLC) -c $<

.mll.ml:
	$(OCAMLLEX) $<

.ml.cmo:
	$(OCAMLC) -annot -c $<

.ml.o:
	$(OCAMLOPT) -annot -c $<

.ml.cmx:
	$(OCAMLOPT) -annot -c $<

$(EXE).byte: $(CMO)
	$(OCAMLC) -o $(EXE).byte str.cma unix.cma $(CMO) 

$(EXE) : $(CMX) 
	$(OCAMLOPT) -o $(EXE) str.cmxa unix.cmxa $(CMX) 

app: 
	$(OCAMLC) -g -annot -c compute_app_html.ml
	$(OCAMLC) -g -o compute_app_html.byte str.cma unix.cma compute_app_html.cmo
	$(OCAMLOPT) -g -annot -c compute_app_html.ml
	$(OCAMLOPT) -g -o compute_app_html str.cmxa unix.cmxa compute_app_html.cmx

ucore: 
	$(OCAMLC) -annot -c compute_ucore_html.ml
	$(OCAMLC) -o compute_ucore_html.byte str.cma unix.cma compute_ucore_html.cmo
	$(OCAMLOPT) -annot -c compute_ucore_html.ml
	$(OCAMLOPT) -o compute_ucore_html str.cmxa unix.cmxa compute_ucore_html.cmx

exp: 
	$(OCAMLC) -annot -c compute_exp_html.ml
	$(OCAMLC) -o compute_exp_html.byte str.cma unix.cma compute_exp_html.cmo
	$(OCAMLOPT) -annot -c compute_exp_html.ml
	$(OCAMLOPT) -o compute_exp_html str.cmxa unix.cmxa compute_exp_html.cmx 

# Cleaning
##########

clean:
	rm -f *~ *.log *.aux *.cm* *.o

dist-clean: clean
	rm -f $(EXE) $(EXE).byte

# Depend
########

depend .depend: $(GENFILES)
	rm -f .depend
	$(OCAMLDEP) *.mli *.ml *.mll > .depend

include .depend


# StarExec-Utilities
Utilities written to interact with the [Star-Exec](http://www.starexec.org "Star-Exec web site") logic solving service.

- filter-unkown.py: reads a XML file for a space with benchmarks and outputs a XML to create a copy of that space with some benchmarks removed. Removed benchmarks are those that have their 'status' attribute set to 'unknown' as well as those that have a 'contains-bv-partial-func' attribute set to 'true'.

- detect-first-check-unknown.sh: outputs to standard output all paths to files in the current directory (recursively) such that the first 'check-sat' command is not immediately preceded by a 'set-info :status sat|unsat' command.

- detect-some-check-unknown.sh: outputs to standard output all paths to files in the current directory (recursively) such that some 'check-sat' command is not immediately preceded by a 'set-info :status sat|unsat' command.

#!/usr/bin/env gnuplot
# run this to create difficultyplot.eps

set xlabel 'Average solver execution time (in minutes)'
set ylabel 'Assigned difficulty'
set key top left
set terminal postscript eps enhanced monochrome
set output "difficultyplot.eps"
f(x) = (5*log(1+x*x))/log(1+30*30)
finv(x) = sqrt(exp((x*log(1+30*30)/5))-1)
#x=.5; set label sprintf("A = %g, d = %.2f", x, f(x)) at x,f(x) left point offset .7,-.2 enhanced
#x=1; set label sprintf("A = %g, d = %.2f", x, f(x)) at x,f(x) left point offset .7,-.2 enhanced
#x=1.5; set label sprintf("A = %g, d = %.2f", x, f(x)) at x,f(x) left point offset .7,-.2 enhanced
#x=2; set label sprintf("A = %g, d = %.2f", x, f(x)) at x,f(x) left point offset .7,-.2 enhanced
#x=3; set label sprintf("A = %g, d = %.2f", x, f(x)) at x,f(x) left point offset .7,-.2 enhanced
#x=4; set label sprintf("A = %g, d = %.2f", x, f(x)) at x,f(x) left point offset .7,-.2 enhanced
#x=5; set label sprintf("A = %g, d = %.2f", x, f(x)) at x,f(x) left point offset .7,-.2 enhanced
#x=10; set label sprintf("A = %g, d = %.2f", x, f(x)) at x,f(x) left point offset .6,-.3 enhanced
#x=15; set label sprintf("A = %g, d = %.2f", x, f(x)) at x,f(x) right point offset -1.2,.3 enhanced
#x=20; set label sprintf("A = %g, d = %.2f", x, f(x)) at x,f(x) right point offset -1.2,.3 enhanced
#x=25; set label sprintf("A = %g, d = %.2f", x, f(x)) at x,f(x) right point offset -1.2,.3 enhanced
#x=30; set label sprintf("A = %g, d = %.2f", x, f(x)) at x,f(x) right point offset -1.2,.3 enhanced

x=1; set label sprintf("A = %.2g, d = %.2f", finv(x), x) at finv(x),x left  point offset .7,-.2 enhanced
x=2; set label sprintf("A = %.2g, d = %.2f", finv(x), x) at finv(x),x left  point offset .7,-.2 enhanced
x=3; set label sprintf("A = %.2g, d = %.2f", finv(x), x) at finv(x),x left  point offset .7,-.2 enhanced
x=4; set label sprintf("A = %.2g, d = %.2f", finv(x), x) at finv(x),x right point offset -1.2,.3 enhanced
x=5; set label sprintf("A = %.2g, d = %.2f", finv(x), x) at finv(x),x right point offset -1.2,.3 enhanced

plot [0:30] f(x) title "(5 * ln(1 + x^2)) / ln(1 + 30^2)"


set title "Robot commands movement"
set xlabel "Time (ms)"
set ylabel "Command (PWM)"
set grid

plot "debug.data" u 1:10 w line title "Translation P",\
"debug.data" u 1:11 w line title "Translation I",\
"debug.data" u 1:12 w line title "Translation D",\
"debug.data" u 1:13 w line title "Rotation P",\
"debug.data" u 1:14 w line title "Rotation I",\
"debug.data" u 1:15 w line title "Rotation D",\

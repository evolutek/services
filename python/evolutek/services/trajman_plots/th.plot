set title "Rotation `cat rotpid.data`"
set xlabel "Time (ms)"
set ylabel "Position (rad)"
set grid

plot "debug.data" u 1:4 w line title "Theta position",\
"debug.data" u 1:7 w line title "Theta wanted position",\
"debug.data" u 1:9 w line title "Rotation speed"

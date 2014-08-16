set title "Robot th movement"
set xlabel "Time (ms)"
set ylabel "Position (mm)"
set grid
plot "fthmove.data" title "Movement" w line, "fthcommand.data" title "Command" w line

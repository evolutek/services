set title "Robot y movement"
set xlabel "Time (ms)"
set ylabel "Position (mm)"
set y2label "Speed (mm/s)"
set grid
plot "fymove.data" title "Movement" w line, "fycommand.data" title "Command" w line, "fspeedtr.data" axes x1y2 title "Speed" w line

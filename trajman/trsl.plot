set title "Translation `cat trslpid.data`"
set xlabel "Time (ms)"
set ylabel "Position (mm)"
set y2label "Speed (m/s)"
set y2tics
set grid

plot "debug.data"  using 1:2 w line title "X position",\
"debug.data" using 1:5 w line title "X wanted position",\
"debug.data" using 1:8 w line title "Speed" axes x1y2,\
"debug.data" u 1:3 w line title "Y position",\
"debug.data" u 1:6 w line title "Y wanted position"


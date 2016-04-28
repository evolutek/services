set title "Position on the world"
set xlabel "X position (ms)"
set ylabel "Y position (mm)"
set y2tics
set grid
set size ratio -1
set size square

plot "debug.data" using 2:3 w line title "Position on the world",\
"debug.data" using 5:6 w line title "Wanted position"

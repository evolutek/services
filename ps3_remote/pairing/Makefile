CFILES=usb_pairing.c
CC=gcc
CFLAGS=-Wall -std=gnu99 -O2
LDFLAGS=-lusb
EXE="pairing"
O=${CFILES:.c=.o}

${EXE}: clean ${O}
	${CC} -o $@ ${O} ${CFLAGS} ${LDFLAGS}

.SUFFIXES: .c .o
.c.o:
	${CC} -c $< ${CFLAGS}

clean:
	rm -vf *.o
	rm -vf ${EXE}

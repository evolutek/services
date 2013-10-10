CFILES = blueshock.c
OBJ = ${CFILES:.c=.o}
CC = gcc
CFLAGS = -Wall -std=gnu99 -O2
LDFLAGS = -lpthread
EXE = libblueshock

all: $(OBJ)
	ar csr $(EXE).a $(OBJ)

clean:
	@rm -rf $(OBJ)
	@rm -rf $(EXE).a

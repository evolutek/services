CC = gcc
CFILES = src/main.c
OBJ = $(CFILES:.c=.o)
CFLAGS = -Wall -std=gnu99 -Iblueshock/include/
LDFLAGS = -lpthread -lclas -Lblueshock/ -lblueshock
BIN = ps3_remote

all: gen_lib $(OBJ)
	$(CC) $(OBJ) $(LDFLAGS) -o $(BIN)

gen_lib:
	make -C blueshock

pairing:
	make -C pairing

clean:
	@rm -rf $(OBJ)
	@rm -f $(BIN)
	make -C blueshock clean
	make -C pairing clean

.PHONY: clean pairing

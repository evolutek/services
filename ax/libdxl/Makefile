TARGET  = libdxl.so
SOURCES = dxl_hal.c dynamixel.c
OBJECTS = $(SOURCES:.c=.o)
CFLAGS  = -W -Wall -O2 -fPIC
CFLAGS += -DUSE_USB2AX
CC      = gcc
#CC = /opt/FriendlyARM/toolschain/4.5.1/bin/arm-none-linux-gnueabi-gcc

$(TARGET): $(OBJECTS)
	$(CC) -shared $^ -o $@

clean:
	rm -f $(OBJECTS) $(TARGET)

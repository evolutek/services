TARGET  = libdxl.so
SOURCES = dxl_hal.c dynamixel.c
OBJECTS = $(SOURCES:.c=.o)
CFLAGS  = -W -Wall -O2 -fPIC
CC      = gcc

$(TARGET): $(OBJECTS)
	$(CC) -shared $^ -o $@

clean:
	rm -f $(OBJECTS) $(TARGET)

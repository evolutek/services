#ifndef BLUESHOCK_H
# define BLUESHOCK_H

#include <stdint.h>
#include <bluetooth/bluetooth.h>
#include <bluetooth/l2cap.h>

typedef struct dualshock3_s *dualshock3_t;
struct dualshock3_s {
    struct {
        uint8_t
            leftStick_x,
            leftStick_y,
            rightStick_x,
            rightStick_y;
    } stick;

    struct {
        uint8_t
            select:1,
            l3:1,
            r3:1,
            start:1,
            up:1,
            right:1,
            down:1,
            left:1,
            l2:1,
            r2:1,
            l1:1,
            r1:1,
            triangle:1,
            circle:1,
            cross:1,
            square:1;
    } digitalInput;

    struct {
        uint8_t l1;
        uint8_t l2;
        uint8_t r1;
        uint8_t r2;
        uint8_t triangle;
        uint8_t circle;
        uint8_t cross;
        uint8_t square;
        uint8_t up;
        uint8_t right;
        uint8_t down;
        uint8_t left;
    } analogInput;

    struct {
        int8_t x;
        int8_t y;
        int8_t z;
        int8_t gZ;
    }axis;
};

int blueshock_start();
int blueshock_get(int index, dualshock3_t buttons);
void blueshock_setLeds(int index, int num);
void blueshock_stop();

#endif

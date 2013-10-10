#include <stdlib.h>
#include <stdio.h>
#include <curses.h>
#include <unistd.h>
#include <limits.h>
#include <clas/clas.h>
#include "blueshock.h"

#define INCREMENT 500

struct dualshock3_s b;
clasClient c;
int maxPWM = 0;

static void setMaxPwm()
{
    static int upState = 0;
    static int downState = 0;

    if(b.digitalInput.up == 0)
        upState = 0;
    if(b.digitalInput.down == 0)
        downState = 0;

    if(b.digitalInput.up > 0 && upState == 0) {
        upState = 1;
        if(maxPWM < 4000) {
            maxPWM += INCREMENT;
            fprintf(stdout, "Max pwm is %d\n", maxPWM);
            blueshock_setLeds(0, maxPWM / INCREMENT);
        }
    }
    if(b.digitalInput.down > 0 && downState == 0) {
        downState = 1;
        if(maxPWM > 0) {
            maxPWM -= INCREMENT;
            fprintf(stdout, "Max pwm is %d\n", maxPWM);
            blueshock_setLeds(0, maxPWM / INCREMENT);
        }
    }
}

static void send_cmd(int l, int r)
{
    static int last_l = 0;
    static int last_r = 0;
    cJSON *ret, *arg;

    if (l != last_l || r != last_r)
    {
        arg = cJSON_CreateObject();
        cJSON_AddNumberToObject(arg, "l", l);
        cJSON_AddNumberToObject(arg, "r", r);
        clas_client_query(c, "trajman", NULL, "set-pwm", arg, &ret);
    }
    last_l = l;
    last_r = r;
}

void splitStick()
{
    int spos = ((float)(b.stick.leftStick_y - 127.5) / 127.5) * 100;
    float rpos = ((float)(b.stick.rightStick_x - 127.5) / 127.5) * 100.;
    int pwmpc = maxPWM / 10;
    int max = spos * maxPWM / 100;
    int leftPWM = max;
    int rightPWM = max;
    if (spos > 10 && spos < 10)
    {
        if (rpos < -10 || rpos > 10)
        {
            leftPWM = (float)-maxPWM * rpos / 100.;
            rightPWM = (float)maxPWM * rpos / 100.;
        }
        else
            return;
    }
    else
    {
        if (rpos < 10)
            leftPWM = ((float)leftPWM) / (-rpos);
        else if (rpos > 10)
            rightPWM = ((float)rightPWM) / rpos;
        else
            return;
    }
    printf("left %d, right %d\n", leftPWM, rightPWM);
    //send_cmd(leftPWM, rightPWM);
}

void dualStick()
{
    int leftPWM = ((float)(b.stick.leftStick_y - 127.5) / 127.5) * -maxPWM;
    int rightPWM = ((float)(b.stick.rightStick_y - 127.5) / 127.5) * -maxPWM;
    if(leftPWM < 250 && leftPWM > -250)
        leftPWM = 0;
    if(rightPWM < 250 && rightPWM > -250)
        rightPWM = 0;
    send_cmd(leftPWM, rightPWM);
}

int main(int argc, const char* argv[])
{
    int mode = 0;
    if(argc < 3)
        fprintf(stdout, "No mode specified, using dualstick mode\n");
    else {
        if(!strcmp(argv[1], "--mode")) {
            if(!strcmp(argv[2], "split"))
                mode = 2;
            if(!strcmp(argv[2], "dual"))
                mode = 0;
        }
    }
    fprintf(stdout, "Init libblueshock...");
    fflush(stdout);
    if(blueshock_start() == -1)
        exit(EXIT_FAILURE);
    fprintf(stdout, " [DONE]\n");

    fprintf(stdout, "Waiting for a controller");
    while(blueshock_get(0, &b) == -1) {
        usleep(1000 * 250);
        fprintf(stdout, ".");
    }
    fprintf(stdout, " [DONE]\n");

    c = clas_client_init(NULL, 0);

    while(1) {
        if(!blueshock_get(0, &b)) {
            setMaxPwm();
            if(mode == 2)
                splitStick();
            else if(mode == 1)
                dualStick();
        }
    }
    clas_client_stop(c);
    return EXIT_SUCCESS;
}

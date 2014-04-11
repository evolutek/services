#include <stdlib.h>
#include <stdio.h>
#include <curses.h>
#include <unistd.h>
#include <limits.h>
#include <clas/clas.h>
#include "blueshock.h"

#define INCREMENT 500

typedef void (*handler_f)();
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
    float spos = ((float)(b.stick.leftStick_y) - 127.5) / 127.5;
    float rpos = ((float)(b.stick.rightStick_x) - 127.5) / 127.5;

    int leftPWM = 0;
    int rightPWM = 0;

    // if speed joystick is activated
    if (spos > 0.05 || spos < -0.05)
    {
        leftPWM = maxPWM * spos;
        rightPWM = maxPWM * spos;

        if (rpos < 0.05)
            leftPWM *= -rpos;
        else if (rpos > 0.05)
            rightPWM *= rpos;
    }
    else
    {
        if (rpos > 0.1 || rpos < -0.1)
        {
            leftPWM = maxPWM * rpos;
            rightPWM = -maxPWM * rpos;
        }
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

const struct {
    const char *name;
    handler_f   func;
} modes[] = {
    { "dual",  dualStick },
    { "split", splitStick },
    { NULL,    0 }
};

static void usage(const char *prg)
{
    printf(
        "Usage: %s [OPTIONS]\n"
        "Options:\n"
        "   -h,--help\n"
        "   -m,--mode <mode>\n"
        , prg);
    for (int i = 0; modes[i].name; ++i)
        printf("      %s\n", modes[i].name);
}

typedef enum {
    PARSE_OK,
    PARSE_EXIT,
    PARSE_EXIT_ERR
} parse_e;

static handler_f parse_opts(int argc, const char *argv[])
{
    handler_f h = dualStick;
    parse_e ok = PARSE_OK;

    for (int i = 1; i < argc; ++i)
    {
        if (argv[i][0] == '-')
        {
            if (argc > i + 1 &&
                (!strcmp(argv[i], "-m") || !strcmp(argv[i], "--mode")))
            {
                ++i;
                bool found = false;
                for (int j = 0; modes[j].name; ++j)
                {
                    if (!strcmp(argv[i], modes[j].name))
                    {
                        h = modes[j].func;
                        found = true;
                        break;
                    }
                }

                if (!found)
                    ok = PARSE_EXIT_ERR;
            }
            else
            {
                ok = PARSE_EXIT_ERR;
                break;
            }
        }
        else
        {
            ok = PARSE_EXIT_ERR;
            break;
        }
    }

    if (ok != PARSE_OK)
    {
        usage(argv[0]);
        exit(ok == PARSE_EXIT ? 0 : 1);
    }

    return h;
}

static void init_blueshock()
{
    fprintf(stdout, "Init libblueshock...");
    fflush(stdout);
    if(blueshock_start() == -1)
        exit(EXIT_FAILURE);
    fprintf(stdout, " [DONE]\n");

    fprintf(stdout, "Waiting for a controller");
    fflush(stdout);
    while(blueshock_get(0, &b) == -1) {
        usleep(1000 * 250);
        fprintf(stdout, ".");
        fflush(stdout);
    }
    fprintf(stdout, " [DONE]\n");
}

int main(int argc, const char* argv[])
{
    handler_f handler = parse_opts(argc, argv);
    if (!handler)
        return EXIT_FAILURE;

    init_blueshock();
    c = clas_client_init(NULL, 0);

    while(1) {
        if(!blueshock_get(0, &b)) {
            setMaxPwm();
            handler();
        }
    }

    clas_client_stop(c);
    return EXIT_SUCCESS;
}

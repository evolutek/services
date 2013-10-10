#include "blueshock.h"
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <sys/time.h>
#include <sys/socket.h>

controller_t controllerList_g = NULL;
volatile int quit_g = 0;
static int csk = 0;
static int isk = 0;

static int l2cap_listen(const bdaddr_t *bdaddr, unsigned short psm);
static int blueshock_init();
static void blueshock_setupDevice(int sk, int index);
static void blueshock_handle();
static void blueshock_handleDis();
static void blueshock_handleReport(unsigned char buf[static 49], int len,
        controller_t c);
static void* blueshock_mainLoop();

int blueshock_start()
{
    pthread_t t;

    if(csk == 0 && isk == 0) {
        if(blueshock_init(&csk, &isk) == -1)
            return -1;
        pthread_create(&t, NULL, &blueshock_mainLoop, NULL);
    }
    quit_g = 0;
    return 0;
}

void blueshock_stop()
{
    controller_t it, tmp;
    quit_g = 1;
    for (it = controllerList_g; it; it = it->next) {
        tmp = it->next;
        close(it->csk);
        close(it->isk);
        free(it);
        it = tmp;
    }
    controllerList_g = NULL;
    close(csk);
    close(isk);
}

int blueshock_get(int index, dualshock3_t buttons)
{
    controller_t c;
    LOG("Get index %d\n", index);
    for (c = controllerList_g; c && c->index != index; c = c->next)
        ;
    if(c == NULL) {
        LOG("Index %d not found\n", index);
        return -1;
    }
    pthread_mutex_lock(&c->mutex);
    *buttons = c->buttons;
    pthread_mutex_unlock(&c->mutex);

    return 0;
}

static int l2cap_listen(const bdaddr_t *bdaddr, unsigned short psm)
{
    int sk = socket(PF_BLUETOOTH, SOCK_SEQPACKET, BTPROTO_L2CAP);
    if (sk < 0)
        fatal("socket");

    struct sockaddr_l2 addr;
    memset(&addr, 0, sizeof(addr));
    addr.l2_family = AF_BLUETOOTH;
    addr.l2_bdaddr = *BDADDR_ANY;
    addr.l2_psm = htobs(psm);
    if (bind(sk, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        fatal("bind");
        close(sk);
        return -1;
    }
    if (listen(sk, 5) < 0)
        fatal("listen");
    return sk;
}

static int blueshock_init()
{
    uid_t uid = getuid();
    if(uid) {
        fprintf(stderr, "Run as root, and you will be happy :)\n");
        return -1;
    }
    csk = l2cap_listen(BDADDR_ANY, L2CAP_PSM_HIDP_CTRL);
    isk = l2cap_listen(BDADDR_ANY, L2CAP_PSM_HIDP_INTR);

    if (csk < 0 || isk < 0) {
        fprintf(stderr, "Unable to listen on HID PSMs.\n");
        return -1;
    }
    LOG("%s", "Waiting for Bluetooth s.\n");
    return 0;
}

static void blueshock_handle()
{
    static unsigned currentIndex = 0;
    int cs, is;
    bdaddr_t baddr;

    LOG("%s", "New Device\n");
    if((cs = accept(csk, NULL, NULL)) < 0)
        fatal("accept(CTRL)");
    if((is = accept(isk, NULL, NULL)) < 0)
        fatal("accept(INTR)");

    struct sockaddr_l2 addr;
    socklen_t addrlen = sizeof(addr);
    if (getpeername(isk, (struct sockaddr *)&addr, &addrlen) < 0)
        fatal("getpeername");
    baddr = addr.l2_bdaddr;

    unsigned char resp[64];
    char get03f2[] = { HIDP_TRANS_GET_REPORT | HIDP_DATA_RTYPE_FEATURE | 8,
        0xf2, sizeof(resp), sizeof(resp)>>8 };
    (void)send(csk, get03f2, sizeof(get03f2), 0);
    (void)recv(csk, resp, sizeof(resp), 0);


    controller_t c;
    for (c = controllerList_g; c; c = c->next)
        if(!bacmp(&c->addr, &baddr))
            break;
    if(!c) {
        c = malloc(sizeof(struct controller_s));
        c->index = currentIndex++;
        pthread_mutex_init(&c->mutex, NULL);
        c->addr = baddr;
        c->next = controllerList_g;
        controllerList_g = c;
    }
    c->csk = cs;
    c->isk = is;
    c->paired = 1;

    blueshock_setupDevice(c->csk, c->index);
}

static void blueshock_handleDis(controller_t c)
{
    c->paired = 0;
}

static void blueshock_handleReport(unsigned char buf[static 49], int len,
        controller_t c)
{
    if (buf[0] != 0xa1)
        return;

    pthread_mutex_lock(&c->mutex);
    /* Digital */
    c->buttons.digitalInput.select   = (buf[3] & 0x01) >> 0;
    c->buttons.digitalInput.l3       = (buf[3] & 0x02) >> 1;
    c->buttons.digitalInput.r3       = (buf[3] & 0x04) >> 2;
    c->buttons.digitalInput.start    = (buf[3] & 0x08) >> 3;
    c->buttons.digitalInput.up       = (buf[3] & 0x10) >> 4;
    c->buttons.digitalInput.right    = (buf[3] & 0x20) >> 5;
    c->buttons.digitalInput.down     = (buf[3] & 0x40) >> 6;
    c->buttons.digitalInput.left     = (buf[3] & 0x80) >> 7;
    c->buttons.digitalInput.l2       = (buf[4] & 0x01) >> 1;
    c->buttons.digitalInput.r2       = (buf[4] & 0x02) >> 2;
    c->buttons.digitalInput.l1       = (buf[4] & 0x04) >> 3;
    c->buttons.digitalInput.r1       = (buf[4] & 0x08) >> 4;
    c->buttons.digitalInput.triangle = (buf[4] & 0x10) >> 5;
    c->buttons.digitalInput.circle   = (buf[4] & 0x20) >> 6;
    c->buttons.digitalInput.cross    = (buf[4] & 0x40) >> 7;
    c->buttons.digitalInput.square   = (buf[4] & 0x80) >> 8;

    /* Sticks */
    c->buttons.stick.leftStick_x     = buf[7];
    c->buttons.stick.leftStick_y     = buf[8];
    c->buttons.stick.rightStick_x    = buf[9];
    c->buttons.stick.rightStick_y    = buf[10];

    /* Analog */
    c->buttons.analogInput.l2        = buf[19];
    c->buttons.analogInput.r2        = buf[20];
    c->buttons.analogInput.l1        = buf[21];
    c->buttons.analogInput.r1        = buf[22];
    c->buttons.analogInput.triangle  = buf[23];
    c->buttons.analogInput.circle    = buf[24];
    c->buttons.analogInput.cross     = buf[25];
    c->buttons.analogInput.square    = buf[26];

    /* Axis */
    c->buttons.axis.x                = buf[43];
    c->buttons.axis.y                = buf[45];
    c->buttons.axis.z                = buf[47];
    c->buttons.axis.gZ               = buf[47];

    pthread_mutex_unlock(&c->mutex);
}

static void* blueshock_mainLoop()
{
    int ret;

    LOG("%s", "MainLoop\n");
    while (!quit_g) {
        fd_set fds;
        struct timeval tv = { .tv_sec = 2, .tv_usec = 0 };
        FD_ZERO(&fds);
        FD_SET(STDIN_FILENO, &fds);
        int fdmax = 0;
        FD_SET(csk, &fds);
        FD_SET(isk, &fds);
        fdmax = csk > isk ? csk : isk;

        for (controller_t c = controllerList_g; c; c = c->next) {
            FD_SET(c->csk, &fds);
            if (c->csk > fdmax)
                fdmax = c->csk;
            FD_SET(c->isk, &fds);
            if (c->isk > fdmax)
                fdmax = c->isk;
        }
        ret = select(fdmax + 1, &fds, NULL, NULL, &tv);
        if(ret < 0)
            fatal("select");
        if(ret == 0)
            continue;

        if (FD_ISSET(csk, &fds))
            blueshock_handle();

        for (controller_t c = controllerList_g; c; c = c->next) {
            if (FD_ISSET(c->isk, &fds)) {
                unsigned char report[256];
                int nr = recv(c->isk, report, sizeof(report), 0);
                if (nr <= 0)
                    blueshock_handleDis(c);
                else
                    blueshock_handleReport(report, nr, c);
            }
        }

    }
    return NULL;
}

static void blueshock_setupDevice(int sk, int index)
{
    char set03f4[] = { HIDP_TRANS_SET_REPORT | HIDP_DATA_RTYPE_FEATURE,
        0xf4, 0x42, 0x03, 0x00, 0x00 };
    send(sk, set03f4, sizeof(set03f4), 0);
    unsigned char ack;
    int nr = recv(sk, &ack, sizeof(ack), 0);
    if (nr != 1 || ack != 0)
        fatal("ack");
    static const char ledmask[10] = { 1, 2, 4, 8, 6, 7, 11, 13, 14, 15 };
    char set0201[] = {
        HIDP_TRANS_SET_REPORT | HIDP_DATA_RTYPE_OUTPUT, 0x01,
        0x00, 0x00, 0x00, 0,0, 0x00, 0x00, 0x00,
        0x00, ledmask[index%10],
        LED_PERMANENT,
        LED_PERMANENT,
        LED_PERMANENT,
        LED_PERMANENT,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
    };
    set0201[3] = set0201[5] = 4;
    set0201[5] = 0;
    set0201[6] = 0x70;
    send(sk, set0201, sizeof(set0201), 0);
    nr = recv(sk, &ack, sizeof(ack), 0);
    if (nr != 1 || ack != 0)
        fatal("ack");
}

static void dualshock_setLeds(int sk, int num)
{
    int nr;
    unsigned char ack;
    char buf[] = {
        HIDP_TRANS_SET_REPORT | HIDP_DATA_RTYPE_OUTPUT, 0x01,
        0x00, 0x00, 0x00, 0,0, 0x00, 0x00, 0x00,
        0x00, num << 1,
        LED_PERMANENT,
        LED_PERMANENT,
        LED_PERMANENT,
        LED_PERMANENT,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
    };
    send(sk, buf, sizeof(buf), 0);
    nr = recv(sk, &ack, sizeof(ack), 0);
    if (nr != 1 || ack != 0)
        fatal("ack");
}

void blueshock_setLeds(int index, int num)
{
    for (controller_t c = controllerList_g; c; c = c->next)
        if(c->index == index)
            dualshock_setLeds(c->csk, num);
}

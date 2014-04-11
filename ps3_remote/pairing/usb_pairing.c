#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
#include <sys/socket.h>
#include <sys/time.h>
#include <usb.h>

#include <bluetooth/bluetooth.h>
#include <bluetooth/l2cap.h>

#define USB_DIR_IN 0x80
#define USB_DIR_OUT 0
#define USB_GET_REPORT 0x01
#define USB_SET_REPORT 0x09

#define VENDOR_SONY 0x054c
#define PRODUCT_SIXAXIS_DS3 0x0268

bdaddr_t newAddr;

void fatal(char *msg) {
    if ( errno ) perror(msg); else fprintf(stderr, "%s\n", msg);
    exit(1);
}

void check_uid()
{
    uid_t uid = getuid();
    if(uid) {
        fprintf(stderr, "Run as root, and you will be happy :)\n");
        exit(EXIT_FAILURE);
    }
}

int mystr2ba(const char *s, bdaddr_t *ba) {
    if ( strlen(s) != 17 ) return 1;
    for ( int i=0; i<6; ++i ) {
        int d = strtol(s+15-3*i, NULL, 16);
        if ( d<0 || d>255 ) return 1;
        ba->b[i] = d;
    }
    return 0;
}

const char *myba2str(const bdaddr_t *ba) {
    static char buf[2][18];  // Static buffer valid for two invocations.
    static int index = 0;
    index = (index+1)%2;
    sprintf(buf[index], "%02x:%02x:%02x:%02x:%02x:%02x",
            ba->b[5], ba->b[4], ba->b[3], ba->b[2], ba->b[1], ba->b[0]);
    return buf[index];
}

bdaddr_t get_pairing_address(usb_dev_handle *devh, int itfnum)
{
    bdaddr_t current_ba;
    int res;
    unsigned char msg[8];
    res = usb_control_msg
        (devh, USB_DIR_IN | USB_TYPE_CLASS | USB_RECIP_INTERFACE,
         USB_GET_REPORT, 0x03f5, itfnum, (void*)msg, sizeof(msg), 5000);
    if (res < 0)
        fatal("usb_control_msg(read master)");
    for (int i = 0; i < 6; ++i)
        current_ba.b[i] = msg[7-i];
    return current_ba;
}

void set_pairing_address(usb_dev_handle *devh, int itfnum, bdaddr_t ba)
{
    int res;
    char msg[8] = { 0x01, 0x00,
        ba.b[5],ba.b[4],ba.b[3],ba.b[2],ba.b[1],ba.b[0] };
    res = usb_control_msg
        (devh, USB_DIR_OUT | USB_TYPE_CLASS | USB_RECIP_INTERFACE,
         USB_SET_REPORT, 0x03f5, itfnum, msg, sizeof(msg), 5000);
    if (res < 0)
        fatal("usb_control_msg(write master)");

}

bdaddr_t get_local_bdaddr()
{
    bdaddr_t ba;
    char ba_s[18];
    FILE *f = popen("hcitool dev", "r");
    if (!f || fscanf(f, "%*s\n%*s %17s", ba_s)!=1 || mystr2ba(ba_s, &ba))
        fatal("Unable to retrieve a valid bluetooth address.\n");
    pclose(f);
    return ba;
}

void usb_pair_device(struct usb_device *dev, int itfnum)
{
    usb_dev_handle *devh = usb_open(dev);
    if (!devh)
        fatal("usb_open");
    usb_detach_kernel_driver_np(devh, itfnum);
    int res = usb_claim_interface(devh, itfnum);
    if (res < 0)
        fatal("usb_claim_interface");

    bdaddr_t ba, oldAddr;
    if(!memcmp(newAddr.b, (char[6]){0}, 6))
        ba = get_local_bdaddr();
    else
        ba = newAddr;
    oldAddr = get_pairing_address(devh, itfnum);
    fprintf(stderr, "%s -> %s\n", myba2str(&oldAddr), myba2str(&ba));
    set_pairing_address(devh, itfnum, ba);
    fprintf(stderr, "Done\n");
}

struct usb_bus *pairing_init()
{
    struct usb_bus *busses;
    usb_init();
    if (usb_find_busses() < 0)
        fatal("usb_find_busses");
    if (usb_find_devices() < 0)
        fatal("usb_find_devices");
    busses = usb_get_busses();
    if (!busses)
        fatal("usb_get_busses");
    return busses;
}

int is_dualshock(struct usb_device *dev, struct usb_interface_descriptor *alt)
{
    return (dev->descriptor.idVendor == VENDOR_SONY &&
            dev->descriptor.idProduct == PRODUCT_SIXAXIS_DS3 &&
            alt->bInterfaceClass == 3);
}

void usb_scan(struct usb_bus *busses)
{
    struct usb_bus *bus;
    for (bus = busses; bus; bus=bus->next) {
        struct usb_device *dev;
        for (dev = bus->devices; dev; dev = dev->next) {
            struct usb_config_descriptor *cfg;
            for (cfg = dev->config;
                    cfg < dev->config + dev->descriptor.bNumConfigurations;
                    ++cfg ) {
                int itfnum;
                for (itfnum = 0; itfnum < cfg->bNumInterfaces; ++itfnum) {
                    struct usb_interface *itf = &cfg->interface[itfnum];
                    struct usb_interface_descriptor *alt;
                    for (alt = itf->altsetting;
                            alt < itf->altsetting + itf->num_altsetting;
                            ++alt) {
                        if(is_dualshock(dev, alt))
                            usb_pair_device(dev, itfnum);
                    }
                }
            }
        }
    }
}

int main(int argc, char* argv[])
{
    check_uid();
    if(argc > 1)
        if(mystr2ba(argv[1], &newAddr) == 1) {
            fprintf(stderr, "Invalid arg\n");
            exit(EXIT_FAILURE);
        }
    struct usb_bus *busses = pairing_init();
    usb_scan(busses);
    return 0;
}


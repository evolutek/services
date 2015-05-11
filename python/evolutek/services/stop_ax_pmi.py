from cellaserv.proxy import CellaservProxy

def main():
    cs = CellaservProxy()
    cs.ax["1"].turn(True, 0)
    cs.ax["2"].turn(True, 0)
    cs.ax["3"].turn(True, 0)
    cs.ax["4"].turn(True, 0)
    cs.ax["1"].free()
    cs.ax["2"].free()
    cs.ax["3"].free()
    cs.ax["4"].free()
    cs.ax["5"].free()
    print("Roger is stop")

if __name__ == '__main__':
    main()


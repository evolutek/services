from cellaserv.proxy import CellaservProxy

ROBOT="pal"

def home():
    cs = CellaservProxy()
    #cs.robot[ROBOT].recalibration(x=False, y=True, x_sensor="right", init=True)
    #cs.robot[ROBOT].goto(1830, 1130)
    
    cs.robot[ROBOT].place_under()

home()

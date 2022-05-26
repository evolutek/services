from cellaserv.proxy import CellaservProxy

ROBOT="pal"

def home():
    cs = CellaservProxy()
    cs.robot[ROBOT].place_under()

home()

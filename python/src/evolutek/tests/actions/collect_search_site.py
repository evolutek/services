from cellaserv.proxy import CellaservProxy

ROBOT="pal"

def home():
    cs = CellaservProxy()
    cs.robot[ROBOT].collect_search_site()

home()

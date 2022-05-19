from evolutek.lib.status import RobotStatus
from evolutek.lib.utils.wrappers import if_enabled, use_queue

#########
# PUMPS #
#########

def mirror_pump_id(self, id):
    if not self.side:
        if id in [1,3]:
            id = 4 - id
    return id

@if_enabled
@use_queue
def pumps_get(self, ids, mirror=True):
    if isinstance(ids, str):
        ids = ids.split(",")

    if isinstance(mirror, str):
        mirror = mirror == 'true'

    _ids = []
    for id in ids:
        _ids.append(self.mirror_pump_id(int(id)) if mirror else int(id))
    if 1 in _ids: _ids.append(3)
    if 4 in _ids: _ids.append(5)

    return self.actuators.pumps_get(_ids)

@if_enabled
@use_queue
def pumps_drop(self, ids, mirror=True):
    if isinstance(ids, str):
        ids = ids.split(",")

    if isinstance(mirror, str):
        mirror = mirror == 'true'

    _ids = []
    for id in ids:
        _ids.append(self.mirror_pump_id(int(id)) if mirror else int(id))
    if 1 in _ids: _ids.append(3)
    if 4 in _ids: _ids.append(5)

    return self.actuators.pumps_drop(_ids)
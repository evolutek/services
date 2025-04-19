from enum import Enum
from evolutek.lib.utils.boolean import get_boolean
from evolutek.lib.status import RobotStatus
from evolutek.lib.utils.color import Color
from evolutek.lib.utils.task import async_task
from evolutek.lib.utils.wrappers import if_enabled
from time import sleep, time
from evolutek.lib.actuators.i2c_acts import I2CActsHandler, I2CActType, ESCVariation
from evolutek.lib.actuators.ax12 import AX12Controller


# ====== Elevator ======

# (Right ID, Left ID)
class ElevatorId(Enum):
    FRONT = (1, 2)
    #BACK = (2, 3)

class ElevatorPosition(Enum):
    LOWEST = {ElevatorId.FRONT: (390, 630)}
    MIDDLE = {ElevatorId.FRONT: (420, 600)}
    HIGHEST = {ElevatorId.FRONT: (760, 260)}

@if_enabled
@async_task
def move_elevator(self, elevator_id: ElevatorId, position: ElevatorPosition, wait = True):
    if isinstance(elevator_id, str):
        elevator_id = ElevatorId[elevator_id]

    if isinstance(position, str):
        position = ElevatorPosition[position]

    self.actuators.ax_set_speed(elevator_id.value[0], 256)
    self.actuators.ax_set_speed(elevator_id.value[0], 256)

    """
    if position == ElevatorPosition.HIGH:
        self.actuators.ax_set_speed(1, 220)
        self.actuators.ax_set_speed(2, 220)
    else:
        self.actuators.ax_set_speed(1, 170)
        self.actuators.ax_set_speed(2, 170)
    """

    angles = position.value[elevator_id]

    # TODO: Moving the two AX12 with two Cellaserv command can be too slow (too much delay between two commands)
    status = RobotStatus.check(
        self.actuators.ax_move(elevator_id.value[0], angles[0]), # Right servo
        self.actuators.ax_move(elevator_id.value[1], angles[1])  # Left servo
    )

    if RobotStatus.get_status(status) != RobotStatus.Done:
        return status

    sleep(2)

    """
    if wait:
        if position != ElevatorPosition.HIGH:
            threshold = 1100
            # Check if the servos are forcing
            end_time = time() + (0.6 if position != ElevatorPosition.LOW else 0.8)
            while time() < end_time:
                if abs(self.actuators.ax_get_load(1)) > threshold or abs(self.actuators.ax_get_load(2)) > threshold:
                    self.actuators.ax_move(1, ElevatorPosition.HIGH.value[0]), # Right servo
                    self.actuators.ax_move(2, ElevatorPosition.HIGH.value[1])  # Left servo
                    return RobotStatus.return_status(RobotStatus.Failed)
                sleep(0.1)
        else:
            sleep(0.3)
    """

    return RobotStatus.return_status(RobotStatus.Done)

@if_enabled
@async_task
def move_elevator_ex(self, elevator_id: ElevatorId, position: float, wait = True):
    if isinstance(elevator_id, str):
        elevator_id = ElevatorId[elevator_id]

    if isinstance(position, str):
        position = float(position)


    self.actuators.ax_set_speed(elevator_id.value[0], 256)
    self.actuators.ax_set_speed(elevator_id.value[0], 256)

    angles = (
        (ElevatorPosition.HIGHEST.value[elevator_id][0] - ElevatorPosition.LOWEST.value[elevator_id][0]) * position + ElevatorPosition.LOWEST.value[elevator_id][0],
        (ElevatorPosition.HIGHEST.value[elevator_id][1] - ElevatorPosition.LOWEST.value[elevator_id][1]) * position + ElevatorPosition.LOWEST.value[elevator_id][1]
    )

    # TODO: Moving the two AX12 with two Cellaserv command can be too slow (too much delay between two commands)
    status = RobotStatus.check(
        self.actuators.ax_move(elevator_id.value[0], angles[0]), # Right servo
        self.actuators.ax_move(elevator_id.value[1], angles[1])  # Left servo
    )

    if RobotStatus.get_status(status) != RobotStatus.Done:
        return status

    sleep(2)

    return RobotStatus.return_status(RobotStatus.Done)


# ====== Plank Arm ======

# (Right, Left)
class PlankArmId(Enum):
    FRONT = (8, 7)
    #BACK = (7, 8)

class PlankArmPosition(Enum):
    LIFT       = {PlankArmId.FRONT: (118, 83)}
    EXPANDED   = {PlankArmId.FRONT: (90, 110)}
    COLLAPSED  = {PlankArmId.FRONT: (180, 20)}

@if_enabled
@async_task
def move_plank_arm(self, plank_arm_id: PlankArmId, position: PlankArmPosition):
    if isinstance(plank_arm_id, str):
        plank_arm_id = PlankArmPosition[plank_arm_id]

    if isinstance(position, str):
        position = PlankArmPosition[position]

    angles = position.value[plank_arm_id]

    status = RobotStatus.check(self.actuators.servos_set_angles(
        [plank_arm_id.value[0], plank_arm_id.value[1]],
        [angles[0], angles[1]]
    ))

    if RobotStatus.get_status(status) != RobotStatus.Done:
        return status

    sleep(1)

    return RobotStatus.return_status(RobotStatus.Done)

    """
    _ids = []
    for id in ids:
        _ids.append(int(id))
    status = []
    for clamp_id in _ids:
        status.append(self.actuators.servo_set_angle(CLAMP_ID_TO_SERVO_ID[clamp_id], position.value[clamp_id]))
    return RobotStatus.check(*status)
    """


# ====== Magnets ======

class MagnetId(Enum):
    FRONT_MAGNET_1 = 6
    FRONT_MAGNET_2 = 5
    FRONT_MAGNET_3 = 4
    FRONT_MAGNET_4 = 3
    #BACK_MAGNET_1 = 4
    #BACK_MAGNET_2 = 5
    #BACK_MAGNET_3 = 6
    #BACK_MAGNET_4 = 7

class MagnetsSet(Enum):
    FRONT_MAGNETS = [
        MagnetId.FRONT_MAGNET_1,
        MagnetId.FRONT_MAGNET_2,
        MagnetId.FRONT_MAGNET_3,
        MagnetId.FRONT_MAGNET_4
    ]
    #BACK_MAGNETS = [
    #    MagnetId.BACK_MAGNET_1,
    #    MagnetId.BACK_MAGNET_2,
    #    MagnetId.BACK_MAGNET_3,
    #    MagnetId.BACK_MAGNET_4
    #]

# TODO: Set angles
class MagnetState(Enum):
    DISABLE = {
        MagnetId.FRONT_MAGNET_1: 180,
        MagnetId.FRONT_MAGNET_2: 0,
        MagnetId.FRONT_MAGNET_3: 180,
        MagnetId.FRONT_MAGNET_4: 0,
        #MagnetId.BACK_MAGNET_1: 0,
        #MagnetId.BACK_MAGNET_2: 0,
        #MagnetId.BACK_MAGNET_3: 0,
        #MagnetId.BACK_MAGNET_4: 0
    }
    ENABLE = {
        MagnetId.FRONT_MAGNET_1: 0,
        MagnetId.FRONT_MAGNET_2: 180,
        MagnetId.FRONT_MAGNET_3: 0,
        MagnetId.FRONT_MAGNET_4: 180,
        #MagnetId.BACK_MAGNET_1: 90,
        #MagnetId.BACK_MAGNET_2: 90,
        #MagnetId.BACK_MAGNET_3: 90,
        #MagnetId.BACK_MAGNET_4: 90
    }

@if_enabled
@async_task
def toggle_magnets(self, magnets: MagnetsSet, state: MagnetState):
    if isinstance(magnets, str):
        magnets = MagnetsSet[magnets]

    if isinstance(state, str):
        state = MagnetState[state]

    ids = list(map(lambda x: x.value, magnets.value))
    angles = list(map(lambda x: state.value[x], magnets.value))

    status = RobotStatus.check(self.actuators.servos_set_angles(ids, angles))
    # TODO: Wait if status is OK ?

    return status


# ====== Pumps ======

# TODO
class PumpsSet(Enum):
    FRONT_PLANK = [0, 1]
    #BACK_PLANK = [2, 3]

@if_enabled
@async_task
def toggle_pumps(self, pumps: PumpsSet, grab: bool):
    if isinstance(pumps, str):
        pumps = PumpsSet[pumps]

    grab = get_boolean(grab)

    if grab:
        return RobotStatus.check(self.actuators.pumps_grab(pumps.value))
    else:
        return RobotStatus.check(self.actuators.pumps_drop(pumps.value))


# ====== Pumps Arms ======

class PumpsArmId(Enum):
    FRONT = 9
    #BACK = ?

class PumpsArmPosition(Enum):
    COLLAPSED       = {PumpsArmId.FRONT: 20}
    EXPANDED        = {PumpsArmId.FRONT: 105}
    ALMOST_EXPANDED = {PumpsArmId.FRONT: 90}

@if_enabled
@async_task
def move_pumps_arm(self, pumps_arm_id: PumpsArmId, position: PumpsArmPosition):
    if isinstance(pumps_arm_id, str):
        pumps_arm_id = PumpsArmId[pumps_arm_id]

    if isinstance(position, str):
        position = PumpsArmPosition[position]

    angles = position.value[pumps_arm_id]

    status = RobotStatus.check(self.actuators.servo_set_angle(
        pumps_arm_id.value,
        position.value[pumps_arm_id]
    ))

    if RobotStatus.get_status(status) != RobotStatus.Done:
        return status

    sleep(1)

    return RobotStatus.return_status(RobotStatus.Done)


# ====== Side Arms ======

# (Right, Left)
class SideArmsId(Enum):
    FRONT = (3, 4)
    #BACK = (?, ?)

# TODO: Set angles
class SideArmPosition(Enum):
    NORMAL   = {SideArmsId.FRONT: (200, 830)}
    SPREADED = {SideArmsId.FRONT: (600, 430)}

@if_enabled
@async_task
def move_side_arms(self, side_arms_id: SideArmsId, position: SideArmPosition):
    if isinstance(side_arms_id, str):
        side_arms_id = SideArmsId[side_arms_id]

    if isinstance(position, str):
        position = SideArmPosition[position]

    angles = position.value[side_arms_id]

    status = RobotStatus.check(
        self.actuators.ax_move(side_arms_id.value[0], angles[0]), # Right servo
        self.actuators.ax_move(side_arms_id.value[1], angles[1])  # Left servo
    )

    if RobotStatus.get_status(status) != RobotStatus.Done:
        return status

    sleep(1)

    return RobotStatus.return_status(RobotStatus.Done)

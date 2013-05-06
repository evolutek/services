#!/usr/bin/env python3

try:
    import readline
except ImportError:
    print("You don't have readline, too bad for you...")

__doc__ = \
    "############################################" \
    "Bienvenue dans le shell de la carte moteur !" \
    "############################################" \
    "     Les commandes disponibles sont les suivantes :" \
    "     gotoxy x y                              //Alias : go" \
    "     gototh theta                            //Alias : gt" \
    "     mvtrsl dist acc dec maxspeed sens" \
    "     mvrot dist acc dec maxspeed sens" \
    "     free                                    //Alias : f" \
    "     recal sens" \
    "     unfree                                  //Alias : re" \
    "     setpidt P I D" \
    "     setpidr P I D" \
    "     debug on/off" \
    "     settracc acc" \
    "     settrmax vmax" \
    "     settrdec dec" \
    "     setrotacc acc" \
    "     setrotmax vmax" \
    "     setrotdec dec" \
    "     setx x" \
    "     sety y" \
    "     sett theta" \
    "     getpidt" \
    "     getpidr" \
    "     getpos                                  //Alias : gp" \
    "     getspeeds" \
    "     courbe desttr acc dec max sens destrot acc dec max sens" \
    "     help" \
    "     cl" \
    "     fp" \
    "     setwheels diam1 diam2                   //Alias : sw" \
    "     setspacing dist" \
    "     getwheels" \
    "     cws [all|spacing|diam] //Calculate wheels size" \
    " w a s d "

def main():
    commands = {
            "gotoxy": GotoXY,
            "go": GotoXY,
            "gt": GotoTheta,
            "mvtrsl": MoveTrsl,
            "mt": MoveTrsl,
            "mvrot": MoveRot,
            "mr": MoveRot,
            "free": FreeMotors,
            "f": FreeMotors,
            "recal": Recalage,
            "unfree": UnFreeMotors,
            "re": UnFreeMotors,
            "setpidt": SetPIDTrsl,
            "setpidr": SetPIDRot,
            "debug": SetDebug,
            "settracc": SetTrslAcc,
            "settrmax": SetTrslMaxSpeed,
            "settrdec": SetTrslDec,
            "setrotacc": SetRotAcc,
            "setrotmax": SetRotMaxSpeed,
            "setrotdec": SetRotDec,
            "setx": SetX,
            "sety": SetY,
            "sett": SetTheta,
            "getpidt": GetPIDTrsl,
            "getpidr": GetPIDRot,
            "getpos": GetPosition,
            "gp": GetPosition,
            "getspeeds": GetSpeeds,
            "help": DisplayHelp,
            "curve": Curve,
            "courbe": Courbe,
            "setwheels": SetWheels,
            "setspacing": SetWheelSpacing,
            "getwheels": GetWheels,
            "computewheelssize": compute_wheels_size,
            "cws": compute_wheels_size,
            "sw": SetWheels,
            "tq": TestQueued,
            "tr": TestRot,
            "tt": TestTrsl,
            "fp": FindPos,
            "cl": Clear,
            "cl": Clear,
            "w": w,
            "a": a,
            "d": d,
            "s": s,
    }

    print(__doc__)

    while True:
        s = input()
        words = s.split()
        if words[0] in commands:
            commands[words[0]](*words[1:])
        else:
            print("Command not found.")

if __name__ == "__main__":
    main()


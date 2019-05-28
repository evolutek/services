import json

class FileGenerator():
    def __init__(self):
        self.actions = {}
        self.goals = []

    def add_start(self, x:int, y:int, theta:str=None):
        self.start = {"x": x, "y": y}
        if theta is not None:
            self.start['theta'] = theta

    def add_action(self, name:str, service:str, idt:str, fct:str, avoid:bool=True):
        self.actions[name] = {"service": service, "id": idt, "fct": fct, "avoid": avoid}

    def add_goal(self, name:str, score:int):
        self.goals.append({"name" : name, "score" : score})
        self.goals[-1]["path"] = []
        self.goals[-1]["actions"] = []
        return self

    def add_path(self, x:int, y:int, theta:str=None):
        path = {"x": x, "y": y}
        if theta is not None:
            path["theta"] = theta
        self.goals[-1]["path"].append(path)
        return self

    def add_subaction(self, name:str, args:dict=None, avoid:str=None, score:int = None):
        action = {"name": name}
        if args is not None:
            action["args"] = args
        if score is not None:
            action["score"] = score
        if avoid is not None:
            action["avoid_strategy"] = avoid
        self.goals[-1]["actions"].append(action)
        return self

    def add_goto_xy_subaction(self, x:int, y:int, avoid:bool=True, avoid_strategy=None):
        action = "goto_xy_with_avoid" if avoid else "goto_xy_without_avoid"
        return self.add_subaction(action, {"x": x, "y": y}, avoid=avoid_strategy)

    def add_goto_theta_subaction(self, theta:str, avoid:bool=True):
        action = "goto_theta_with_avoid" if avoid else "goto_theta_without_avoid"
        return self.add_subaction(action, {"theta": theta})


    def generate_file(self, path):
        group = {"start": self.start, "actions": self.actions, "goals": self.goals}
        raw = json.dumps(group, indent=4)
        with open(path, "w") as f:
            f.write(raw)

fg = FileGenerator()
fg.add_start(750, 225, theta="0")
fg.add_action("push_ejecteur", "actuators", "pal", "push_ejecteur", False)
fg.add_action("reset_ejecteur", "actuators", "pal", "reset_ejecteur", False)
fg.add_action("init_ejecteur", "actuators", "pal", "init_ejecteur", False)
fg.add_action("drop_goldenium", "actuators", "pal", "drop_goldenium", False)
fg.add_action("get_goldenium", "actuators", "pal", "get_goldenium", False)
fg.add_action("get_blue_palet", "actuators", "pal", "get_blue_palet", False)
fg.add_action("get_palet", "actuators", "pal", "get_palet", False)
fg.add_action("drop_blue_palet", "actuators", "pal", "drop_blue_palet", False)
fg.add_action("drop_palet", "actuators", "pal", "drop_palet", False)
fg.add_action("goto_xy_with_avoid", "trajman", "pal", "goto_xy", True)
fg.add_action("goto_xy_without_avoid", "trajman", "pal", "goto_xy", False)
fg.add_action("goto_theta_with_avoid", "trajman", "pal", "goto_theta")
fg.add_action("goto_theta_without_avoid", "trajman", "pal", "goto_theta", False)
fg.add_action("move_trsl", "trajman", "pal", "move_trsl", False)
fg.add_action("set_x", "trajman", "pal", "set_x", False)
fg.add_action("set_y", "trajman", "pal", "set_y", False)
fg.add_action("set_theta", "trajman", "pal", "set_theta", False)
fg.add_action("free", "trajman", "pal", "free", False)

#fg.add_goal("Test", 0)\
#    .add_path(600, 1200)\
#    .add_path(1300, 1200)\
#    .add_path(500, 1200)\
#    .add_path(1300, 1200)\
#    .add_path(500, 1200)\
#    .add_path(1300, 1200)

#fg.add_goal("Test", 0)\
#    .add_goto_xy_subaction(1000, 500, True, avoid_strategy="Avoid.Skip")\
#    .add_goto_xy_subaction(1000, 1350, True, avoid_strategy="Avoid.Skip")\
#    .add_goto_xy_subaction(1000, 500, True, avoid_strategy="Avoid.Skip")\
#    .add_goto_xy_subaction(1000, 1350, True, avoid_strategy="Avoid.Skip")\
#    .add_goto_xy_subaction(1000, 500, True, avoid_strategy="Avoid.Timeout")\
#    .add_goto_xy_subaction(1000, 1350, True)\
#    .add_goto_xy_subaction(1000, 500, True)

fg.add_goal("Push Front Palet", 0)\
    .add_path(1325, 225)\
    .add_goto_xy_subaction(1325, 500, False)\
    .add_goto_xy_subaction(850, 500, False)

fg.add_goal("Push Chaos Zone", 20)\
    .add_path(750, 1400)\
    .add_goto_xy_subaction(1200, 1400, True)\
    .add_goto_xy_subaction(1200, 1175, False)\
    .add_goto_xy_subaction(615, 375, True)

"""
fg.add_goal("Get palets", 0)\
    .add_path(1840, 225)\
    .add_subaction("move_trsl", {"dest": 50, "acc": 100, "dec": 100, "maxspeed":500, "sens": 1})\
    .add_subaction("free")\
    .add_subaction("set_x", {"x": 1880})\
    .add_subaction("move_trsl", {"dest": 100, "acc": 100, "dec": 100, "maxspeed":500, "sens": 0})\
    .add_goto_theta_subaction("pi/2", False)\
    .add_subaction("move_trsl", {"dest": 50, "acc": 100, "dec": 100, "maxspeed":500, "sens": 0})\
    .add_subaction("free")\
    .add_subaction("set_y", {"y": 130})\
    .add_subaction("set_theta", {"theta": "pi/2"})\
    .add_subaction("move_trsl", {"dest": 50, "acc": 100, "dec": 100, "maxspeed":500, "sens": 1})\
    .add_goto_xy_subaction(1840, 225, False)\
    .add_goto_theta_subaction(0, False)\
    .add_subaction("get_palet")\
    .add_goto_xy_subaction(1285, 225, False)\
"""

    #.add_path(1265, 800)\
fg.add_goal("Get blue palet and drop it", 12)\
    .add_path(1265, 800)\
    .add_goto_theta_subaction("0", False)\
    .add_subaction("get_blue_palet")\
    .add_goto_xy_subaction(1380, 1320, False)\
    .add_goto_theta_subaction("pi/2", False)\
    .add_subaction("move_trsl", {"dest": 60, "acc": 100, "dec": 100, "maxspeed":500, "sens": 1})\
    .add_subaction("free")\
    .add_subaction("set_y", {"y": 1360})\
    .add_subaction("set_theta", {"theta": "pi/2"})\
    .add_subaction("move_trsl", {"dest": 70, "acc": 100, "dec": 100, "maxspeed":500, "sens": 0})\
    .add_goto_theta_subaction("pi/6", False)\
    .add_subaction("drop_blue_palet")\
    .add_subaction("move_trsl", {"dest": 75, "acc": 100, "dec": 100, "maxspeed":500, "sens": 0})\

fg.add_goal("Push Blue Palet", 70)\
    .add_path(1000, 1320)\
    .add_goto_xy_subaction(600, 1620, True)\
    .add_goto_xy_subaction(150, 1620, False)\
    .add_subaction("move_trsl", {"dest": 60, "acc": 100, "dec": 100, "maxspeed":500, "sens": 0})\
    .add_subaction("push_ejecteur")\
    .add_subaction("reset_ejecteur")\
    .add_subaction("free")\
    .add_subaction("set_x", {"x": 150})\
    .add_subaction("set_theta", {"theta": "0"})\
    .add_subaction("move_trsl", {"dest": 60, "acc": 500, "dec": 500, "maxspeed":500, "sens": 1})\
    .add_goto_xy_subaction(500, 1625, True)


#fg.add_goal("Push Front Homo", 0)\
#    .add_path(1325, 225)\
#    .add_goto_xy_subaction(1325, 500, True)\
#    .add_goto_xy_subaction(800, 225, True)


fg.add_goal("Get Goldenium", 20)\
    .add_path(450, 2240)\
    .add_goto_theta_subaction("pi", False)\
    .add_goto_xy_subaction(235, 2225, False)\
    .add_subaction("get_goldenium", avoid="Avoid.Skip", score=20)\
    .add_goto_xy_subaction(500, 2225, True)

fg.add_goal("Drop Goldenium", 24)\
    .add_path(1050, 1325)\
    .add_goto_theta_subaction("0", False)\
    .add_goto_xy_subaction(1425, 1330, False)\
    .add_subaction("drop_goldenium")\

fg.add_goal("Push leftover palets", 0)\
    .add_goto_xy_subaction(1050, 1330)\
    .add_goto_xy_subaction(750, 575)\
    .add_goto_xy_subaction(575, 575)\
    .add_goto_theta_subaction("pi/2")

fg.generate_file("test.json")

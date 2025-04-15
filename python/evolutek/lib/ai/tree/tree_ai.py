import json


class Node:
    def __init__(self):
        pass

    def run(self):
        pass


class ActionNode(Node):
    def __init__(self):
        super().__init__()
        self.action: str = ""
        self.args: dict[str,] = dict()
        self.callback: function = None
        self.on_success_node: Node = None
        self.on_failure_node: Node = None

    def run(self):
        pass


class BranchNode(Node):
    def __init__(self):
        super().__init__()
        self.condition: str = ""
        self.args: dict[str,] = dict()
        self.callback: function = None
        self.on_true_node: Node = None
        self.on_false_node: Node = None


class EntryPoint:
    def __init__(self):
        self.first_node: Node = None


class TreeAI:
    def __init__(self):
        self.entries: list[EntryPoint] = []
        self.actions: dict[str, function] = dict()
        self.conditions: dict[str, function] = dict()

    def parse_file(self, filename: str):
        with open(filename, 'r', encoding = 'utf8') as file:
            data = json.load(file)
        self.parse_json(data)

    def parse_json(self, data):
        data[""]

    def run(self):
        pass

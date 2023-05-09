class Component:

    def __init__(self, name, id):

        self.init = False
        self.name = name
        self.id = int(id)

        self.initialize()

    def _initialize(self):
        self.init = True
        return self.init

    def initialize(self):

        print('[%s] Init %s %d' % ((self.name, self.name, self.id)))

        if not self._initialize():
            print('[%s] Failed to initialize %s %d' % (self.name, self.name, self.id))
        else:
            print('[%s] %s %d initialized' % (self.name, self.name, self.id))
            self.init = True

    def is_initialized(self):
        return self.init

    def __str__(self):
        s = "----------\n"
        s += "%s; %d\n" % (self.name, self.id)
        s += "----------"
        return s

    def __dict__(self):
        return {
            'name' : self.name,
            'id' : self.id
        }

class ComponentsHolder:

    def __init__(self, name, components, component_type, components_common_params=None):

        self.init = False
        self.name = name
        self.components = {}

        self.initialize(components, component_type, components_common_params)

    def _initialize(self):
        return True

    def _post_initialize(self):
        return True

    def initialize(self, components, component_type, components_common_params):
        self.init = False

        print('[%s] Init %s holder' % (self.name, self.name))

        if not self._initialize():
            print('[%s] Failed to initialize %s holder' % (self.name, self.name))
            return False
        else:
            print('[%s] %s holder initialized' % (self.name, self.name))

        if components_common_params is None:
            components_common_params = []

        self.init = True

        for component in components:
            if isinstance(components, list):
                self.components[component] = component_type(component, *components_common_params)
            else:
                if isinstance(components[component], dict):
                    self.components[component] = component_type(component, *components_common_params, **(components[component]))
                else:
                    self.components[component] = component_type(component, *components_common_params, *(components[component]))

            self.init &= self.components[component].is_initialized()

        if not self.init:
            return False
        
        self.init &= self._post_initialize()
        return self.init

    def is_initialized(self):
        if not self.init:
            return False

        status = True
        for component in self.components:
            if not self.components[component].init:
                print("component %s %d is not init" % (self.components[component].name, self.components[component].id))
                status = False
        return status

    def __str__(self):
        s = "%s status:" % self.name
        for i in self.components:
            s += '\n' + str(self.components[i])
        return s

    def __dict__(self):
        return {
            self.name : [ self.components[component].__dict__() for component in self.components ]
        }

    def __iter__(self):
        return iter(self.components)

    def __getitem__(self, key):
        if not isinstance(key, int):
            print('[%s] bad key id' % self.name)
            return None
        if key not in self:
            print('[%s] %s %d not registered' % (self.name, self.name, key))
            return None
        return self.components[key]

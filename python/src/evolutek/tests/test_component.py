from evolutek.lib.component import Component, ComponentsHolder

from time import sleep


class Dummy(Component):

    def __init__(self, id):
        super().__init__('Dummy', id)

    def _initialize(self):
        print('INITIALIZING COMPONENT')
        self.init = True
        return True

    def test(self):
        print("Dummy test %d" % self.id)

    def __str__(self):
        return "DUMMY %d" % self.id

class DummyHolder(ComponentsHolder):

    def __init__(self, components):
        super().__init__('Dummy holder', components, Dummy)

    def __initialize(self):
        print('INITIALIZING HOLDER')
        return True

dummy_holder = DummyHolder([1, 2])
print(dummy_holder)
dummy_holder[1].test()
dummy_holder[2].test()
print(dummy_holder[1].is_initialized())
print(dummy_holder[2].is_initialized())
print(dummy_holder.is_initialized())

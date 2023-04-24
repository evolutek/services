from time import sleep
from evolutek.lib.actuators.ax12 import AX12Controller

ax12 = AX12Controller([1])
print(ax12)

while True:
    ax12[1].move(512)
    print(ax12[1])
    sleep(1)
    ax12[1].move(775)
    print(ax12[1])
    sleep(1)


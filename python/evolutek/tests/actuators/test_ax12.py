from time import sleep
from evolutek.lib.actuators.ax12 import AX12Controller

ax12 = AX12Controller([4])
print(ax12)

while True:
    ax12[4].move(470)
    print(ax12[4])
    sleep(1)
    ax12[4].move(550)
    print(ax12[4])
    sleep(1)


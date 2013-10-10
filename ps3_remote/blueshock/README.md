Lib blueshock
=============
Libblueshock is a simple library intended to easily interact with a
dualshock3 (ps3 controller).
This library has originaly been written to control a robot running an
embedded linux.

Requirements
------------
- Linux
- bluez
- pthread

Using blueshock
---------------
You need to uncomment the following line in /etc/bluetooth/main.conf :
`DisablePlugins = network,input`

See the examples in the "samples" folder.

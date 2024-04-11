# How to install on a Raspberry Pi 3

First set the date with
`sudo date ...`

Please replace "..." with the current date and time in format `MMddHHmmYYYY`

Install required packages:
```sh
sudo apt update
sudo apt upgrade
sudo apt auto-remove
sudo apt install python3 python-is-python3 git cmake build-essential libgeos-dev python3-pil python3-pil.imagetk
sudo python3 -m pip install -U pip
```

Install python-cellaserv3 dependency:
```sh
cd
git clone --recurse-submodules https://github.com/evolutek/python-cellaserv3.git
cd python-cellaserv3
git checkout beforeAsyncio
sudo python3 -m pip install --prefer-binary -e .
```

Install services:
```sh
cd
git clone https://github.com/evolutek/services.git
cd services/python
sudo python3 -m pip install --prefer-binary -e .
```

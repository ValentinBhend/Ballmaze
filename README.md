# Ballmaze
This project is showcased in this video:

[![thumbnail_yt](misc/thumbnail_yt.png)](https://img.youtube.com/vi/cLjqs_h8txE/0.jpg)](https://www.youtube.com/watch?v=cLjqs_h8txE)

The goal is to automate playing the ballmaze dexterity game. There are quite a few challanges in this and a lot of things can be improved from the current solution. 

<p align="center">
  <img src="./misc/wood_maze.gif" width="45%" />
  <img src="./misc/my_maze.gif" width="45%" />
</p>

This is what it can do currently with roughly 50h of (real-world only) training:

![gif_own](misc/gif_own.gif)

## Want to build one yourself?
It's still a work in progress but it works. Some previous experience with a RaspberryPi or similar and a little experience in programming in Python would surely help. And of couse a great interest in robotics/control/machine learning :) <br>
In total the materials cost about 50 - 90 $/€ depending on whether you or someone you know has a 3D printer, or you have to order the 3D printed parts from somewhere. 

### List of materials
Most parts can be replaced by similar ones or whatever you might already have. 

| Part                                              | Price ($/€ approx) | Where to buy |
|---------------------------------------------------|--------------------|--------------|
| 1x RaspberryPi Zero 2W (or better)*               | 15*                | [1](https://www.mouser.ch/ProductDetail/358-SC0721) |
| 2x Servo (e.g. SER0050)                           | 5 (x2)             | [1](https://www.mouser.ch/ProductDetail/426-SER0050) |
| 1x Pi Camera V1.3                                 | 7                  | [1](https://www.mouser.ch/ProductDetail/713-114110127) |
| 1x Pi Camera Cable 300mm                          | 2                  | [1](https://www.mouser.ch/ProductDetail/358-SC1129) |
| 1x uSD card 32GB+                                 | 5                  | [1](https://www.mouser.ch/ProductDetail/358-SC1628) |
| 1x 5V 2A+ USB charger (likely already got one)    | 5                  | [1](https://www.mouser.ch/ProductDetail/490-SWI10B-5-EW-I38) |
| 1x USB Cable to power Pi (micro USB for Pi Zero)  | 2                  | [1](https://www.mouser.ch/ProductDetail/530-SC-2AMK003F) |
| A few metal balls with diameter ~6mm              | 5                  | [1](https://www.amazon.com/0-236-Precision-Chrome-Steel-Bearing/dp/B07L8MLK2N) |
| 3D printed Parts (~300g PLA/PETG)                 | 5 - 40             | ... |
| Some cables + soldering iron would be<br>useful to connect the servos (not required) |                    |  |
| 2x Googly eyes (strictly required) |                    |  |

*The latest version used a RaspberryPi 5 which is about 80€ with a cooler. But I'm working on getting it as fast on the Pi Zero. 

*If you built this, please send me a link to where you bought the parts, so I can add them to the table.*

### Physical setup
... some pictures & stuff ...

### Setup on the PC
To get the code on your PC running, first download the repo as a .zip and unpack, or clone it to a local folder. <br>
There are requirements.txt files in the respective folders. Those were generated with Python 3.12.3, so might not work exactly the same for other versions. <br>
To execute the Python scripts and try the algorithms provided here, first set up a Python virtual environment (venv) in each of the folders which contain python files. <br>
In a Linux terminal it would be: <br>
if not installed: `sudo apt install python3-venv` <br>
`cd Code_on_PC/` or other folders <br>
`python3 -m venv .venv` creates the virtual environment<br>
`source .venv/bin/activate` activates the venv (has to be executed again after you open a new terminal later on)<br>
`pip install -r requirements.txt` installs the list of packages<br>
 for Windows/Mac it is similar, see here [docs.python.org/3/library/venv.html](https://docs.python.org/3/library/venv.html) <br>
Alternatively you can also install the Python packages manually.

### RaspberryPi setup
I used a RaspberryPi but any other single-board computer should work if it has these features: <br>
- 2 Hardware PWMs to control the servos. (Software PWMs, at least on my Pi, don't work for servos under load)
- Connection to the camera (Picam Zero v1.3 in my case)
- Connection to a PC (preferrably wired to reduce lag, alternatively SSH over local Wi-Fi)

A good tutorial to set up a RaspberryPi with PiOS to then communicate to your PC over your local Wi-Fi via SSH can be found here: [randomnerdtutorials.com/installing-raspbian-lite-enabling-and-connecting-with-ssh](https://randomnerdtutorials.com/installing-raspbian-lite-enabling-and-connecting-with-ssh/) (Skip steps 3 & 4 by already doing them in step 2 as it says. )<br>

I first used a the slower RaspberryPi Zero 2W and later switched to the RaspberryPi 5 because the image detection was too slow. I used a moderately sized deep-learning model to detect the ball. It should be possible to get it to work on the smaller & cheaper Pi Zero with a simpler and lighter detection-algorithm though. On the Pi Zero, the setup is a bit weird because of the out-of-date PiCamera package. So I'll describe the setups seperately:

<table>
  <tr>
    <td valign="top" width="50%">

### Pi Zero 2W setup
Here I have chosen the `Legacy 64-bit Lite` (Debian GNU/Linux 11) version in the Pi Imager shown in the above linked tutorial. <br>
- Open a SSH terminal on the Pi and check the OS version with the command:
```bash
uname -m
```
this should show: `aarch64`. If it shows `armv7l` you choose the 32bit version which will not work, rewrite the image onto the SD card with the 64bit version.<br>
Then run:
```bash
cat /etc/os-release
```
This should show: (if not, the wrong version might have been selected in the Pi Imager)
```plaintext
PRETTY_NAME="Debian GNU/Linux 11 (bullseye)"
NAME="Debian GNU/Linux"
VERSION_ID="11"
VERSION="11 (bullseye)"
VERSION_CODENAME=bullseye
ID=debian
HOME_URL="https://www.debian.org/"
SUPPORT_URL="https://www.debian.org/support"
BUG_REPORT_URL="https://bugs.debian.org/"
```
- Also on the Pi, run the commands: (takes a rew minutes)
```bash
sudo apt update
sudo apt -y upgrade
sudo apt install -y libgl1
sudo sed -i \
  '1i\
# enables hardware PWM on pins GPIO_18, GPIO_19 (Pins 12, 35)\
dtoverlay=pwm-2chan\
# limits camera memory to 320MB, not required on e.g. a Pi 4/5\
dtoverlay=vc4-kms-v3d,cma-320' \
  /boot/config.txt
sudo reboot
```

Once you can connect to the Pi over the terminal, follow these steps: <br>

This restarts the Pi, connect to it again. 
- Download this git repo to your PC (if not already done).
- Copy the folder **Code_on_RaspberryPi** the the /home/USER directory on the Pi.<br>
  USER and DEVICE are whatever you called them in the Pi imager, USER is `pi` by default.<br>
  For this open a <ins>**termina/Powershell on your PC**</ins> and run:<br>
```bash
scp -r path/on/your/PC/to/the/folder/Code_on_RaspberryPi \
USER@DEVICE.local:/home/USER
```
Alternatively you can also copy the folder onto the SD card. 
- Now back to the Pi SSH terminal, check if it has the `Code_on_RaspberryPi` folder by:
```bash
ls
```
this should show the folder: `Code_on_RaspberryPi`
- Run these commands still in the current (`home/pi`) directory:
```bash
sudo apt install -y python3-picamera2 --no-install-recommends
sudo apt install -y python3-venv
cd Code_on_RaspberryPi
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
pip install --upgrade pip
pip install openvino==2025.0.0 opencv-python==4.11.0.86 \
zmq==0.0.0 rpi_hardware_pwm==0.2.2 scipy==1.10.1 numpy==1.19.5
pip install numpy==1.19.5 scikit-optimize==0.9.0
```

  </td>
  <td valign="top" width="50%">

### Pi 5 setup
Here I have chosen the newest 64bit Pi OS with a GUI (Debian GNU/Linux 12) version in the Pi Imager shown in the above linked tutorial. The headless version would need manual installation of the camera driver, but the Pi 5 is fast enough to handle the unused GUI in the background.<br>
- Open a SSH terminal on the Pi and check the OS version with the command:
```bash
uname -m
```
this should show: `...`. If it shows `...` you choose the 32bit version which will not work, rewrite the image onto the SD card with the 64bit version.<br>
Then run:
```bash
cat /etc/os-release
```
This should show: (if not, the wrong version might have been selected in the Pi Imager)
```plaintext
TODO...
```

- Also on the Pi, run the commands: (takes a rew minutes)
```bash
sudo apt update
sudo apt -y upgrade
sudo sed -i \
  '1i\
# enables hardware PWM on pins GPIO_18, GPIO_19 (Pins 12, 35)\
dtoverlay=pwm-2chan\
  /boot/config.txt
sudo reboot
```

Once you can connect to the Pi over the terminal, follow these steps: <br>

This restarts the Pi, connect to it again. 
- Download this git repo to your PC (if not already done).
- Copy the folder **Code_on_RaspberryPi** the the /home/USER directory on the Pi.<br>
  USER and DEVICE are whatever you called them in the Pi imager, USER is `pi` by default.<br>
  For this open a <ins>**termina/Powershell on your PC**</ins> and run:<br>
```bash
scp -r path/on/your/PC/to/the/folder/Code_on_RaspberryPi \
USER@DEVICE.local:/home/USER
```
Alternatively you can also copy the folder onto the SD card. 
- Now back to the Pi SSH terminal, check if it has the `Code_on_RaspberryPi` folder by:
```bash
ls
```
this should show the folder: `Code_on_RaspberryPi`
- Run these commands still in the current (`home/pi`) directory:
```bash
sudo apt install -y python3-picamera2
sudo apt install -y python3-venv
cd Code_on_RaspberryPi
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install openvino opencv-python zmq \
rpi_hardware_pwm scipy numpy scikit-optimize
```

  </td>
  </tr>
</table>

It now shows `(.venv)` at the start of the line in the terminal, which indicated the venv is running ([Read more about venv](https://docs.python.org/3/library/venv.html)). Whenever you open a new terminal, go to the Code-folder with `cd Code_on_RaspberryPi` and activate the venv with `source .venv/bin/activate`. 
- Run this Python script to check the installation:
```bash
python3 check_installation.py
```
It if gives any errors, read it and try re-running the installation commands it might correspond to. 

### Check setup
*TODO, not implemented: Now slide the empty-maze-plate in and put a metal ball on it. Then run the script `python3 check_everything_PC.py` on the PC together with `python3 check_everything_Pi.py` on the Pi while connected to the same Wi-Fi.*

When the check was succesfull, run `python3 pi_calibration.py` on RaspberryPi with the empty-maze-plate still inserted. <br>
It is recommended to run `pi_calibration.py` before every session. It measures the relative position of the camera and adjusts it for lighting conditions. 

## Further plans
- Write a simulation to pretrain a model.
- Pretrain the CNN as part of an autoencoder.
- Make a proper hyperparameter sweep, including the reward-structure.
- Use (implicit) meta-learning to train on different maze layouts and/or with different builds (an algorithm trained on one build/setup might not work on another because of slight imprecisions).
- Cut some costs: Smaller servo motors, cheaper camera, working (faster) Pi Zero setup, ... -> Then build more of them to train in parallel.
- Make some more games in the same style and reuse most of the hardware. 

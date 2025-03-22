# Ballmaze
This project is showcased in ...add link to yt-video/channel...

The goal is to automate playing the ballmaze dexterity game. There are quite a few challanges in this and a lot of things can be improved from the current solution. 

<p align="center">
  <img src="./docs/wood_maze.gif" width="45%" />
  <img src="./docs/my_maze.gif" width="45%" />
</p>

## Want to build one yourself?

I'll try my best to give some instructions here, but some previous experience with a RaspberryPi or similar and a little experience in programming in python would surely help. And of couse a great interest in robotics/machine learning :) <br>
In total the materials cost about 50 - 90 $/€ depending on whether you or someone you know has a 3D printer, or you have to order the 3D printed parts from somewhere. 

### List of materials
Most parts can be replaced by similar ones or whatever you might already have. 

| Part                                              | Price ($/€ approx) | Where to buy |
|---------------------------------------------------|--------------------|--------------|
| 1x RaspberryPi Zero 2W (or better)                | 15                 | [1](https://www.mouser.ch/ProductDetail/358-SC0721) |
| 2x Servo (e.g. SER0050)                           | 5 (x2)             | [1](https://www.mouser.ch/ProductDetail/426-SER0050) |
| 1x Pi Camera V1.3                                 | 7                  | [1](https://www.mouser.ch/ProductDetail/713-114110127) |
| 1x Pi Camera Cable 300mm                          | 2                  | [1](https://www.mouser.ch/ProductDetail/358-SC1129) |
| 1x uSD card 32GB+                                 | 5                  | [1](https://www.mouser.ch/ProductDetail/358-SC1628) |
| 1x 5V 2A+ USB charger (likely already got one)    | 5                  | [1](https://www.mouser.ch/ProductDetail/490-SWI10B-5-EW-I38) |
| 1x USB Cable to power Pi (micro USB for Pi Zero)  | 2                  | [1](https://www.mouser.ch/ProductDetail/530-SC-2AMK003F) |
| A few metal balls with diameter ~6mm              | 5                  | [1](https://www.amazon.com/0-236-Precision-Chrome-Steel-Bearing/dp/B07L8MLK2N) |
| 2x Nuts & bolts...                                | xx                 | [1]() |
| 3D printed Parts (~300g PLA/PETG)                 | 5 - 40             | [1](https://www.sculpteo.com) [2](https://craftcloud3d.com/) [3](https://jlc3dp.com/3d-printing-quote) |

*If you built this, please send me a link to where you bought the parts, so I can add them to the table.*

### Physical setup
... some pictures & stuff ...

### Setup on the PC
To get the code on your PC running, first download the Repo as a .zip and unpack, or clone it to a local folder. <br>
There are requirements.txt files in the respective folders, which were generated with Python 3.12.3. Those might not work exactly the same in the future. <br>
To execute the python scripts and try the algorithms provided here, first set up a venv in each of the folders which contain python files. <br>
In a Linux terminal it would be (for Windows/Mac it is similar, see here [docs.python.org/3/library/venv.html](https://docs.python.org/3/library/venv.html)): <br>
if not installed: `sudo apt install python3-venv` <br>
`cd Code_on_PC/` or other folders <br>
`python3 -m venv .venv` creates the virtual environment<br>
`source .venv/bin/activate` activates the venv (has to be executed again after you open a new terminal later on)<br>
`pip install -r requirements.txt` installs the list of packages<br>
Alternatively you can also install the Python packages manually.

### RaspberryPi setup
I used a RaspberryPi Zero 2w, so Pi 3,4 or 5 should work too. Or any other single-board computer should work if it has the features I use from the RaspberryPi: <br>
- 2 Hardware PWMs to control the servos. (Software PWMs, at least on my Pi are hot garbage)
- Connection to the camera (Picam Zero v1.3 in my case)
- Enough computation power to run 4fps object detection on at least 128x128 images.
- Connection to a PC (SSH over local Wi-Fi in my case, USB also possible)

A good tutorial to set up a RaspberryPi with PiOS to then communicate to your PC over your local Wi-Fi via SSH can be found here: [randomnerdtutorials.com/installing-raspbian-lite-enabling-and-connecting-with-ssh](https://randomnerdtutorials.com/installing-raspbian-lite-enabling-and-connecting-with-ssh/) (Skip steps 3 & 4 by already doing them in step 2 as it says. )<br>
I chose the PiOS Legacy Lite version, but if you haven't set up a RaspberryPi before maybe choose the non-Lite version so you have the option to connect a monitor, keyboard and mouse which makes it easier if something went wrong. 

If you can now connect to the Pi over SSH, next download a copy of this repo to your PC and copy/move the folder [Code_on_RaspberryPi](Code_on_RaspberryPi) onto the Pi. <br>
There are a few different ways to do this, with the Terminal/Powershell on your PC that would be simply: <br>
`scp -r path/on/your/PC/to/the/folder/Code_on_RaspberryPi USER@DEVICE.local:/home/USER` <br>
(replace USER, DEVICE & path/on/your/PC/to/...)

In the project folder on the Pi (e.g. /home/USER/Code_on_RaspberryPi) set up a Python venv (optional but recommended, [Read more about venv](https://docs.python.org/3/library/venv.html)). Then install the packages listed in requirements.txt with `pip install -r requirements.txt` in the project folder (with the venv enabled). <br> 

For the hardware PWMs and PiCamera you have to edit the file /boot/config.txt on the Pi. Do this with: <br>
`sudo nano /boot/config.txt` <br>
Go to the bottom of the file and add the line(s): <br>
dtoverlay=pwm-2chan # enables hardware PWM on pins GPIO_18, GPIO_19 (Pins 12, 35) <br>
dtoverlay=vc4-kms-v3d,cma-320 # limits camera memory to 320MB, not required on e.g. a Pi 4/5

### Check setup
Now slide the empty-maze-plate in and put a metal ball on it. Then run the script `check_everything_PC.py` on the PC together with `check_everything_Pi.py` on the Pi while connected to the same Wi-Fi. <br>
If anything from the setup except the Pi and PC is missing, no worries, it will just test the rest. 

If everything works, nice :)

## Current progress and goals
The sort of end goal is to come up with a solution/algorithm which will train on one or more given maze layout(s) for a fixed ammount of time. Then it will get a new maze layout it hasn't seen before and has to complete that in the minimum ammount of time. 

### Attempt 1 - SAC with 4 state variables
*Not the first appempt, but the first one that sort of worked :)* <br>
I used the RL (reinforcement learning) algorithm SAC (Soft Actor-Critic) to control the ball. The algorithm just gets the current ball position in the maze (x,y in 0...1), the current tilt angle of the maze ($\theta_x$, $\theta_y$ in -1...1), and a reward. It then can change the two angles up to a maximum of a fixed portion of the max-angle. It gets a reward if the current position is further trough the maze than it was before in this episode. It gets punished/negative reward for falling in a hole and then some smaller adjustments. 

### Attempt 2 - SAC with CNN + 4 variables state-space
...

### Attempt 3 - Fitting a dynamics model and training in simulation
...




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
| 2x Servo (e.g. SER0050)                           | 5                  | [1](https://www.mouser.ch/ProductDetail/426-SER0050) |
| 1x Pi Camera V1.3                                 | 7                  | [1](https://www.mouser.ch/ProductDetail/713-114110127) |
| 1x Pi Camera Cable 300mm                          | 2                  | [1](https://www.mouser.ch/ProductDetail/358-SC1129) |
| 1x uSD card 32GB+                                 | 5                  | [1](https://www.mouser.ch/ProductDetail/358-SC1628) |
| 1x USB Cable to power Pi (micro USB for Pi Zero)  | 2                  | [1](https://www.mouser.ch/ProductDetail/530-SC-2AMK003F) |
| a few metal balls diameter ~6mm                   | 5                  | [1](https://www.amazon.com/0-236-Precision-Chrome-Steel-Bearing/dp/B07L8MLK2N) |
| 2x Nuts & bolts...                                | xx                 | [1]() |
| 3D printed Parts (~300g PLA/PETG)                 | 6 - 45             | [1](https://www.sculpteo.com) [2](https://craftcloud3d.com/) [3](https://jlc3dp.com/3d-printing-quote) |

*If you built this, please send me a link to where you bought the parts, so I can add them to the table.*

### Physical setup
... some pictures & stuff ...

### Software setup
How to set up the RaspberryPi is described in [Code_on_RaspberryPi/README.md](Code_on_RaspberryPi/README.md) <br>

To get the code on your PC running, first download the Repo as a .zip and unpack, or clone it to a local folder. <br>
There are requirements.txt files in the respective folders, which were generated with Python 3.12.3. Those might not work exactly the same in the future. <br>
To execute the python scripts and try the algorithms provided here, first set up a venv in each of the folders which contain python files. <br>
In a Linux terminal it would be: <br>
if not installed: `sudo apt install python3-venv` <br>
`cd Code_on_PC/` or other folders <br>
`python3 -m venv .venv` <br>
`source .venv/bin/activate` <br>
`pip install -r requirements.txt` <br>
On Windows/Mac it would be similar, see here: [https://docs.python.org/3/library/venv.html](https://docs.python.org/3/library/venv.html). Or install the python packages manually. 

### Check setup
Now slide the empty-maze-plate in and put a metal ball on it. Then run the script `check_everything_PC.py` on the PC and `check_everything_Pi.py` on the Pi while connected to the same Wi-Fi. <br>
If anything from the setup except the Pi and PC is missing, no worries, it will just test the rest. 

If everything works, nice :)





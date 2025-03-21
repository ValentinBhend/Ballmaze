I used a RaspberryPi Zero 2w, so Pi 3,4 or 5 should work too. Or any other single-board computer should work if it has the features I use from the RaspberryPi: <br>
- 2 Hardware PWMs to control the servos. (Software PWMs, at least on my Pi are hot garbage)
- Connection to the camera (Picam Zero v1.3 in my case)
- Enough computation power to run 4fps object detection on 128x128 images.
- Connection to a PC (SSH over LAN in my case, USB also possible)

#### RaspberryPi Setup
A more comprehensive guide can be found on the official website: [RaspberryPi - Getting started](https://www.raspberrypi.com/documentation/computers/getting-started.html)
1. Download the RaspberryPi Imager here: [https://www.raspberrypi.com/software/](https://www.raspberrypi.com/software/)
2. Choose any Pi OS, I choose the Legacy Lite version. Lite means no GUI which might make it a little faster but creates more pain of anything goes wrong.
3. Enable SSH and give it the local Wi-Fi credentials (I had problems with my router so used my phone mobile-hotspot instead).
4. Write it to the SD card, plug the Pi in and connect to it over your Wi-Fi with SSH. 
5. Execute the commands in pi_setup.sh in the Pi. I tested them on my Pi Zero 2w, this might not work exacly as it on other versions.
6. Edit the /boot/config.txt file (in the command line):
   execute in the Pi terminal: `sudo nano /boot/config.txt`
   Go to the bottom of the file and add the lines:
   dtoverlay=pwm-2chan # enables hardware PWM on pins GPIO_18, GPIO_19 (Pins 12, 35)
   dtoverlay=vc4-kms-v3d,cma-320 # limits camera memory to 320MB, not required on e.g. a Pi 4/5
7. Test the camera with `python3 Test_Camera.py`. Then look at the image in the Pi GUI or get the image [to your PC using SCP](https://www.pluralsight.com/resources/blog/cloud/ssh-and-scp-howto-tips-tricks).
8. Test the PWM Servo control with `python3 Test_Servos.py`, they should move as described in the prints.

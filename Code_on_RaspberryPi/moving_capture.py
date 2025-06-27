from Camera import Camera
from Servos import Servos
import threading
import time
import os

cam = Camera()
servos = Servos()
def move():
    while True:
        print("starting next move-loop")
        servos.temp_play()

thread = threading.Thread(target=move)


print("input foldername")
foldername = input()
path = "capture_datasets/" + foldername + "/"
if os.path.isdir(path):
    assert False, "folder already exists"
os.mkdir(path)

thread.start()

for i in range(2000):
    filename = f"{path}img{i}.png"
    cam.capture_save(filename)
    print(f"image {i} taken")
    time.sleep(0.5)




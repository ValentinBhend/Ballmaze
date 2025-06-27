import pickle
import numpy as np
import cv2
from Camera import Camera
from Servos import Servos
from Detector import Detector
import time
import subprocess


class HardwareController:
    calibration_filename = "PiCalibration.pkl"
    def __init__(self):
        with open(self.calibration_filename, "rb") as f:
            self.calibration = pickle.load(f)
        self.camera = Camera(
            AnalogueGain = self.calibration["AnalogueGain"], 
            ExposureTime = self.calibration["ExposureTime"])
        self.servos = Servos(mode="100hz")
        self.detector = Detector()

        offset = 3/101 + 1/101 # r_ball + wall at the side
        pts_dst = np.array([
            [offset, offset],      # point a'
            [offset, 1-offset], # TODO: check if BR & TL switched
            [1-offset, 1-offset],      # point c'
            [1-offset, offset]       # point d'
        ], dtype=np.float32)
        pts_src = self.calibration["image_corners"]
        self.position_transform_matrix = cv2.getPerspectiveTransform(pts_src, pts_dst)
        servo_setpoints = self.calibration["servo_setpoints"]
        target = np.array([[-1.0,-1.0], [-1.0,1.0], [1.0,1.0], [1.0,-1.0]], dtype=np.float32)
        self.setpoint_transform_matrix = cv2.getPerspectiveTransform(target, servo_setpoints)
        #self.detector_reset_count = 0

    def tests(self):
        setpoint = np.zeros(2).astype(np.float32)
        for _ in range(200):
            thread = self.move_servo(*setpoint, speed=3)
            position = None
            while position is None:
                position = self.get_position()
            setpoint -= 0.05 * position
            setpoint = np.clip(setpoint, -1.0, 1.0)

    def move_servo(self,x,y,speed=1):
        points_in = np.array([[[x,y]]], dtype=np.float32)
        setpoints = cv2.perspectiveTransform(points_in, self.setpoint_transform_matrix)[0,0]
        return self.servos.smooth(*setpoints, speed=speed)

    def move_servo_blocking(self,x,y,speed=1):
        thread = self.move_servo(x, y, speed=speed)
        thread.join()

    def get_position(self, conf=0.001, save=False):
        #self.detector_reset_count += 1
        #if self.detector_reset_count > 1000:
        #    self.detector = init_free_Detector(Det=self.detector)
        #    self.detector_reset_count = 0
        #T = self.get_cpu_temp()
        #if T > 65:
        #    print(f"\33[31mCPU overheating during play: {T}>65\33[0m")
        #    time.sleep(1)
        #print(T)

        arr = self.camera.capture_np(save=save)
        xywhn = self.detector.get_xywhn(arr, conf=conf)
        if xywhn is None:
            print("no detect!")
            return None
        position_camera = xywhn[:2].reshape(1, 1, 2)
        position_transformed = cv2.perspectiveTransform(position_camera, self.position_transform_matrix)[0,0]
        return position_transformed*2-1

    def reset_special_solve(self):
        A = [[1,-1]]
        B = [[-1,-1]]
        C = [[1,1]]
        D = [[-1,1]]
        reset_actions = np.array(
            B*10+
            A*5+
            B*5+
            D*5+
            B*5+
            D*5+
            C*10+
            D*5+
            C*5+
            D*10+
            B*5+
            A*5+
            B*10+
            A*5+
            C*5+
            A*5+
            B*8+
            A*5+
            C*5+
            A*5+
            C*10+
            D*10+
            B*5+
            A*5+
            B*10+
            D*10+
            C*10
            )
        position = 0
        while position is not None:
            for act in reset_actions:
                self.move_servo_blocking(*act, speed=3.5)
            position = self.get_position(conf=0.02)

    def reset(self):
        #self.detector = init_free_Detector(Det=self.detector)
        #self.detector_reset_count = 0
        #self.reset_special_solve() ############ ONLY FOR THE MAZE WITH NO HOLES!! comment out otherwise
        position = None
        while position is None:
            print("starting reset")
            self.servos.smooth_blocking(0.5,0.5,speed=0.5)
            time.sleep(0.5)
            self.servos.smooth_blocking(0.7,-1,speed=0.8)
            time.sleep(1)
            self.servos.smooth_blocking(-1,-1,speed=2)
            time.sleep(1)
            self.servos.smooth_blocking(-1,0.7,speed=1)
            time.sleep(1)
            self.servos.smooth_blocking(0.7,0.7,speed=0.5)
            time.sleep(1)
            self.move_servo_blocking(1,-1,speed=1)
            time.sleep(0.2)
            self.move_servo_blocking(1,1,speed=1.5)
            time.sleep(0.2)
            self.move_servo_blocking(0,0,speed=1)
            time.sleep(1)

            position = self.get_position(conf=0.05)
        #T = self.get_cpu_temp()
        #while T>60:
        #    print(f"\33[31mCPU temp too high after reset: {T}>60\33[0m")
        #    time.sleep(2)
        #    T = self.get_cpu_temp()
        #print(f"CPU temp: {T}")
        return position

    def get_image(self): # only for debugging
        raise NotImplementedError
        return np.zeros((128,128,3))
    
    @staticmethod
    def get_cpu_temp():
        output = subprocess.check_output(["vcgencmd", "measure_temp"]).decode()
        temp_str = output.split('=')[1].split("'")[0]
        return float(temp_str)


if __name__ == "__main__":
    HC = HardwareController()
    HC.reset()


import os
import pickle
import time
import numpy as np
import cv2
from scipy.optimize import minimize
from skopt import gp_minimize
from Camera import Camera
from Servos import Servos
from Detector import Detector
import csv # temp


class PiCalibration:
    filename = "PiCalibration.pkl"
    default_calibration = {
        "AnalogueGain": 30,
        "ExposureTime": 25_000,
        "image_corners": np.array([[1.0,1.0],[1.0,0.0],[0.0,0.0],[0.0,1.0]], dtype=np.float32), # no np array bc of some wired dependancy issues with np & camera
        "servo_setpoints": np.array([[-0.3,-0.3], [-0.3,0.4], [0.4,0.4], [0.4,-0.3]], dtype=np.float32) # TODO: check if still a problem
    }
    def __init__(self):
        print("INSERT EMPTY-MAZE-PLATE AND PUT THE BALL ON IT")
        self.read_last_calibration()
        self.current_calibration = self.last_calibration.copy()
        self.camera = Camera(
            AnalogueGain = self.last_calibration["AnalogueGain"], 
            ExposureTime = self.last_calibration["ExposureTime"])
        self.servos = Servos()
        self.detector = Detector()

    def run(self):
        """self.current_calibration["servo_setpoints"] = np.array([[0.0, -0.2],
                                                                [-0.2, 0.4],
                                                                [0.4, 0.4],
                                                                [0.4, -0.2]], dtype=np.float32)"""
        
        self.camera_gain_adjust(n_calls=30) # only rougly, good enough to set servo setpoints properly
        #self.current_calibration["AnalogueGain"] = 14
        #self.servo_setpoint_adjust()
        #self.camera_gain_exposure_adjust(n_calls=100)
        self.write_current_calibration()
        print("Calibration finished")
        #self.control()
    
    def control(self):
        print("IT SHOULD NOW GO TO ALL CORNERS 3 TIMES, START WITH ENTER")
        input()
        max_sets = np.array([[-1.0,-1.0], [-1.0,1.0], [1.0,1.0], [1.0,-1.0]], dtype=np.float32)
        for _ in range(3):
            for sp in max_sets:
                self.adjusted_servo_smooth_blocking(*sp, speed=0.2)
                time.sleep(2)

    def read_last_calibration(self):
        if not os.path.exists(self.filename):
            print("No previous calibration found, staring from default values.")
            with open(self.filename, "wb") as f:
                pickle.dump(self.default_calibration, f)

        with open(self.filename, "rb") as f:
            self.last_calibration = pickle.load(f)
            print(f"using last calibration: {self.last_calibration}")

    def write_current_calibration(self):
        with open(self.filename, "wb") as f:
            pickle.dump(self.current_calibration, f)
        print("current calibration written")

    def camera_gain_adjust(self, n_calls=100):
        gains = []
        losses = []
        def camera_gain_evaluate(AnalogueGain):
            AnalogueGain = np.array(AnalogueGain)
            self.camera.change_config(AnalogueGain=AnalogueGain, ExposureTime=None)
            repetitions = 1
            print(f"GAIN: {AnalogueGain}")
            loss = 0
            test_setpoints = np.array([[-1,-1], [-1,1], [1,1], [1,-1]])
            for _ in range(repetitions):
                for i,servo_setpoint in enumerate(test_setpoints):
                    confs = []
                    #thread = self.adjusted_servo_smooth(*servo_setpoint, speed=0.5)
                    self.adjusted_servo_smooth_blocking(*servo_setpoint, speed=3)
                    time.sleep(2)
                    t0 = time.time()
                    #while thread.is_alive():
                    while time.time() - t0 < 0.5:
                        arr = self.camera.capture_np()
                        xywhn, conf = self.detector.eval_image(arr)
                        dist = np.linalg.norm(xywhn[:2] - self.current_calibration["image_corners"][i])
                        #print(dist)
                        if dist > 0.015:
                            conf = 1e-12
                        confs.append(conf)
                        time.sleep(0.02)
                    confs = np.array(confs)
                    #print(f"confs: {confs}")
                    loss -= np.mean(np.log(confs))
            loss /= (repetitions * len(test_setpoints))
            print(f"loss {loss}")
            gains.append(AnalogueGain[0])
            losses.append(loss)
            return loss

        self.adjusted_servo_smooth_blocking(0,0, speed=0.5)
        bounds = [(10.0, 80.0)]
        res = gp_minimize(
            func=camera_gain_evaluate, 
            dimensions=bounds, 
            x0=[self.current_calibration["AnalogueGain"]], 
            n_calls=n_calls, 
            noise=0.02)
        print("Optimized Gain:", res.x[0])
        print("Minimum Function Value:", res.fun)
        self.current_calibration["AnalogueGain"] = res.x[0]
        with open("gain_saves.csv", "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(gains)
            writer.writerow(losses)
        """with open("gain_saves.csv", "r") as f:
            reader = csv.reader(f)
            content = [list(map(float, row)) for row in reader]
            print(f"content: {content}")"""

    def camera_gain_exposure_adjust(self, n_calls=100):
        def camera_gain_exposure_evaluate(params):
            AnalogueGain, ExposureTime = params
            AnalogueGain = np.array(AnalogueGain)
            ExposureTime = np.array(ExposureTime)
            self.camera.change_config(AnalogueGain=AnalogueGain, ExposureTime=ExposureTime)
            repetitions = 3
            print(f"AnalogueGain: {AnalogueGain}, ExposureTime: {ExposureTime}")
            loss = 0
            test_setpoints = np.array([[-1,-1,1], [1,1,1], [-1,-1,1], [1,1,1], 
                                       [-1,1,1], [1,-1,1], [-1,1,1], [1,-1,1], 
                                       [0,0,1], [1,0,1], [0,0,1], [0,1,1],  
                                       [0,0,1], [-1,0,1], [0,0,1], [0,-1,1]])
            for _ in range(repetitions):
                for x,y,speed in test_setpoints:
                    confs = []
                    thread = self.adjusted_servo_smooth(x,y, speed=speed)
                    while thread.is_alive():
                        arr = self.camera.capture_np()
                        xywhn, conf = self.detector.eval_image(arr)
                        confs.append(conf)
                    confs = np.array(confs)
                    #print(f"confs: {confs}")
                    loss -= np.mean(np.log(confs))
            loss /= repetitions
            print(f"loss {loss}")
            return loss

        bounds = [(1.0, 300.0), (1_000.0, 50_000.0)]
        res = gp_minimize(
            func=camera_gain_exposure_evaluate, 
            dimensions=bounds, 
            x0=[self.current_calibration["AnalogueGain"],self.current_calibration["ExposureTime"]], 
            n_calls=n_calls, 
            noise=2.0)
        print(f"Optimized AnalogueGain: {res.x[0]}, Optimized ExposureTime: {res.x[1]}")
        print(f"Minimum Function Value: {res.fun}")
        self.current_calibration["AnalogueGain"] = res.x[0]

    def servo_setpoint_adjust(self):
        assert False, "redo this ..."
        max_sets = np.array([[-1.0,-1.0], [-1.0,1.0], [1.0,1.0], [1.0,-1.0]], dtype=np.float32)
        image_corners = self.find_image_corners(max_sets)
        self.current_calibration["image_corners"] = image_corners
        print(f"found image_corners: {image_corners}")
    
    def find_optimal_servo_setpoints(self):
        image_corners = self.current_calibration["image_corners"]
        def opt_setpoints_rough(params):
            xm, a = params
            if xm - a < -1 or xm + a > 1:
                return 3 + a
            setpoints = np.array([[xm-a,xm-a], [xm-a,xm+a], [xm+a,xm+a], [xm+a,xm-a]], dtype=np.float32)
            corner_positions = np.zeros((4,2), dtype=np.float32)
            for i in range(4):
                self.servos.smooth_blocking(*setpoints[i], speed=0.3)
                time.sleep(1)
                arr = self.camera.capture_np()
                xywhn, conf = self.detector.eval_image(arr)
                corner_positions[i] = xywhn[:2]
            image_distance = np.sum(np.linalg.norm(corner_positions - image_corners, axis=1))
            cost = a
            if image_distance > 0.2:
                print(f"dist too high: {image_distance}")
                return 3 + a
            print(f"cost: {cost}")
            return cost
        
        def opt_setpoints(params):
            xm, ym, a, b = params
            if xm - a < -1 or xm + a > 1 or ym - b < -1 or ym + b > 1:
                return 3 + a + b
            setpoints = np.array([[xm-a,ym-b], [xm-a,ym+b], [xm+a,ym+b], [xm+a,ym-b]], dtype=np.float32)
            corner_positions = np.zeros((4,2), dtype=np.float32)
            for i in range(4):
                self.servos.smooth_blocking(*setpoints[i], speed=0.3)
                time.sleep(2)
                arr = self.camera.capture_np()
                xywhn, conf = self.detector.eval_image(arr)
                corner_positions[i] = xywhn[:2]
            image_distance = np.sum(np.linalg.norm(corner_positions - image_corners, axis=1))
            cost = a + b
            if image_distance > 0.2:
                print(f"dist too high: {image_distance}")
                return 3 + a + b
            print(f"cost: {cost}")
            return cost
        
        bounds = [(-1.0, 0.8), (0.0, 1.0)]
        x0 = [[0.0, 0.5]]
        res = gp_minimize(
            func=opt_setpoints_rough, 
            dimensions=bounds, 
            x0=x0, 
            n_calls=30, 
            #noise=0.0
            )
        xm0, a0 = res.x
        #xm0, a0 = 0.08495746738108645, 0.2183916126025503
        
        xl = max(-1,xm0-0.2)
        xh = min(1,xm0+0.2)
        al = max(0,a0-0.2)
        ah = min(2,a0+0.2)
        bounds = [(xl,xh), (xl,xh), (al,ah), (al,ah)]
        x0 = [[xm0,xm0,a0,a0]]
        res = gp_minimize(
            func=opt_setpoints, 
            dimensions=bounds, 
            x0=x0, 
            n_calls=30, 
            #noise=0.0
            )
        xm, ym, a, b = res.x
        
        servo_setpoints = np.array([[xm-a,ym-b], [xm-a,ym+b], [xm+a,ym+b], [xm+a,ym-b]], dtype=np.float32)
        self.current_calibration["servo_setpoints"] = servo_setpoints
        print(f"found servo_setpoints: {servo_setpoints}")

    def find_image_corners(self, max_sets):
        servo_setpoints = max_sets.copy()
        image_corners = np.zeros((4,2), dtype=np.float32)
        self.servos.smooth_blocking(*servo_setpoints[0], speed=1)
        time.sleep(2)
        arr = self.camera.capture_np()
        xywhn, conf = self.detector.eval_image(arr)
        image_corners[0] = xywhn[:2]
        image_corners[1], servo_setpoints[1] = self.find_next_corner(image_corners[0], servo_setpoints[0], servo_setpoints[1])
        image_corners[2], servo_setpoints[2] = self.find_next_corner(image_corners[1], servo_setpoints[1], servo_setpoints[2])
        image_corners[3], servo_setpoints[3] = self.find_next_corner(image_corners[2], servo_setpoints[2], servo_setpoints[3])
        image_corners[0], servo_setpoints[0] = self.find_next_corner(image_corners[3], servo_setpoints[3], servo_setpoints[0])
        print(f"found image corners: {image_corners}")
        return image_corners

    def find_next_corner(self, pos0, set0, set1_max):
        substeps = 10
        confidence_cutoff = 0.2
        min_plausible_corner_distance = 0.5
        pos = pos0.copy()
        for i in range(1, substeps+1):
            setpoint = set0 * (1 - i/substeps) + set1_max * (i/substeps)
            self.servos.smooth_blocking(*setpoint, speed=1)
            time.sleep(0.1)
            arr = self.camera.capture_np()
            xywhn, conf = self.detector.eval_image(arr)
            pos = xywhn[:2]
            if conf >= confidence_cutoff and np.linalg.norm(pos0 - pos) >= min_plausible_corner_distance:
                break
        time.sleep(5)
        arr = self.camera.capture_np()
        xywhn, conf = self.detector.eval_image(arr)
        pos = xywhn[:2]
        return pos, setpoint
    
    def adjusted_servo_smooth(self, x, y, speed):
        points_in = np.array([[[x,y]]], dtype=np.float32)
        servo_setpoints = np.array(self.current_calibration["servo_setpoints"], dtype=np.float32)
        target = np.array([[-1,-1], [-1,1], [1,1], [1,-1]], dtype=np.float32)

        setpoint_transform_matrix = cv2.getPerspectiveTransform(target, servo_setpoints)
        setpoints = cv2.perspectiveTransform(points_in, setpoint_transform_matrix)[0,0]
        #setpoints = self.linearize_servo_setpoints(setpoints)
        return self.servos.smooth(*setpoints, speed=speed)
    
    def adjusted_servo_smooth_blocking(self, x, y, speed):
        thread = self.adjusted_servo_smooth(x, y, speed)
        thread.join()
    
    def linearize_servo_setpoints(self, setpoints):
        assert False, "linearize_servo_setpoints need to be changed..."
        x, y = setpoints
        Ax = 0.14 # experimantal
        Ay = 0.12 # experimantal
        x = -Ax * x**2 + x + Ax
        y = -Ay * y**2 + y + Ay
        return np.array([x,y])


if __name__ == "__main__":
    print("starting calibration")
    calibration = PiCalibration()
    calibration.run()

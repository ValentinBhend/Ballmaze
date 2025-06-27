from picamera2 import Picamera2
import time
import numpy as np
import cv2

class Camera:
    format_configs = {"size": (128,128),"format":"RGB888"} #    YUV420
    def __init__(self, ExposureTime=25000, AnalogueGain=64) -> None:
        self.picam2 = Picamera2()
        #camera_config = self.picam2.create_preview_configuration(main=self.format_configs)
        camera_config = self.picam2.create_video_configuration(main=self.format_configs)
        self.picam2.configure(camera_config)
        self.picam2.set_controls({"ExposureTime": ExposureTime, "AnalogueGain": AnalogueGain})
        self.picam2.set_controls({"FrameDurationLimits": (10000, 10000)}) ##########
        self.picam2.start()
        print({"ExposureTime": ExposureTime, "AnalogueGain": AnalogueGain})
        time.sleep(2)
        print("\033[32mCamera is ready\033[0m")

    def change_config(self, ExposureTime: int, AnalogueGain: int) -> None:
        current = {}
        if ExposureTime is not None:
            current["ExposureTime"] = ExposureTime
        if AnalogueGain is not None:
            current["AnalogueGain"] =  AnalogueGain
        self.picam2.set_controls(current)

    def test_img(self,filename: str) -> None:
        self.picam2.capture_file(filename)

    def capture_np(self, save=False) -> np.ndarray:
        arr = self.picam2.capture_array()
        if save:
            print("saving img")
            cv2.imwrite(f"play_capture/{int(time.time()*1000)}.png", arr)
        return arr

    def speed_test(self) -> None:
        N = 10000
        T_rested = np.zeros(N)
        T_repeat = np.zeros(N)
        arr = self.capture_np()
        for i in range(N):
            t0 = time.perf_counter()
            arr = self.capture_np()
            t1 = time.perf_counter()
            T_repeat[i] = t1-t0
        print(f"max repeat capture: {1000*np.mean(T_repeat):.4f}ms +/- {1000*np.std(T_repeat):.4f}ms")
        return
        for i in range(N):
            time.sleep(1)
            t0 = time.time()
            arr = self.capture_np()
            t1 = time.time()
            T_rested[i] = t1-t0
        print(f"rested capture time: {1000*np.mean(T_rested):.4f}ms +/- {1000*np.std(T_rested):.4f}ms")


if __name__ == "__main__":
    cam = Camera()
    cam.test_img("test_img_vid.png")
    #cam.test_img("test_img5.png")
    #cam.capture_np()
    #cam.speed_test()
    #cam.capture_save("iso_img_test.png")



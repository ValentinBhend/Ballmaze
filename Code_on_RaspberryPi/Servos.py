from rpi_hardware_pwm import HardwarePWM
import time
from threading import Thread

class Servos:
    def __init__(self, mode="50hz"):
        self.mode = mode
        if mode=="50hz":
            self.pwm1 = HardwarePWM(pwm_channel=0, hz=50, chip=0)
            self.pwm2 = HardwarePWM(pwm_channel=1, hz=50, chip=0)
            self.v0, self.v1 = 6, 11
        elif mode=="100hz":
            self.pwm1 = HardwarePWM(pwm_channel=0, hz=100, chip=0)
            self.pwm2 = HardwarePWM(pwm_channel=1, hz=100, chip=0)
            self.v0, self.v1 = 12, 22
        else:
            assert False, f"invalid mode: {mode}"
        self.pwm1.start(2)
        self.pwm2.start(2)
        self.x = -0.5
        self.y = -0.5
        self.set(self.x, self.y)
        time.sleep(1)
    
    def set(self,x,y):
        assert (x<=1 and x>=-1 and y<=1 and y>=-1), "set x,y between -1 and 1"
        dc1 = (self.v1-self.v0)*0.5*x + (self.v1+self.v0)*0.5
        dc2 = (self.v1-self.v0)*0.5*y + (self.v1+self.v0)*0.5
        self.pwm1.change_duty_cycle(dc1)
        self.pwm2.change_duty_cycle(dc2)
    
    def smooth_blocking_pizero(self, x1, y1, speed=1):
        x0 = self.x
        y0 = self.y
        T = 0.5 / speed
        N_steps = int(T/T_step)
        for i in range(1, N_steps+1):
            t_start = time.monotonic()
            x = x0 + (x1 - x0) * (i / N_steps)
            y = y0 + (y1 - y0) * (i / N_steps)
            self.set(x, y)
            elapsed = time.monotonic() - t_start
            time.sleep(max(0, T_step - elapsed))
        self.x = x
        self.y = y
    
    def smooth_blocking(self, x1, y1, speed=1):
        x0 = self.x
        y0 = self.y
        T = 0.5 / speed
        if self.mode == "50hz":
            T_step = 0.02
        elif self.mode == "100hz":
            T_step = 0.01
        N_steps = int(T/T_step)
        assert N_steps>0, "speed too fast for servos"
        for i in range(1, N_steps+1):
            t_start = time.monotonic()
            x = x0 + (x1 - x0) * (i / N_steps)
            y = y0 + (y1 - y0) * (i / N_steps)
            self.set(x, y)
            elapsed = time.monotonic() - t_start
            time.sleep(max(0, T_step - elapsed))
        self.x = x
        self.y = y

    def smooth(self,x1,y1,speed=1):
        thread = Thread(target=self.smooth_blocking, args=(x1, y1, speed))
        thread.start()
        return thread

    def stop(self):
        self.smooth(-0.5, -0.5)
        self.pwm1.stop()
        self.pwm2.stop()

    def temp_play(self):
        #self.reset()
        self.smooth(0.45,0.82,speed=0.2)
        time.sleep(0.2)
        self.smooth(0.45,0.45,speed=1)
        self.smooth(0.45,0.82,speed=1)
        time.sleep(0.4)
        self.smooth(0.45,0.65,speed=0.5)
        time.sleep(0.8)
        self.smooth(0.7,0.82,speed=0.8)
        self.smooth(0.45,0.45,speed=0.5)
        time.sleep(0.5)
        self.smooth(0.82,0.45,speed=0.5)
        time.sleep(0.2)
        self.smooth(0.45,0.82,speed=0.5)
        time.sleep(0.2)

if __name__ == "__main__":
    def check_smoothness_range(servos):
        speeds = [0.5, 1, 2, 3, 4, 5]
        for speed in speeds:
            print(f"speed: {speed}")
            servos.smooth_blocking(-1,-1)
            servos.smooth_blocking(1,1)

    x,y = 0,0

    servos = Servos()
    servos.set(x,y)
    print("50hz set")
    #del servos
    time.sleep(2)
    servos = Servos(mode="100hz")
    servos.set(x,y)
    print("100hz set")
    time.sleep(2)


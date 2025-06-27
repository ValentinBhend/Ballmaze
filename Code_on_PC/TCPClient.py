import zmq
import pickle
import numpy as np


class TCPClient:
    # run `ifconfig` in the Pi terminal to get the IP (under wlan0 -> inet)
    # TODO: find a way to find the Pi IP automatically. 
    def __init__(self, PiIP="192.168.10.2"): # TODO: Replace with actual IP
        print(f"Connecting to IP: {PiIP} ...")
        context = zmq.Context()
        self.req_socket = context.socket(zmq.REQ)
        self.req_socket.connect(f"tcp://{PiIP}:5555")
        self.check_connection()

    def set_xy_get_position(self, x, y, speed=1, save_img=False):
        if save_img:
            cmd = f"set_servo_get_position_save_img {x:2f} {y:2f} {speed:2f}"
        else:
            cmd = f"set_servo_get_position {x:2f} {y:2f} {speed:2f}"
        data = self._send_str(cmd)
        return self.data_to_xy(data)

    def get_position(self):
        data = self._send_str("get_position")
        return self.data_to_xy(data)

    def reset(self):
        data = self._send_str("reset")
        return self.data_to_xy(data)

    def calibrate(self):
        data = self._send_str("calibrate")
        print(f"Calibration answer: {data}")
    
    def check_connection(self):
        data = self._send_str("dummy_request")
        if data == "dummy_answer":
            print("\033[32mTCP connection to the Pi working\033[0m")
            return True
        else:
            print(f"\033[91mConnection problem to the Pi, recieved: {data}\033[0m")
            return False
    
    def _send_str(self, message):
        self.req_socket.send_string(message)
        data = self.req_socket.recv_string()
        return data
    
    @staticmethod
    def data_to_xy(data):
        #print(f"converting data: {data}")
        if data == "None":
            return None
        xywhn = list(map(float, data.split())) # space-separated
        return np.array(xywhn[:2])

    ############## Methods below are not used, but useful for debugging.  ##################3
    def _set_xy(self, x, y, speed=1):
        cmd = f"set_servo_{x:2f} {y:2f} {speed:2f}"
        response = self._send_str(cmd)

    def _request_image(self):
        self.req_socket.send_string("get_image")
        data = self.req_socket.recv()
        arr = pickle.loads(data)
        return arr
    


if __name__ == "__main__": # Usame example
    PiClient = TCPClient(PiIP="192.168.105.150")
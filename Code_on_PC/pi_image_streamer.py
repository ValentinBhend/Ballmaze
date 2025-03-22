import zmq
import time
import pickle
import numpy as np
import cv2
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

class PiImageStreamer:
	def __init__(self, mode="visual"):
		self.init_tcp()
		#if mode == "visual":
		#	self.init_visual()
	def init_tcp(self):
		context = zmq.Context()
		# REQ socket to send requests
		self.req_socket = context.socket(zmq.REQ)
		#self.req_socket.connect("tcp://192.168.5.11:5555")  # Replace with Pi's IP
		self.req_socket.connect("tcp://192.168.179.11:5555")
		# PUB socket to send broadcasts
		self.pub_socket = context.socket(zmq.PUB)
		self.pub_socket.bind("tcp://*:5556")  # Broadcast to subscribers
		print("Laptop TCP Client Running...")
	def init_visual(self):
		fig, ax = plt.subplots()
		self.img = ax.imshow(np.zeros((480, 640, 3), dtype=np.uint8))
		plt.ion()
		plt.show()
	def request_image(self):
		self.req_socket.send_string("req_image")
		data = self.req_socket.recv()
		arr = pickle.loads(data)
		return arr
	def send_str(self, msg):
		self.req_socket.send_string(msg)
		data = self.req_socket.recv()
		return data
	def update_visual(self, arr):
		self.img.set_data(arr[...,(2,1,0)]) # permutation xause of matplotlib
		plt.draw()
		#plt.pause(1)


def preview():
	stream = PiImageStreamer(mode="visual")
	while True:
		arr = stream.request_image()
		stream.update_visual(arr)
		plt.pause(1)

if __name__ == "__main__":
	preview()













from pi_image_streamer import PiImageStreamer
	
class Pi:
	def __init__(self):
		self.stream = PiImageStreamer()
	def set_xy(self, x, y, speed=1):
		# [-1,1] -> [min,max]
		min_set = 0.45
		max_set = 0.82
		x = x * (max_set - min_set)/2 + (min_set + max_set)/2
		y = y * (max_set - min_set)/2 + (min_set + max_set)/2
		cmd = f"req_set_servo_{x:2f} {y:2f} {speed:2f}"
		response = self.stream.send_str(cmd)
		return response
	def reset(self):
		success = False
		while not success:
			cmd = f"req_reset_servo"
			data = self.stream.send_str(cmd)
			if data != b'None':
				success = True
			else:
				pass
				#print("reset failed")
		xywhn = list(map(float, data.split())) # space-separated
		return xywhn
	def get_position(self):
		data = self.stream.send_str("req_position")
		if data == b'None':
			return None
		xywhn = list(map(float, data.split())) # space-separated
		return xywhn
	
	def set_xy_get_position(self, x, y, speed=1):
		min_set = 0.45
		max_set = 0.82
		x = x * (max_set - min_set)/2 + (min_set + max_set)/2
		y = y * (max_set - min_set)/2 + (min_set + max_set)/2
		cmd = f"req_get_pos_set_servo_{x:2f} {y:2f} {speed:2f}"
		data = self.stream.send_str(cmd)
		if data == b'None':
			return None
		xywhn = list(map(float, data.split())) # space-separated
		return xywhn


if __name__ == "__main__":
	import time
	pi = Pi()
	#pi.reset()
	for _ in range(20):
		t1 = time.time()
		pi.set_xy(.5,.5)
		t2 = time.time()
		pi.get_position()
		t3 = time.time()
		print(t2-t1, t3-t2)
	#print(pi.get_position())
	#print(pi.get_position())
	




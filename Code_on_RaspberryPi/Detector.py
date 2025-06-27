import cv2
import numpy as np
from openvino import Core


class Detector:
    def __init__(self):
        ie = Core()
        ie.set_property("CPU", {
            "INFERENCE_NUM_THREADS": 1,
            "NUM_STREAMS": "1",
        })
        model_path = "trained_openvino_model_v2/trained_openvino_model_v2.xml"
        self.compiled_model = ie.compile_model(model=model_path, device_name="CPU") # , config={"NUM_STREAMS": "1"}
        dummy_warmup_in = np.random.rand(128,128,3)
        self.get_xywhn(dummy_warmup_in)

    def from_png(self, img_path):
        img = cv2.imread(img_path)
        if img is None:
            raise ValueError("Image not found or unable to load.")
        img_resized = cv2.resize(img, (128, 128))
        img_resized = img_resized.astype(np.float32)
        return self.get_xywhn(img_resized)

    def get_xywhn(self, arr, conf=0.5):
        xywhn, conf_measured = self.eval_image(arr)
        print(f"conf_measured: {conf_measured}")
        if conf_measured < conf:
            print(f"conf = {conf_measured} < {conf}")
            return None
        return xywhn

    def eval_image(self, arr): # expects (128,128,3) array
        img_input = np.transpose(arr, (2, 0, 1))
        img = img_input[[1, 2, 0], :, :] / 255.0 #
        #img = img_input[[2, 1, 0], :, :] / 255.0 # TODO: this micht be the right one (performs similar)
        img_input = np.expand_dims(img, axis=0)
        results = self.compiled_model([img_input])
        output_array = list(results.values())[0]  # shape (1, 5, 336)
        confidence_scores = output_array[0, 4, :]
        max_idx = np.argmax(confidence_scores)
        most_certain_prediction = output_array[0, :, max_idx]
        xywhn = most_certain_prediction[:4]/128
        conf = most_certain_prediction[4]
        return xywhn, conf

"""def init_free_Detector(Det=None):
    del Det
    #del Core
    #from openvino import Core
    gc.collect()
    libc = ctypes.CDLL("libc.so.6")
    libc.malloc_trim(0)
    Det = Detector()
    return Det"""


if __name__ == "__main__":
    import subprocess
    import time

    import psutil, os
    proc = psutil.Process(os.getpid())
    def log_resource_usage():
        mem = proc.memory_info().rss / (1024**2)
        threads = proc.num_threads()
        print(f"RSS={mem:.1f} MB, threads={threads}")

    def get_cpu_temp():
        output = subprocess.check_output(["vcgencmd", "measure_temp"]).decode()
        temp_str = output.split('=')[1].split("'")[0]
        return float(temp_str)

    def get_cpu_freq_mhz():
        with open("/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq") as f:
            khz = int(f.read().strip())
        return khz / 1000.0

    D = Detector()
    #D = init_free_Detector()
    img_path = "test_img5.png"
    res = D.from_png(img_path)
    print(res)

    t1 = time.time()
    N = 90 * 60 * 30
    tA = t1
    for _ in range(N):
        r = D.from_png(img_path)
        tB = time.time()
        print(_, tB-tA)
        print("🌡️ CPU Temp:", get_cpu_temp(), "°C")
        print(get_cpu_freq_mhz())
        log_resource_usage()
        assert tB-tA < 0.5, "overheat"
        #time.sleep(0.005)
        tA = time.time()
    t2 = time.time()
    print(f"from png time: {(t2-t1)/N}")

import zmq
import pickle
from HardwareController import HardwareController
from PiCalibration import PiCalibration
import time

# Decorator function to register command handlers
def command(name):
    """Decorator to register command handlers."""
    def decorator(func):
        func._command_name = name  # Attach command name to function
        return func
    return decorator

class TCPCommandServer:
    def __init__(self, host="0.0.0.0", port=5555):
        self.host = host
        self.port = port
        self.command_handlers = {}
        self.controller = HardwareController()
        self.last_thread = None

        # Set up ZeroMQ for communication
        self.context = zmq.Context()
        self.rep_socket = self.context.socket(zmq.REP)
        self.rep_socket.bind(f"tcp://*:{self.port}")  # Listen for messages
        self.poller = zmq.Poller()
        self.poller.register(self.rep_socket, zmq.POLLIN)

        # Automatically register all decorated handlers
        self._register_commands()
        self.run()

    def _register_commands(self):
        """Register all methods decorated with @command."""
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if callable(attr) and hasattr(attr, "_command_name"):
                self.command_handlers[attr._command_name] = attr

    def handle_command(self, command):
        """Process the received command."""
        handler = self.command_handlers.get(command.split()[0])  # Handle first part of command string
        if handler:
            # Pass the parameters (if any) to the handler function
            return handler(*command.split()[1:])
        error_msg = f"ERROR: Unknown command '{command}'"
        return error_msg

    def event_handler(self):
        """Handle incoming commands."""
        events = dict(self.poller.poll())
        if self.rep_socket in events:
            #print("waiting for message")
            message = self.rep_socket.recv_string()
            #print(f"got message {message}")
            response = self.handle_command(message)
            self.rep_socket.send_string(response)

    def run(self):
        """Start the server and handle events."""
        print("Pi Server Running...")
        while True:
            self.event_handler()
    
    @staticmethod
    def position_to_str(position):
        if position is None:
            return "None"
        return f"{position[0]} {position[1]}"

    # ----- Command Handlers -----

    @command("dummy_request")
    def handle_dummy(self):
        """Handle an image request."""
        print("Received dummy_request")
        return "dummy_answer"

    @command("set_servo_get_position")
    def handle_set_servo_get_position(self, x, y, speed):
        """Handle set_servo_get_position command with dynamic parameters."""
        x = float(x)
        y = float(y)
        speed = float(speed)
        if self.last_thread is not None:
            if self.last_thread.is_alive():
                t = time.time()
                self.last_thread.join()
                print(f"\033[33mServos were still moving for {(time.time()-t)*1000:.3f}ms, increase servo-speed in env\033[0m")
        #t1 = time.time()
        self.last_thread = self.controller.move_servo(x,y,speed)
        #t2 = time.time()
        #print(f"Received set_servo_get_position with x={x}, y={y}, speed={speed}")
        position = self.controller.get_position()
        #t3 = time.time()
        #print(f"servos: {1000*(t2-t1):.3f}, detect: {1000*(t3-t2):.3f}")
        #print(f"Sending position {position}")
        return self.position_to_str(position)

    @command("set_servo_get_position_save_img")
    def handle_set_servo_get_position_save_img(self, x, y, speed):
        """Handle set_servo_get_position command with dynamic parameters."""
        x = float(x)
        y = float(y)
        speed = float(speed)
        if self.last_thread is not None:
            if self.last_thread.is_alive():
                t = time.time()
                self.last_thread.join()
                print(f"\033[33mServos were still moving for {(time.time()-t)*1000:.3f}ms, increase servo-speed in env\033[0m")
        self.last_thread = self.controller.move_servo(x,y,speed)
        #print(f"Received set_servo_get_position with x={x}, y={y}, speed={speed}")
        position = self.controller.get_position(save=True)
        #print(f"Sending position {position}")
        return self.position_to_str(position)

    @command("get_position")
    def handle_get_position(self):
        """Handle set_servo_get_position command with dynamic parameters."""
        #print(f"Received get_position")
        position = self.controller.get_position()
        #print(f"Sending position {position}")
        return self.position_to_str(position)

    @command("reset")
    def handle_reset(self):
        position = self.controller.reset()
        return self.position_to_str(position)

    @command("calibrate")
    def handle_calibrate(self):
        calibration = PiCalibration()
        calibration.run()
        self.controller = HardwareController()

# ---- Create server instance and run ----
if __name__ == "__main__":
    server = TCPCommandServer()
    server.run()


import serial, time
import serial.tools.list_ports

import inverseKinematics as ik
from positionMapper import Mapper, hardCoded

class RobotController:
    def __init__(self) -> None:
        self.serial: serial.Serial
    
    def connect(self, port, baudrate) -> None:
        "Connect to the robot"
        self.port = port
        self.baudrate = baudrate
        self.serial = serial.Serial(self.port, self.baudrate, timeout=2.0)
        self.serial.flush()
        time.sleep(3)
    
    def disconnect(self) -> None:
        "Disconnect from the robot"
        self.serial.close()

    def start(self) -> None:
        "Start the robot"
        self.enable()
        self.home()

    def wait(self, **kwargs) -> None:
        interface: RobotController= kwargs.get("interface", self)
        interface.send("M400")

    def shutdown(self) -> None:
        "Shutdown the robot"
        self.openGripper()
        self.move(z=0)
        self.home()
        self.disable()
        self.disconnect()

    def __sendRaw(self, data) -> None:
        "Send data to the serial port"
        self.serial.write(data)
        
    def __readRaw(self) -> bytes:
        "Read data from the serial port"
        return self.serial.readall()

    def send(self, command: str) -> None:
        "Send a command to the robot"
        self.__sendRaw(f"{command}\r".encode('utf-8'))
        print(command, end=": ")
        print(self.read())
    
    def sendNoRead(self, command: str) -> None:
        "Send a command to the robot"
        self.__sendRaw(f"{command}\r".encode('utf-8'))

    def read(self) -> bytes:
        "Read data from the serial port"
        return self.__readRaw().decode('utf-8').rstrip()
    
    def enable(self) -> None:
        "Enables robot motors"
        self.send("M17")

    def disable(self) -> None:
        "Disables robot motors"
        self.send("M18")
    
    def move(self, x: float=None, y: float=None, z: float=None, **kwargs) -> None:
        "Moves robot to coordinates"
        out = "G0"
        if x is not None: out += f" X{x}"
        if y is not None: out += f" Y{y}"
        if z is not None: out += f" Z{z}"
        interface: RobotController= kwargs.get("interface", self)
        interface.send(out)

    def home(self, **kwargs) -> None:
        "Homes robot"
        interface: RobotController= kwargs.get("interface", self)
        interface.sendNoRead("G0 X0 Y0 Z0")
    
    def dock(self, **kwargs) -> None:
        "Docks robot"
        interface: RobotController= kwargs.get("interface", self)
        interface.sendNoRead("G0 X90 Y-2.903")

    def getPosition(self) -> None:
        "Gets current position"
        self.send("M114")

    def gripper(self, s: float, **kwargs) -> None:
        "Sets gripper position"
        interface: RobotController= kwargs.get("interface", self)
        interface.send(f"M280 P0 S{s}")

    def getGripper(self) -> None:
        "Gets gripper position"
        self.send("M280 P0")

    def closeGripper(self, **kwargs) -> None:
        "Closes gripper"
        interface: RobotController= kwargs.get("interface", self)
        interface.send("M280 P0 S110")
    
    def openGripper(self, **kwargs) -> None:
        "Opens gripper"
        interface: RobotController= kwargs.get("interface", self)
        interface.send("M280 P0 S10")

class Robot(RobotController):
    class Sequencer:
        def __init__(self) -> None:
            self.sequence = []
        
        def send(self, command: str) -> None:
            "Add command to sequence"
            self.sequence.append(command)
        
        def clear(self) -> None:
            "Clear sequence"
            self.sequence = []
        
        def run(self, interface: RobotController) -> None:
            "Run sequence"
            print(self.sequence)
            [interface.sendNoRead(command) for command in self.sequence]
        
        def __del__(self):
            self.clear()
    
    def __init__(self, port, baudrate) -> None:
        super().__init__()
        self.connect(port, baudrate)
        self.mapperX = Mapper((1, 8), (4.0, 27)) # X axis
        self.mapperY = Mapper((1, 8), (-11.5, 12.0)) # Y axis
        self.letter2number = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F":6, "G": 7, "H": 8}

    def move2square(self, square: str, **kwargs) -> None:
        "Moves robot to square"
        if square not in hardCoded:
            print("Inverse kinematics", square)
            return self.move(*ik.inverseKinematics(self.mapperX.map(self.letter2number[square[0]]), self.mapperY.map(int(square[1]))), **kwargs)
        else:
            print("Hard coded", square)
            return self.move(hardCoded[square], **kwargs)

    def pickUp(self, altitude=-60, **kwargs) -> None:
        "Picks up piece"
        self.openGripper(**kwargs)
        self.move(z=altitude, **kwargs)
        self.wait(**kwargs)
        self.closeGripper(**kwargs)
        self.move(z=0, **kwargs)
        
    def putDown(self, altitude=-57.5, **kwargs) -> None:
        "Puts down piece"
        self.move(z=altitude, **kwargs)
        self.wait(**kwargs)
        self.openGripper(**kwargs)
        self.move(z=0, **kwargs)

    def movePiece(self, start, end, **kwargs):
        "Moves piece from start to end"
        self.move2square(start, **kwargs)
        self.pickUp(**kwargs)
        self.move2square(end, **kwargs)
        self.putDown(**kwargs)
        
    def takePiece(self, start, end, **kwargs):
        "Takes piece from square"
        self.move2square(end, **kwargs),
        self.pickUp(**kwargs),
        self.dock(**kwargs),
        self.putDown(**kwargs),
        self.move2square(start, **kwargs),
        self.pickUp(**kwargs),
        self.move2square(end, **kwargs),
        self.putDown(**kwargs)
        
class RobotTester(Robot):
    def __init__(self, port, baudrate) -> None:
        super().__init__(port, baudrate)
    
    def test(self) -> None:
        sequence = self.Sequencer()
        self.move2square("A8", interface=sequence)
        self.pickUp(interface=sequence)
        self.move2square("D4", interface=sequence)
        self.putDown(interface=sequence)
        sequence.run(self)

class RobotContext:
    def __init__(self, port, baudrate) -> None:
        self.robot = RobotTester(port, baudrate)
    
    def __enter__(self) -> RobotTester:
        self.robot.start()
        return self.robot
    
    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.robot.shutdown()

test = 0

if __name__ == "__main__":
    port = [port.device for port in serial.tools.list_ports.comports() if port.description.startswith("USB-SERIAL")][0]
    with RobotContext(port, 115200) as robot:
        if test:
            robot.test()
        else:
            while True:
                cmd = input("Enter command: ")
                if cmd in ("exit", "e", ""): break
                elif cmd == "home": robot.home()
                elif cmd == "get": robot.getPosition()
                elif cmd == "dock": robot.dock()
                elif cmd == "f": robot.send(r"G0 X20\r\nG0 X-20")
                else:
                    try: robot.send(cmd)
                    except Exception as e:
                        print("Error:", e)
                        continue
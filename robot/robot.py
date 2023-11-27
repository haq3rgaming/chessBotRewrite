import serial, time
import serial.tools.list_ports

import inverseKinematics as ik
import robotCoordinates as rc

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

    def shutdown(self) -> None:
        "Shutdown the robot"
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
        interface = kwargs.get("interface", self)
        interface.send(out)

    def home(self, **kwargs) -> None:
        "Homes robot"
        interface = kwargs.get("interface", self)
        interface.send("G0 X0 Y0 Z0")
    
    def dock(self, **kwargs) -> None:
        "Docks robot"
        interface = kwargs.get("interface", self)
        interface.send("G0 X90 Y-2.903")

    def getPosition(self) -> None:
        "Gets current position"
        self.send("M114")

    def gripper(self, s: float, **kwargs) -> None:
        "Sets gripper position"
        interface = kwargs.get("interface", self)
        interface.send(f"M280 P0 S{s}")

    def getGripper(self) -> None:
        "Gets gripper position"
        self.send("M280 P0")

    def closeGripper(self, **kwargs) -> None:
        "Closes gripper"
        interface = kwargs.get("interface", self)
        interface.send("M280 P0 S110")
    
    def openGripper(self, **kwargs) -> None:
        "Opens gripper"
        interface = kwargs.get("interface", self)
        interface.send("M280 P0 S10")

class Robot(RobotController):
    class Sequencer:
        def __init__(self, commandSeparator:str ="\r") -> None:
            self.sequence = []
            self.commandSeparator = commandSeparator
        
        def send(self, command: str) -> None:
            "Add command to sequence"
            self.sequence.append(command)
        
        def clear(self) -> None:
            "Clear sequence"
            self.sequence = []
        
        def run(self, interface: RobotController) -> None:
            "Run sequence"
            print(self.sequence)
            interface.send(self.commandSeparator.join(self.sequence))
        
        def __del__(self):
            self.clear()
    
    def __init__(self, port, baudrate) -> None:
        super().__init__()
        self.connect(port, baudrate)

    def move2square(self, square: str, **kwargs) -> None:
        "Moves robot to square"
        if square not in rc.hardCoded.keys():
            return self.move(*ik.inverseKinematics(rc.x[square[1]], rc.y[square[0]]), **kwargs)
        else:
            print("Hard coded", square)
            return self.move(*rc.hardCoded[square], **kwargs)

    def pickUp(self, altitude=-30) -> None:
        "Picks up piece"
        sequencer = self.Sequencer()
        self.openGripper(interface=sequencer)
        self.move(z=altitude, interface=sequencer)
        self.closeGripper(interface=sequencer)
        self.move(z=0, interface=sequencer)
        sequencer.run(self)
        
    def putDown(self, altitude=-30) -> None:
        "Puts down piece"
        sequencer = self.Sequencer()
        self.move(z=altitude, interface=sequencer)
        self.openGripper(interface=sequencer)
        self.move(z=0, interface=sequencer)
        self.closeGripper(interface=sequencer)
        sequencer.run(self)

    def movePiece(self, start, end):
        "Moves piece from start to end"
        sequencer = self.Sequencer()
        self.move2square(start, interface=sequencer)
        self.pickUp(interface=sequencer)
        self.move2square(end, interface=sequencer)
        sequencer.run(self)
    
    def takePiece(self, start, end):
        "Takes piece from square"
        sequencer = self.Sequencer()
        self.move2square(end, interface=sequencer),
        self.pickUp(interface=sequencer),
        self.dock(interface=sequencer),
        self.putDown(interface=sequencer),
        self.move2square(start,interface=sequencer),
        self.pickUp(interface=sequencer),
        self.move2square(end, interface=sequencer),
        self.putDown(interface=sequencer)
        sequencer.run(self)

class RobotTester(Robot):
    def __init__(self, port, baudrate) -> None:
        super().__init__(port, baudrate)
    
    def cornerTest(self):
        "Test all corners"
        self.move2square("A1")
        self.move2square("H1")
        self.move2square("A8")
        self.move2square("H8")

    def cornerTestSeq(self):
        "Test all corners"
        sequencer = self.Sequencer("|")
        self.move2square("A1", interface=sequencer)
        self.move2square("H1", interface=sequencer)
        self.move2square("A8", interface=sequencer)
        self.move2square("H8", interface=sequencer)
        self.home(interface=sequencer)
        sequencer.run(self)

    def squareTest(self):
        "Test all squares"
        sequencer = self.Sequencer("|")
        for letter in rc.y.keys():
            for number in rc.x.keys():
                self.move2square(letter + number, interface=sequencer)
        self.home(interface=sequencer)
        sequencer.run(self)

class RobotContext:
    def __init__(self, port, baudrate) -> None:
        self.robot = RobotTester(port, baudrate)
    
    def __enter__(self) -> RobotTester:
        self.robot.start()
        return self.robot
    
    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.robot.shutdown()

test = False

if __name__ == "__main__":
    port = [port.device for port in serial.tools.list_ports.comports() if port.description.startswith("USB-SERIAL")][0]
    with RobotContext(port, 115200) as robot:
        if test:
            robot.cornerTest()
        else:
            while True:
                cmd = input("Enter command: ")
                if cmd in ("exit", "e", ""): break
                elif cmd == "home": robot.home()
                elif cmd == "get": robot.getPosition()
                else:
                    try: robot.send(cmd)
                    except Exception as e:
                        print("Error:", e)
                        continue
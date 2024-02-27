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
        self.sendNoRead("G0 Z0")
        self.home()
        self.disable()
        self.disconnect()

    def __sendRaw(self, data) -> None:
        "Send data to the serial port"
        self.serial.write(data)
        
    def __readRaw(self) -> bytes:
        "Read data from the serial port"
        return self.serial.readall()

    def send(self, command: str, console: bool=False) -> None:
        "Send a command to the robot"
        self.__sendRaw(f"{command}\r".encode('utf-8'))
        if console:
            print(command, end=": ")
            print(self.read())
        else:
           return self.read()
    
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
        interface.send("G0 X0 Y0 Z0")
    
    def dock(self, **kwargs) -> None:
        "Docks robot"
        interface: RobotController= kwargs.get("interface", self)
        interface.sendNoRead("G0 X90 Y-2.903")

    def dropOff(self, **kwargs) -> None:
        "Drops off piece"
        interface: RobotController= kwargs.get("interface", self)
        interface.sendNoRead("G0 X45 Y135")

    def getPosition(self) -> None:
        "Gets current position"
        print(self.send("M114"))

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
        interface.send("M280 P0 S80")
    
    def openGripper(self, **kwargs) -> None:
        "Opens gripper"
        interface: RobotController= kwargs.get("interface", self)
        interface.send("M280 P0 S30")

class Robot(RobotController):
    class Sequencer:
        def __init__(self) -> None:
            self.sequence = []
        
        def send(self, command: str) -> None:
            "Add command to sequence"
            self.sequence.append(command)
        sendNoRead = send

        def wait(self) -> None:
            "Add wait command to sequence"
            self.sequence.append("M400")

        def clear(self) -> None:
            "Clear sequence"
            self.sequence = []
        
        def run(self, interface: RobotController) -> None:
            "Run sequence"
            [interface.sendNoRead(command) for command in self.sequence]
            interface.wait()
            self.clear()
        
        def __del__(self):
            self.clear()
    
    def __init__(self, port, baudrate) -> None:
        self.mapperX = Mapper((1, 8), (4.0, 27)) # X axis
        self.mapperY = Mapper((1, 8), (-11.5, 12.0)) # Y axis
        self.mapperZ = Mapper((1, 8), (9, 0)) # Z axis, not sure where or how to implement this yet
        self.letter2number = {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5, "f":6, "g": 7, "h": 8}

        super().__init__()
        self.connect(port, baudrate)
        self.openGripper()
        
    def move2square(self, square: str, **kwargs) -> None:
        "Moves robot to square"
        if square not in hardCoded:
            print("Inverse kinematics", square)
            return self.move(*ik.inverseKinematics(self.mapperX.map(self.letter2number[square[0]]), self.mapperY.map(int(square[1]))), **kwargs)
        else:
            print("Hard coded", square)
            return self.move(hardCoded[square], **kwargs)

    def moveZ(self, square: str, z: float, **kwargs) -> None:
        "Moves robot to square with z"
        z -= self.mapperZ.map(self.letter2number[square[0]])
        self.move(z=z, **kwargs)

    def move2squareZ(self, square:str, z: float, **kwargs) -> None:
        "Moves robot to square with z"
        square = square.lower()
        z -= self.mapperZ.map(self.letter2number[square[0]])
        if square not in hardCoded:
            print("Inverse kinematics", square)
            return self.move(*ik.inverseKinematics(self.mapperX.map(self.letter2number[square[0]]), self.mapperY.map(int(square[1]))), z, **kwargs)
        else:
            print("Hard coded", square)
            return self.move(*hardCoded[square], z, **kwargs)

    def movePiece(self, moveFrom, moveTo, altitude=87, **kwargs) -> None:
        "Moves piece from square to square"
        self.move2square(moveFrom, **kwargs)
        self.moveZ(moveFrom, -altitude, **kwargs)
        self.wait(**kwargs)
        self.closeGripper(**kwargs)
        self.moveZ(moveFrom, 0, **kwargs)
        self.move2square(moveTo, **kwargs)
        self.moveZ(moveTo, -altitude, **kwargs)
        self.wait(**kwargs)
        self.openGripper(**kwargs)
        self.moveZ(moveTo, 0, **kwargs)
    
    def removePiece(self, square, altitude=87, **kwargs) -> None:
        "Removes piece from square"
        self.move2square(square, **kwargs)
        self.moveZ(square, -altitude, **kwargs)
        self.wait(**kwargs)
        self.closeGripper(**kwargs)
        self.moveZ(square, 0, **kwargs)
        self.dropOff(**kwargs)
        self.moveZ(square, -altitude, **kwargs)
        self.wait(**kwargs)
        self.openGripper(**kwargs)
        self.moveZ(square, 0, **kwargs)


        
class RobotTester(Robot):
    def __init__(self, port, baudrate) -> None:
        super().__init__(port, baudrate)
    
    def test(self) -> None:
        sequence = self.Sequencer()
        self.removePiece("D5", interface=sequence)
        sequence.run(self)
        self.movePiece("D4", "E5", interface=sequence)
        sequence.run(self)

    def cornerTest(self) -> None:
        sequence = self.Sequencer()
        self.move2square("A1", interface=sequence)
        self.wait(interface=sequence)
        self.move2square("H1", interface=sequence)
        self.wait(interface=sequence)
        self.move2square("A8", interface=sequence)
        self.wait(interface=sequence)
        self.move2square("H8", interface=sequence)
        self.wait(interface=sequence)
        sequence.run(self)

class RobotContext:
    def __init__(self, port, baudrate) -> None:
        self.robot = RobotTester(port, baudrate)
    
    def __enter__(self) -> RobotTester:
        self.robot.start()
        return self.robot
    
    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.robot.shutdown()
        print("Robot shutdown")

test = 1

if __name__ == "__main__":
    port = [port.device for port in serial.tools.list_ports.comports() if port.description.startswith("USB-SERIAL")][0]
    with RobotContext(port, 115200) as robot:
        if test:
            robot.movePiece("h1", "h5")
            robot.movePiece("h5", "d5")
        else:
            robot.closeGripper()
            while True:
                cmd = input("Enter command: ")
                match cmd:
                    case "exit" | "e" | "":
                        break
                    case "home":
                        robot.home()
                    case "get":
                        robot.getPosition()
                    case "dock":
                        robot.dock()
                    case "f":
                        robot.move2squareZ("A8", -80)
                    case "g":
                        robot.move2squareZ("H8", -80)
                    case _:
                        try: robot.send(cmd)
                        except Exception as e:
                            print("Error:", e)
                            continue
                    
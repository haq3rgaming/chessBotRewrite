import inverseKinematics as ik
from robot import Robot, RobotContext
import robotCoordinates as rc

def moveRobot(robot, x, y, side="auto"):
    q1, q2 = ik.inverseKinematics(x, y, side)
    robot.move(q1, q2, 0)

with RobotContext("COM10", 115200) as robot:
    while True:
        cmd = input("Enter command: ")
        if cmd in ("exit", "e", ""): break
        elif cmd == "home": robot.home()
        elif cmd == "dock": moveRobot(robot, 15.3, 18, "left")
        elif cmd == "get": robot.getPosition()
        elif cmd == "open": robot.openGripper()
        elif cmd == "close": robot.closeGripper()
        else:
            try:
                if cmd not in rc.hardCoded.keys():
                    letter, number = [i for i in cmd]
                    x, y = rc.x[number], rc.y[letter]
                    moveRobot(robot, x, y)
                else:
                    robot.move(*rc.hardCoded[cmd])
            except Exception:
                try: robot.send(cmd)
                except Exception as e:
                    print("Error:", e)
                    continue
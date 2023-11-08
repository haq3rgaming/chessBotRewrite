from math import degrees, radians
from math import acos, atan, atan2, sin, cos

arm1Lenght = 15.3
arm2Lenght = 16.1
reachRadius = arm1Lenght + arm2Lenght
armCorrection = 33/62

angleProtectionQ1 = 110
angleProtectionQ2 = 170

def inverseKinematics(x, y, side="auto"):
    """Returns the angles of the arms in degrees"""
    try:
        if (x**2 + y**2 > reachRadius**2):
            print("Out of reach")
            return 0, 0
        if (y > reachRadius or y < -reachRadius):
            print(f"Out of bounds (y={y})")
            return 0, 0
        if side == "right": side = True
        elif side == "left": side = False
        elif side == "auto": side = y > 0
        else:
            print(f"Invalid side ({side})")
            return 0, 0
        if side:
            q2 = degrees(acos((x**2 + y**2 - arm1Lenght**2 - arm2Lenght**2)/(2*arm1Lenght*arm2Lenght)))
            q1 = degrees(atan2(y,x) - atan((arm2Lenght*sin(radians(q2)))/(arm1Lenght + arm2Lenght*cos(radians(q2)))))
        else:
            q2 = -degrees(acos((x**2 + y**2 - arm1Lenght**2 - arm2Lenght**2)/(2*arm1Lenght*arm2Lenght)))
            q1 = degrees(atan2(y,x) - atan((arm2Lenght*sin(radians(q2)))/(arm1Lenght + arm2Lenght*cos(radians(q2)))))
        q1, q2 = round(q1, 3), round(q2 + armCorrection*q1, 3)
        if (q1 > angleProtectionQ1 or q1 < -angleProtectionQ1) or (q2 > angleProtectionQ2 or q2 < -angleProtectionQ2):
            print(f"Calculation error: Angle out of range (q1={q1}, q2={q2})")
            return 0, 0
        return q1, q2
    except Exception as e:
        print("Calculation error:", e)
        return 0, 0

if __name__ == "__main__":
    print(inverseKinematics(20, 10, "left"))
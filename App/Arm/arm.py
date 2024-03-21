import xarm
import time
import datetime
from .gripper import Gripper
from Kinematics.inverse_kinematics import calculate_inverse_kinematics as ik
from Kinematics.forward_kinematics import forward_kinematics as fk
class Arm:
    def __init__(self, com, serialcom):
        self.arm = xarm.Controller(com)
        self.gripper=Gripper(self.arm,serialcom)
        self.moveToDefault()
    def __calculateT5(self,T1,angle):
        T5=T1+angle
        if T5>90:
            T5=T5-180
        if T5<-90:
            T5=180+T5
        return T5
    def moveToPosition(self, dx,dy,dz,angle):
        T1,T2,T3,T4=ik(fk=[dx, dy, dz])
        T5=self.__calculateT5(T1,angle)
        
        print(datetime.datetime.now())
        self.moveArm(T1,T2,T3,T4,T5)
        self.gripper.close_gripper()

    def moveArm(self, T1,T2,T3,T4,T5):
        self.arm.setPosition([[1,T1],[2,-T2],[3,T3],[4,T4],[5,T5],[6,0.]],duration=4000,wait=True)

    def moveToDefault(self):
        self.arm.setPosition([[1,1500],[2,1500],[3,1500],[4,1500],[5,1500],[6,1500]],duration=3000,wait=True)

    def unload(self):
        self.arm.setPosition([[2,1500]],duration=1500,wait=True)
        self.arm.setPosition([[1,2451],[2,1852],[3,1092],[4,913],[5,500]],duration=4000,wait=True)
        self.arm.setPosition([[6,1500]],duration=2000,wait=True)
        self.moveToDefault()

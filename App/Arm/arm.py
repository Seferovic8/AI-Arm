import xarm
import time
from Hands.hand import HandDetector
import datetime
import numpy as np
from .gripper import Gripper
from Kinematics.inverse_kinematics import calculate_inverse_kinematics as ik
from Kinematics.forward_kinematics import forward_kinematics as fk
class Arm:
    def __init__(self, com, serialcom):
        self.arm = xarm.Controller(com)
        self.gripper=Gripper(self.arm,serialcom)
        self.handDetector= HandDetector(imgUrl="http://192.168.1.10:8080/shot.jpg",wsUrl="ws://localhost:8765")

        self.moveToDefault()
    def __calculateT5(self,T1,angle,follow=False):
        if follow:
            return 0.
        T5=T1+angle
        if T5>90:
            T5=T5-180
        if T5<-90:
            T5=180+T5
        return T5
    def moveToPosition(self, dx,dy,dz,angle):
        T1,T2,T3,T4=ik(fk=[dx, dy, dz])
        T5=self.__calculateT5(T1,angle)
        self.moveArm(T1,T2,T3,T4,T5)
        self.gripper.close_gripper()
    
    def moveToFollow(self,dy,dz,isHandOpen,handStatus):
        x=220
        if dz>297:
            x=150
        elif dz>277:
            x=180
        elif dz>250:
            x=200
        T1,T2,T3,T4=ik(fk=[x, dy, dz],follow=True)
        T6=0.
        if handStatus:
            T6=1. if isHandOpen else 90.
        self.moveArm(T1,T2,T3,T4,0,T6,follow=True,duration=100)

    def moveArm(self, T1,T2,T3,T4,T5,T6=0,duration=4000,follow=False):
        if not follow:
            self.arm.setPosition([[1,T1],[2,-T2],[3,T3],[4,T4],[5,T5],[6,0.]],duration=duration,wait=True)
        else:
            if(T6==0):
                self.arm.setPosition([[1,T1],[2,-T2],[3,T3],[4,T4]],duration=duration,wait=True)
            else:
                self.arm.setPosition([[1,T1],[2,-T2],[3,T3],[4,T4],[6,T6]],duration=duration,wait=True)

    def moveToDefault(self):
        self.arm.setPosition([[1,1500],[2,1500],[3,1500],[4,1500],[5,1500],[6,1500]],duration=3000,wait=True)

    def unload(self):
        self.arm.setPosition([[2,1500],[3,1100],[4,1200]],duration=1500,wait=True)
        self.arm.setPosition([[1,2451],[2,1852],[3,1092],[4,913],[5,500]],duration=4000,wait=True)
        self.arm.setPosition([[6,1500]],duration=2000,wait=True)
        self.moveToDefault()
    
    def __map_value(self,x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
    
    def follow(self):
        self.arm.setPosition([[2,1500],[3,1100],[4,1200]],duration=1500,wait=True)
        self.handDetector.reset_values()
        self.handDetector.work = True
        handStatus = False
        while self.handDetector.work:
            img=self.handDetector.findHands()
            x,y,isHandOpen=self.handDetector.findPosition(img)
            if (x is not None and y is not None):
                y_=self.__map_value(x,in_min=0,in_max=img.shape[1],out_min=-250,out_max=250)
                z_=self.__map_value(y,in_min=0,in_max=img.shape[0],out_min=320,out_max=20)
                if isHandOpen:
                    handStatus=True
                self.moveToFollow(y_,z_,isHandOpen,handStatus)

            time.sleep(0.1)
            #work=False
        self.moveToDefault()

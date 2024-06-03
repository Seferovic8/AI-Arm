import time
import threading
class Gripper:
    def __init__(self,arm,serial):
        self.arm = arm
        self.arduino = serial
        self.vibrating = False  # Shared variable to indicate vibration status
        self.lock = threading.Lock()  # Lock to ensure safe access to shared variable
        self.is_vibrating_thread = threading.Thread(target=self.__is_vibrating_thread, daemon=True)
        self.is_vibrating_thread.start()

    def __is_vibrating_thread(self):
        while True:
            with self.lock:
                data= self.arduino.read_data()
                if data!=2:
                    self.vibrating = bool(self.arduino.read_data())
            time.sleep(0.1)  # Adjust sleep time as needed

    def __is_vibrating(self):
        with self.lock:
            return self.vibrating
    
    
    def last_check(self):
        time.sleep(1)
        if self.__is_vibrating():
            self.open_gripper(2500)

    def close_gripper(self):

        self.arm.setPosition([[6,1500]],duration=300)
        duration=50
        time_to_sleep=0.05
        for i in range(21):
            if self.__is_vibrating():
                self.open_gripper(1500+(i*50))
                break
            if(i<13):
                duration=50
                time_to_sleep=0.04
            elif(i>13 and i<17):
                duration=300
                time_to_sleep=0.25
            else:
                duration=500
                time_to_sleep=0.45
            self.arm.setPosition([[6,1500+(i*50)]],duration=duration)
            time.sleep(time_to_sleep)
            #print(i)
        self.last_check()

    def open_gripper(self,position):
        for i in range(41):
            self.arm.setPosition([[6,position-(i*25)]])
            if not self.__is_vibrating():
                time.sleep(0.5)
                if not self.__is_vibrating(): break
            time.sleep(0.25)

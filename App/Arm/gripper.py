import serial
import time
import threading
class Gripper:
    def __init__(self,arm,com):
        self.arm = arm
        self.arduino = serial.Serial(com, 9600, timeout=1)
        self.arduino.read()
        self.vibrating = False  # Shared variable to indicate vibration status
        self.lock = threading.Lock()  # Lock to ensure safe access to shared variable
        self.is_vibrating_thread = threading.Thread(target=self.__is_vibrating_thread, daemon=True)
        self.is_vibrating_thread.start()

    def __is_vibrating_thread(self):
        while True:
            with self.lock:
                self.vibrating = bool(self.__read_data())
            time.sleep(0.1)  # Adjust sleep time as needed

    def __is_vibrating(self):
        with self.lock:
            return self.vibrating
        
    def __read_data(self):
        data = self.arduino.read().decode("utf-8")
        print(f"data: {data}")
        if data =='':
            data=0
        return int(data)
    
    def last_check(self):
        time.sleep(1)
        if self.__is_vibrating():
            self.open_gripper(2500)

    def close_gripper(self):

        self.arm.setPosition([[6,1500]],duration=300)
        print(self.__is_vibrating())
        for i in range(21):
            if self.__is_vibrating():
                self.open_gripper(1500+(i*50))
                break

            self.arm.setPosition([[6,1500+(i*50)]],duration=300)
            #print(i)
            #if(i>13):
            time.sleep(0.25)
            if self.__is_vibrating():
                self.open_gripper(1500+(i*50))
                break
        self.last_check()

    def open_gripper(self,position):
        for i in range(41):
            self.arm.setPosition([[6,position-(i*25)]],duration=300)
            if not self.__is_vibrating():
                time.sleep(0.2)
                if not self.__is_vibrating(): break
            time.sleep(0.25)

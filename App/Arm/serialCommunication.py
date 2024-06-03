import serial

class SerialCommunication:
    def __init__(self,com):
        self.arduino = serial.Serial(com, 9600, timeout=1)
        self.arduino.read()

    def read_data(self):
        data = self.arduino.read().decode("utf-8")
        #print(f"data: {data}")
        if data =='':
            data=2
        return int(data)
    def send_error(self,error):
        self.arduino.write(str(error.value).encode())
        
from enum import Enum
class Errors(Enum):
    ObjectDoesNotExist = 1
    HandCameraNotAvailable = 2
    Others = 3

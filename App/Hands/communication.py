import json
import base64
import websocket
import cv2 
import requests
import numpy as np
import imutils
import os

class Communication:
    def __init__(self,host,wsUrl):
        self.host = host
        self.ws = websocket.create_connection(wsUrl)
    def isHostAlive(self):
        if os.system(f"ping -W 1.2 -c 1 {self.host.split('/')[2].split(':')[0]}") == 0:
            return True
        return False
    def __base64_encode_img(self,frame):
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        frame_base64 = base64.b64encode(frame_bytes).decode('utf-8')
        return frame_base64
    def sendToWS(self,img,isOpen):
        self.ws.send(json.dumps({"img":self.__base64_encode_img(img),"isOpen": isOpen}))

    def getImage(self):
        img_resp = requests.get(self.host) 
        img_arr = np.array(bytearray(img_resp.content), dtype=np.uint8) 
        img = cv2.imdecode(img_arr, -1) 
        img = imutils.resize(img, width=1000, height=1800) 
        return img
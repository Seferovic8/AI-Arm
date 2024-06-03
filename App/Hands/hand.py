import requests 
import cv2 
import numpy as np 
import imutils 
import websocket
import base64
import mediapipe as mp
import json
class HandDetector():
    def __init__(self,imgUrl,wsUrl,mode=False,maxHands=1,modelComplexity=1,detectionCon=0.7,trackCon = 0.7):
        self.mode = mode
        self.imgUrl = imgUrl
        #self.wsUrl = wsUrl
        self.maxHands = maxHands
        self.modelComplex = modelComplexity
        self.detectionCon = detectionCon
        self.trackCon = trackCon
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode,self.maxHands,self.modelComplex,self.detectionCon,self.trackCon)
        self.hands2 = self.mpHands.Hands(self.mode,2,self.modelComplex,self.detectionCon,self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils
        self.ws = websocket.create_connection(wsUrl)
        self.i = 0
        self.palmStatus = False
        self.closeStatus = False
        self.work=False
    def reset_values(self):
        self.i=0
        self.palmStatus=False
        self.closeStatus = False

    def __base64_encode_img(self,frame):
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        frame_base64 = base64.b64encode(frame_bytes).decode('utf-8')
        return frame_base64
    
    def getImage(self):
        img_resp = requests.get(self.imgUrl) 
        img_arr = np.array(bytearray(img_resp.content), dtype=np.uint8) 
        img = cv2.imdecode(img_arr, -1) 
        img = imutils.resize(img, width=1000, height=1800) 
        return img
    def sendToWS(self,img,isOpen):
        self.ws.send(json.dumps({"img":self.__base64_encode_img(img),"isOpen": isOpen}))

    def findHands(self,draw=True):
        img=self.getImage()
        img = cv2.flip(img,1)
        imgRGB = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        if not self.closeStatus:
            self.results = self.hands.process(imgRGB)
        else:
            self.results = self.hands2.process(imgRGB)
        #print(results.multi_hand_landmarks)
        if self.results.multi_hand_landmarks:
            for handlms in self.results.multi_hand_landmarks:   
                if draw:
                    self.mpDraw.draw_landmarks(img,handlms,self.mpHands.HAND_CONNECTIONS)
        return img

    def is_hand_open(self,handNo=0):
        if self.results.multi_hand_landmarks:
            myHand=self.results.multi_hand_landmarks[handNo]
            fingers =self.mpHands.HandLandmark
            landmark=myHand.landmark
            i = 0
            if(landmark[fingers.INDEX_FINGER_PIP].y<landmark[fingers.INDEX_FINGER_TIP].y):
                i+=1
            if(landmark[fingers.MIDDLE_FINGER_PIP].y<landmark[fingers.MIDDLE_FINGER_TIP].y):
                i+=1 
            if(landmark[fingers.RING_FINGER_PIP].y<landmark[fingers.RING_FINGER_TIP].y):
                i+=1
            if(landmark[fingers.PINKY_PIP].y<landmark[fingers.PINKY_TIP].y):
                i+=1
            if i > 2: 
                return False
            else:
                return True

    def findHandCordinates(self,myHand,img,draw=True,color=(0,255,0)):
        h,w,c = img.shape
        x_max = 0
        y_max = 0
        x_min = w
        y_min = h
        for lm in myHand.landmark:
            cx,cy = int(lm.x*w),int(lm.y*h)
            if cx > x_max:
                x_max = cx
            if cx < x_min:
                x_min = cx
            if cy > y_max:
                y_max = cy
            if cy < y_min:
                y_min = cy
            if draw:
                cv2.circle(img,(cx,cy),5,color,cv2.FILLED)
        cv2.rectangle(img, (x_min, y_min), (x_max, y_max), color, 2)
        return (x_min+x_max)/2, (y_min+y_max)/2
    
    def findPosition(self,img,handNo=0,draw=True):
        if self.results.multi_hand_landmarks:
            myHand=self.results.multi_hand_landmarks[handNo]
            x,y = self.findHandCordinates(myHand,img)
            isHandOpen = self.is_hand_open()
            handStatus=isHandOpen
            self.sendToWS(img,isHandOpen)
            if isHandOpen!=self.palmStatus:
                self.i+=1
                self.palmStatus=isHandOpen
                if self.i>2:
                    self.closeStatus=True
            if self.closeStatus:
                if len(self.results.multi_hand_landmarks)>1:
                    handTwo=self.results.multi_hand_landmarks[handNo+1]
                    x_two,y_two = self.findHandCordinates(handTwo,img,color=(255,0,0))
                    isOpen =self.is_hand_open(handNo=handNo+1)
                    if x_two<x:
                        check= y_two>y
                    else:
                        check=y>y_two
                        handStatus=isOpen
                        isOpen= isHandOpen
                        temp=x
                        x = x_two
                        x_two = temp
                        temp = y
                        y = y_two
                        y_two = temp
                    if not isOpen and check and abs(x-x_two)>150 and abs(y-y_two)>50:
                        self.work = False
            return x,y,handStatus
        else:
            self.sendToWS(img,False)
            return None,None,None
import numpy as np
import cv2
import cv2.aruco as aruco
import threading
import time
import base64
import json
import requests
class ArucoDetector:
    def __init__(self):
        self.markerCorners=np.array([])
        self.markerIds=np.array([])
        self.markerDetails = {}
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH,800) 
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT,600) 
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        self.line1=0
        self.line2=0
        self.img = None#np.zeros(shape=(640,640,3))
        self.lock = threading.Lock()  # Lock to ensure safe access to shared variable
        self.get_image_thread = threading.Thread(target=self.__get_image_thread, daemon=True)
        self.get_image_thread.start()

    def __base64_encode_img(self,frame):
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        frame_base64 = base64.b64encode(frame_bytes).decode('utf-8')
        return frame_base64
    def __get_image_thread(self):
        while True:
            with self.lock:
                if self.cap.isOpened():
                    succes, img = self.cap.read()
                    #async with websockets.connect("ws://localhost:5000/",origin="*") as websocket:   
                    self.img =cv2.cvtColor( cv2.resize(img,(640,640)), cv2.COLOR_BGR2RGB)
                    cv2.imwrite("img.png",img)
            #time.sleep(0.5)

    def __get_image(self):
      with self.lock:
            return self.img
    def remove_aruco_markers(self):
        color=(255,255,255)
        clear_img=self.img
        for i,ids in enumerate(self.markerIds):
            #print(self.markerIds[i])
            aruco=self.markerCorners[i]
            x_u=np.min(aruco[:,0]).astype(np.int32)-5
            x_d=np.max(aruco[:,0]).astype(np.int32)+5
            y_u=np.min(aruco[:,1]).astype(np.int32)-5
            y_d=np.max(aruco[:,1]).astype(np.int32)+5
            color=clear_img[y_u-2,x_u-2]
            clear_img[y_u:y_d,
                x_u:x_d] = np.full(((y_d-y_u),(x_d-x_u),3), color)
        pts=np.array([self.markerDetails[0][0],self.markerDetails[1][0],
                      self.markerDetails[2][0],[self.markerDetails[2][0][0],self.markerDetails[0][0][1]],
                      [0,0],[0,640],[640,640],[640,0],
                      [0,0],[self.markerDetails[2][0][0],self.markerDetails[0][0][1]]]) 
        pts = pts.reshape((-1,1,2))
        cv2.fillPoly(clear_img, [pts], tuple(int(x) for x in color))
        return cv2.cvtColor(clear_img, cv2.COLOR_BGR2RGB)
    
    def __detect_aruco_markers(self):
        self.__get_image()
        gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        arucoDict = dictionary = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
        arucoParams = aruco.DetectorParameters()
        detector = aruco.ArucoDetector(dictionary, arucoParams)
        markerCorners, markerIds, rejectedCandidates = detector.detectMarkers(self.img)
        print(len(markerCorners))
        if(len(markerCorners)!=3):
            self.__detect_aruco_markers()
        #aruco.drawDetectedMarkers(img,markerCorners)
        self.markerCorners=np.squeeze(markerCorners)
        self.markerIds=markerIds

    
    def get_aruco_informations(self):
        self.__detect_aruco_markers()
        for i,ida in enumerate(self.markerIds):
            rect = cv2.minAreaRect(self.markerCorners[i].reshape((-1, 1, 2)))
            # Extract the center and other information from the rectangle
            center, size, angle = rect
            self.markerDetails[ida[0]]=np.array([np.round(center),np.round(size)],dtype=np.int16)
        self.line1=cv2.norm(self.markerDetails[0][0],self.markerDetails[1][0])
        self.line2=cv2.norm(self.markerDetails[1][0],self.markerDetails[2][0])
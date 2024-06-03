from ultralytics import YOLO
import numpy as np
import cv2
class YOLOPredictor():
    def __init__(self,model_path):
        self.model_path = model_path
        self.model=YOLO(model_path,task="obb")
    
    def predict(self,img):
        cv2.imwrite("pred.png",img)
        results=self.model.predict(img,conf=0.55,)[0].obb
        #plt.imshow(img)
        for i, result in enumerate(results.cls):
            yield np.append(np.array([result.numpy(),results.conf[i]]),np.array([results.xyxyxyxy[i].numpy().reshape(1,-1)[0]]))
            #self.predictions=np.append(self.predictions,np.append(np.array([result.numpy(),results.conf[i]]),np.array([results.xyxyxyxy[i].numpy().reshape(1,-1)[0]])))
        #self.predictions = self.predictions.reshape(-1,5,2)

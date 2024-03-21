import numpy as np
import cv2

class PositionCalculator:
    def __init__(self,arucoDetector,YOLOPredictor):
        self.line1_lenght=315
        self.line2_lenght=330
        self.y_zero=140
        self.x_zero=54
        self.predDetails = np.array([])
        self.arucoDetector=arucoDetector
        self.YOLOPredictor=YOLOPredictor

    def __get_center(self,class_num):
        return self.predDetails[self.predDetails[:,0,0]==class_num][0,1]
    def __get_angle(self,class_num):
        return self.predDetails[self.predDetails[:,0,0]==class_num][0,0,1]    
    
    def __get_z(self,c):
        if(c<130):
            return 8
        if c<=160:
            return 8+(2/30)*(c-130)
        if c<=190:
            return 10+(4/30)*(c-160)
        if c<=220:
            return 14+(6/30)*(c-190)
        if c<=250:
            return 20+(5/30)*(c-220)
        if c>=250:
            return 25+(7/20)*(c-250)
        
    def get_cordinates(self,class_num):
        center = self.__get_center(class_num)
        x=(center[1]-self.arucoDetector.markerDetails[0][0,1])*(self.line1_lenght/self.arucoDetector.line1)-self.x_zero
        y=(self.arucoDetector.markerDetails[1][0,0]-center[0])*(self.line2_lenght/self.arucoDetector.line2)-self.y_zero
        if y<=0:
            y+=y/10
        else:
            y+=y/4.5
        
        x+=x/14
        return np.round(x),np.round(-y),np.round(self.__get_z(np.sqrt(x**2+y**2))),np.round(self.__get_angle(class_num))
    def calculate_angle(self,pred,pred_angle):
        x_preds=np.array([pred[2],pred[4],pred[6],pred[8]])
        y_preds=np.array([pred[3],pred[5],pred[7],pred[9]])
        # X_1, y_1
        x_pos=np.where(x_preds==np.max(x_preds))
        X_1=x_preds[x_pos][0]
        y_1=y_preds[x_pos][0]
        y_pos=np.where(y_preds==np.max(y_preds))
        X_2=x_preds[y_pos][0]
        y_2=y_preds[y_pos][0]
        
        # X_2, y_2
        x_pos2=np.where(x_preds==np.min(x_preds))
        X_1_=x_preds[x_pos2][0]
        y_1_=y_preds[x_pos2][0]
        y_pos2=np.where(y_preds==np.max(y_preds))
        X_2_=x_preds[y_pos2][0]
        y_2_=y_preds[y_pos2][0]
        
        # Calculate distances
        line1=cv2.norm(np.round([X_1,y_1]).astype(np.int32),np.round([X_2,y_2]).astype(np.int32))
        line2=cv2.norm(np.round([X_1_,y_1_]).astype(np.int32),np.round([X_2_,y_2_]).astype(np.int32))

        if(line1>line2):
            return 90-pred_angle
        else:
            return -pred_angle
    def get_positions(self,img):
        for pred in self.YOLOPredictor.predict(img):
            center, size, pred_angle = cv2.minAreaRect(pred[2:].reshape(-1,1,2))
            angle=self.calculate_angle(pred,pred_angle)
            self.predDetails=np.append(self.predDetails,[[pred[0],angle],np.round(center),np.round(size)])
        self.predDetails=self.predDetails.reshape(-1,3,2)
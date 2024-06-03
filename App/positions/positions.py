from .arucoDetector import ArucoDetector
from .positionCalculator import PositionCalculator
from .yoloPredictor import YOLOPredictor
import numpy as np
class Positions:
    def __init__(self,model_path):
        self.arucoDetector = ArucoDetector()
        self.YOLOPredictor =YOLOPredictor(model_path=model_path)
        self.positionCalculator =PositionCalculator(arucoDetector=self.arucoDetector,YOLOPredictor=self.YOLOPredictor)
    def find_positions(self):
        self.arucoDetector.get_aruco_informations()
        self.positionCalculator.get_positions(img=self.arucoDetector.remove_aruco_markers())
    def get_cordinates(self,class_num):
        return self.positionCalculator.get_cordinates(class_num)
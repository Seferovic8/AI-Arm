from positions.positions import Positions
from Arm.arm import Arm
from SpeechRecognition.speechRecognition import SpeechRecognition

from flask import Flask, send_file,Response,render_template,request,jsonify
import cv2
import tensorflow as tf
import numpy as np
import base64
from tensorflow import keras
from flask_cors import CORS  # Import CORS from flask_cors
app = Flask(__name__)
CORS(app)
label_names=np.array(['premjesti bateriju', 'premjesti zvakacu gumu', 'premjesti cokoladicu', 'premjesti cigarete', 'premjesti kremu',
            'premjesti upaljac', 'premjesti kemijsku olovku', 'premjesti srafciger', 'premjesti usb'])
arm = Arm("USB",serialcom="COM3")


model=SpeechRecognition("model.keras")
position = Positions(model_path='./obb-best.pt',)

@app.route('/test',methods=["GET"])
def test():
    return Response(status=200)
 
@app.route('/send_audio',methods=["POST"])
def get_audio():
    query = request.json
    data=query['data']
   # print(query['data'])
    audio_binary = base64.b64decode(data)
    pred=model.predict(audio_binary)
    position.find_positions()
    cordinates=position.get_cordinates(pred)
    arm.moveToPosition(*cordinates)
    arm.unload()
    print(label_names[pred])
    new_data = {
            "pred":str(pred),
            }
    return jsonify(new_data),200


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')


import time
print("proso")
time.sleep(100)
position.find_positions()
cordinates=position.get_cordinates(5)
print(cordinates)
position=[151.,12.,10.,33.]
arm.moveToPosition(*cordinates)
#arm.unload()
print("ended")

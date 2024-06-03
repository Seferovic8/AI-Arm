from positions.positions import Positions
from Arm.arm import Arm
from SpeechRecognition.speechRecognition import SpeechRecognition
from flask import Flask,Response,request,jsonify
import base64
import threading    
from flask_cors import CORS  # Import CORS from flask_cors
import time
import warnings

# Suppress the specific UserWarning from google.protobuf.symbol_database
warnings.filterwarnings(
    "ignore",
    message="SymbolDatabase.GetPrototype() is deprecated. Please use message_factory.GetMessageClass() instead.",
    category=UserWarning
)


time.sleep(5)
app = Flask(__name__)
CORS(app)

arm = Arm("USB",serialcom="/dev/ttyACM0")


model=SpeechRecognition("/root/Ai-Arm/model_2.checkpoint6.keras",doPath="/root/Ai-Arm/model1.keras")
position = Positions(model_path='/root/Ai-Arm/obb-best_openvino_model')

@app.route('/test',methods=["GET"])
def test():
    return Response(status=200)
def do_function(doPred,objectPred):
    # Your function code here
    position.find_positions()
    cordinates = position.get_cordinates(objectPred)
    if cordinates==False: return
    arm.moveToPosition(*cordinates)
    if(doPred==False):
        arm.unload()
    else:
        arm.follow()
@app.route('/send_audio',methods=["POST"])
def get_audio():
    query = request.json
    data=query['data']
   # print(query['data'])
    audio_binary = base64.b64decode(data)
    doPred, objectPred=model.predict(audio_binary)

    threading.Thread(target=do_function, args=(doPred,objectPred)).start()
    new_data = {
                "doPred":str(doPred),
                "objectPred":str(objectPred),
                }
    #print(new_data)
    return jsonify(new_data),200


if __name__ == '__main__':
    app.run(debug=False,host='0.0.0.0')
    #arm.follow()
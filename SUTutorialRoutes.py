from flask import Flask, render_template, request, Blueprint,send_from_directory,session,redirect,url_for,jsonify
import os
from random import randint
import binascii
import time
from similarUI import  SimilarUIBOW,similarUIUtility
# from similarUI import  SimilarUIBOWTest
from helpers import StrokeParse
import pickle
from mlModule.FastPredict import FastPredict
import pickle
from mlModule.Predict23LSTM import Predictor23LSTM
from RectUtils.RectObj import RectObj
from mlModule import GetPrediction

# Set Folder for model
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
output_directory = os.path.join(APP_ROOT,'My23Records5')
export_dir = os.path.join(APP_ROOT,'My23Records5','tb')
RICO_PATH= os.path.join(APP_ROOT, 'similarUI',"RICO23BOWCount.pkl")
# Load dictionary for searching
pkl_file = open(RICO_PATH, 'rb')
RICO = pickle.load(pkl_file)
pkl_file.close()
TEMPLATE_FOLDER = os.path.join(APP_ROOT, 'templates','Tutorials')


sUTutorialRoutes = Blueprint('SUTutorialRoutes', __name__, template_folder=TEMPLATE_FOLDER)
RICO2 = {18: 1.3078818029580455, 17: 1.139763200847382, 7: 1.6042572583253525, 23: 0.20480255166735367, 13: 1.2705841196816363, 21: 1.2151277497211468, 14: 1.109574534964655, 4: 1.27350305661627, 1: 0.5610761239057094, 8: 1.2898451990888444, 3: 1.1001165287284727, 19: 0.2384449560029641, 22: 1.3393355557525861, 0: 0.9671365739392712, 2: 1.6390691490153984, 15: 0.8551847317189294, 6: 2.3419400282173046, 20: 0.026601131356820077, 9: 1.2291284704809808, 12: 0.6849345254248218, 16: 1.076536962335742, 10: 0.10631666807601393, 5: 0.254524251188198, 11: 0}
# Load model for faster prediction
PREDICTOR = Predictor23LSTM(export_dir,output_directory)
FASTPREDICT = FastPredict(PREDICTOR.classifier,PREDICTOR.example_input_fn)

# Create Json dict from rect to pass it to canvas to sketch.
def rectObjtoJson(rectObj):
    dictObj = {'x':str(rectObj.x), 'y':str(rectObj.y),'width':str(rectObj.width),'height':str(rectObj.height),'iconID':str(rectObj.iconID),'elementId':str(rectObj.elementId)}
    return dictObj

# Generate token to record the drawing of current session
def generateToken(tokenSize):
    byteToken = os.urandom(tokenSize)
    hexToken = binascii.hexlify(byteToken)
    return hexToken.decode("utf-8")

# Setting page for Tutorials
@sUTutorialRoutes.route('/toolIns/')
def toolIns():
    return render_template('UIRetTutorial1.html')

# Setting page for Tutorials

@sUTutorialRoutes.route('/toolIns_1/')
def toolIns_1():
    session['ELEMENTID'] =  0
    session['RectObjs'] = []
    return render_template('UIRetTutorial2.html')

# Setting page for Tutorials
@sUTutorialRoutes.route('/toolIns_2/')
def toolIns_2():
    return render_template('UIRetTutorial3.html')

@sUTutorialRoutes.route('/UIRetTutorial/')
def UIRetTutorial():
    if 'username' not in session:
        session['username'] = generateToken(16)
    session['ELEMENTID'] =  0
    session['RectObjs'] = []
    return render_template('UIRetTutorial4.html')


@sUTutorialRoutes.route('/similarUI/')
def similarUI():
    session['ELEMENTID'] = 0
    session['RectObjs'] = []

    return render_template('SimilarUIRetrieval.html')



# Ger prediction while drawing
@sUTutorialRoutes.route('/MidPredictSimilar/', methods=['GET','POST'])
def MidPredictSimilar():
    if request.method == 'POST':
        canvas_strokes = request.form['save_data']
#        start = timeit.default_timer()
        if(session['strtTime']==-1):
            session['strtTime'] = round(time.monotonic()*1000)


        compressStroke,rect = StrokeParse.compressDataForFullUI(canvas_strokes)

        if len(compressStroke)==0:
            result = "Unchanged"
        else:
            result =GetPrediction.getFasterTop3Predict(compressStroke, PREDICTOR, FASTPREDICT )


        response = jsonify(predictedResult =result)
        return response





# Remove last icon from the session and update page accordingly for last tutorial

@sUTutorialRoutes.route('/RemoveLastIconForTest/', methods=['GET', 'POST'])
def RemoveLastIconForTest():
    elementID = session['ELEMENTID']
    rectObjs = session['RectObjs']

    for item in rectObjs:
        if (item['elementId'] == str(elementID - 1)):
            rectObjs.remove(item)
            break

    session['RectObjs'] = rectObjs
    session['ELEMENTID'] = elementID - 1
    if len(rectObjs) == 0:
        response = jsonify(similarUI=[])
        return response

    jsonRectObjs = session['RectObjs']
    canvasWidth = int(session['canvas_width'])
    canvasHeight = int(session['canvas_height'])
    similarUIArray = SimilarUIBOW.findSimilarUIForTest(jsonRectObjs, RICO, canvasWidth, canvasHeight, RICO2)

    response = jsonify(similarUI=similarUIArray)
    return response


# Find if there is a text button in the drawings on the session. It's for class select.
@sUTutorialRoutes.route('/FindTextButtonOnClassSelect/', methods=['GET', 'POST'])
def FindTextButtonOnClassSelect():
    elementID = session['ELEMENTID']
    if request.method == 'POST':
        jsonRectObjs = session['RectObjs']
        width = request.form['canvas_width']
        height = request.form['canvas_height']
        hasText = similarUIUtility.isATextButton(jsonRectObjs,int(width),int(height))
        session['ELEMENTID'] = elementID + 1
        responseResult = "No"
        if(hasText):
            responseResult= "Yes"
        response = jsonify(reponseText=responseResult)
        return response

# Find if there is a text button in the drawings on the session plus current drawing.
@sUTutorialRoutes.route('/FindTextButton/', methods=['GET', 'POST'])
def FindTextButton():
    hasText = False
    elementID = session['ELEMENTID']
    if request.method == 'POST':
        canvas_strokes = request.form['save_data']
        compressStroke, rect = StrokeParse.compressDataForFullUI(canvas_strokes)
        if len(compressStroke) == 0:
            responseResult = "Unchanged"
        else:
            result = GetPrediction.getFasterTop3Predict(compressStroke, PREDICTOR, FASTPREDICT)
            resultID = int(result[session['CurrentClassLabel']][1])
            rectObj = RectObj(rect, resultID, elementID)
            jsonRectObj = rectObjtoJson(rectObj)

            #   Maintaining Session for Tracking Elements
            jsonRectObjs = session['RectObjs']
            jsonRectObjs.append(jsonRectObj)
            session['RectObjs'] = jsonRectObjs
            width = request.form['canvas_width']
            height = request.form['canvas_height']
            hasText = similarUIUtility.isATextButton(jsonRectObjs,int(width),int(height))
        session['ELEMENTID'] = elementID + 1
        responseResult = "No"
        if(hasText):
            responseResult= "Yes"
        response = jsonify(reponseText=responseResult)
        return response


# Saving drawings in the session for further process for first Tutorial
@sUTutorialRoutes.route('/DrawSaveForFirstTutorial/', methods=['GET', 'POST'])
def DrawSaveForFirstTutorial():
    elementID = session['ELEMENTID']
    if request.method == 'POST':
        canvas_strokes = request.form['save_data']
        compressStroke, rect = StrokeParse.compressDataForFullUI(canvas_strokes)
        if len(compressStroke) == 0:
            responseResult = "Unchanged"
        else:
            result = GetPrediction.getFasterTop3Predict(compressStroke, PREDICTOR, FASTPREDICT)
            resultID = int(result[session['CurrentClassLabel']][1])
            rectObj = RectObj(rect, resultID, elementID)
            jsonRectObj = rectObjtoJson(rectObj)

            #   Maintaining Session for Tracking Elements
            jsonRectObjs = session['RectObjs']
            jsonRectObjs.append(jsonRectObj)
            session['RectObjs'] = jsonRectObjs
            responseResult ="Changed"
        session['ELEMENTID'] = elementID + 1

        response = jsonify(predictedResult=responseResult)
        return response

# Saving drawings in the session for further process for last tutorial

@sUTutorialRoutes.route('/DrawSaveForTest/', methods=['GET', 'POST'])
def DrawSaveForTest():
    elementID = session['ELEMENTID']
    if request.method == 'POST':
        canvas_strokes = request.form['save_data']
        similarUIArray=[]
        compressStroke, rect = StrokeParse.compressDataForFullUI(canvas_strokes)
        if len(compressStroke) == 0:
            responseResult = "Unchanged"
        else:
            result = GetPrediction.getFasterTop3Predict(compressStroke, PREDICTOR, FASTPREDICT)
            resultID = int(result[session['CurrentClassLabel']][1])
            rectObj = RectObj(rect, resultID, elementID)

            jsonRectObj = rectObjtoJson(rectObj)

            #   Maintaining Session for Tracking Elements
            jsonRectObjs = session['RectObjs']
            jsonRectObjs.append(jsonRectObj)
            session['RectObjs'] = jsonRectObjs


            canvasWidth = int(session['canvas_width'])
            canvasHeight = int(session['canvas_height'])


            similarUIArray = SimilarUIBOW.findSimilarUIForTest(jsonRectObjs, RICO, canvasWidth, canvasHeight, RICO2)
            responseResult = "Updated"

        session['ELEMENTID'] = elementID + 1

        response = jsonify(predictedResult=responseResult, similarUI=similarUIArray)
        return response



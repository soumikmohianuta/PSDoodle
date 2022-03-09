from flask import Flask, render_template, request, Blueprint,send_from_directory,session,redirect,url_for,jsonify
import os
from random import randint
import binascii
import time
from similarUI import  SimilarUIBOW
# from helpers import DynamoDBCompare,StrokeParse
import pickle
from mlModule.FastPredict import FastPredict
import pickle
from mlModule.Predict23LSTM import Predictor23LSTM
from RectUtils.RectObj import RectObj
from mlModule import GetPrediction
from helpers import StrokeParse
# set all folders for model
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
output_directory = os.path.join(APP_ROOT,'My23Records5')
export_dir = os.path.join(APP_ROOT,'My23Records5','tb')
RICO_PATH= os.path.join(APP_ROOT, 'similarUI',"RICO23BOWCount.pkl")

# loads dictionary for prediction
pkl_file = open(RICO_PATH, 'rb')
RICO = pickle.load(pkl_file)
pkl_file.close()

# set blueprint for the route
similarUIRoutes = Blueprint('SimilarUIRoutes', __name__, template_folder='templates')


RICO2 = {18: 1.3078818029580455, 17: 1.139763200847382, 7: 1.6042572583253525, 23: 0.20480255166735367, 13: 1.2705841196816363, 21: 1.2151277497211468, 14: 1.109574534964655, 4: 1.27350305661627, 1: 0.5610761239057094, 8: 1.2898451990888444, 3: 1.1001165287284727, 19: 0.2384449560029641, 22: 1.3393355557525861, 0: 0.9671365739392712, 2: 1.6390691490153984, 15: 0.8551847317189294, 6: 2.3419400282173046, 20: 0.026601131356820077, 9: 1.2291284704809808, 12: 0.6849345254248218, 16: 1.076536962335742, 10: 0.10631666807601393, 5: 0.254524251188198, 11: 0}
# loads model for prediction
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

# Set all the session to deafault. This page is for comparison (A UI at left). Let cosider all item with this page as- "Compare"
@similarUIRoutes.route('/UIRetrieval/')
def UIRetrieval():
    if 'username' not in session:
        session['username'] = generateToken(16)
    session['ELEMENTID'] =  0
    session['RectObjs'] = []
    session['SimilarStrokes']=[]
    session['strtTime'] = -1
    session['endTime'] = -1
    session['canvasStrokes'] =  []
    session['retrievedImage'] =  []
    return render_template('UIRetrieval.html')

# Set all the session to deafault. This page is for paid review
@similarUIRoutes.route('/UIRetEval/')
def UIRetEval():
    if 'username' not in session:
        session['username'] = generateToken(16)
    session['ELEMENTID'] =  0
    session['RectObjs'] = []
    session['SimilarStrokes']=[]
    session['strtTime'] = -1
    session['endTime'] = -1
    session['canvasStrokes'] =  []
    session['retrievedImage'] =  []

    return render_template('UIRetEval.html')

# Set all the session to deafault. This page is for a Test page. No user data stored for this session.

@similarUIRoutes.route('/UIRetrievalTest/')
def UIRetrievalTest():
    if 'username' not in session:
        session['username'] = generateToken(16)
    session['ELEMENTID'] =  0
    session['RectObjs'] = []
    return render_template('UIRetrievalTest.html')

# A single canvas with for search. Let cosider all item with this page as- "Similar"
@similarUIRoutes.route('/similarUI/')
def similarUI():
    session['ELEMENTID'] = 0
    session['RectObjs'] = []

    return render_template('SimilarUIRetrieval.html')


# Similar and compare functions are different. Have to track drawings in the session for prediction.

# Add mid prediction for Similar page
@similarUIRoutes.route('/MidPredictSimilar/', methods=['GET','POST'])
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



# Remove last drawing from session for Similar and update search result.
@similarUIRoutes.route('/RemoveLastIconForSimilar/', methods=['GET', 'POST'])
def RemoveLastIconForSimilar():
    elementID = session['ELEMENTID']
    rectObjs = session['RectObjs']
    for item in rectObjs:
        if (item['elementId'] == str(elementID - 1)):
            rectObjs.remove(item)
            break
    #    print(rectObjs)
    session['RectObjs'] = rectObjs
    session['ELEMENTID'] = elementID - 1
    if len(rectObjs) == 0:
        response = jsonify(similarUI=[])
        return response

    # print(len(rectObjs))
    canvasWidth = int(session['canvas_width'])
    canvasHeight = int(session['canvas_height'])

    similarUIArray = SimilarUIBOW.findSimilarUI(rectObjs, RICO, canvasWidth, canvasHeight, RICO2)

    response = jsonify(similarUI=similarUIArray)
    return response

# Get last drawing from Canvas for Similar and update search result.

@similarUIRoutes.route('/DrawSaveWithSimilar/', methods=['GET', 'POST'])
def DrawSaveWithSimilar():
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

            jsonRectObjs = session['RectObjs']

            jsonRectObjs.append(jsonRectObj)
            session['RectObjs'] = jsonRectObjs

            canvasWidth = int(session['canvas_width'])
            canvasHeight = int(session['canvas_height'])
            # tic = time.clock()

            similarUIArray = SimilarUIBOW.findSimilarUI(jsonRectObjs, RICO, canvasWidth, canvasHeight, RICO2)

            session['ELEMENTID'] = elementID + 1
            responseResult = "Updated"

        response = jsonify(predictedResult=responseResult, similarUI=similarUIArray)
        return response

# Get last drawing from Canvas for Compare, update search result and also put drawings in the session.

@similarUIRoutes.route('/RemoveLastIconForSimilarCompare/', methods=['GET', 'POST'])
def RemoveLastIconForSimilarCompare():
    elementID = session['ELEMENTID']
    rectObjs = session['RectObjs']
    print(len(rectObjs))

    for item in rectObjs:
        if (item['elementId'] == str(elementID - 1)):
            rectObjs.remove(item)
            break

    currentStrokes = session['SimilarStrokes']
    if len(currentStrokes) != 0:
        currentStrokes.pop()
    session['SimilarStrokes'] = currentStrokes

    session['RectObjs'] = rectObjs
    session['ELEMENTID'] = elementID - 1

    if len(rectObjs) == 0:
        response = jsonify(similarUI=[])
        return response

    jsonRectObjs = session['RectObjs']
    drawingStroke = session['SimilarStrokes']
    canvasWidth = int(session['canvas_width'])
    canvasHeight = int(session['canvas_height'])
    curTs = round(time.monotonic() * 1000) - session['strtTime']
    similarUIArray = SimilarUIBOW.findSimilarUIForCompare(jsonRectObjs, currentStrokes, RICO, canvasWidth, canvasHeight,
                                                          RICO2, session['taskID'], session['UIISimilarImage'], curTs)
    session['retrievedImage'] = similarUIArray[0:10]
    # similarUIArray = SimilarTFIDFWithFiltering.findSimilarGridLoadedRICO(jsonRectObjs,RICO,RICO1,RICO2,canvasWidth,canvasHeight)
    session['endTime'] = round(time.monotonic() * 1000)
    response = jsonify(similarUI=similarUIArray)
    return response

# Remove last drawing from session for Compare and update search result. As all json object of drawings are stored in the session, we need to change the json object.
@similarUIRoutes.route('/DrawSaveForCompare/', methods=['GET', 'POST'])
def DrawSaveForCompare():
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

            #   Maintaining Session for Tracking Elements
            currentStrokes = session['SimilarStrokes']
            currentStrokes.append(compressStroke)
            session['SimilarStrokes'] = currentStrokes

            canvasWidth = int(session['canvas_width'])
            canvasHeight = int(session['canvas_height'])

            curTs = round(time.monotonic() * 1000) - session['strtTime']

            similarUIArray = SimilarUIBOW.findSimilarUIForCompare(jsonRectObjs, currentStrokes, RICO, canvasWidth,
                                                                  canvasHeight, RICO2, session['taskID'],
                                                                  session['UIISimilarImage'], curTs)
            session['retrievedImage'] = similarUIArray[0:10]
            # similarUIArray = SimilarTFIDFWithFiltering.findSimilarGridLoadedRICO(jsonRectObjs,RICO,RICO1,RICO2,canvasWidth,canvasHeight)
            responseResult = "Updated"
        session['endTime'] = round(time.monotonic()*1000)
        session['ELEMENTID'] = elementID + 1

        response = jsonify(predictedResult=responseResult, similarUI=similarUIArray)
        return response


# Fetch prediction during drawing
@similarUIRoutes.route('/MidPredictDoodle/', methods=['GET','POST'])
def MidPredictDoodle():
    if request.method == 'POST':
        canvas_strokes = request.form['save_data']

        compressStroke,rect = StrokeParse.compressDataForFullUI(canvas_strokes)

        if len(compressStroke)==0:
            result = "Unchanged"
        else:
            result =GetPrediction.getFasterTop3Predict(compressStroke, PREDICTOR, FASTPREDICT )

        response = jsonify(predictedResult =result)
        return response

# When user press sucess update the dyanamoDB table accordingly
@similarUIRoutes.route('/SuccessRelevance/')
def SuccessRelevance():

    # curTs = session['endTime'] - session['strtTime']
             # remove for free up the session
    session['ELEMENTID'] = 0
    session['RectObjs'] = []
    session['strtTime'] = -1
    session['endTime'] = -1
    # DynamoDBCompare.setSuccess(session['taskID'], True, curTs)
    return render_template('UIRetrievalRelevance.html')

# When user press failure update the dyanamoDB table accordingly
@similarUIRoutes.route('/FailureRelevance/')
def FailureRelevance():
        curTs = session['endTime'] - session['strtTime']
        session['ELEMENTID'] = 0
        session['RectObjs'] = []
        session['strtTime'] = -1
        session['endTime'] = -1
        # DynamoDBCompare.setSuccess(session['taskID'], False, curTs)
        return render_template('UIRetrievalRelevance.html')

# When user press success update the dyanamoDB table accordingly. Similar as upper success remove this for redundancy later.

@similarUIRoutes.route('/SuccessRelevanceEval/')
def SuccessRelevanceEval():

    curTs = session['endTime'] - session['strtTime']
             # remove for free up the session
    session['ELEMENTID'] = 0
    session['RectObjs'] = []
    session['strtTime'] = -1
    session['endTime'] = -1
    # DynamoDBCompare.setSuccess(session['taskID'], True, curTs)
    return render_template('UIRelevanceForEval.html')

# When user press failure update the dyanamoDB table accordingly. Similar as upper success remove this for redundancy later.

@similarUIRoutes.route('/FailureRelevanceEval/')
def FailureRelevanceEval():
        curTs = session['endTime'] - session['strtTime']
        session['ELEMENTID'] = 0
        session['RectObjs'] = []
        session['strtTime'] = -1
        session['endTime'] = -1
        # DynamoDBCompare.setSuccess(session['taskID'], False, curTs)
        return render_template('UIRelevanceForEval.html')

# Image from RICO considered for compare. Set it randomly
@similarUIRoutes.route('/setUIISimilarImage/', methods=['GET', 'POST'])
def setUIISimilarImage():
    if request.method == 'POST':
        session['taskID'] = generateToken(12)
        dataArraY = [10319, 10779, 1095, 11011, 11231, 11365, 11714, 11739, 11949, 1212, 12181, 1224, 12282, 12421,
                     12768, 12905, 13201, 13204, 13210, 13248, 13308, 13361, 13419, 1354, 13559, 13630, 13677, 13804,
                     1407, 14159, 14578, 15260, 1536, 16072, 17370, 1758, 17829, 17906, 18170, 18453, 18574, 20675,
                     22393, 22809, 24211, 25008, 27497, 27553, 28072, 28915, 293, 29365, 29833, 30208, 31233, 32310,
                     32805]

        randNo = randint(0, len(dataArraY) - 1)
        imageID = str(dataArraY[randNo])
        session['UIISimilarImage'] = imageID
        srcImage = "https://ricoimage.s3.us-east-2.amazonaws.com/OnlyImage/" + imageID + ".jpg"
        response = jsonify(image=srcImage)

        # DynamoDBCompare.creteNewItem(session['taskID'], session['username'], session['UIISimilarImage'])

        return response

# Image from RICO considered for compare. Set it randomly and also set dyanamoDB to indicate it is a paid review.
@similarUIRoutes.route('/setUIISimilarImageForEval/', methods=['GET', 'POST'])
def setUIISimilarImageForEval():
    if request.method == 'POST':
        session['taskID'] = generateToken(12)
        dataArraY= [10319,10779,1095,11011,11231,11365,11714,11739,11949,1212,12181,1224,12282,12421,12768,12905,13201,13204,13210,13248,13308,13361,13419,1354,13559,13630,13677,13804,1407,14159,14578,15260,1536,16072,17370,1758,17829,17906,18170,18453,18574,20675,22393,22809,24211,25008,27497,27553,28072,28915,293,29365,29833,30208,31233,32310,32805]

        randNo = randint(0, len(dataArraY) - 1)
        imageID = str(dataArraY[randNo])
        session['UIISimilarImage'] = imageID
        srcImage = "https://ricoimage.s3.us-east-2.amazonaws.com/OnlyImage/" +imageID + ".jpg"
        response = jsonify(image=srcImage)

        # DynamoDBCompare.creteNewItemForEval(session['taskID'], session['username'], session['UIISimilarImage'])

        return response

# Set Relevance Page. Get drawing from session and sent to the front end
@similarUIRoutes.route('/setPageForRelevance/', methods=['GET', 'POST'])
def setPageForRelevance():
        if request.method == 'POST':
            imageArray=[]
            sketchArray=[]
            if('SimilarStrokes' in session and 'retrievedImage' in session):
                imageArray = session['retrievedImage']

                sketchArray = session['SimilarStrokes']
            response = jsonify(image=imageArray, sketch=sketchArray)

            return response

# Save the relevance result into dynamoDB

@similarUIRoutes.route('/SaveRelevance/', methods=['GET', 'POST'])
def SaveRelevance():
    if request.method == 'POST':

        curRelObj = request.form['save_data']
        # DynamoDBCompare.setRelevance(session['taskID'], curRelObj)
        return "Ok"




# Only for Test Page. Not required at this moment. Remove it.

@similarUIRoutes.route('/RemoveLastIconForTest/', methods=['GET', 'POST'])
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

# Only for Test Page. Not required at this moment. Remove it.

@similarUIRoutes.route('/DrawSaveForTest/', methods=['GET', 'POST'])
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
# Only for Test Page. Not required at this moment. Remove it.

@similarUIRoutes.route('/setUIISimilarImageTest/', methods=['GET', 'POST'])
def setUIISimilarImageTest():
    if request.method == 'POST':

        dataArraY = ['10690', '1119', '12329', '1239', '12711', '1281', '1282', '12921', '12928', '12932', '12936',
                     '12940', '13194', '13763', '13764', '13803', '1405', '1406', '16962', '16967', '17027', '17704',
                     '18524', '18533', '19093', '23115', '23615', '24012', '25253', '25261', '2579', '27241', '27955',
                     '28221', '28223', '28909', '28969', '28975', '2964', '29768', '29770', '29771', '29825', '29911',
                     '30131', '30626', '31143', '32464', '32799', '32800', '33176', '33185', '33578', '34140', '34747',
                     '35724', '3721', '37242', '38448', '40383', '40544', '40573', '41038', '4134', '4144', '41568',
                     '4157', '42159', '45645', '47187', '47382', '50314', '50839', '50917', '52988', '54833', '56556',
                     '64094', '64105', '65960', '6605', '69254', '69255', '8530', '8948']

        randNo = randint(0, len(dataArraY) - 1)
        session['UIISimilarImage'] = dataArraY[randNo]
        srcImage = "https://ricoimage.s3.us-east-2.amazonaws.com/OnlyImage/" + dataArraY[randNo] + ".jpg"
        response = jsonify(image=srcImage)
        return response

@similarUIRoutes.route('/RetrieveSuccessTest/', methods=['GET', 'POST'])
def RetrieveSuccessTest():
    if request.method == 'POST':

        return "Ok"


@similarUIRoutes.route('/RetrieveFailedTest/', methods=['GET', 'POST'])
def RetrieveFailedTest():
    if request.method == 'POST':
        return "Ok"

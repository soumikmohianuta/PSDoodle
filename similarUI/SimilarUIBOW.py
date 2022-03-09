"""
Created on Tue Feb 25 12:17:00 2020

@author: sxm6202xx
"""
import os
from similarUI import similarUIUtility
from similarUI import FindIntersectingPercentage
# from helpers import DynamoDBCompare
import pickle

# divide the canvas into 4 by 6 zones
WidthZone = 4
HeightZone = 6

# Mapping class Name to Dictionay Key

dictMapper = {'avatar': 0, 'back': 1, 'camera': 2, 'cancel': 3, 'checkbox': 4, 'generalIcon': 5, 'dropDown': 6,
              'envelope': 7, 'forward': 8, 'house': 9, 'imageIcon': 10, 'leftarrow': 1, 'menu': 12, 'play': 13,
              'plus': 14, 'search': 15, 'settings': 16, 'share': 17, 'sliders': 18, 'square': 19, 'squiggle': 20,
              'star': 21, 'switch': 22, 'textButton': 23}
hierMapper = {'avatar': 24, 'back': 25, 'camera': 26, 'cancel': 27, 'checkbox': 28, 'generalIcon': 29, 'dropDown': 30,
              'envelope': 31, 'forward': 32, 'house': 33, 'imageIcon': 25, 'leftarrow': 35, 'menu': 36, 'play': 37,
              'plus': 38, 'search': 39, 'settings': 40, 'share': 41, 'sliders': 42, 'square': 43, 'squiggle': 44,
              'star': 45, 'switch': 46, 'textButton': 47}
noOfElement = 24


# Divide canvas into 4 by 4 grid and find position of element in the grid
def findPosition(x, y, width, height):
    # print(x,y,width, height)
    xGridSize = width / WidthZone
    yGridSize = height / HeightZone
    xGrid = int(x / xGridSize)
    yGrid = int(y / yGridSize)
    return xGrid + yGrid * WidthZone


def cordToInt(x, y):
    return x + y * WidthZone


# From the elementType and position generate object position weight. Current no use of parent hierarchy

def getPositionObj(elementType, parent, curPosAreas, recPosDict):
    elementKey = dictMapper[elementType]

    for curPos in range(24):
        if curPosAreas[curPos] != 0:
            if elementKey not in recPosDict:
                curElmPosObj = {}
                curElmPosObj[curPos] = (curPosAreas[curPos], 1)
                recPosDict[elementKey] = curElmPosObj
            else:
                if curPos not in recPosDict[elementKey]:
                    curElmPosObj = (curPosAreas[curPos], 1)
                    # curElmPosObj[curPos] = (curPosAreas[curPos],1)
                    recPosDict[elementKey][curPos] = curElmPosObj
                else:
                    curElmPosObj = recPosDict[elementKey][curPos]
                    newCurPosAreas = round(curElmPosObj[0] + curPosAreas[curPos], 3)
                    recPosDict[elementKey][curPos] = (newCurPosAreas, curElmPosObj[1] + 1)


def hierArchyToDictObjInternal(parent, child, rectPositionDict, width, height):
    elementType = child.getIconName()

    # if child.iconID !=-1:
    xCur = child.x + parent.x
    yCur = child.y + parent.y
    curPosAreas = FindIntersectingPercentage.findRectAreaPercent(xCur, yCur, child.width, child.height, width, height,
                                                                 WidthZone, HeightZone)

    getPositionObj(elementType, parent, curPosAreas, rectPositionDict)
    # if hierarchy matches then give weight 1

    for curChild in child.mChildren:
        hierArchyToDictObjInternal(child, curChild, rectPositionDict, width, height)
    return

# From hierarchy of Rectobj's create dictionay object for comparison.
def hierArchyToDictObj(rootObj, width, height):
    rectPositionDict = {}
    for curChild in rootObj.mChildren:
        hierArchyToDictObjInternal(rootObj, curChild, rectPositionDict, width, height)

    return rectPositionDict


# create hierarchy for finding text button
# then convert elements into array of element
def getRectObjsWithHier(jsonRootObjs, width, height):
    # print(jsonRootObjs)
    rawRects = similarUIUtility.jsonToRect(jsonRootObjs)

    rectObj = {}
    if (len(rawRects) != 0):
        rootObj = similarUIUtility.createHierachy(rawRects, width, height)

        rectObj = hierArchyToDictObj(rootObj, width, height)

    return rectObj


# For a position find the neighbors in the bigger grid. Like for 4 by 6, look for 2 by 3 grid.

def find2Grid(pos):
    if pos in [0,1,4,5]:
        return [0,1,4,5]
    elif pos in [2,3,6,7]:
        return [2,3,6,7]
    elif pos in [8,9,12,13]:
        return [8,9,12,13]
    elif pos in [10,11,14,15]:
        return [10,11,14,15]
    elif pos in [16,17,20,21]:
        return [16,17,20,21]
    else:
        return [18,19,22,23]

# For a position find the neighbors in 8 diection.


def find2GridNeighbor(pos):
    neighDict = {0:[0,1,4,5],1:[0,1,4,5,2,6],2:[1,2,3,5,6,7],3:[2,3,6,7],
                 4:[0,1,4,5,8,9],5:[0,1,2,4,5,6,8,9,10],6:[1,2,3,5,6,7,9,10,11],7:[2,3,6,7,10,11],
                 8:[4,5,8,9,12,13],9:[4,5,6,8,9,10,12,13,14],10:[5,6,7,9,10,11,13,14,15],11:[6,7,10,11,14,15],
                 12:[8,9,12,13,16,17],13:[8,9,10,12,13,14,16,17,18],14:[9,10,11,13,14,15,17,18,19],15:[10,11,14,15,18,19],
                  16:[12,13,16,17,20,21],17:[12,13,14,16,17,18,20,21,22],18:[13,14,15,17,18,19,21,22,23],19:[14,15,18,19,22,23],
                 20:[16,17,20,21],21:[16,17,18,20,21,22],22:[17,18,19,21,22,23],23:[18,19,22,23]}
    return neighDict[pos]

def common_member(a, b):
    a_set = set(a)
    b_set = set(b)
    if (a_set & b_set):
        return True
    else:
        return False

# A simpple implementation where it looks for whole image, 2 by 3 and 4 by 6 and multiply by weight
def findWeightBase(posObject, posRico):
    firstGrid=1
    secondGrid=2
    thirdGrid = 30
    weight=firstGrid
    ricoDictKyes = posRico.keys()
    # print(posObject)
    for pos in posObject:
        if pos in ricoDictKyes:
            weight = weight+thirdGrid*(posObject[pos][0]/posObject[pos][1])*(posRico[pos][0]/posRico[pos][1])
        elif common_member(find2Grid(pos),ricoDictKyes):
            weight = weight + secondGrid*(posObject[pos][0]/posObject[pos][1])
    return weight


def findWeightWithArea(posObject, posRico):
    # Paremters are optimized in another project for sample data.
    parameters=[9,8,39,0.4,547]
    # Weight for match in whole UI
    firstPyramid=parameters[0]
    # Weight for match in same neighbor grid
    secondPyramid=parameters[1]
    # Weight for match in same grid

    thirdPyramid = parameters[2]
    ricoDictKyes = posRico.keys()
    weight=firstPyramid
    # Penalty if number of elements in RICO and current drawing differs for a certain element in a certain grid.
    elemDifferPenalty = parameters[3]
    # Penalty if weight of elements in RICO and current drawing differs for a certain element in a certain grid.
    # weight = element unit area / no of element
    singledifferWeight = parameters[4]

    for pos in posObject:
        if pos in ricoDictKyes:
            noOfElement = posObject[pos][1]
            drawingAreaPosWeight = posObject[pos][0] / noOfElement

            elementInRICO = posRico[pos][1]
            # weight = element unit area / no of element
            areaWeightInRICO = posRico[pos][0] / (100 * elementInRICO)

            noOfElement = posObject[pos][1]

            elementDifferWeight = 1
            # Find difference in element number
            elementDiffer = abs(noOfElement - elementInRICO)

            # Penalty if element number differ
            if elementDiffer != 0:
                elementDifferWeight = elementDifferWeight - elemDifferPenalty * elementDiffer
            if elementDifferWeight < 0:
                elementDifferWeight = 0

            # Penalty if element weight differ

            areaWeightDiffer = 1-abs(areaWeightInRICO - drawingAreaPosWeight)

            # Scoring function
            weight = weight+thirdPyramid*(posObject[pos][0]/posObject[pos][1])*(posRico[pos][0]/posRico[pos][1]) + (noOfElement*elementDifferWeight*areaWeightDiffer * singledifferWeight)

            # Scoring function for neighbor match

        elif common_member(find2Grid(pos),ricoDictKyes):
            weight = weight + secondPyramid*(posObject[pos][0]/posObject[pos][1])
    return weight

def findAllUI(elementType, rectPosObj, similarUI, rico, idf):
    newSimilarUI={}
    if elementType != dictMapper['square']:
        # loop through individual UI element in drawing and calucate weight:
            ricoObjs = rico[elementType]
            for indvUI in ricoObjs:

                if str(indvUI) not in newSimilarUI:
                    newSimilarUI[str(indvUI)]=findWeightWithArea(rectPosObj,rico[elementType][indvUI])*idf[elementType]
                else:
                     newSimilarUI[str(indvUI)] = newSimilarUI[str(indvUI)] +findWeightWithArea(rectPosObj, rico[elementType][indvUI]) * idf[elementType]

    similarUI = {x: similarUI.get(x, 0) + newSimilarUI.get(x, 0) for x in set(similarUI).union(newSimilarUI)}

    return similarUI



def findSimilarUIForCompare(jsonRectObjs,currentStoke, rico, canvasWidth, canvasHeight, idf, taskID, targetUI, curTime):
    # print(canvasWidth, canvasHeight)
    similarUI = {}


    rectObjs = getRectObjsWithHier(jsonRectObjs, canvasWidth, canvasHeight)

    for elementType in rectObjs:
        # for singleElement in rectElementObj[elementType]:
        similarUI = findAllUI(elementType, rectObjs[elementType], similarUI, rico, idf)

    resultUI = [k for k, v in sorted(similarUI.items(), key=lambda item: item[1], reverse=True)]
    # Get rank for comparison and storing in the DB.

    curRank = -1

    if targetUI in resultUI:
        curRank = resultUI.index(targetUI)


    # DynamoDBCompare.setItem(taskID, curRank, curTime, currentStoke)

    return resultUI

    # Just a test function to Test the implementation on collected Data
def findSimilarUIForTest(jsonRectObjs, rico, canvasWidth, canvasHeight, idf):
    # print(canvasWidth, canvasHeight)
    similarUI = {}


    rectObjs = getRectObjsWithHier(jsonRectObjs, canvasWidth, canvasHeight)

    # print(rectObjs)
    # print(targetUI)

    for elementType in rectObjs:
        # for singleElement in rectElementObj[elementType]:
        similarUI = findAllUI(elementType, rectObjs[elementType], similarUI, rico, idf)

    resultUI = [k for k, v in sorted(similarUI.items(), key=lambda item: item[1], reverse=True)]



    return resultUI

def findSimilarUI(jsonRectObjs, rico, canvasWidth, canvasHeight, idf):
    similarUI = {}
    rectObjs = getRectObjsWithHier(jsonRectObjs, canvasWidth, canvasHeight)

    for elementType in rectObjs:
        similarUI = findAllUI(elementType, rectObjs[elementType], similarUI, rico, idf)

    resultUI = [k for k, v in sorted(similarUI.items(), key=lambda item: item[1], reverse=True)]

    return resultUI

   # Check perforamnce on collected Data
def justCheck(rectObjs, rico, idf):
    similarUI = {}

    for elementType in rectObjs:
        # for singleElement in rectElementObj[elementType]:
        similarUI = findAllUI(elementType, rectObjs[elementType], similarUI, rico, idf)

    resultUI = [k for k, v in sorted(similarUI.items(), key=lambda item: item[1], reverse=True)]
    # print(result)
    # get only the result
    targetUI = '18533'

    print("-----------------")
    print("Top Result Value")
    print(resultUI[2])
    print(similarUI[resultUI[2]])
    print("-----------------")

    if targetUI in resultUI:
        print("Current Result Value")
        print(similarUI[targetUI])
        print("Index")
        print(resultUI.index(targetUI))
        print("-*-*-*-*-*-*-*-*-*-*-*-*")

    return resultUI


if __name__ == "__main__":
    APP_ROOT = os.path.dirname(os.path.abspath(__file__))
    idf = {18: 1.3078818029580455, 17: 1.139763200847382, 7: 1.6042572583253525, 23: 0.20480255166735367,
           13: 1.2705841196816363, 21: 1.2151277497211468, 14: 1.109574534964655, 4: 1.27350305661627,
           1: 0.5610761239057094, 8: 1.2898451990888444, 3: 1.1001165287284727, 19: 0.2384449560029641,
           22: 1.3393355557525861, 0: 0.9671365739392712, 2: 1.6390691490153984, 15: 0.8551847317189294,
           6: 2.3419400282173046, 20: 0.026601131356820077, 9: 1.2291284704809808, 12: 0.6849345254248218,
           16: 1.076536962335742, 10: 0.10631666807601393, 5: 0.254524251188198, 11: 0}

    RICO_PATH = os.path.join(APP_ROOT, 'RICO23BOWCount.pkl')

    pkl_file = open(RICO_PATH, 'rb')
    rico = pickle.load(pkl_file)
    pkl_file.close()
    rectObj = {15: {3: (1.0, 1)}, 1: {0: (1.0, 1)}, 20: {0: (0.714, 1), 1: (0.286, 1)},
      18: {1: (0.244, 1), 2: (0.508, 1), 3: (0.248, 1)}}

    # rectObj = {1: {0: (1.0, 1)},
    #            20: {1: (1.57, 2), 2: (0.178, 1), 0: (0.252, 1), 4: (0.092, 1), 5: (0.24, 1), 6: (0.24, 1),
    #                 7: (0.057, 1), 8: (0.052, 1), 9: (0.134, 1), 10: (0.134, 1), 11: (0.032, 1)},
    #            10: {5: (0.894, 1), 6: (0.106, 1)}}
    # rectObj = {1: {0: (1.0, 1)}, 12: {3: (1.0, 1)}}

    justCheck(rectObj, rico, idf)

# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 16:16:28 2020

@author: sxm6202xx
"""

import os
import random
import json
from shutil import copyfile
from ast import literal_eval
from DictionaryGeneration import FindIntersectingPercentage
import pickle

# Folder where the Hierarchy JSON Folder resides
data_folder = r"similar_annotations_valid"

# Output Path
single_json = r"similarUI"
# Map Rico to Doodle supported element cluster
WidthZone = 4
HeightZone = 6
mapper = {'Text': 'squiggle', 'Background Image': 'imageIcon', 'Image': 'imageIcon', 'menu': 'menu', 'close': 'cancel',
          'arrow_forward': 'forward', 'share': 'share', 'play': 'play', 'sliders': 'sliders', 'arrow_backward': 'back',
          'Text Button': 'textButton', 'check': 'checkbox', 'star': 'star', 'On/Off Switch': 'switch',
          'Date Picker': 'dropDown', 'Checkbox': 'checkbox', 'settings': 'settings', 'add': 'plus',
          'Radio Button': 'checkbox', 'search': 'search', 'Slider': 'sliders', 'Toolbar': 'square', 'email': 'envelope',
          'photo': 'camera', 'home': 'house', 'avatar': 'avatar', 'otherIcon': 'generalIcon', 'filter_list': 'menu',
          'list': 'menu'}

childConsider = ['On/Off Switch', 'Checkbox']

radioButtonInclusion = ['Radio Button']

dictMapper = {'avatar': 0, 'back': 1, 'camera': 2, 'cancel': 3, 'checkbox': 4, 'generalIcon': 5, 'dropDown': 6,
              'envelope': 7, 'forward': 8, 'house': 9, 'imageIcon': 10, 'leftarrow': 1, 'menu': 12, 'play': 13,
              'plus': 14, 'search': 15, 'settings': 16, 'share': 17, 'sliders': 18, 'square': 19, 'squiggle': 20,
              'star': 21, 'switch': 22, 'textButton': 23}
hierMapper = {'avatar': 24, 'back': 25, 'camera': 26, 'cancel': 27, 'checkbox': 28, 'generalIcon': 29, 'dropDown': 30,
              'envelope': 31, 'forward': 32, 'house': 33, 'imageIcon': 34, 'leftarrow': 35, 'menu': 36, 'play': 37,
              'plus': 38, 'search': 39, 'settings': 40, 'share': 41, 'sliders': 42, 'square': 43, 'squiggle': 44,
              'star': 45, 'switch': 46, 'textButton': 47}

basicElement = ['On/Off Switch', 'Checkbox']


def findPosition(x, y, width, height):
    xGridSize = width / WidthZone
    yGridSize = height / HeightZone
    xGrid = int(x / xGridSize)
    yGrid = int(y / yGridSize)
    return xGrid + yGrid * WidthZone


def findArea(curWidth, curHeight, width, height):
    areaFraction = int(((curHeight * curHeight) / (width * height)) * 1000) / 1000.0
    return areaFraction

# Additional Criteria to find visually similar icon from hierarchy information
def additionalCriteria(elementTypes, elementTypeinRico, ancestors, classes):
    lastAncestor = ancestors[0]
    ancestorTypes = lastAncestor.split('.')
    ancestorTypes = ancestorTypes[-1]
    classlabel = classes.split('.')
    classlabel = classlabel[-1]

    if elementTypeinRico in ['Text', 'Image', 'Text Button', 'Input']:
        allowedAncestorTypeForCheck = ['CheckedTextView', 'AppCompatCheckedTextView', 'AppCompatCheckBox',
                                       'CheckableImageView', 'AnimationCheckBox', 'CheckableImageButton', 'CheckBox',
                                       'ColorableCheckBoxPreference']
        allowedClassTypeForCheck = ['AppCompatCheckBox', 'PreferenceCheckbox', 'CheckboxChoice', 'CheckboxTextView',
                                    'CenteredCheckBox', 'StyledCheckBox', 'CheckButton', 'AppCompatCheckBox',
                                    'CheckBox', 'CheckBoxMaterial']

        if ancestorTypes in allowedAncestorTypeForCheck or classlabel in allowedClassTypeForCheck:
            elementTypes.append('Checkbox')

        allowedAncestorTypeForSeek = ['RangeSeekBar', 'SeekBar']
        allowedClassTypeForSeek = ['RangeSeekBar', 'TwoThumbSeekBar', 'EqSeekBar', 'PriceRangeSeekBar',
                                   'VideoSliceSeekBar', 'SliderButton']
        if ancestorTypes in allowedAncestorTypeForSeek or classlabel in allowedClassTypeForSeek:
            elementTypes.append('Slider')

        allowedAncestorTypeForStar = ['RatingBar']
        allowedClassTypeForStar = ['RatingWidget', 'RatingSliderView', 'RatingView', 'Rating']
        if ancestorTypes in allowedAncestorTypeForStar or classlabel in allowedClassTypeForStar:
            elementTypes.append('star')

        allowedAncestorTypeForSwitch = ['SwitchCompat', 'Switch']
        allowedClassTypeForSwitch = ['SwitchCompat', 'CustomThemeSwitchButton', 'BetterSwitch', 'LabeledSwitch',
                                     'CustomToggleSwitch', 'CheckSwitchButton', 'CustomSwitch', 'MySwitch',
                                     'SwitchButton', 'Switch']
        if ancestorTypes in allowedAncestorTypeForSwitch or classlabel in allowedClassTypeForSwitch:
            elementTypes.append('On/Off Switch')

        allowedClassTypeForSwitch = ['CustomSearchView', 'SearchEditText', 'CustomSearchView', 'SearchBoxButton']
        if classlabel in allowedClassTypeForSwitch:
            elementTypes.append('search')


def radioButtonFix(prechild):
    ancestors = prechild['ancestors']
    isRadioButton = True
    for ancestor in ancestors:
        if 'TextView' in ancestor:
            isRadioButton = False
    if isRadioButton:
        return 'Radio Button'
    else:
        return 'Text Button'


def recursivelyFindChildren(parents, prechild, singleJSON, fileCount, width, height):

    bound = prechild['bounds']

    curPosAreas = FindIntersectingPercentage.findRectAreaPercent(bound[0], bound[1], bound[2] - bound[0],
                                                                 bound[3] - bound[1], width, height, WidthZone,
                                                                 HeightZone)

    # print(prechild['children'])
    elementTypeinRico = prechild['componentLabel']
    elementTypes = []
    # print(prechild)
    if elementTypeinRico in childConsider:
        if 'children' in prechild:
            # print('Coming Here')
            elementTypeinRico = "Avoid"

    if elementTypeinRico == "Icon" or 'iconClass' in prechild or "textButtonClass" in prechild:
        if "textButtonClass" in prechild:
            buttonType = prechild['textButtonClass']
            # if buttonType in mapper:
            #    elementTypes.append(buttonType)
        else:
            elementTypeinRico = prechild['iconClass']
            # play sometimes looks as arrow forward
            if elementTypeinRico == 'arrow_forward':
                elementTypes.append('play')
            if elementTypeinRico == 'play':
                elementTypes.append('arrow_forward')
            if elementTypeinRico == 'avatar':
                elementTypes.append('Image')

            if elementTypeinRico not in mapper:
                elementTypeinRico = 'otherIcon'

    if 'children' not in prechild:
        additionalCriteria(elementTypes, elementTypeinRico, prechild['ancestors'], prechild['class'])


    if elementTypeinRico == 'Radio Button':
        elementTypeinRico = radioButtonFix(prechild)


    elementTypes.append(elementTypeinRico)


    for elementType in elementTypes:

        if elementType in mapper:

            elementType = mapper[elementType]


            elementKey = dictMapper[elementType]

            if elementType != "square":
                for curPos in range(24):
                    if curPosAreas[curPos] != 0:

                        # print(elementKey)
                        if elementKey in singleJSON:

                            if fileCount in singleJSON[elementKey]:
                                if curPos in singleJSON[elementKey][fileCount]:
                                    singleJSON[elementKey][fileCount][curPos] = (singleJSON[elementKey][fileCount][curPos][0]+curPosAreas[curPos],singleJSON[elementKey][fileCount][curPos][1]+1)
                                else:
                                    singleJSON[elementKey][fileCount][curPos] = (curPosAreas[curPos],1)
                            else:
                                curDict={}
                                curDict[curPos] =(curPosAreas[curPos],1)
                                singleJSON[elementKey][fileCount]= curDict


                        else:
                           curDictPos = {}
                           curDictPos[curPos] = (curPosAreas[curPos],1)
                           curDict={}
                           curDict[fileCount] = curDictPos
                           singleJSON[elementKey] = curDict


    if 'children' in prechild:
        # print(prechild['children'])
        childrens = prechild['children']
        for child in childrens:
            recursivelyFindChildren(elementType, child, singleJSON, fileCount, width, height)
    return


def readJson(filename, singleJSON, fileCount):
    # rootObj = {}
    try:

        s = open(filename, 'r', encoding="utf8").read()
        outDict = json.loads(s)
        # print(outDict)
        #        print(outDict)
        bound = outDict['bounds']
        width = bound[2]
        height = bound[3]
        par = 'root'
        childrens = outDict['children']

        for child in childrens:
            recursivelyFindChildren(par, child, singleJSON, fileCount, width, height)
    except:
        pass
    #    print(singleJSON)
    # print(rootObj)
    return


def parserAllDirectory(folder):
    singleJSON = {}
    singleJSONPath = os.path.join(single_json, "RICO23BOWCount.json")
    #    global withinElement
    for file in os.listdir(folder):
        if 'json' in file:
            filePath = os.path.join(folder, file)
            # outfilePath = os.path.join(json_folder, file)
            fileCount = file.split('.')
            readJson(filePath, singleJSON, int(fileCount[0]))

    # print(singleJSON)
    f = open(singleJSONPath, "w+")
    f.write(str(singleJSON))
    f.close()
    return singleJSON


def SingleParse(fileName):
    singleJSON = {}
    filePath = os.path.join(data_folder, fileName)
    # outfilePath = os.path.join(json_folder, file)
    fileCount = fileName.split('.')
    readJson(filePath, singleJSON, fileCount[0])


    return singleJSON




def convertTointRound1():
    filePath = os.path.join(single_json,"RICO23BOWCount.json")
    s = open(filePath, 'r', encoding="utf8").read()
    inDict =  literal_eval(s)

    outDict = {}
    # db['key'] = 'value'
    # db['today'] = 'Sunday'
    # db['author'] = 'Doug'
    # db.close()
    for elemkey in inDict:
        outDict[elemkey] = {}
        for file in inDict[elemkey]:
            # posDict=[]
            outDict[elemkey][file] ={}
            for pos in inDict[elemkey][file]:
                if(inDict[elemkey][file][pos] !=0):
                    outDict[elemkey][int(file)][pos]=(int(inDict[elemkey][int(file)][pos][0]*100),inDict[elemkey][int(file)][pos][1])
    singleJSONPath=  os.path.join(single_json,"RICO23BOWCountInt.json")
    f = open(singleJSONPath, "w+")
    f.write(str(outDict))
    f.close()
    return

def convertToPickle():
    filePath = os.path.join(single_json,"RICO23BOWCountInt.json")
    s = open(filePath, 'r', encoding="utf8").read()
    ricoObj =  literal_eval(s)

    singleJSONPath= os.path.join(single_json,"RICO23BOWCountTB.pkl")

    output = open(singleJSONPath, 'wb')
    pickle.dump(ricoObj, output)
    output.close()


if __name__ == '__main__':
    # parserAllDirectory(data_folder)
    # convertTointRound1()
    # convertToPickle()
    # singleJSON = SingleParse('21420.json')
    # print(singleJSON[10]['21420'])
    val = SingleParse('13308.json')
    print(val[23])


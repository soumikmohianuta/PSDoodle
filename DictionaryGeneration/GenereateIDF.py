from collections import Counter
# from num2words import num2words
from ast import literal_eval
import decimal
import os
import math

# Folder where the Hierarchy JSON Folder resides
content_folder = r"contentJSON"

# Map Rico to Doodle supported element cluster
mapper = {'Text': 'text', 'Image': 'userImage', 'menu': 'hamburger', 'close': 'cancel', 'arrow_forward': 'forward',
          'share': 'share', 'play': 'play', 'sliders': 'sliders', 'arrow_backward': 'back', 'Text Button': 'textButton',
          'check': 'checkbox', 'star': 'star', 'On/Off Switch': 'toogle', 'Date Picker': 'dropDown',
          'Checkbox': 'checkbox', 'settings': 'settings', 'add': 'plus', 'Radio Button': 'toogle', 'search': 'search',
          'Slider': 'sliders', 'Toolbar': 'square', 'email': 'envelope', 'photo': 'camera'}

listElement = ['back', 'camera', 'cancel', 'checkbox', 'checkbox', 'dropDown', 'envelope', 'forward', 'hamburger',
               'play', 'plus', 'search', 'settings', 'share', 'sliders', 'sliders', 'square', 'star', 'text',
               'textButton', 'toogle', 'userImage']

# Map Doodle cluster to index
dictMapper = {'back': 0, 'camera': 1, 'cancel': 2, 'checkbox': 4, 'dropDown': 5, 'envelope': 6, 'forward': 7,
              'hamburger': 8, 'play': 9, 'plus': 10, 'search': 11, 'settings': 12, 'share': 13, 'sliders': 15,
              'square': 16, 'star': 17, 'text': 18, 'textButton': 19, 'toogle': 20, 'userImage': 21}

# General TFIDF Calculations

# Create all word set

def createAllWordset():
    wordSet = set()
    for item in listElement:
        for i in range(16):
            wordSet.add(item + "." + str(i))

    for item in listElement:
        for i in range(16):
            wordSet.add("square." + item + "." + str(i))
    return wordSet

# Compute word set

def computeIDF(docList):
    idfDict = {}
    N = len(docList)

    idfDict = dict.fromkeys(docList[0].keys(), 0)
    for doc in docList:
        for word, val in doc.items():
            if val > 0:
                idfDict[word] += 1

    for word, val in idfDict.items():
        if val == 0:
            idfDict[word] = 0
        else:
            idfDict[word] = math.log10(N / float(val))

    return idfDict


def computeTFIDF(tfBow, idfs):
    tfidf = {}
    for word, val in tfBow.items():
        tfidf[word] = val * idfs[word]
    return tfidf


def computeTF(wordDict, bow):
    tfDict = {}
    bowCount = len(bow)
    for word, count in wordDict.items():
        tfDict[word] = count / float(bowCount)
    return tfDict


def createWordSet(dictObj):
    wordSet = set()
    for key in dictObj:
        wordSet = wordSet.union(set(dictObj[key]))
    return wordSet


def createWordDict(dictObj, wordSet):
    wordDict = []
    for key in dictObj:
        print(key)
        curDict = dict.fromkeys(wordSet, 0)
        for word in dictObj[key]:
            curDict[word] += 1
        wordDict.append(curDict)

    return wordDict


def calCulateAllTF(wordDict, dictObj):
    tfBow = []
    count = 0
    for key in dictObj:
        tfCur = computeTF(wordDict[count], dictObj[key])
        count = count + 1
        tfBow.append(tfCur)

    return tfBow


def calculateAllIDF(wordDict):
    fullList = []
    for curObj in wordDict:
        fullList.extend(curObj)

    idfs = computeIDF(fullList)

    return idfs


# def keyMapperToElementAndPos(count):


def listToDict(dictTFIDF):
    dictObj = {}
    count = 0
    for key in dictTFIDF:
        splitKey = key.split('.')
        if (dictTFIDF[key] != 0):
            curDictObj = {}
            curDictObj[dictMapper[splitKey[0]]] = round(dictTFIDF[key], 5)
            dictObj[splitKey[1]] = curDictObj
        count = count + 1
    return dictObj


def calculateAllTFIDF(tfBow, idfs, dataset):
    tfidfBow = {}
    count = 0
    for key in dataset:
        curtfBow = tfBow[count]
        curtfidf = computeTFIDF(curtfBow, idfs)

        tfidfBow[key] = curtfidf
        count = count + 1

    return tfidfBow



# Read Content
def readContentData(dataset, fileName, fileCount):
    file = open(fileName)
    text = file.read()
    file.close()

    dictObj = literal_eval(text)

    allTexts = []

    for key in dictObj:
        allObjects = dictObj[key]
        for elmnt in allObjects:
            allTexts.append(elmnt + "." + key)

    dataset[fileCount] = allTexts
    return

# Parse all JSON File
def parserAllDirectory(folder):
    dataset = {}
    for file in os.listdir(folder):
        filePath = os.path.join(folder, file)
        fileCount = file.split('.')
        readContentData(dataset, filePath, fileCount[0])

    return dataset


def createWordSetAddition(dictObj):
    wordSet = set()
    for key in dictObj:
        wordSet = wordSet.union(set(dictObj[key]))

    return wordSet


if __name__ == '__main__':
    dataset = parserAllDirectory(content_folder)
    wordSet = createWordSetAddition(dataset)

    wordDict = createWordDict(dataset, wordSet)
    print(wordDict)

    idfs = computeIDF(wordDict)
    print(idfs)


# -*- coding: utf-8 -*-
"""
Created on Sun Nov  3 01:16:09 2019

@author: sxm6202xx
"""
from RectUtils.Rect import Rect
from RectUtils.RectObj import RectObj
from RectUtils import RectUtil


# if there is a text button. Only 1 child and it is squiggle
def isTextButton(rectObj):

    if (len(rectObj.mChildren)==1) and rectObj.mChildren[0].isText():
        return True
    else:
        return False

# Look through all rects to find if there is a text and update rects accordingly.
def searchForTextButton(rectPar):
    for rectObj in rectPar.mChildren:
        if isTextButton(rectObj):
            # print("Coming Here")
            rectObj.mChildren = []
#            print("Coming Here")
            rectObj.iconID= 23
        else:
            searchForTextButton(rectObj)


# Look through all rects to find if one rect resides inside other rect to find the hierarchy of all rects
def createHierachy(rects, width, height):
    
    rootObj= RectObj(Rect(0,0,width,height))
    rootObj.iconID = -1
    sortedRectObjs = sorted(rects, key=lambda x: x.rectArea)
    elementLength = len(sortedRectObjs)
    if(elementLength==1):
         rootObj.mChildren.append(sortedRectObjs[0])
         return rootObj
    for i in range(elementLength-1):
        item=sortedRectObjs[i]
        validElement = True
        isChild = False
        for j in range(i+1,elementLength):
            parItem = sortedRectObjs[j]
            if parItem != item:
                item, validElement, isChild = RectUtil.fixHierarchy(parItem,item,width,height)
                if isChild:
                    parItem.mChildren.append(item)
                    break
                if not validElement:
                    break
        if validElement and not isChild:            
            rootObj.mChildren.append(item)
    rootObj.mChildren.append(sortedRectObjs[elementLength-1])
    
    searchForTextButton(rootObj)
    return rootObj
                
# convert json returned by canvas to rects
def jsonToRect(jsonRects):
    rectObjs=[]
    for item in jsonRects:
#        print(item)
        rectObj = RectObj(Rect(int(item['x']),int(item['y']),int(item['width']),int(item['height'])),int(item['iconID']),int(item['elementId']))
        rectObjs.append(rectObj)
    return rectObjs

# Below functions to help tutorial find the text button

# return if there a textbutton
def isThereATextButton(rectPar):

    if (len(rectPar.mChildren) == 1) and rectPar.mChildren[0].isText():
        return True
    else:
        return False

    return False

# Create hierarchy of drawings in the tutorial drawings only and look for text button in the hierarchy
def searchForTextInHierarchy(rects, width, height):
    rootObj = RectObj(Rect(0, 0, width, height))
    rootObj.iconID = -1
    sortedRectObjs = sorted(rects, key=lambda x: x.rectArea)
    elementLength = len(sortedRectObjs)
    if (elementLength == 1):
        rootObj.mChildren.append(sortedRectObjs[0])
        return rootObj
    for i in range(elementLength - 1):
        item = sortedRectObjs[i]
        validElement = True
        isChild = False
        #        print(item.rectArea)
        for j in range(i + 1, elementLength):
            parItem = sortedRectObjs[j]
            if parItem != item:
                item, validElement, isChild = RectUtil.fixHierarchy(parItem, item, width, height)
                if isChild:
                    parItem.mChildren.append(item)
                    break
                if not validElement:
                    break
        if validElement and not isChild:
            rootObj.mChildren.append(item)
    rootObj.mChildren.append(sortedRectObjs[elementLength - 1])


    for curRect in rootObj.mChildren:
        if(isThereATextButton(curRect)):
            return True
    return False

# helper function to find textbutton in the drawing
def isATextButton(jsonRootObjs,width,height):
    print(jsonRootObjs)
    print(width)
    print(height)

    rawRects = jsonToRect(jsonRootObjs)
    if (len(rawRects) != 0):
        return searchForTextInHierarchy(rawRects, width, height)
    return False
        
def hierArchyToArrayInternal(rectObj, rectPar):
    for child in rectPar.mChildren:  
        rectObj.append(child)
        hierArchyToArrayInternal(rectObj, child)

# from hierarchy create the array         
def hierArchyToArray(rootObj):
    rectObj= []
    hierArchyToArrayInternal(rectObj, rootObj)
    return rectObj
        

#create hierarchy for finding text button
# then convert elements into array of element
def getRectObjs(jsonRootObjs):
    rawRects = jsonToRect(jsonRootObjs)
    rectObj= []
    if(len(rawRects)!=0):
        rootObj = createHierachy(rawRects, 500,600)
        hierArchyToArrayInternal(rectObj, rootObj)
        
    return rectObj

if __name__=="__main__":
    rectOb = [{'elementId': '0', 'height': '70', 'iconID': '15', 'width': '96', 'x': '25', 'y': '140'}, {'elementId': '1', 'height': '84', 'iconID': '17', 'width': '80', 'x': '357', 'y': '144'}, {'elementId': '2', 'height': '93', 'iconID': '19', 'width': '151', 'x': '134', 'y': '431'}, {'x': '160', 'y': '464', 'width': '97', 'height': '33', 'iconID': '20', 'elementId': '3'}]
    width =500
    heihgt= 800
    print(isATextButton(rectOb,width,heihgt))
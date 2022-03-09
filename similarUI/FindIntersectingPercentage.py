
from RectUtils.Rect import Rect


def findIntersectingArea(curRect, gridRects):
    dictAreas =[]
    for gRect in gridRects:
        (gRectbrX ,gRectbrY) = gRect.br()
        (curRectbrX ,curRectbrY) = curRect.br()
        xLeft =max(curRect.x ,gRect.x)
        yLeft =max(curRect.y ,gRect.y)
        xBR = min(gRectbrX ,curRectbrX)
        yBR = min(gRectbrY ,curRectbrY)
        if xLeft>=xBR or yLeft>=yBR:
            dictAreas.append(0)
        else:
            area = round((xBR -xLeft ) *(yBR -yLeft ) /curRect.area() ,3)
            dictAreas.append(area)

    return dictAreas


def findAllRects(width, height, widthZone, heightZone):

    dictRects =[]
    gridWidht = width /widthZone
    gridHeight = height /heightZone
    for i in range(heightZone):
        for j in range(widthZone):
            curRect = Rect( gridWidht *j ,gridHeight * i, gridWidht, gridHeight)
            dictRects.append(curRect)

    return dictRects


def findRectAreaPercent(x, y, width, height, canvasWidht, canvasHeight, widthZone, heightZone):
    # print(x,y,width, height, canvasWidht, canvasHeight, widthZone, heightZone)
    curRect = Rect(x, y, width, height)
    allRects = findAllRects(canvasWidht, canvasHeight, widthZone, heightZone)
    return findIntersectingArea(curRect, allRects)


if __name__ == "__main__":
    print("do nothing")    
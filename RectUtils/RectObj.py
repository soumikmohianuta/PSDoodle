import RectUtils.RectViewUtil as RectViewTypes
from RectUtils.Rect import Rect
import RectUtils.RectUtil as RectUtil

# Rect obj used for sketch 

class RectObj(Rect):
 
    def __init__(self,rect,iconID=0,elementId=0 ):
        super().__init__(rect.x,rect.y,rect.width,rect.height)
        self.mChildren = []
        self.mType = ""
        self.mColor =  int(0xFFFFFFFF)
        self.elementId=elementId
        self.iconID= iconID   
        self.rectArea = self.width*self.height
        
    def __hash__(self):
        return hash((self.tl(), self.br(), self.mType))

    def __eq__(self, other):
        
        if other is None:
            return self.area() == 0
        elif type(other) != type(self):
                return False
        else:
            return (self.x, self.y,self.width, self.height)== (other.x, other.y,other.width, other.height) and (self.mType == other.mType)

    def __ne__(self, other):
        return not(self.__eq__(other))

# check if rects contain by other rect

    def includes(self,bound):
        return RectUtil.contains(self.rect, bound)

    def default(self):
            return self.__dict__

# return overlap ratio
    def getOverlapRatio(self):
        overlapRatio = 0.0
        for rawView in self.mChildren :
            overlapRatio += rawView.area()
        
        return overlapRatio / self.rect.area()

# add  all child to rect    
    def addAllChild(self,child):
        self.mChildren.extend(child)
    
    def addChild(self,rawView):
        self.mChildren.append(rawView)
        
# convert to string
    def toString(self):
        textInfo = "Info: "
        if self.mType == self.VIEW_TYPE_TEXT:
            textInfo += "TEXT: " + self.mTextInfo.textWrapper.getText();
            
        elif self.mType ==  self.VIEW_TYPE_IMAGE:
            textInfo += "IMAGE: " + self.mImageInfo.drawableId + ", drawable_id: " + self.mImageInfo.drawableId;
			
        else:
            textInfo += "RECT: " + self.mTextWithLocations;
			
        return "Bound: " + self.bound() + ", Text Children: " + self.mTextChildren + ", " + self.textInfo


# check which type of element is this
    def isIconButton(self):
        nonImageClass = [0,4,6,10,15,18,19,20,21,22,23,34]
        if(self.iconID not in nonImageClass):
            return True
        else:
            return False
    
    def isContainer(self):
        if(self.getIconName() == 'square'):
            return True
        else:
            return False
    
    def isText(self):
        if(self.getIconName() == 'squiggle'):
            return True
        else:
            return False
    
    def isSlider(self):
        if(self.getIconName() == 'sliders'):
            return True
        else:
            return False     
    
    
    def isToogle(self):
        if(self.getIconName() == 'switch'):
            return True
        else:
            return False 
    
    def isCheckbox(self):
        if(self.getIconName() == 'checkbox'):
            return True
        else:
            return False 
        
    def isDropDown(self):
        if(self.getIconName() == 'dropDown'):
            return True
        else:
            return False
        
    def isRating(self):
        if(self.getIconName() == 'star'):
            return True
        else:
            return False       
    
    def isSearchBar(self):
        if(self.getIconName() == 'search'):
            return True
        else:
            return False    
    
    def isUserImage(self):
        if(self.getIconName() == 'avatar'):
            return True
        else:
            return False    
        
    def isButtonText(self):
        if(self.getIconName() == 'textButton'):
            return True
        else:
            return False  
        
        
    def isImage(self):
        if(self.getIconName() == 'imageIcon'):
            return True
        else:
            return False
        
    def getIconName(self):
        if self.iconID == 50:
            return 'root'
        class_names23 = ['avatar','back','camera','cancel','checkbox','generalIcon','dropDown','envelope','forward','house','imageIcon','leftarrow','menu','play','plus','search','settings','share','sliders','square','squiggle','star','switch','textButton','root']

        # class_names= ['back','camera','cancel','checkbox','dropDown','envelope','forward','hamburger','leftarrow','play','plus','search','settings',
               # 'share','sliders','square','star','text','toogle','userimage', 'textButton','root']
        return class_names23[self.iconID]
    
    
    def getViewTypeForAtomicElement(self):
        viewTypes = [RectViewTypes.VIEW_TYPE_ICON,RectViewTypes.VIEW_TYPE_ICON,RectViewTypes.VIEW_TYPE_ICON,RectViewTypes.VIEW_TYPE_ICON,RectViewTypes.VIEW_TYPE_ICON,
                     RectViewTypes.VIEW_TYPE_ICON,RectViewTypes.VIEW_TYPE_ICON,RectViewTypes.VIEW_TYPE_ICON,RectViewTypes.VIEW_TYPE_ICON,RectViewTypes.VIEW_TYPE_ICON,RectViewTypes.VIEW_TYPE_SEARCH,
                     RectViewTypes.VIEW_TYPE_ICON,RectViewTypes.VIEW_TYPE_ICON,RectViewTypes.VIEW_TYPE_ICON,RectViewTypes.VIEW_TYPE_CONTAINER, RectViewTypes.VIEW_TYPE_RATING]
        

        return viewTypes[self.iconID-1]
    
    def getElementID(self):
       return "element_" + str(self.elementId)

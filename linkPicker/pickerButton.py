from PySide2 import QtWidgets
from PySide2 import QtGui
from PySide2 import QtCore


class PickerButton(QtWidgets.QWidget):
    
    def __repr__(self):
        return f'< Buttton: globalPos: ({self.pos().x()}, {self.pos().y()}), localPos: ({self.localPos.x()}, {self.localPos.y()})>'
    
    def __init__(self, globalPos : QtCore.QPointF, 
                       parentPos : QtCore.QPointF, 
                       color     : QtGui.QColor = QtGui.QColor(100, 100, 100),
                       sceneScale: float = 1.0, 
                       scaleX    : int = 40,
                       scaleY    : int = 40,
                       parent    : QtWidgets.QWidget = None):  
        '''
        Args:
            globalPos (QPointF): Initial global position of the button when created.
            parentPos (QPointF): Virtual position relative to the picker, used to calculate the button's position relative to it.
            color (QColor)     : Button background color.
            sceneScale (float) : Scale factor of the scene.
            scaleX (int)       : Button width.
            scaleY (int)       : Button height.
            parent (QWidget)   : Parent widget.
        '''
        super().__init__(parent)

        self.scaleX     = scaleX
        self.scaleY     = scaleY
        self.color      = color
        self.sceneScale = sceneScale
        
        # -------------------------------------------------
        _width  = round(scaleX * sceneScale)
        _height = round(scaleY * sceneScale)
        
        buttonGlobalCenterPos = QtCore.QPointF(globalPos.toPoint().x() - _width / 2, globalPos.toPoint().y() - _height / 2) # get button center pos
        
        self.resize(_width, _height)
        self.move(buttonGlobalCenterPos.toPoint())
        
        '''
        Initialize the local position relative to the virtual axis based on the global position at the time of button creation.
        '''
        self.localPos = PickerButton.globalToLocal(buttonGlobalCenterPos, parentPos, sceneScale)
        
        self.setMinimumSize(8, 8)
        self.setMaximumSize(400, 400)
        
        self.selected = False
        
    
    def resetPos(self) -> None:
        self.resize(self.scaleX, self.scaleY)
        self.move(self.localPos.toPoint())
    
    
    @staticmethod
    def globalToLocal(globalPos: QtCore.QPointF, parentPos: QtCore.QPointF, sceneScale: float) -> QtCore.QPointF:  
        '''
        Convert global position to local position based on parent position and scene scale.
        '''
        return (globalPos - parentPos) * 1.0 / sceneScale 
    
    
    def updateLocalPos(self, globalPos: QtCore.QPointF, parentPos: QtCore.QPointF, sceneScale: float) -> None:
        self.localPos = PickerButton.globalToLocal(globalPos, parentPos, sceneScale)
        
         
    def updateColor(self, color: QtGui.QColor) -> None:
        if color == self.color:
            return
        self.color  = color
        self.update()
        
    # ----------------------------------------------------------------------------    
    def updateScaleX(self, scaleX: int, sceneScale: float) -> None:
        if scaleX == self.scaleX:
            return
        self.scaleX  = scaleX
        self.resize(round(scaleX * sceneScale), self.height()) 
        
        
    def updateScaleY(self, scaleY: int, sceneScale: float) -> None:
        if scaleY == self.scaleY:
            return
        self.scaleY  = scaleY
        self.resize(self.width(), round(scaleY * sceneScale))
    # ----------------------------------------------------------------------------       
        
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.fillRect(event.rect(), self.color)
        
if __name__ == '__main__':
    p = PickerButton(QtCore.QPointF(0, 0), QtCore.QPointF(0, 0))
    p.show()
    p.updateColor(QtGui.QColor(10, 200, 200))
    p.updateScaleY(150, 1)
        
        

        
from PySide2 import QtWidgets
from PySide2 import QtGui
from PySide2 import QtCore




class PickerButton(QtWidgets.QWidget):
    SELECTED_COLOR = QtGui.QColor(225, 225, 225)
    
    def __repr__(self):
        #return f'< Buttton: globalPos: ({self.pos().x()}, {self.pos().y()}), localPos: ({self.localPos.x()}, {self.localPos.y()})>'
        #return f'<Buttton: local: ({self.localPos.x()}, {self.localPos.y()})>'
        return f'<Buttton: {self.labelText}>'
        
    def __str__(self):
        return str('kangddan')
        
    def __init__(self, globalPos : QtCore.QPointF, 
                       parentPos : QtCore.QPointF, 
                       color     : QtGui.QColor = QtGui.QColor(100, 100, 100),
                       sceneScale: float = 1.0, 
                       scaleX    : int = 40,
                       scaleY    : int = 40,
                       textColor : QtGui.QColor = QtGui.QColor(10, 10, 10),
                       labelText : str = '',
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
        
        #self.setMinimumSize(8, 8)
        #self.setMaximumSize(400, 400)
        
        # -------------------------------------------------
        self.buttonColor = color
        self.selected    = False
        # -------------------------------------------------
        self.labelText = labelText
        self.textColor = textColor
        self._createWidgets()
        self._createLayouts()
        self.updateLabelText(self.labelText)
        self.updateLabelColor(self.textColor)
        self.setToolTip(str(self))
        
    # ---------------------------------------------------------------------------------
    def _createWidgets(self):
        self.textLabel = QtWidgets.QLabel('', self)
        self.textLabel.setAlignment(QtCore.Qt.AlignCenter)
        
    def _createLayouts(self):
        mainLayout = QtWidgets.QVBoxLayout(self)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.addWidget(self.textLabel)
        
    def updateLabelText(self, text: str):
        self.labelText = text
        self.textLabel.setFont(QtGui.QFont("Arial", 10))
        self.textLabel.setText(self.labelText)
        
    def updateLabelColor(self, color: QtGui.QColor):
        self.textColor = color
        palette = self.textLabel.palette()
        palette.setColor(QtGui.QPalette.WindowText, self.textColor) 
        self.textLabel.setPalette(palette)
    
    # ---------------------------------------------------------------------------------
    def setSelected(self, selected: bool) -> None:
        self.selected    = selected
        self.buttonColor = PickerButton.SELECTED_COLOR if self.selected else self.color
        self.update()
    
    
    def resetPos(self) -> None:
        self.resize(self.scaleX, self.scaleY)
        self.move(self.localPos.toPoint())
    
    
    @staticmethod
    def globalToLocal(globalPos: QtCore.QPointF, 
                      parentPos: QtCore.QPointF, 
                      sceneScale: float) -> QtCore.QPointF:  
        '''
        Convert global position to local position based on parent position and scene scale.
        '''
        return (globalPos - parentPos) * 1.0 / sceneScale 
    
    
    def updateLocalPos(self, globalPos: QtCore.QPointF, 
                             parentPos: QtCore.QPointF, 
                             sceneScale: float) -> None:
        self.localPos = PickerButton.globalToLocal(globalPos, parentPos, sceneScale)
        
         
    def updateColor(self, color: QtGui.QColor) -> None:
        if color == self.color:
            return
        self.color = self.buttonColor = color
        self.update()
        
    # ----------------------------------------------------------------------------    
    def updateScaleX(self, scaleX: int, sceneScale: float, parentPos: QtCore.QPointF) -> None:  
        if scaleX == self.scaleX:
            return
 
        self.scaleX = scaleX
        self._scale(sceneScale, parentPos)
        

    def updateScaleY(self, scaleY: int, sceneScale: float, parentPos: QtCore.QPointF) -> None:
        if scaleY == self.scaleY:
            return
 
        self.scaleY = scaleY
        self._scale(sceneScale, parentPos)
    
    
    def _scale(self, sceneScale: float, parentPos: QtCore.QPointF) -> None:
        newWidth  = round(self.scaleX * sceneScale)
        newHeight = round(self.scaleY * sceneScale)
        
        globalPos = (self.localPos * sceneScale) + parentPos
        
        oldCenter = globalPos + QtCore.QPointF(self.width() / 2, self.height() / 2)
        self.resize(newWidth, newHeight)
        newCenter = globalPos + QtCore.QPointF(self.width() / 2, self.height() / 2)
        
        newPosition = globalPos + (oldCenter - newCenter)
        self.move(newPosition.toPoint())
        self.updateLocalPos(newPosition, parentPos, sceneScale)
        

    # ----------------------------------------------------------------------------       
        
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.fillRect(event.rect(), self.buttonColor)
        
if __name__ == '__main__':
    p = PickerButton(QtCore.QPointF(0, 0), QtCore.QPointF(0, 0))
    p.show()
    p.updateColor(QtGui.QColor(10, 100, 200))
    #p.updateScaleY(150, 1)
    #p.setSelected(False)
    #p.updateColor(QtGui.QColor(88, 55, 55))

        

        
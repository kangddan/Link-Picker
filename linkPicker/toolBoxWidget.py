from PySide2 import QtWidgets
from PySide2 import QtCore
from PySide2 import QtGui

import importlib
from linkPicker import colorWidget, widgets
importlib.reload(colorWidget)

class ToolBoxWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._createWidgets()
        self._createLayouts()
        self.updateLayout = True

        
    def _createWidgets(self):
        self.colorLabel           = QtWidgets.QLabel('<span style="font-size: 15px; font-weight: 400;">Color</span>')
        self.buttonColorLabel     = colorWidget.ColorWidget(34, 24)
        self.widthLabel           = QtWidgets.QLabel('<span style="font-size: 15px; font-weight: 400;">Width</span>')
        self.widthNumberLineEdit  = widgets.NumberLineEdit('int', 40, 1, 8, 400)

        self.heightLabel          = QtWidgets.QLabel('<span style="font-size: 15px; font-weight: 400;">Height</span>')
        self.heightNumberLineEdit = widgets.NumberLineEdit('int', 40, 1, 8, 400)

        self.buttonLabel         = QtWidgets.QLabel('<span style="font-size: 15px; font-weight: 400;">Label</span>')
        self.labelTextColorLabel = colorWidget.ColorWidget(34, 24)
        self.labelLineEdit       = QtWidgets.QLineEdit()
        self.labelLineEdit.setPlaceholderText('name...')
        
        
    def _createLayouts(self):
        mainLayout = QtWidgets.QVBoxLayout(self)
        mainLayout.setContentsMargins(4, 0, 4, 0)
        mainLayout.setSpacing(4)
        
        self.toolBoxLayout1 = QtWidgets.QHBoxLayout()
        self.toolBoxLayout1.setContentsMargins(0, 0, 0, 0)
        
        self.toolBoxLayout2 = QtWidgets.QHBoxLayout()
        self.toolBoxLayout2.setContentsMargins(0, 0, 0, 0)
        
        self.toolBoxLayout1.addWidget(self.colorLabel)
        self.toolBoxLayout1.addWidget(self.buttonColorLabel)
        self.toolBoxLayout1.addWidget(self.widthLabel)
        self.toolBoxLayout1.addWidget(self.widthNumberLineEdit)
        self.toolBoxLayout1.addWidget(self.heightLabel)
        self.toolBoxLayout1.addWidget(self.heightNumberLineEdit)
        
        self.toolBoxLayout1.addWidget(self.buttonLabel)
        self.toolBoxLayout1.addWidget(self.labelTextColorLabel)
        self.toolBoxLayout1.addWidget(self.labelLineEdit)

        mainLayout.addLayout(self.toolBoxLayout1)
        mainLayout.addLayout(self.toolBoxLayout2)
        
        
    def _moveWidgets(self, fromLayout, toLayout, widgets):
        for widget in widgets:
            if fromLayout.indexOf(widget) != -1:
                fromLayout.removeWidget(widget) 
                toLayout.addWidget(widget) 
 
    def resizeEvent(self, event):
        width = self.width()
        if width < 450 and self.updateLayout:
            self.updateLayout = False
            self._moveWidgets(self.toolBoxLayout1, self.toolBoxLayout2, [self.buttonLabel, self.labelTextColorLabel, self.labelLineEdit])

        elif width > 450 and not self.updateLayout:
            self.updateLayout = True
            self._moveWidgets(self.toolBoxLayout2, self.toolBoxLayout1, [self.buttonLabel, self.labelTextColorLabel, self.labelLineEdit])

        super().resizeEvent(event)
        
        
    # -----------------------------
    def getButtonColor(self) -> QtGui.QColor:
        pass
    
    def getWidth(self) -> int:
        return self.widthNumberLineEdit.get()
        
    def getHeight(self) -> int:
        return self.heightNumberLineEdit.get()
        
    def getText(self) -> str:
        return self.labelLineEdit.text()
        
    def getTextColor(self) -> QtGui.QColor:
        pass
        
    # -----------------------------
    def setButtonColor(self, color: QtGui.QColor):
        pass
    
    def setWidth(self, width: int):
        self.widthNumberLineEdit.set(width)
        
    def setHeight(self, height: int):
        self.heightNumberLineEdit.set(height)
        
    def setText(self, text: str):
        self.labelLineEdit.setText(text)
        
    def setTextColor(self, color: QtGui.QColor):
        pass
        
if __name__ =='__main__':        

    t = ToolBoxWidget()
    t.show()      
    t.setWidth(85.36) 
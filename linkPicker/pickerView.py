from PySide2 import QtWidgets
from PySide2 import QtGui
from PySide2 import QtCore

import importlib
from linkPicker import qtUtils, pickerButton
importlib.reload(qtUtils)
importlib.reload(pickerButton)


class SelectionBox(QtWidgets.QRubberBand):
    def __init__(self, parent=None, shape=QtWidgets.QRubberBand.Line):
        super().__init__(shape, parent)
        
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setPen(QtGui.QPen(QtGui.QColor(150, 150, 150), 4, QtCore.Qt.SolidLine))
        painter.setBrush(QtGui.QColor(100, 100, 100, 50))
        painter.drawRect(self.rect())
        
        
class AxisWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.resize(100, 100)
        self.createWidgets()
        
    def createWidgets(self):
        self.axisLabel = QtWidgets.QLabel(self)
        self.axisLabel.setText('(0.000, 0.000)')
        self.axisLabel.move(10, 10)
        
    def reset(self):
        self.move(QtCore.QPoint(0, 0))
        self.resize(100, 100)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)  
        painter.setPen(QtGui.QPen(QtCore.Qt.red, self.width() / 20))
        painter.drawLine(0, 0, self.width(), 0)
        painter.setPen(QtGui.QPen(QtCore.Qt.green, self.height() / 20))
        painter.drawLine(0, 0, 0, self.height())
        painter.end()
  
        self.axisLabel.setText(f'({self.pos().x()}, {self.pos().y()})')
        

class PickerView(QtWidgets.QWidget):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True) 
        self.setObjectName('PickerView')
        self.setStyleSheet('#PickerView { background-color: #333333;}')
        self.setMouseTracking(True)
        
        self._createMenu()
        self._createWidgets()
        self._createConnections()
        
        # -------------------------------------
        self.sceneScale = 1.0
        self.origScale  = 1.0
        
        self.MoveView  = False
        self.scaleView = False

        self.clickedParentPos = QtCore.QPointF()
        self.buttonsParentPos = QtCore.QPointF()
        self.clickedPos       = QtCore.QPointF()

        self.buttonGlobalPos  = QtCore.QPointF() # set button global pos by menu
        # -------------------------------------
        '''
        This variable might cause confusion.
        It is only set to True when holding down the left mouse button to perform a box selection. 
        It takes effect when holding down Ctrl to deselect through the selectionBox,
        performing a second check on the buttons. 
        If a button is inside or intersects with the box, it will be deselected
        '''
        self.clearMoveTag     = False
        
        self.selected         = False
        self.startPos         = QtCore.QPoint() # selectionBox start pos
        self.endtPos          = QtCore.QPoint() # selectionBox end pos
        self.selectionBoxRect = QtCore.QRect()  # selectionBox Rect
        
        self.pickerButtons   = []
        self.selectedButtons = []
        self.shiftAddButtons = []
        # --------------------------------------
        self.buttonsMoveTag = False
        self.buttonsTranslateOffset = {}
        
    def _createMenu(self):
        self.pickerViewMenu       = QtWidgets.QMenu(self)
        self.addOneButtonAction   = QtWidgets.QAction(QtGui.QIcon(':addClip.png'), 'Add One Button', self.pickerViewMenu)
        self.addManyButtonsAction = QtWidgets.QAction('Add Many Buttons',  self.pickerViewMenu)
        self.updateButtonAction   = QtWidgets.QAction(QtGui.QIcon(':refresh.png'), 'Update Button', self.pickerViewMenu)
        self.deleteButtonAction   = QtWidgets.QAction(QtGui.QIcon(':delete.png'), 'Delete Button',  self.pickerViewMenu)
        
        self.resetViewAction = QtWidgets.QAction(QtGui.QIcon(':rvRealSize.png'), 'Reset View', self.pickerViewMenu)
        self.frameViewAction = QtWidgets.QAction(QtGui.QIcon(':visible.png'), 'Frame View', self.pickerViewMenu)
        
        self.pickerViewMenu.addAction(self.addOneButtonAction)
        self.pickerViewMenu.addAction(self.addManyButtonsAction)
        self.pickerViewMenu.addAction(self.updateButtonAction)
        self.pickerViewMenu.addAction(self.deleteButtonAction)
        self.pickerViewMenu.addSeparator()
        self.pickerViewMenu.addAction(self.resetViewAction)
        self.pickerViewMenu.addAction(self.frameViewAction)
        
        
    def _createWidgets(self):
        self.parentAxis = AxisWidget(self)
        self.parentAxis.show()
        
        # --------------------------------
        self.selectionBox = SelectionBox(parent=self)
        
    def _createConnections(self):
        self.resetViewAction.triggered.connect(self._resetView)
        self.addOneButtonAction.triggered.connect(self._createButton)
        
    # ------------------------------------------------------------------
    def _getPickerButtons(self) -> list[pickerButton.PickerButton]:
        return [button for button in self.findChildren(pickerButton.PickerButton)]   
        
    def _clearSelectedButtons(self):
        for button in self.selectedButtons:
            button.setSelected(False)
        self.selectedButtons.clear()  
        
    
    # ------------------------------------------------------------------
    
    def _getButtonColor(self) -> QtGui.QColor:
        pass
    
    def _createButton(self):
        buttonColor   = self._getButtonColor() or QtGui.QColor(100, 100, 100)
        buttonScaleX  = 40
        buttonscaleY  = 40
        button = pickerButton.PickerButton(self.buttonGlobalPos, 
                                           self.buttonsParentPos,
                                           buttonColor,
                                           self.sceneScale,
                                           buttonScaleX, 
                                           buttonscaleY,
                                           self)
        self._clearSelectedButtons()
        self.selectedButtons = [button]
        button.setSelected(True)
        button.show()
        
        
    def _resetView(self):
        self.sceneScale = 1.0
        self.origScale  = 1.0
        self.clickedParentPos = QtCore.QPointF()
        self.buttonsParentPos = QtCore.QPointF()
        
        self.parentAxis.move(self.buttonsParentPos.toPoint())
        self.parentAxis.resize(100, 100) 
        
        for but in self._getPickerButtons():
            but.resetPos()
    
    
    @staticmethod        
    def localToGlobal(localPos: QtCore.QPointF, parentPos: QtCore.QPointF, sceneScale: float) -> QtCore.QPointF: 
        return (localPos * sceneScale) + parentPos
        
        
    # ------------------------------------------------------------------------------------------------------------------------------------       
    def mousePressEvent(self, event): 
        # move view
        if event.buttons() == QtCore.Qt.MouseButton.MiddleButton:
            self.setCursor(QtCore.Qt.SizeAllCursor)
            self.MoveView = True
            self.clickedPos, self.clickedParentPos = event.localPos(), self.buttonsParentPos
            self.pickerButtons = self._getPickerButtons()
            return  
        
        # scale view
        if event.modifiers() == QtCore.Qt.AltModifier and event.buttons() == QtCore.Qt.MouseButton.RightButton:
            self.setCursor(QtCore.Qt.SizeHorCursor)
            self.scaleView = True
            self.clickedPos, self.clickedParentPos = event.localPos(), self.buttonsParentPos
            self.pickerButtons = self._getPickerButtons()
            return
                
        # show menu
        if event.buttons() == QtCore.Qt.MouseButton.RightButton and event.modifiers() == QtCore.Qt.NoModifier:
            self.buttonGlobalPos = event.localPos() # update button global pos
            self.pickerViewMenu.exec_(event.globalPos())
            return
            
        # selected buttons and updare Selection Box
        if event.buttons() == QtCore.Qt.MouseButton.LeftButton and event.modifiers() != QtCore.Qt.ControlModifier:
            self.selected = True
            self.startPos = event.pos()
            self.selectionBox.setGeometry(QtCore.QRect(self.startPos, QtCore.QSize())); self.selectionBox.show() # show selectionBox

            self.pickerButtons = self._getPickerButtons()
            
            self.clickedButton = None
            for button in self.pickerButtons:
                if button.geometry().contains(self.startPos):
                    self.clickedButton = button
                    break
                    
            if self.clickedButton is not None:
                if event.modifiers() == QtCore.Qt.ShiftModifier:
                    if self.clickedButton not in self.selectedButtons:
                        self.selectedButtons.append(self.clickedButton)
                        self.clickedButton.setSelected(True)
                        
                elif event.modifiers() != QtCore.Qt.AltModifier:
                    self._clearSelectedButtons()
                    self.selectedButtons = [self.clickedButton]
                    self.clickedButton.setSelected(True)
                        
            else: 
                if not (event.modifiers() & (QtCore.Qt.ShiftModifier | QtCore.Qt.AltModifier)):
                    self._clearSelectedButtons()
            return  
            
        # move buttons
        if event.modifiers() == QtCore.Qt.ControlModifier and event.buttons() == QtCore.Qt.MouseButton.LeftButton:
            self.buttonsMoveTag = True
            localPos = event.pos()

            oneButton = next((but for but in self._getPickerButtons() if but.geometry().contains(localPos)), None)
            
            if oneButton is not None and oneButton not in self.selectedButtons:
                self._clearSelectedButtons()
                self.selectedButtons = [oneButton]
                oneButton.setSelected(True)
                self.buttonsTranslateOffset[oneButton] = oneButton.pos() - localPos
                
            elif self.selectedButtons and any(but.geometry().contains(localPos) for but in self.selectedButtons):
                for button in self.selectedButtons:
                    self.buttonsTranslateOffset[button] = button.pos() - localPos
            else:
                self._clearSelectedButtons()
            return 
        
        super().mousePressEvent(event)
        
        
    def mouseMoveEvent(self, event):
        self.update()
        # move view
        if self.MoveView:
            self.buttonsParentPos = self.clickedParentPos + (event.localPos() - self.clickedPos)
            self.parentAxis.move(self.buttonsParentPos.toPoint())
            
            # move buttons
            for but in self.pickerButtons:
                globalPos = PickerView.localToGlobal(but.localPos, self.buttonsParentPos, self.sceneScale)
                but.move(globalPos.toPoint())
            return 
            
        # scale view
        if self.scaleView:
            offset = event.localPos() - self.clickedPos
            self.sceneScale = max(0.20, min(self.origScale + (offset.x() + offset.y()) / 200.0, 10.00)) # update scale
            
            _scale = self.sceneScale / self.origScale
            cx, cy = self.clickedPos.x(), self.clickedPos.y()
            self.buttonsParentPos = QtCore.QPointF(cx + _scale * (self.clickedParentPos.x() - cx), 
                                                   cy + _scale * (self.clickedParentPos.y() - cy))
                                                   
            self.parentAxis.move(self.buttonsParentPos.toPoint())
            self.parentAxis.resize(round(100 * self.sceneScale), round(100 * self.sceneScale)) 
            
            # move buttons
            for but in self.pickerButtons:
                globalPos = PickerView.localToGlobal(but.localPos, self.buttonsParentPos, self.sceneScale)
                but.move(globalPos.toPoint())
                but.resize(round(but.scaleX * self.sceneScale), round(but.scaleY * self.sceneScale))
            return
            
        # selected buttons and updare Selection Box    
        if self.selected:
            self.endPos  = event.pos()
            self.clearMoveTag = True # clear tag
            self.selectionBox.setGeometry(QtCore.QRect(self.startPos, self.endPos).normalized()) # update selectionBox
            self.selectionBoxRect = QtCore.QRect(self.startPos, self.endPos)
            
            if not (event.modifiers() & QtCore.Qt.AltModifier):
                for button in self.pickerButtons:
                    inSelection = self.selectionBoxRect.intersects(button.geometry())
                    
                    if event.modifiers() == QtCore.Qt.ShiftModifier:
                        if inSelection and button not in self.selectedButtons:
                            button.setSelected(True)
                            self.selectedButtons.append(button)
                            self.shiftAddButtons.append(button)
                        elif not inSelection and button in self.shiftAddButtons:
                            button.setSelected(False)
                            self.selectedButtons.remove(button)
                            self.shiftAddButtons.remove(button)
                    elif inSelection:
                        if button not in self.selectedButtons:
                            button.setSelected(True)
                            self.selectedButtons.append(button)
                    else:
                        button.setSelected(False)
                        if button in self.selectedButtons:
                            self.selectedButtons.remove(button)
            return
            
        # move buttons
        if self.buttonsMoveTag:
            for button, offset in self.buttonsTranslateOffset.items():
                globalPos = event.pos() + offset
                button.move(globalPos)
                button.updateLocalPos(QtCore.QPointF(globalPos), self.buttonsParentPos, self.sceneScale)
            return 
        
        super().mouseMoveEvent(event)
            

    def mouseReleaseEvent(self, event):
        
        # move view
        if self.MoveView:
            self.MoveView = False
            self.pickerButtons.clear()
            
        # scale view    
        if self.scaleView:
            self.scaleView = False
            self.origScale = self.sceneScale
            self.pickerButtons.clear()
            
        # selected buttons and updare Selection Box    
        if self.selected:
            self.selected = False
            self.shiftAddButtons = []
            self.selectionBox.hide() # hide selectionBox
            
            # clear selected button
            if self.clickedButton is not None:
                if event.modifiers() == QtCore.Qt.AltModifier and event.button() != QtCore.Qt.MouseButton.RightButton:
                    self.clickedButton.setSelected(False)
                    if self.clickedButton in self.selectedButtons:
                        self.selectedButtons.remove(self.clickedButton)
                      
            if self.clearMoveTag:
                '''
                Perform a second check. If the button is inside or intersects with the box, it will be deselected!!
                '''  
                if event.modifiers() == QtCore.Qt.AltModifier:
                    for button in self.pickerButtons:
                        if self.selectionBoxRect.intersects(button.geometry()) and button in self.selectedButtons:
                            button.setSelected(False)
                            self.selectedButtons.remove(button)
                self.clearMoveTag = False
                
        # move buttons        
        if self.buttonsMoveTag:
            self.buttonsTranslateOffset.clear()
            self.buttonsMoveTag = False

        self.setCursor(QtCore.Qt.ArrowCursor)
        super().mouseReleaseEvent(event)
        print(self.selectedButtons)


if __name__ =='__main__':
    UI = QtWidgets.QDialog(parent=qtUtils.getMayaMainWindow())
    UI.setWindowFlags(QtCore.Qt.WindowType.Window)
    UI.resize(500, 650)
    layout = QtWidgets.QVBoxLayout(UI)
    layout.addWidget(PickerView())
    UI.show()
    
    

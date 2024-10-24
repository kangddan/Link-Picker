from functools import partial
from PySide2 import QtWidgets
from PySide2 import QtGui
from PySide2 import QtCore
from maya import cmds

import importlib
from linkPicker import qtUtils, pickerButton, config, widgets
importlib.reload(qtUtils)
importlib.reload(pickerButton)
importlib.reload(config)
importlib.reload(widgets)
        

class PickerView(QtWidgets.QWidget):

    buttonSelected     = QtCore.Signal(list)
    requestToolboxData = QtCore.Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True) 
        self.setObjectName('PickerView')
        self.setStyleSheet('#PickerView { background-color: #333333;}')
        self.setMouseTracking(True)
        
        self._createMenu()
        self._createActions()
        self._createWidgets()
        self._createConnections()
        
        # -------------------------------------
        self.sceneScale = 1.0
        self.origScale  = 1.0
        
        self.frameMoveTag = True
        self.MoveView     = False
        self.scaleView    = False

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
        # --------------------------------------
        # init button attr
        self.buttonAttributes = [QtGui.QColor(QtCore.Qt.yellow), 40, 40, QtGui.QColor(QtCore.Qt.black), '']
        # create buttons
        self.isAddingButtons = False
        self.trackedButtons  = []
        

    def _createMenu(self):
        self.pickerViewMenu = QtWidgets.QMenu(self)


    def _createActions(self):
        self.addSingleButtonAction    = QtWidgets.QAction(QtGui.QIcon(':addClip.png'), 'Add Single Button', self.pickerViewMenu)
        self.addMultipleButtonsAction = QtWidgets.QAction('Add Multiple Buttons',  self.pickerViewMenu)
        self.updateButtonAction       = QtWidgets.QAction(QtGui.QIcon(':refresh.png'), 'Update Button', self.pickerViewMenu)
        self.deleteButtonAction       = QtWidgets.QAction(QtGui.QIcon(':delete.png'), 'Delete Selected Button(s)',  self.pickerViewMenu)
        
        self.addCommandButtonAction  = QtWidgets.QAction(QtGui.QIcon(config.pythonLogo), 'Add Command Button',  self.pickerViewMenu)
        self.alignHorizontallyAction = QtWidgets.QAction(QtGui.QIcon(config.alignHorizontallyIcon), 'Align Buttons Horizontally', self.pickerViewMenu)
        self.alignVerticallyAction   = QtWidgets.QAction(QtGui.QIcon(config.alignVerticallyIcon), 'Align Buttons Vertically',  self.pickerViewMenu)
        self.distributeButtonsAction = QtWidgets.QAction('Distribute Buttons Evenly', self.pickerViewMenu)
        
        self.mirrorAction = QtWidgets.QAction(QtGui.QIcon(':teLoopTool.png'), 'Mirror', self.pickerViewMenu)
        self.reverseAction = QtWidgets.QAction(QtGui.QIcon(':reverseOrder.png'), 'Reverse', self.pickerViewMenu)
        
        self.frameDefaultAction   = QtWidgets.QAction(QtGui.QIcon(':home.png'), 'Frame Default', self.pickerViewMenu)
        self.frameSelectionAction = QtWidgets.QAction(QtGui.QIcon(':visible.png'), 'Frame Selection', self.pickerViewMenu, shortcut='F')
        
        
        self.raiseButtonAction  = QtWidgets.QAction(QtGui.QIcon(':nodeGrapherArrowUp.png'), 'Bring to Front', self.pickerViewMenu)
        self.lowerButtonAction = QtWidgets.QAction(QtGui.QIcon(':nodeGrapherArrowDown.png'), 'Send to Back', self.pickerViewMenu)
        
        self.moveForwardAction = QtWidgets.QAction(QtGui.QIcon(':moveUVUp.png'), 'Move Forward', self.pickerViewMenu, shortcut='Up')
        self.moveBackwardAction = QtWidgets.QAction(QtGui.QIcon(':moveUVDown.png'), 'Move Backward', self.pickerViewMenu, shortcut='Down')
        
        # ----------------------------------------------------
        self.pickerViewMenu.addAction(self.addSingleButtonAction)
        self.pickerViewMenu.addAction(self.addMultipleButtonsAction)
        self.pickerViewMenu.addAction(self.updateButtonAction)
        self.pickerViewMenu.addAction(self.deleteButtonAction)
        
        self.pickerViewMenu.addSeparator()
        self.pickerViewMenu.addAction(self.addCommandButtonAction)
        
        self.pickerViewMenu.addSeparator()
        self.pickerViewMenu.addAction(self.alignHorizontallyAction)
        self.pickerViewMenu.addAction(self.alignVerticallyAction)
        self.pickerViewMenu.addAction(self.distributeButtonsAction)
        
        self.pickerViewMenu.addSeparator()
        self.pickerViewMenu.addAction(self.mirrorAction)
        self.pickerViewMenu.addAction(self.reverseAction)
        
        self.pickerViewMenu.addSeparator()
        self.zOrderMenu = self.pickerViewMenu.addMenu(QtGui.QIcon(':out_displayLayer.png'), 'Z-Order')
        self.zOrderMenu.setTearOffEnabled(True)
        self.zOrderMenu.addAction(self.raiseButtonAction)
        self.zOrderMenu.addAction(self.moveForwardAction)
        self.zOrderMenu.addAction(self.moveBackwardAction)
        self.zOrderMenu.addAction(self.lowerButtonAction)
        
        self.pickerViewMenu.addSeparator()
        self.pickerViewMenu.addAction(self.frameDefaultAction)
        self.pickerViewMenu.addAction(self.frameSelectionAction)
        
    
    def keyPressEvent(self, event): 
        if event.key() == QtCore.Qt.Key_F: 
            self._frameSelection()
        elif event.key() == QtCore.Qt.Key_Up: 
            self._moveSelectedButtonsUp()
        elif event.key() == QtCore.Qt.Key_Down: 
            self._moveSelectedButtonsDown()
            
            
    def _updatePickerMenuActions(self):
        sel = cmds.ls(sl=True, fl=True)
        hasSelBut = True if self.selectedButtons else False
        
        self.addSingleButtonAction.setEnabled(True if sel else False)
        self.addMultipleButtonsAction.setEnabled(True if len(sel) > 1 else False)
        self.deleteButtonAction.setEnabled(hasSelBut)
        # add sel node name
        self.addSingleButtonAction.setData(sel)
        self.addMultipleButtonsAction.setData(sel)
        
        # -------------------------------------------------------------------
        self.alignHorizontallyAction.setEnabled(True if len(self.selectedButtons) > 1 else False)
        self.alignVerticallyAction.setEnabled(True if len(self.selectedButtons) > 1 else False)
        self.distributeButtonsAction.setEnabled(True if len(self.selectedButtons) > 2 else False)
        # -------------------------------------------------------------------
        self.raiseButtonAction.setEnabled(hasSelBut)
        self.lowerButtonAction.setEnabled(hasSelBut)
        self.moveForwardAction.setEnabled(hasSelBut)
        self.moveBackwardAction.setEnabled(hasSelBut)
        
        
    def _createWidgets(self):
        self.parentAxis = widgets.AxisWidget(self)
        self.parentAxis.show()
        # --------------------------------
        self.selectionBox = widgets.SelectionBox(parent=self)
        
        
    def _createConnections(self):
        self.pickerViewMenu.aboutToShow.connect(self._updatePickerMenuActions)
        
        self.addSingleButtonAction.triggered.connect(self.createButton)
        self.addMultipleButtonsAction.triggered.connect(partial(self.updateAddingButtons, True))
        self.deleteButtonAction.triggered.connect(self._deleteSelectedButton)
        
        self.distributeButtonsAction.triggered.connect(self._distributeButtonsEvenly)
        
        self.alignHorizontallyAction.triggered.connect(self.alignButtonsHorizontally)
        self.alignVerticallyAction.triggered.connect(self.alignButtonsVertically)
        

        self.raiseButtonAction.triggered.connect(self._raiseSelectedButtons)
        self.lowerButtonAction.triggered.connect(self._lowerSelectedButtons)
        self.moveForwardAction.triggered.connect(self._moveSelectedButtonsUp)
        self.moveBackwardAction.triggered.connect(self._moveSelectedButtonsDown)
        
        self.frameDefaultAction.triggered.connect(self._frameDefault)
        self.frameSelectionAction.triggered.connect(self._frameSelection)
         
    # ------------------------------------------------------------------
    def _deleteSelectedButton(self):
        if not self.selectedButtons:
            return
        
        for button in list(self.selectedButtons):
            button.deleteLater()
        self.selectedButtons.clear()
        
    def _raiseSelectedButtons(self):
        for but in self.selectedButtons:
            but.raise_()
        
        
    def _lowerSelectedButtons(self):
        for but in self.selectedButtons:
            but.lower()
            
    
    def _moveSelectedButtonsUp(self):
        buttons = self._getPickerButtons()
        if len(buttons) <= 1 or not self.selectedButtons:
            return
        for but in reversed(self.selectedButtons):
            index = buttons.index(but) 
            if index == len(buttons) - 1: continue 
            buttons[index], buttons[index + 1] = buttons[index + 1], buttons[index]
        for but in buttons:
            but.raise_()
    
    
    def _moveSelectedButtonsDown(self):
        buttons = self._getPickerButtons()
        if len(buttons) <= 1 or not self.selectedButtons:
            return
        for but in self.selectedButtons:
            index = buttons.index(but)
            if index == 0: continue
            buttons[index], buttons[index - 1] = buttons[index - 1], buttons[index]
        for but in buttons:
            but.raise_()
            
    # ------------------------------------------------------------------
    def _getPickerButtons(self) -> list[pickerButton.PickerButton]:
        pickerButtons = self.findChildren(pickerButton.PickerButton)
        return pickerButtons 
        
        
    def _clearSelectedButtons(self):
        for button in self.selectedButtons:
            button.setSelected(False)
        self.selectedButtons.clear()  


    # ------------------------------------------------------------------
    def updateButtonsColor(self, color: QtGui.QColor):
        for but in self.selectedButtons:
            but.updateColor(color)
            
    def updateButtonsTextColor(self, color: QtGui.QColor):
        for but in self.selectedButtons:
            but.updateLabelColor(color)
            
    def updateButtonsText(self, text: str):
        for but in self.selectedButtons:
            but.updateLabelText(text)
            
    def updateButtonsScaleX(self, value: int):
        #print(f'scaleX -> {value}')
        for but in self.selectedButtons:
            but.updateScaleX(value, self.sceneScale, self.buttonsParentPos)
        
    def updateButtonsScaleY(self, value: int):
        #print(f'scaleY -> {value}')
        for but in self.selectedButtons:
            but.updateScaleY(value, self.sceneScale, self.buttonsParentPos)
            
    # get toolBoxWidget data
    def updateButtonAttributes(self, data: list) -> list:
        self.buttonAttributes = data


    def _createButton(self, node: str | list):
        self.requestToolboxData.emit()
        buttonColor, buttonScaleX, buttonscaleY, labelTextColor, labelText = self.buttonAttributes
        
        button = pickerButton.PickerButton(globalPos  = self.buttonGlobalPos, 
                                           parentPos  = self.buttonsParentPos,
                                           color      = buttonColor,
                                           sceneScale = self.sceneScale,
                                           scaleX     = buttonScaleX, 
                                           scaleY     = buttonscaleY,
                                           textColor  = labelTextColor,
                                           labelText  = labelText,
                                           parent     = self)
        button.show()
        return button
        
        
    def createButton(self):
        nodes = self.addSingleButtonAction.data()
  
        button = self._createButton(nodes)
        self._clearSelectedButtons()
        self.selectedButtons = [button]
        button.setSelected(True)
        
        
    # ---------------------------------------------
    def updateAddingButtons(self, state=True):
        if state:
            self.setCursor(QtGui.QCursor(':leftArrowPlus.png'))
        self.isAddingButtons = state
        
        
    def createButtons(self):
        nodes = self.addMultipleButtonsAction.data()
        self.trackedButtons = [self._createButton(node) for node in nodes]
            
            
    def _updateButtonPositions(self, startPos, endPos):
        count = len(self.trackedButtons)
        for i, button in enumerate(self.trackedButtons):
            t = i / (count - 1) if count > 1 else 0  
            x = (1 - t) * startPos.x() + t * endPos.x()
            y = (1 - t) * startPos.y() + t * endPos.y()

            globalPos = QtCore.QPointF(x - (button.scaleX / 2) * self.sceneScale, 
                                       y - (button.scaleY / 2) * self.sceneScale)
            button.move(globalPos.toPoint())
            button.updateLocalPos(globalPos, self.buttonsParentPos, self.sceneScale)    
            
    # -----------------------------------------------------------------------------------------------        
    def _distributeButtonsEvenly(self):
        startX = self.selectedButtons[0].pos().x() + self.selectedButtons[0].width() / 2
        startY = self.selectedButtons[0].pos().y() + self.selectedButtons[0].height() / 2
        
        endX = self.selectedButtons[-1].pos().x() + self.selectedButtons[-1].width() / 2
        endY = self.selectedButtons[-1].pos().y() + self.selectedButtons[-1].height() / 2
                                                      
        count = len(self.selectedButtons)
        for i, button in enumerate(self.selectedButtons[1:-1], start=1):
            t = i / (count - 1) if count > 1 else 0 
            x = (1 - t) * startX + t * endX
            y = (1 - t) * startY + t * endY

            globalPos = QtCore.QPointF(x - button.width() / 2,  y - button.height() / 2)
            button.move(globalPos.toPoint())
            button.updateLocalPos(globalPos, self.buttonsParentPos, self.sceneScale)
            
    
    def alignButtonsHorizontally(self):
        PickerView.alignButtons(self.selectedButtons, self.buttonsParentPos, self.sceneScale, 'horizontal')


    def alignButtonsVertically(self):
        PickerView.alignButtons(self.selectedButtons, self.buttonsParentPos, self.sceneScale, 'vertical')

    # ------------------------------------------------------------------    
        
    def _frameDefault(self):
        self.sceneScale = 1.0
        self.origScale  = 1.0
        self.clickedParentPos = QtCore.QPointF()
        self.buttonsParentPos = QtCore.QPointF()
        
        self.parentAxis.move(self.buttonsParentPos.toPoint())
        self.parentAxis.resize(100, 100) 
        
        for but in self._getPickerButtons():
            but.resetPos()
        #print(f'origScale -> {self.origScale}', f'sceneScale -> {self.sceneScale}')
    
    
    @staticmethod        
    def localToGlobal(localPos: QtCore.QPointF, 
                      parentPos: QtCore.QPointF, 
                      sceneScale: float) -> QtCore.QPointF: 
        return (localPos * sceneScale) + parentPos
        
        
    # ------------------------------------------------------------------------------------------------------------------------------------       
    def mousePressEvent(self, event): 
        # create buttons
        if self.isAddingButtons:
            if event.buttons() == QtCore.Qt.MouseButton.LeftButton:
                self.buttonGlobalPos = event.localPos() # update button global pos
                self.createButtons()
                self._clearSelectedButtons()
            else:
                self.updateAddingButtons(False)
                self.trackedButtons.clear()
                self.setCursor(QtCore.Qt.ArrowCursor)
            
            return
        
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
            
        # selected buttons and update Selection Box
        if event.buttons() == QtCore.Qt.MouseButton.LeftButton and event.modifiers() != QtCore.Qt.ControlModifier:
            self.selected = True
            self.startPos = event.pos()
            self.selectionBox.setGeometry(QtCore.QRect(self.startPos, QtCore.QSize())); self.selectionBox.show() # show selectionBox

            self.pickerButtons = self._getPickerButtons()
            
            self.clickedButton = None
            for button in self.pickerButtons:
                if button.geometry().contains(self.startPos):
                    self.clickedButton = button
                    '''
                    Do not use 'break' to ensure the loop checks all buttons.
                    This allows selecting the topmost button when multiple buttons overlap.
                    #break
                    '''              
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
            localPos = event.localPos()
            
            '''
            Get the last button that contains the mouse position.
            This ensures that when multiple buttons overlap, the topmost button is selected
            instead of always selecting the bottommost button
            # oneButton = next((but for but in self._getPickerButtons() if but.geometry().contains(localPos.toPoint())), None)
            ''' 
            _oneButton = [but for but in self._getPickerButtons() if but.geometry().contains(localPos.toPoint())]
            oneButton  = _oneButton[-1] if _oneButton else None
                
            if oneButton is not None and oneButton not in self.selectedButtons:
                self._clearSelectedButtons()
                self.selectedButtons = [oneButton]
                oneButton.setSelected(True)
                '''
                Convert from the button's local position to world position to avoid errors caused by floating-point precision
                '''
                globalPos = PickerView.localToGlobal(oneButton.localPos, self.buttonsParentPos, self.sceneScale)
                self.buttonsTranslateOffset[oneButton] = globalPos - localPos
                
            elif self.selectedButtons and any(but.geometry().contains(localPos.toPoint()) for but in self.selectedButtons):
                for button in self.selectedButtons:
                    '''
                    Convert from the button's local position to world position to avoid errors caused by floating-point precision
                    '''
                    globalPos = PickerView.localToGlobal(button.localPos, self.buttonsParentPos, self.sceneScale)
                    self.buttonsTranslateOffset[button] = globalPos - localPos
            else:
                self._clearSelectedButtons()
            return 
        
        super().mousePressEvent(event)
        
        
    def mouseMoveEvent(self, event):
        self.update()
        #self.frameMoveTag = True
        # create buttons
        if self.isAddingButtons and self.trackedButtons:
            self._updateButtonPositions(self.buttonGlobalPos, event.localPos())
            return
            
        # move view
        if self.MoveView:
            self.frameMoveTag = True
            self.buttonsParentPos = self.clickedParentPos + (event.localPos() - self.clickedPos)
            self.parentAxis.move(self.buttonsParentPos.toPoint())
            
            # move buttons
            for but in self.pickerButtons:
                globalPos = PickerView.localToGlobal(but.localPos, self.buttonsParentPos, self.sceneScale)
                but.move(globalPos.toPoint())
            return 
            
        # scale view
        if self.scaleView:
            self.frameMoveTag = True
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
            
        # selected buttons and update Selection Box    
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
                        '''
                        If the mouse click position is on a button
                        check the Z-order of the clicked button and all selected buttons within the selection box to prevent selection from passing through
                        '''
                        if self.clickedButton is not None and self.clickedButton.geometry().contains(self.selectionBoxRect) and (
                            self.pickerButtons.index(self.clickedButton) > self.pickerButtons.index(button)):
    
                            self._clearSelectedButtons()
                            self.clickedButton.setSelected(True)
                            self.selectedButtons.append(self.clickedButton)      
                            
                        elif button not in self.selectedButtons:
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
                globalPos = event.localPos() + offset
                button.move(globalPos.toPoint())
                button.updateLocalPos(globalPos, self.buttonsParentPos, self.sceneScale)
            return 
        
        super().mouseMoveEvent(event)
            

    def mouseReleaseEvent(self, event):
        # create buttons
        if self.isAddingButtons:
            self.updateAddingButtons(False)
            self.selectedButtons.extend(self.trackedButtons)
            self.trackedButtons.clear()
            for but in self.selectedButtons:
                but.setSelected(True)
   
        # move view
        if self.MoveView:
            self.MoveView = False
            self.pickerButtons.clear()
            
        # scale view    
        if self.scaleView:
            self.scaleView = False
            self.origScale = self.sceneScale
            self.pickerButtons.clear()
            
        # selected buttons and update Selection Box    
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
        
        # ----------------------------------
        if self.selectedButtons:
            '''
            Get the last button from the list, emit a signal to the ToolBoxWidget
            '''
            endBut = self.selectedButtons[-1]
            butInfo = [endBut.color, endBut.scaleX, endBut.scaleY, endBut.textColor, endBut.labelText]
            self.buttonSelected.emit(butInfo)
            print(self.selectedButtons)
            
        super().mouseReleaseEvent(event)
        
        #print(f'origScale -> {self.origScale}', f'sceneScale -> {self.sceneScale}')
        
    def resizeEvent(self, event):
        if not self.frameMoveTag:
            self.frameMoveTag = True
        super().resizeEvent(event)
 
 
    def wheelEvent(self, event):  
        value = self.sceneScale * (0.2 if (event.angleDelta().x() if event.modifiers() & QtCore.Qt.AltModifier else event.angleDelta().y()) > 0 else -0.2)

        self.frameMoveTag = True
        self.sceneScale = max(0.20, min(self.origScale + value, 10.0))
        
        _scale = self.sceneScale / self.origScale
        cx, cy = event.pos().x(), event.pos().y()
        self.buttonsParentPos = QtCore.QPointF(cx + _scale * (self.buttonsParentPos.x() - cx), cy + _scale * (self.buttonsParentPos.y() - cy))
                                               
        self.parentAxis.move(self.buttonsParentPos.toPoint())
        self.parentAxis.resize(round(100 * self.sceneScale), round(100 * self.sceneScale)) 
        
        # move buttons
        for but in self._getPickerButtons():
            globalPos = PickerView.localToGlobal(but.localPos, self.buttonsParentPos, self.sceneScale)
            but.move(globalPos.toPoint())
            but.resize(round(but.scaleX * self.sceneScale), round(but.scaleY * self.sceneScale))
            
        self.origScale = self.sceneScale
            
    # --------------------------------------------------------------------------------------------------------------------    
     
    @staticmethod
    def alignButtons(buttons, parentPos, sceneScale, alignType='horizontal'):
        if not buttons or len(buttons) < 2:
            return

        startButton = buttons[0]; endButton = buttons[-1]
        
        if alignType == 'horizontal':
            firstCenter   = startButton.pos().y() + startButton.height() / 2
            lastCenter    = endButton.pos().y() + endButton.height() / 2
            averageCenter = (firstCenter + lastCenter) / 2

            for button in buttons:
                globalPos = QtCore.QPointF(button.pos().x(), averageCenter - button.height() / 2)
                button.move(globalPos.toPoint())
                button.updateLocalPos(globalPos, parentPos, sceneScale)
                
        elif alignType == 'vertical':
            firstCenter   = startButton.pos().x() + startButton.width() / 2
            lastCenter    = endButton.pos().x() + endButton.width() / 2
            averageCenter = (firstCenter + lastCenter) / 2

            for button in buttons:
                globalPos = QtCore.QPointF(averageCenter - button.width() / 2, button.pos().y())
                button.move(globalPos.toPoint())
                button.updateLocalPos(globalPos, parentPos, sceneScale)
                
                
    # --------------------------------------------------------------------------------------------------------------------  
    def _getButtonsBoundingBox(self):
        buttons = self.selectedButtons or self._getPickerButtons()
        if not buttons:
            return None

        boundingBox = QtCore.QRectF()

        for button in buttons:
            '''
            https://doc.qt.io/qtforpython-5/PySide2/QtCore/QRectF.html#PySide2.QtCore.PySide2.QtCore.QRectF.united
            '''
            buttonRect = QtCore.QRectF(button.pos(), button.size())
            boundingBox = boundingBox.united(buttonRect)

        return boundingBox
        
    def _frameSelection(self):
        THRESHOLD = 0.05
        
        boundingBox = self._getButtonsBoundingBox()
        if boundingBox is None:
            self._frameDefault()
            return
        _viewRect  = self.geometry()
        
        # get scale
        scale = min(_viewRect.width() / boundingBox.width(), _viewRect.height() / boundingBox.height())
        '''
        Due to the sufficiently large threshold
        it is necessary to check whether to pan the view, so that the view can still be refreshed after panning!!
        '''
        if abs(scale * self.sceneScale - self.origScale) > THRESHOLD or self.frameMoveTag:
            self.sceneScale = self.origScale * scale
        else:
            return
        
        # move to view center
        boundingBoxCenter = boundingBox.center()
        viewCenter = QtCore.QPointF(_viewRect.width() / 2.0, _viewRect.height() / 2.0)
        
        localPos = (self.buttonsParentPos + (viewCenter - boundingBoxCenter) - viewCenter) * scale
        newButtonsParentPos = viewCenter + localPos
        if abs(newButtonsParentPos.x() - self.buttonsParentPos.x()) > THRESHOLD or abs(newButtonsParentPos.y() - self.buttonsParentPos.y()) > THRESHOLD:
            self.buttonsParentPos = newButtonsParentPos
    
        self.parentAxis.move(self.buttonsParentPos.toPoint())
        self.parentAxis.resize(round(100 * self.sceneScale), round(100 * self.sceneScale))

        # update buttons pos and scale
        for but in self._getPickerButtons():
            globalPos = PickerView.localToGlobal(but.localPos, self.buttonsParentPos, self.sceneScale)
            but.move(globalPos.toPoint())
            but.resize(round(but.scaleX * self.sceneScale), round(but.scaleY * self.sceneScale))

        self.origScale = self.sceneScale
        self.frameMoveTag = False
    


if __name__ =='__main__':
    UI = QtWidgets.QDialog(parent=qtUtils.getMayaMainWindow())
    UI.setWindowFlags(QtCore.Qt.WindowType.Window)
    UI.resize(500, 650)
    layout = QtWidgets.QVBoxLayout(UI)
    layout.addWidget(PickerView())
    UI.show()
    
    
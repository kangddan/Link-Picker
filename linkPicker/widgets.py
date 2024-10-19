# -*- coding: utf-8 -*-
import maya.api.OpenMaya as om2
from PySide2 import QtWidgets
from PySide2 import QtGui
from PySide2 import QtCore


class NullWidget(QtWidgets.QWidget):
    clicked = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True) 
        self.setObjectName('nullWidget')
        self._createWidgets()
        self._createLayouts()
        self._createConnections()
        
        self.setStyleSheet('''
            QPushButton#createBut {background: #282828; border-radius: 5px;  
                         min-width: 180px; min-height: 40px;}
            QPushButton:hover#createBut {background: #232323;}
            QPushButton:pressed#createBut {background: #335872;}
            QWidget#nullWidget {background-color: #333333;}
            
            ''')

    def _createWidgets(self):
        self.iconLabel = QtWidgets.QLabel()
        self.iconLabel.setAlignment(QtCore.Qt.AlignCenter) 
        self.iconLabel.setWordWrap(True)
        self.iconLabel.setText("<img src=':np-head.png'><h4>Create a new picker tab to get started</h4>")
        #path = r'C:\Users\kangddan\Documents\maya\2024\scripts\linkPicker\link.png'
        #self.iconLabel.setText(f"<img src={path}><h4>Create a new picker tab to get started</h4>")
        
        self.createBut = QtWidgets.QPushButton('Create Picker')
        self.createBut.setObjectName('createBut')
    
        
    def _createLayouts(self):
        mainLayout = QtWidgets.QVBoxLayout(self)
        mainLayout.setSpacing(30)
        
        mainLayout.addStretch()
        mainLayout.addWidget(self.iconLabel)

        buttonLayout = QtWidgets.QHBoxLayout() 
        buttonLayout.addStretch()
        buttonLayout.addWidget(self.createBut)
        buttonLayout.addStretch()

        mainLayout.addLayout(buttonLayout)
        mainLayout.addStretch()
        
    def _createConnections(self):
        self.createBut.clicked.connect(self.clicked.emit)
       
        
class MyTabBar(QtWidgets.QTabBar):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
    
class MyTabWidget(QtWidgets.QTabWidget):
    newTab    = QtCore.Signal()
    tabClosed = QtCore.Signal(object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setMovable(True)
        self.setTabsClosable(True)
        self.tabBar = self.tabBar()
        self.tabBar.installEventFilter(self)
        # ------------------------------------------------
        self.isMovingTab      = False 
        self.hasMoved         = False 
        self.MouseRightandMid = False
        self._createMenu()
        self._createWidgets()
        self._createConnections()

    
    def _createWidgets(self):
        self.nullWidget = NullWidget()
     
        self.iconLabel = QtWidgets.QLabel('+')
        self.iconLabel.setFont(QtGui.QFont('Arial', 8, QtGui.QFont.Bold) )
        self.tabBar.setTabButton(self.addTab(self.nullWidget, ''), QtWidgets.QTabBar.RightSide, self.iconLabel)
       
        #self.tabBar.setTabButton(self.addTab(self.nullWidget, '+'), QtWidgets.QTabBar.RightSide, None) # add base tab
        
        
    def _createMenu(self):
        self.addTableMenu = QtWidgets.QMenu(self)
        self.createAction = QtWidgets.QAction('New Tab', self.addTableMenu)
        self.addTableMenu.addAction(self.createAction) 
        # ---------------------------------------------------
        self.TableMenu = QtWidgets.QMenu(self)
        self.duplicateAction   = QtWidgets.QAction('Duplicate Tab',  self.TableMenu)
        self.closeAllAction    = QtWidgets.QAction('Close All Tabs', self.TableMenu)
        self.closeOthersAction = QtWidgets.QAction('Close Others',   self.TableMenu)
        self.TableMenu.addAction(self.duplicateAction)
        self.TableMenu.addSeparator()
        self.TableMenu.addAction(self.closeAllAction)
        self.TableMenu.addAction(self.closeOthersAction)
        
        
    def _createConnections(self):
        self.nullWidget.clicked.connect(self.newTab.emit)
        self.createAction.triggered.connect(self.newTab.emit)
        self.tabCloseRequested.connect(self._closeTab)
        self.tabBarDoubleClicked.connect(self._renameTab)
        
        self.closeAllAction.triggered.connect(self._closeAllTab)
        self.closeOthersAction.triggered.connect(self._closeOthers)
        
        # ----------------------------------------
        self.showTabTimer = QtCore.QTimer(self)
        self.showTabTimer.setSingleShot(True)
        self.showTabTimer.timeout.connect(self._showAddTab)


    def eventFilter(self, obj, event):
        if obj != self.tabBar:
            return super().eventFilter(obj, event)
            
        if event.type() == QtCore.QEvent.Wheel:
            '''
            Skip switching to the last tab (e.g., the "add tab" button)
            '''
            currentIndex = self.currentIndex()
            index = currentIndex - 1 if event.angleDelta().y() > 0 else currentIndex + 1
            if index == self.count() - 1:
                return True
            return False
                   
        if event.type() in [QtCore.QEvent.MouseButtonPress, QtCore.QEvent.MouseButtonDblClick]:
            button = event.button()

            if button in [QtCore.Qt.LeftButton, QtCore.Qt.MiddleButton, QtCore.Qt.RightButton]:
                '''
                All three types of mouse buttons can trigger the addTableMenu
                '''
                if self.tabBar.tabAt(event.pos()) == self.count() - 1:
                    self.addTableMenu.exec_(event.globalPos())
                    return True
                
                elif button == QtCore.Qt.RightButton and event.buttons() == QtCore.Qt.RightButton:
                    self.MouseRightandMid  = True
                    self.closeOthersAction.setData(self.tabBar.tabAt(event.pos())) # get tag index
                    self.TableMenu.exec_(event.globalPos())
                    return True
                
                    
                elif button == QtCore.Qt.MiddleButton and event.buttons() == QtCore.Qt.MiddleButton:
                    '''
                    self.MouseRightandMid  = True
                    self.isMovingTab       = False
                    self.hasMoved          = False
                    '''
                    self.MouseRightandMid  = True
                    self.closeOthersAction.setData(self.tabBar.tabAt(event.pos())) # get tag index
                    self.TableMenu.exec_(event.globalPos())
                    return True
                
                elif button == QtCore.Qt.RightButton:
               
                    '''
                    Ignore to prevent middle/right mouse button from triggering tabBarDoubleClicked
                    Track middle/right button state and reset movement flags
                    '''
                    self.MouseRightandMid  = True
                    self.isMovingTab       = False
                    self.hasMoved          = False
                    return True              
                
            if button == QtCore.Qt.LeftButton:
                self.MouseRightandMid  = True
                self.isMovingTab = True
                self.hasMoved    = False
                return False 

        elif event.type() == QtCore.QEvent.MouseMove and self.MouseRightandMid  and not self.hasMoved:
            # vis end tab
            self.setTabVisible(self.count() - 1, False)
            self.hasMoved = True
            return False

        elif event.type() == QtCore.QEvent.MouseButtonRelease and event.button() == QtCore.Qt.LeftButton:
            if self.hasMoved or self.MouseRightandMid:
                #vis end tab
                #If the interval is too slow, quickly dragging the tab may cause 'New Tab' to appear in the wrong position £¡£¡
                self.showTabTimer.start(250)
            
            if not isinstance(self.widget(self.count() - 1), NullWidget):
                nullWidgetIndex = self.indexOf(self.nullWidget)
                self.tabBar.moveTab(nullWidgetIndex, self.count() - 1)
            # ----------------------------------------------------------------------------
            
            self.isMovingTab      = False
            self.MouseRightandMid = False
            self.hasMoved         = False
            return False
        return False


    def _showAddTab(self):
        self.showTabTimer.stop()
        self.setTabVisible(self.count() - 1, True) 


    def addNewTab(self, widget) -> int:
        tabName: str = self._getNextName()
        index:   int = self.insertTab(self.count() - 1, widget, tabName)
        return index
        
          
    def _closeTab(self, index):
        if self.count() == 1:
            return
        tabName = self.tabText(index)
        reply = QtWidgets.QMessageBox.warning(self, 'Close Tab', 
                "Are you sure you want to close the tab '{}'? \nAll changes will be lost.".format(tabName), 
                QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Yes)
        
        if reply == QtWidgets.QMessageBox.StandardButton.No:
            return 
            
        # Disconnect signals initialized in pickerView before removing the tab
        widget = self.widget(index)
        self.tabClosed.emit(widget)
        
        self.removeTab(index)
        widget.deleteLater()
        self.setCurrentIndex(index - 1)
        
        
    def _closeAllTab(self):
        count = self.count() - 1
        for i in reversed(range(count)):
            try:
                self._closeTab(i)
            except Exception as e:
                import traceback
                traceback.print_exc() 
                om2.MGlobal.displayWarning(f'Incorrect tab. \n{str(e)}')
                continue
            
            
    def _closeOthers(self):
        index = self.closeOthersAction.data()
        count = self.count() - 1
        for i in reversed(range(count)):
            if i == index:
                continue
            self._closeTab(i)

    
    def _renameTab(self, index):
        if self.count() == 1:
            return
        currentName = self.tabText(index)
        newName, isOk = QtWidgets.QInputDialog.getText(self, 'Tab Name', 'New Name', QtWidgets.QLineEdit.Normal, currentName)
        if isOk and newName and newName != currentName:
            self.setTabText(index, newName)
            
            
    def _duplicateTab(self):
        pass
        

    def _getNextName(self) -> str:
        prefix = 'Untitled '
        items  = [self.tabText(i) for i in range(self.count())]
        suffixNumbers = []
        
        for item in items:
            if not item.startswith(prefix):
                continue
            suffix = item[len(prefix):] 
            if suffix.isdigit():
                suffixNumbers.append(int(suffix))  
 
        maxSuffix = max(suffixNumbers) if suffixNumbers else 0
        return f'{prefix}{maxSuffix + 1}'
        
        
        
class ZoomHintWidget(QtWidgets.QWidget):
    pass
    
    
class NumberLineEdit(QtWidgets.QLineEdit):
    
    def __repr__(self):
        return f"< {self.__class__.__name__} '{self.get()}'>"
    
    def __init__(self, dataType: int | float ='int', 
                       defaultValue=0, 
                       step=1, 
                       minimum=-100, 
                       maximum=100, 
                       parent=None):
                        
        super().__init__(parent)
        self.setAlignment(QtCore.Qt.AlignCenter)
        self._dataType    = dataType
        self._step        = step
        self._minimum     = minimum
        self._maximum     = maximum
    
        self._storedValue = self._valueCheck(defaultValue)
        self._cacheNumber = self._formatDisplayValue(self._storedValue)
        self.setText(self._cacheNumber)
        
        self.dragging   = False 
        self.lastMouseX = 0
        

    @staticmethod
    def isNumber(value):
        from re import match
        pattern = r'^[+-]?(\d+(\.\d*)?|\.\d+)$'
        return bool(match(pattern, value))
    
    # ------------------------------------------    
    
    def focusInEvent(self, event):
        self._cacheNumber = self.text()
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        value = self.text()
        if not self.isNumber(value):
            self.setText(self._cacheNumber)
        else:
            value = self._valueCheck(value)
            # ---------------------------------
            self._storedValue = value
            self.setText(self._formatDisplayValue(value))
        super().focusOutEvent(event)
        
    # -----------------------------------------
    def _valueCheck(self, value):
        value = int(float(value)) if self._dataType == 'int' else float(value)
        value = max(self._minimum, min(self._maximum, value))
        return value
        
    def _formatDisplayValue(self, value):
        if self._dataType == 'float':
            return f"{value:.3f}"
        return str(value)
        
    def mousePressEvent(self, event):
        if (event.button() == QtCore.Qt.MiddleButton and 
           QtWidgets.QApplication.keyboardModifiers() == QtCore.Qt.ControlModifier):
            
            self.dragging = True
            self.lastMouseX = event.x()
            self.clearFocus() 
            self.setCursor(QtCore.Qt.SizeHorCursor)
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.dragging:
            delta = event.x() - self.lastMouseX
            if delta != 0:
                adjustment = (delta / (1000.0 if self._dataType == 'float' else 2)) * self._step 
                
                value = self._valueCheck(self._storedValue + adjustment)
                self._storedValue = value
                self.setText(self._formatDisplayValue(value))
                self.lastMouseX = event.x()
                
                self.editingFinished.emit() # update signal emit
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.MiddleButton:
            self.dragging = False
            #self.editingFinished.emit() # update signal emit
            self.setCursor(QtCore.Qt.IBeamCursor)
        else:
            super().mouseReleaseEvent(event)
            
    def get(self):
        return self._storedValue
        
    def set(self, value):
        if not isinstance(value, (int, float)):
            self.setText(self._cacheNumber)
            return
            
        self._storedValue = self._valueCheck(value)
        self.setText(self._formatDisplayValue(self._storedValue))
        
        
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
        
class CustomDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent=None, itemHeight=30):
        super().__init__(parent)
        self.itemHeight = itemHeight

    def sizeHint(self, option, index):
        size = super().sizeHint(option, index)
        size.setHeight(self.itemHeight)
        return size    
        
    def paint(self, painter, option, index):
        painter.fillRect(option.rect, QtGui.QColor(82, 82, 82)) 
        super().paint(painter, option, index)

        
        
import sys
import importlib
from PySide2 import QtWidgets, QtGui, QtCore
from linkPicker import qtUtils, widgets, pickerView, colorWidget, toolBoxWidget
importlib.reload(pickerView)
importlib.reload(widgets)
importlib.reload(colorWidget)
importlib.reload(toolBoxWidget)

class MainUI(QtWidgets.QDialog):
    
    _INSTANCE = None
    
    def __new__(cls, *args, **kwargs):
        if cls._INSTANCE is None:
            cls._INSTANCE = super().__new__(cls) 
        return cls._INSTANCE
        
    def __repr__(self):
        return f'< PickerWindow{self.__class__.__name__} Tab -> {self.tabWidget.count()} >'
        
    def __init__(self, parent=qtUtils.getMayaMainWindow()):
        if hasattr(self, '_init') and self._init:
            return
        self._init = True
        
        super().__init__(parent)
        self.setObjectName('PickerWindow')
        self.setWindowFlags(QtCore.Qt.WindowType.Window)
        self.setFocusPolicy(QtCore.Qt.StrongFocus); self.setFocus()
        self.setWindowTitle('Link Picker v0.1.0-beta.1')
        self.resize(600, 750)
        
        self._createMenu()
        self._createActions()
        self._createWidgets()
        self._createLayouts()
        self._createConnections()
        
    def _createMenu(self):
        self.mainMenuBar = QtWidgets.QMenuBar(self) 
        self.fileMenu    = QtWidgets.QMenu('File',   self.mainMenuBar) 
        self.editMenu    = QtWidgets.QMenu('Edit',   self.mainMenuBar)
        self.pickerMenu  = QtWidgets.QMenu('Picker', self.mainMenuBar)
        self.helpMenu    = QtWidgets.QMenu('Help',   self.mainMenuBar)
        self.fileMenu.setTearOffEnabled(True)
        self.editMenu.setTearOffEnabled(True)
        self.pickerMenu.setTearOffEnabled(True)
        self.helpMenu.setTearOffEnabled(True)
        self.mainMenuBar.addMenu(self.fileMenu)
        self.mainMenuBar.addMenu(self.editMenu)
        self.mainMenuBar.addMenu(self.pickerMenu)
        self.mainMenuBar.addMenu(self.helpMenu)
        
    def _createActions(self):
        
        self.newAction        = QtWidgets.QAction(QtGui.QIcon(':fileNew.png'), 'New...',   self.fileMenu, shortcut='Ctrl+N')
        self.openAction       = QtWidgets.QAction(QtGui.QIcon(':fileOpen.png'), 'Open...', self.fileMenu, shortcut='Ctrl+O')
        self.saveAction       = QtWidgets.QAction(QtGui.QIcon(':fileSave.png'), 'Save',    self.fileMenu, shortcut='Ctrl+S')
        self.saveAsAction     = QtWidgets.QAction('Save as...', self.fileMenu, shortcut='Ctrl+Shift+S')
        self.renameTabAction  = QtWidgets.QAction(QtGui.QIcon(':renamePreset.png'), 'Rename Tab',    self.fileMenu)
        self.closeAction      = QtWidgets.QAction(QtGui.QIcon(':nodeGrapherClose.png'), 'Close Tab', self.fileMenu, shortcut='Ctrl+F4')
        self.closeAllAction   = QtWidgets.QAction('Close All Tab', self.fileMenu, shortcut='Ctrl+Shift+F4')
        self.quitPickerAction = QtWidgets.QAction(QtGui.QIcon(':enabled.png'), 'Quit Picker', self.fileMenu, shortcut='Alt+F4')
        
        self.fileMenu.addAction(self.newAction)
        self.fileMenu.addAction(self.openAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.saveAction)
        self.fileMenu.addAction(self.saveAsAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.renameTabAction)
        self.fileMenu.addAction(self.closeAction)
        self.fileMenu.addAction(self.closeAllAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.quitPickerAction)
        
        # ----------------------------------------------------------------------------------------------------------------
        self.undoAction   = QtWidgets.QAction(QtGui.QIcon(':undo_s.png'), 'Undo', self.editMenu, shortcut='Ctrl+Z')
        self.redoAction   = QtWidgets.QAction(QtGui.QIcon(':redo_s.png'), 'Redo', self.editMenu, shortcut='Ctrl+Y')
        self.cutAction    = QtWidgets.QAction('Cut', self.editMenu, shortcut='Ctrl+X')
        self.copyAction   = QtWidgets.QAction(QtGui.QIcon(':polyCopyUV.png'), 'Copy',   self.editMenu, shortcut='Ctrl+C')
        self.pasteAction  = QtWidgets.QAction(QtGui.QIcon(':polyPasteUV.png'), 'Paste', self.editMenu, shortcut='Ctrl+V')
        self.deleteAction = QtWidgets.QAction(QtGui.QIcon(':delete.png'), 'Delete',     self.editMenu, shortcut='Delete')
        self.mirrorAction = QtWidgets.QAction(QtGui.QIcon(':cursor_loop.png'),'Mirror', self.editMenu)
        self.ToolAction   = QtWidgets.QAction(QtGui.QIcon(':toolSettings.png'),'Hide ToolBox', self.editMenu)
        
        self.editMenu.addAction(self.undoAction)
        self.editMenu.addAction(self.redoAction)
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.cutAction)
        self.editMenu.addAction(self.copyAction)
        self.editMenu.addAction(self.pasteAction)
        self.editMenu.addAction(self.deleteAction)
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.mirrorAction)
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.ToolAction)
        
        # ----------------------------------------------------------------------------------------------------------------
        self.addOneButtonAction      = QtWidgets.QAction(QtGui.QIcon(':addClip.png'), 'Add One Button', self.pickerMenu)
        self.addManyButtonsAction    = QtWidgets.QAction('Add Many Buttons',  self.pickerMenu)
        self.updateButtonAction      = QtWidgets.QAction(QtGui.QIcon(':refresh.png'), 'Update Button',  self.pickerMenu)
        self.changeBackgroundAction  = QtWidgets.QAction(QtGui.QIcon(':file.svg'), 'Change Background', self.pickerMenu)
        self.resizeBackgroundAction  = QtWidgets.QAction('Resize Background', self.pickerMenu)
        self.changeNamespaceAction   = QtWidgets.QAction('Change Namespace',  self.pickerMenu)
        
        self.alignHorizontallyAction = QtWidgets.QAction('Align Horizontally', self.pickerMenu)
        self.alignVerticallyAction   = QtWidgets.QAction('Align Vertically',  self.pickerMenu)
        
        self.resetViewAction         = QtWidgets.QAction(QtGui.QIcon(':rvRealSize.png'), 'Reset View',  self.pickerMenu)
        self.frameViewAction         = QtWidgets.QAction(QtGui.QIcon(':visible.png'), 'Frame View',     self.pickerMenu)
        
        self.deletePickerDataAction  = QtWidgets.QAction(QtGui.QIcon(':delete.png'), 'Delete Picker Data',     self.pickerMenu)
        self.preferencesAction       = QtWidgets.QAction(QtGui.QIcon(':advancedSettings.png'),'Preferences...',  self.pickerMenu, shortcut='Ctrl+E')
        
        self.pickerMenu.addAction(self.addOneButtonAction)
        self.pickerMenu.addAction(self.addManyButtonsAction)
        self.pickerMenu.addAction(self.updateButtonAction)
        self.pickerMenu.addSeparator()
        self.pickerMenu.addAction(self.changeBackgroundAction)
        self.pickerMenu.addAction(self.resizeBackgroundAction)
        self.pickerMenu.addAction(self.changeNamespaceAction)
        self.pickerMenu.addSeparator()
        
        self.pickerMenu.addAction(self.alignHorizontallyAction)
        self.pickerMenu.addAction(self.alignVerticallyAction)
        
        self.pickerMenu.addSeparator()
        self.pickerMenu.addAction(self.resetViewAction)
        self.pickerMenu.addAction(self.frameViewAction)
        self.pickerMenu.addSeparator()
        self.pickerMenu.addAction(self.deletePickerDataAction)
        self.pickerMenu.addAction(self.preferencesAction)
        
        # ----------------------------------------------------------------------------------------------------------------
        self.aboutAction = QtWidgets.QAction(QtGui.QIcon(':help.png'), 'About Link Picker', self.helpMenu)
        self.helpMenu.addAction(self.aboutAction)
        
    def _updateFileMenuActions(self):
        _: bool = self.tabWidget.count() >= 2
        self.saveAction.setEnabled(_)
        self.saveAsAction.setEnabled(_) 
        self.renameTabAction.setEnabled(_)
        self.closeAction.setEnabled(_)
        self.closeAllAction.setEnabled(_)

    def _updateEditMenuActions(self):
        self.ToolAction.setText('Hide ToolBox'if self.toolBoxWidget.isVisible() else 'Show ToolBox')
        
    def _updatePickerMenuActions(self):
        pass
        
    
    def _createWidgets(self):
        self.tabWidget     = widgets.MyTabWidget(parent=self)
        self.toolBoxWidget = toolBoxWidget.ToolBoxWidget()


    def _createLayouts(self):
        mainLayout = QtWidgets.QVBoxLayout(self)
        mainLayout.setSpacing(4)
        mainLayout.setContentsMargins(1, 1, 1, 6)
        mainLayout.setMenuBar(self.mainMenuBar)
        mainLayout.addWidget(self.tabWidget)
        mainLayout.addWidget(self.toolBoxWidget)
        
    def _createConnections(self):
        self.tabWidget.newTab.connect(self._createNewTab)
        
        self.fileMenu.aboutToShow.connect(self._updateFileMenuActions)
        self.editMenu.aboutToShow.connect(self._updateEditMenuActions)
        self.pickerMenu.aboutToShow.connect(self._updatePickerMenuActions)
        
        self.quitPickerAction.triggered.connect(self.close)
        self.newAction.triggered.connect(self.tabWidget.newTab.emit)
        self.closeAction.triggered.connect(self._handleCloseTab)
        self.closeAllAction.triggered.connect(self._handleCloseAllTabs)
        self.renameTabAction.triggered.connect(self._handleRenameTab)
        
        self.ToolAction.triggered.connect(lambda: self.toolBoxWidget.hide() if self.toolBoxWidget.isVisible() else self.toolBoxWidget.show())
        
    def _createNewTab(self):
        pickerViewInstance = pickerView.PickerView()
        index = self.tabWidget.addNewTab(pickerViewInstance)
        if index is not None:
            self.tabWidget.setCurrentIndex(index) # Current Tab
    
    def _handleCloseTab(self):
        index = self.tabWidget.currentIndex()
        self.tabWidget._closeTab(index)
        
    def _handleCloseAllTabs(self):
        self.tabWidget._closeAllTab()
        
    def _handleRenameTab(self):
        index = self.tabWidget.currentIndex()
        self.tabWidget._renameTab(index)


if __name__ == '__main__':
    ui = MainUI()
    ui.show()
    #ui.toolBoxWidget.show()



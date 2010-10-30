# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui
import database
from AnalysisTemplate import *
import lib.Manager

class FileAnalysisView(QtGui.QWidget):
    def __init__(self, parent, mod):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.man = lib.Manager.getManager()
        #print self.window().objectName()
        #self.dm = self.window().dm  ## get module from window
        self.mod = mod
        self.dbFile = None
        self.db = None
        
        self.connect(self.ui.openDbBtn, QtCore.SIGNAL('clicked()'), self.openDbClicked)
        self.connect(self.ui.createDbBtn, QtCore.SIGNAL('clicked()'), self.createDbClicked)
        self.connect(self.ui.addFileBtn, QtCore.SIGNAL('clicked()'), self.addFileClicked)
        
        
    def openDbClicked(self):
        fn = QtGui.QFileDialog.getOpenFileName(self, "Select Database File", self.man.getBaseDir().name(), "SQLite Database (*.sqlite)")
        if fn == '':
            return
        self.ui.databaseText.setText(fn)
        self.dbFile = fn
        self.db = database.AnalysisDatabase(self.dbFile)
        
    def createDbClicked(self):
        fn = QtGui.QFileDialog.getSaveFileName(self, "Create Database File", self.man.getBaseDir().name(), "SQLite Database (*.sqlite)", None, QtGui.QFileDialog.DontConfirmOverwrite)
        if fn is '':
            return
        self.ui.databaseText.setText(fn)
        self.dbFile = fn
        self.db = database.AnalysisDatabase(self.dbFile, self.man.getBaseDir())
        
    def addFileClicked(self):
        cf = self.mod.selectedFile()
        self.db.addDir(cf)
        
        
    





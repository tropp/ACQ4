# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'PatchTemplate.ui'
#
# Created: Sat Jun 12 15:15:46 2010
#      by: PyQt4 UI code generator 4.5.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(267, 343)
        self.verticalLayout_2 = QtGui.QVBoxLayout(Form)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setMargin(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.splitter_3 = QtGui.QSplitter(Form)
        self.splitter_3.setOrientation(QtCore.Qt.Vertical)
        self.splitter_3.setObjectName("splitter_3")
        self.splitter_2 = QtGui.QSplitter(self.splitter_3)
        self.splitter_2.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_2.setObjectName("splitter_2")
        self.layoutWidget = QtGui.QWidget(self.splitter_2)
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout = QtGui.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox_2 = QtGui.QGroupBox(self.layoutWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_2.sizePolicy().hasHeightForWidth())
        self.groupBox_2.setSizePolicy(sizePolicy)
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox_2)
        self.gridLayout_2.setMargin(0)
        self.gridLayout_2.setSpacing(0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.vcPulseCheck = QtGui.QCheckBox(self.groupBox_2)
        self.vcPulseCheck.setChecked(True)
        self.vcPulseCheck.setObjectName("vcPulseCheck")
        self.gridLayout_2.addWidget(self.vcPulseCheck, 2, 1, 1, 1)
        self.vcHoldCheck = QtGui.QCheckBox(self.groupBox_2)
        self.vcHoldCheck.setObjectName("vcHoldCheck")
        self.gridLayout_2.addWidget(self.vcHoldCheck, 3, 1, 1, 1)
        self.icPulseCheck = QtGui.QCheckBox(self.groupBox_2)
        self.icPulseCheck.setChecked(True)
        self.icPulseCheck.setObjectName("icPulseCheck")
        self.gridLayout_2.addWidget(self.icPulseCheck, 4, 1, 1, 1)
        self.icHoldCheck = QtGui.QCheckBox(self.groupBox_2)
        self.icHoldCheck.setObjectName("icHoldCheck")
        self.gridLayout_2.addWidget(self.icHoldCheck, 6, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem, 7, 1, 1, 1)
        self.label = QtGui.QLabel(self.groupBox_2)
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 10, 0, 1, 2)
        self.label_3 = QtGui.QLabel(self.groupBox_2)
        self.label_3.setObjectName("label_3")
        self.gridLayout_2.addWidget(self.label_3, 9, 0, 1, 2)
        self.label_4 = QtGui.QLabel(self.groupBox_2)
        self.label_4.setObjectName("label_4")
        self.gridLayout_2.addWidget(self.label_4, 8, 0, 1, 2)
        self.icModeRadio = QtGui.QRadioButton(self.groupBox_2)
        self.icModeRadio.setObjectName("icModeRadio")
        self.gridLayout_2.addWidget(self.icModeRadio, 4, 0, 1, 1)
        self.vcModeRadio = QtGui.QRadioButton(self.groupBox_2)
        self.vcModeRadio.setChecked(True)
        self.vcModeRadio.setObjectName("vcModeRadio")
        self.gridLayout_2.addWidget(self.vcModeRadio, 2, 0, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.startBtn = QtGui.QPushButton(self.groupBox_2)
        self.startBtn.setCheckable(True)
        self.startBtn.setObjectName("startBtn")
        self.horizontalLayout.addWidget(self.startBtn)
        self.recordBtn = QtGui.QPushButton(self.groupBox_2)
        self.recordBtn.setCheckable(True)
        self.recordBtn.setObjectName("recordBtn")
        self.horizontalLayout.addWidget(self.recordBtn)
        self.gridLayout_2.addLayout(self.horizontalLayout, 0, 0, 1, 3)
        self.icPulseSpin = SpinBox(self.groupBox_2)
        self.icPulseSpin.setMaximumSize(QtCore.QSize(70, 16777215))
        self.icPulseSpin.setObjectName("icPulseSpin")
        self.gridLayout_2.addWidget(self.icPulseSpin, 4, 2, 1, 1)
        self.pulseTimeSpin = SpinBox(self.groupBox_2)
        self.pulseTimeSpin.setMaximumSize(QtCore.QSize(70, 16777215))
        self.pulseTimeSpin.setSingleStep(1.0)
        self.pulseTimeSpin.setObjectName("pulseTimeSpin")
        self.gridLayout_2.addWidget(self.pulseTimeSpin, 9, 2, 1, 1)
        self.delayTimeSpin = SpinBox(self.groupBox_2)
        self.delayTimeSpin.setMaximumSize(QtCore.QSize(70, 16777215))
        self.delayTimeSpin.setMinimum(1.0)
        self.delayTimeSpin.setMaximum(10000.0)
        self.delayTimeSpin.setSingleStep(1.0)
        self.delayTimeSpin.setObjectName("delayTimeSpin")
        self.gridLayout_2.addWidget(self.delayTimeSpin, 8, 2, 1, 1)
        self.vcPulseSpin = SpinBox(self.groupBox_2)
        self.vcPulseSpin.setMaximumSize(QtCore.QSize(70, 16777215))
        self.vcPulseSpin.setObjectName("vcPulseSpin")
        self.gridLayout_2.addWidget(self.vcPulseSpin, 2, 2, 1, 1)
        self.icHoldSpin = SpinBox(self.groupBox_2)
        self.icHoldSpin.setMaximumSize(QtCore.QSize(70, 16777215))
        self.icHoldSpin.setObjectName("icHoldSpin")
        self.gridLayout_2.addWidget(self.icHoldSpin, 5, 2, 2, 1)
        self.cycleTimeSpin = SpinBox(self.groupBox_2)
        self.cycleTimeSpin.setMaximumSize(QtCore.QSize(70, 16777215))
        self.cycleTimeSpin.setSingleStep(1.0)
        self.cycleTimeSpin.setProperty("value", QtCore.QVariant(0.2))
        self.cycleTimeSpin.setObjectName("cycleTimeSpin")
        self.gridLayout_2.addWidget(self.cycleTimeSpin, 10, 2, 1, 1)
        self.vcHoldSpin = SpinBox(self.groupBox_2)
        self.vcHoldSpin.setMaximumSize(QtCore.QSize(70, 16777215))
        self.vcHoldSpin.setObjectName("vcHoldSpin")
        self.gridLayout_2.addWidget(self.vcHoldSpin, 3, 2, 1, 1)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setContentsMargins(0, -1, -1, -1)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.bathModeBtn = QtGui.QToolButton(self.groupBox_2)
        self.bathModeBtn.setObjectName("bathModeBtn")
        self.horizontalLayout_2.addWidget(self.bathModeBtn)
        self.patchModeBtn = QtGui.QToolButton(self.groupBox_2)
        self.patchModeBtn.setObjectName("patchModeBtn")
        self.horizontalLayout_2.addWidget(self.patchModeBtn)
        self.cellModeBtn = QtGui.QToolButton(self.groupBox_2)
        self.cellModeBtn.setObjectName("cellModeBtn")
        self.horizontalLayout_2.addWidget(self.cellModeBtn)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.gridLayout_2.addLayout(self.horizontalLayout_2, 1, 0, 1, 3)
        self.verticalLayout.addWidget(self.groupBox_2)
        self.groupBox = QtGui.QGroupBox(self.layoutWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setObjectName("groupBox")
        self.formLayout = QtGui.QFormLayout(self.groupBox)
        self.formLayout.setMargin(0)
        self.formLayout.setSpacing(0)
        self.formLayout.setObjectName("formLayout")
        self.resetBtn = QtGui.QToolButton(self.groupBox)
        self.resetBtn.setObjectName("resetBtn")
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.resetBtn)
        self.inputResistanceCheck = QtGui.QCheckBox(self.groupBox)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.inputResistanceCheck.setFont(font)
        self.inputResistanceCheck.setChecked(True)
        self.inputResistanceCheck.setObjectName("inputResistanceCheck")
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.inputResistanceCheck)
        self.inputResistanceLabel = QtGui.QLabel(self.groupBox)
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setWeight(75)
        font.setBold(True)
        self.inputResistanceLabel.setFont(font)
        self.inputResistanceLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.inputResistanceLabel.setObjectName("inputResistanceLabel")
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.inputResistanceLabel)
        self.accessResistanceCheck = QtGui.QCheckBox(self.groupBox)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.accessResistanceCheck.setFont(font)
        self.accessResistanceCheck.setObjectName("accessResistanceCheck")
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.accessResistanceCheck)
        self.accessResistanceLabel = QtGui.QLabel(self.groupBox)
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setWeight(75)
        font.setBold(True)
        self.accessResistanceLabel.setFont(font)
        self.accessResistanceLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.accessResistanceLabel.setObjectName("accessResistanceLabel")
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.accessResistanceLabel)
        self.restingPotentialCheck = QtGui.QCheckBox(self.groupBox)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.restingPotentialCheck.setFont(font)
        self.restingPotentialCheck.setObjectName("restingPotentialCheck")
        self.formLayout.setWidget(3, QtGui.QFormLayout.LabelRole, self.restingPotentialCheck)
        self.restingPotentialLabel = QtGui.QLabel(self.groupBox)
        self.restingPotentialLabel.setMinimumSize(QtCore.QSize(140, 0))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setWeight(75)
        font.setBold(True)
        self.restingPotentialLabel.setFont(font)
        self.restingPotentialLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.restingPotentialLabel.setObjectName("restingPotentialLabel")
        self.formLayout.setWidget(3, QtGui.QFormLayout.FieldRole, self.restingPotentialLabel)
        self.restingCurrentCheck = QtGui.QCheckBox(self.groupBox)
        self.restingCurrentCheck.setObjectName("restingCurrentCheck")
        self.formLayout.setWidget(4, QtGui.QFormLayout.LabelRole, self.restingCurrentCheck)
        self.restingCurrentLabel = QtGui.QLabel(self.groupBox)
        self.restingCurrentLabel.setMinimumSize(QtCore.QSize(120, 0))
        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.restingCurrentLabel.setFont(font)
        self.restingCurrentLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.restingCurrentLabel.setObjectName("restingCurrentLabel")
        self.formLayout.setWidget(4, QtGui.QFormLayout.FieldRole, self.restingCurrentLabel)
        self.capacitanceCheck = QtGui.QCheckBox(self.groupBox)
        self.capacitanceCheck.setObjectName("capacitanceCheck")
        self.formLayout.setWidget(5, QtGui.QFormLayout.LabelRole, self.capacitanceCheck)
        self.capacitanceLabel = QtGui.QLabel(self.groupBox)
        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.capacitanceLabel.setFont(font)
        self.capacitanceLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.capacitanceLabel.setObjectName("capacitanceLabel")
        self.formLayout.setWidget(5, QtGui.QFormLayout.FieldRole, self.capacitanceLabel)
        self.fitErrorCheck = QtGui.QCheckBox(self.groupBox)
        self.fitErrorCheck.setObjectName("fitErrorCheck")
        self.formLayout.setWidget(6, QtGui.QFormLayout.LabelRole, self.fitErrorCheck)
        self.fitErrorLabel = QtGui.QLabel(self.groupBox)
        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.fitErrorLabel.setFont(font)
        self.fitErrorLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.fitErrorLabel.setObjectName("fitErrorLabel")
        self.formLayout.setWidget(6, QtGui.QFormLayout.FieldRole, self.fitErrorLabel)
        self.verticalLayout.addWidget(self.groupBox)
        self.splitter = QtGui.QSplitter(self.splitter_2)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName("splitter")
        self.patchPlot = PlotWidget(self.splitter)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.patchPlot.sizePolicy().hasHeightForWidth())
        self.patchPlot.setSizePolicy(sizePolicy)
        self.patchPlot.setObjectName("patchPlot")
        self.commandPlot = PlotWidget(self.splitter)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.commandPlot.sizePolicy().hasHeightForWidth())
        self.commandPlot.setSizePolicy(sizePolicy)
        self.commandPlot.setObjectName("commandPlot")
        self.layoutWidget1 = QtGui.QWidget(self.splitter_3)
        self.layoutWidget1.setObjectName("layoutWidget1")
        self.plotLayout = QtGui.QVBoxLayout(self.layoutWidget1)
        self.plotLayout.setSpacing(0)
        self.plotLayout.setObjectName("plotLayout")
        self.verticalLayout_2.addWidget(self.splitter_3)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Patch", None, QtGui.QApplication.UnicodeUTF8))
        self.vcPulseCheck.setText(QtGui.QApplication.translate("Form", "Pulse", None, QtGui.QApplication.UnicodeUTF8))
        self.vcHoldCheck.setText(QtGui.QApplication.translate("Form", "Hold", None, QtGui.QApplication.UnicodeUTF8))
        self.icPulseCheck.setText(QtGui.QApplication.translate("Form", "Pulse", None, QtGui.QApplication.UnicodeUTF8))
        self.icHoldCheck.setText(QtGui.QApplication.translate("Form", "Hold", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Form", "Cycle Time", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Form", "Pulse Length", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("Form", "Delay Length", None, QtGui.QApplication.UnicodeUTF8))
        self.icModeRadio.setText(QtGui.QApplication.translate("Form", "IC", None, QtGui.QApplication.UnicodeUTF8))
        self.vcModeRadio.setText(QtGui.QApplication.translate("Form", "VC", None, QtGui.QApplication.UnicodeUTF8))
        self.startBtn.setText(QtGui.QApplication.translate("Form", "Start", None, QtGui.QApplication.UnicodeUTF8))
        self.recordBtn.setText(QtGui.QApplication.translate("Form", "Record", None, QtGui.QApplication.UnicodeUTF8))
        self.icPulseSpin.setSuffix(QtGui.QApplication.translate("Form", "A", None, QtGui.QApplication.UnicodeUTF8))
        self.pulseTimeSpin.setSuffix(QtGui.QApplication.translate("Form", "s", None, QtGui.QApplication.UnicodeUTF8))
        self.delayTimeSpin.setSuffix(QtGui.QApplication.translate("Form", "s", None, QtGui.QApplication.UnicodeUTF8))
        self.vcPulseSpin.setSuffix(QtGui.QApplication.translate("Form", "V", None, QtGui.QApplication.UnicodeUTF8))
        self.icHoldSpin.setSuffix(QtGui.QApplication.translate("Form", "A", None, QtGui.QApplication.UnicodeUTF8))
        self.cycleTimeSpin.setSuffix(QtGui.QApplication.translate("Form", "s", None, QtGui.QApplication.UnicodeUTF8))
        self.vcHoldSpin.setSuffix(QtGui.QApplication.translate("Form", "V", None, QtGui.QApplication.UnicodeUTF8))
        self.bathModeBtn.setText(QtGui.QApplication.translate("Form", "Bath", None, QtGui.QApplication.UnicodeUTF8))
        self.patchModeBtn.setText(QtGui.QApplication.translate("Form", "Patch", None, QtGui.QApplication.UnicodeUTF8))
        self.cellModeBtn.setText(QtGui.QApplication.translate("Form", "Cell", None, QtGui.QApplication.UnicodeUTF8))
        self.resetBtn.setText(QtGui.QApplication.translate("Form", "Reset History", None, QtGui.QApplication.UnicodeUTF8))
        self.inputResistanceCheck.setText(QtGui.QApplication.translate("Form", "Input Res.", None, QtGui.QApplication.UnicodeUTF8))
        self.inputResistanceLabel.setText(QtGui.QApplication.translate("Form", "0", None, QtGui.QApplication.UnicodeUTF8))
        self.accessResistanceCheck.setText(QtGui.QApplication.translate("Form", "Access Res.", None, QtGui.QApplication.UnicodeUTF8))
        self.accessResistanceLabel.setText(QtGui.QApplication.translate("Form", "0", None, QtGui.QApplication.UnicodeUTF8))
        self.restingPotentialCheck.setText(QtGui.QApplication.translate("Form", "Rest Potential", None, QtGui.QApplication.UnicodeUTF8))
        self.restingPotentialLabel.setText(QtGui.QApplication.translate("Form", "0", None, QtGui.QApplication.UnicodeUTF8))
        self.restingCurrentCheck.setText(QtGui.QApplication.translate("Form", "Rest Current", None, QtGui.QApplication.UnicodeUTF8))
        self.restingCurrentLabel.setText(QtGui.QApplication.translate("Form", "0", None, QtGui.QApplication.UnicodeUTF8))
        self.capacitanceCheck.setText(QtGui.QApplication.translate("Form", "Capacitance", None, QtGui.QApplication.UnicodeUTF8))
        self.capacitanceLabel.setText(QtGui.QApplication.translate("Form", "0", None, QtGui.QApplication.UnicodeUTF8))
        self.fitErrorCheck.setText(QtGui.QApplication.translate("Form", "Fit Error", None, QtGui.QApplication.UnicodeUTF8))
        self.fitErrorLabel.setText(QtGui.QApplication.translate("Form", "0", None, QtGui.QApplication.UnicodeUTF8))

from lib.util.SpinBox import SpinBox
from lib.util.pyqtgraph.PlotWidget import PlotWidget

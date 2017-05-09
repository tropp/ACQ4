from PyQt4 import QtCore, QtGui
from acq4.devices.Device import TaskGui

class TDTTaskGui(TaskGui):
    
    def __init__(self, dev, taskRunner):
        TaskGui.__init__(self, dev, taskRunner)
        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)
        self.attenSpin = QtGui.QSpinBox()
        self.attenSpin.setMaximum(120)
        self.attenSpin.setMinimum(0)
        self.attenSpin.setStep(0.5)
        self.layout.addWidget(self.attenSpin)

    def generateTask(self):
        return {'PA5.attenuation': self.attenSpin.value()}
# -*- coding: utf-8 -*-
from acq4.util.debug import *
from tdt import *    
from acq4.devices.Device import *
import time, traceback, sys
#from taskGUI import *
#from numpy import byte
import numpy as np
#from scipy.signal import resample, bessel, lfilter
import scipy.signal, scipy.ndimage
import acq4.util.advancedTypes as advancedTypes
from acq4.util.debug import *
import acq4.util.Mutex as Mutex
from acq4.pyqtgraph import ptime
from win32com.client import Dispatch

class TDTDevice(Device):
    """
    Config options:
        defaultAIMode: 'mode'  # mode to use for ai channels by default ('rse', 'nrse', or 'diff')
    """
    def __init__(self, dm, config, name):
        Device.__init__(self, dm, config, name)
        self.config = config
        ## make local copy of device handle
    	print "TDT activated!"
        
    def createTask(self, cmd, parentTask):
        return TDTTask(self, cmd, parentTask)
        
class TDTTask(DeviceTask):
    def __init__(self, dev, cmd, parentTask):
        DeviceTask.__init__(self, dev, cmd, parentTask)
        self.lastPulseTime = None

    def configure(self):
        self.circuit = DSPCircuit('C:\Users\Experimenters\Desktop\ABR_Code\FreqStaircase3.rcx', 'RP2')
        assert self.circuit.is_connected

        #Set relevant timing values
        tdur = 50
        tipi = 200
        nreps = 1

        fmin=0.1
        fstep=0.25
        fmax = fstep*10
        flist=np.arange(fmin,fmax,fstep)
        if flist[9]<fmax:
            flist=np.append(flist,fmax)
        freqs=1000*2**flist
        

        npip=len(freqs)
        print('npip = ', npip)
        schtime=npip*(tdur + tipi)
        print('schtime = ', schtime)
        cyctime=schtime + (tdur+tipi)*npip
        print('cyctime = ', cyctime)

        print(freqs)
        #direction=input('please enter "up" or "down":')
        #Set the tag values
        #If ascending tone pips:  Set Basefreq to fmin, Stepsize to fstep and Maxfreq to fmax
        #If descending tone pips:  Set Basefreq to fmax, Stepsize to -fstep and MaxFreq to fmin
        direction = 'down'
        if direction=='up':
            self.circuit.set_tag('BaseFreq', fmin)
            self.circuit.set_tag('StepSize', fstep)
            self.circuit.set_tag('MaxFreq', fmax)
        elif direction=='down':
            self.circuit.set_tag('BaseFreq', fmax)
            self.circuit.set_tag('StepSize', -1*fstep)
            self.circuit.set_tag('MaxFreq', fmax)
        else:
            DSPError()
        
    #   circuit.set_tag('SchmittTime', schtime)
        self.circuit.set_tag('PipDuration', tdur)
    #circuit.set_tag('InterPipTime', tipi)
        self.circuit.set_tag('NPip', npip)
    #   circuit.set_tag('Reps', nreps)
    #   circuit.set_tag('CycleTime',cyctime)

        self.amplifier = Dispatch('PA5.x')
        self.amplifier.ConnectPA5('USB',1)
        self.amplifier.SetAtten(50)

    def start(self):
        self.circuit.start()

        self.circuit.trigger(1,mode='pulse')
        self.starttime = ptime.time()


    def isDone(self):
        if self.lastPulseTime is None:
            pulseread = self.circuit.get_tag('Pulses')
            print(pulseread)
            if pulseread == 1:
                self.lastPulseTime = ptime.time()
            return False
        else:
            return ptime.time() > self.lastPulseTime + 0.1

    def stop(self, abort=False):
        self.circuit.stop()
        self.amplifier.SetAtten(120)

        # elapsed=0
        # PC=0
        # while elapsed<(cyctime*nreps)/1000.0 and PC<=freqs[-1]:
        #     PC=circuit.get_tag('freqout')
        #     elapsed=time.time()-starttime
        #     Pulseread=circuit.get_tag('Pulses')
        #     if Pulseread==1:
        #         #print(Pulseread)
        #         #print(PC)
        #         time.sleep(0.1)
        #         circuit.stop()
        #         amplifier.SetAtten(120)
        #         break
                # print(elapsed)

        # for i in range(5):
        #   PC=circuit.get_tag('freqout')
        #   print(PC)
        #   time.sleep(1)
        # #time.sleep(5)
    #   circuit.stop()
    
        ## get DAQ device
        #daq = self.devm.getDevice(...)
        

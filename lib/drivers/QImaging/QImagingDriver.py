print __file__

import ptime
from ctypes import *
import sys, os
d = os.path.dirname(__file__)
sys.path.append(os.path.join(d, '../../util'))
from clibrary import *
from numpy import empty, uint16, ascontiguousarray, concatenate, newaxis
from pyqtgraph import graphicsWindows as gw
from PyQt4 import QtGui
from Mutex import Mutex, MutexLocker
from advancedTypes import OrderedDict
import atexit
import traceback
modDir = os.path.dirname(__file__)
sdkDir = r"C:\Program Files\QImaging\SDK\Headers"

## check for installed SDK, fall back to local header copies
if os.path.isdir(sdkDir):
    headerDir = sdkDir
else:
    headerDir = modDir
print headerDir
p = CParser(os.path.join(headerDir, "QCamApi.h"), cache=os.path.join(modDir, 'QCamApi.h.cache'), macros={'_WIN32': '', '__int64': ('long long')})

if sys.platform == 'darwin':
    dll = cdll.LoadLibrary('/Library/Frameworks/QCam.framework/QCam')
else:
    dll = windll.QCamDriver
lib = CLibrary(dll, p, prefix = 'QCam_')        #makes it so that functions in the header file can be accessed using lib.nameoffunction, ie: QCam_LoadDriver is lib.LoadDriver
                                                #also interprets all the typedefs for you....very handy
                                                #anything from the header needs to be accessed through lib.yourFunctionOrParamete


#modDir = os.path.dirname(__file__)
#headerFiles = [
#    #"C:\Program Files\Photometrics\PVCam32\SDK\inc\master.h",
#    #"C:\Program Files\Photometrics\PVCam32\SDK\inc\pvcam.h"
#    os.path.join(modDir, "QCamApi.h")
#    #os.path.join(modDir, "pvcam.h")
#]
#HEADERS = CParser(headerFiles, cache=os.path.join(modDir, 'pvcam_headers.cache'), copyFrom=winDefs())
#LIB = CLibrary(windll.Pvcam32, HEADERS, prefix='pl_')
#

###functions that are called from CameraDevice:
# setUpCamera(self) - """Prepare the camera at least so that get/setParams will function correctly"""
# listParams(self, params=None)
# setParams(self, params, autoRestart=True, autoCorrect=True)
# getParams(self, params=None)
# quit(self)

externalParams = ['triggerMode',
                  #'triggerType', ## Add this in when we figure out TriggerModes
                  'exposure',
                  #'exposureMode',
                  'binning',
                  #'binningX',
                  #'binningY',
                  'regionX',
                  'regionY',
                  'regionW',
                  'regionH',
                  'gain',
                  'qprmS32AbsoluteOffset',
                  'qprmReadoutSpeed',
                  'qprmCoolerActive',
                  'qprmS32RegulatedCoolingTemp',
                  'qprmBlackoutMode',
                  #'qprmImageFormat',
                  'qprmSyncb',
                  'ringSize'
                  ]
cameraDefaults = {
    'ALL':{
        'qprmImageFormat':'qfmtMono16',
    }}

#def init():
#    ## System-specific code
#    global QCam
#    QCam = _QCamDriverClass()
        
class QCamFunctionError(Exception):
    def __init__(self, value, message):
        self.value = value
        self.message = message
    #def _message(self, message)
    
    def __str__(self):
        return repr(self.message)

class QCamDriverClass:
    def __init__(self):
        self.cams = {}
        self.paramTable = OrderedDict()
        
        self.loadDriver()
        
        
        global externalParams
        for p in externalParams:
            self.paramTable[p] = p        
    
    def call(self, function, *args):
        a = function(*args)
        #print "Call Result for %s: a()=%i" %(function.name, a())
        if a() == None:
            return a
        elif a() != 0:
            for x in lib('enums', 'QCam_Err'):
                if lib('enums', 'QCam_Err')[x] == a():
                    raise QCamFunctionError(a(), "There was an error running %s. Error code = %s" %(function.name,x))
        else:
            return a

    def loadDriver(self):
        self.call(lib.LoadDriver)
 
    #def releaseDriver(self):
    #    self.call(lib.ReleaseDriver)
        
    def listCameras(self):
        number = c_ulong(10)
        L = lib.CamListItem * 10
        l = L()
        self.call(lib.ListCameras, l, number)
        cams = []
        for x in list(l)[:number.value]:
            cams.append(x.cameraId)
        return cams
    
    def getCamera(self, cam):
        #print "QIdriver: getting camera...."
        if not self.cams.has_key(cam):
            #print "    creating camera class..."
            self.cams[cam] = QCameraClass(cam, self)
            #print "    camera class created for cam: %s" %cam
        return self.cams[cam]
        
    def __del__(self):
        if len(self.cams) != 0:
            self.quit()
        else:
            self.call(lib.ReleaseDriver)

    def quit(self):
        #print "quit() called from QCamDriverClass."
        for c in self.cams:
            self.cams[c].quit()
        self.call(lib.ReleaseDriver) ###what if we don't open the camera?

        
class QCameraClass:
    def __init__(self, name, driver):
        #print "QCamera Class: setting self variables..."
        self.name = name
        self.driver = driver
        self.isOpen = False
        self.handle = self.open()
        self.ringSize = 10
        self.paramAttrs = OrderedDict()
        self.cameraInfo = {}
        self.frames = []
        self.arrays = []
        self.frameTimes = []
        self.i = 0
        self.stopSignal = True
        self.mutex = Mutex(Mutex.Recursive)
        self.lastImage = (None,0)
        self.fnp1 = lib.AsyncCallback(self.callBack1)
        self.fnpNull = lib.AsyncCallback(self.doNothing)
        self.counter = 0
        
        
        ## Some parameters can be accessed as groups
        self.groupParams = {
            #'binning':['binningX', 'binningY']
            'region': ['regionX', 'regionY', 'regionW', 'regionH'],
            'sensorSize': ['qinfCcdWidth', 'qinfCcdHeight'] 
        }

        self.paramEnums = {
            'qprmImageFormat': 'QCam_ImageFormat',
            #'qprmPostProcessImageFormat': 'QCam_ImageFormat',
            'qprmSyncb': 'QCam_qcSyncb',
            'qprmReadoutSpeed': 'QCam_qcReadoutSpeed',
            #'qprmColorWheel': 'QCam_qcWheelColor',
            'qprmTriggerType': 'QCam_qcTriggerType'
        }
        
        self.userToCameraDict = {
            'triggerMode':'qprmTriggerType',
            'exposure':'qprm64Exposure',
            'binning':'qprmBinning',
            'binningX':'qprmBinning',
            'binningY':'qprmBinning',
            'regionX':'qprmRoiX',
            'regionY':'qprmRoiY',
            'regionW':'qprmRoiWidth',
            'regionH':'qprmRoiHeight',
            'gain':'qprmNormalizedGain',
            'Normal':'qcTriggerFreerun',
            'Strobe':'qcTriggerEdgeHi',
            'Bulb':'qcTriggerPulseHi',
            'bitDepth':'qinfBitDepth'
        }
        
        self.cameraToUserDict = {
            'qprmTriggerType':'triggerMode',
            'qprm64Exposure':'exposure',
            'qprmBinning':'binning',
            'qprmRoiX':'regionX',
            'qprmRoiY':'regionY',
            'qprmRoiWidth':'regionW',
            'qprmRoiHeight':'regionH',
            'qprmNormalizedGain':'gain',
            'qcTriggerFreerun':'Normal',
            #'qcTriggerNone':'Normal',
            'qcTriggerEdgeHi':'Strobe',
            'qcTriggerPulseHi':'Bulb',
            'qinfBitDepth':'bitDepth'
        }
        self.unitConversionDict = {
            'gain': 1e-6,     #QCam expects microunits
            'exposure': 1e-9  #QCam expresses exposure in nanoseconds
            }
        #print "      variables set. About to run listParams()"
        
        self.listParams()
        #print "      listParams returned."
        self.getCameraInfo()
        #print "      getCameraInfo returned. About to set defaults settings..."
        for x in cameraDefaults['ALL'].keys():
            self.setParams([(x, cameraDefaults['ALL'][x])]) #### FIX this so that you aren't sending settings to cam the entire time!
        #print "      returned from setting default params."
            
       
        
    def call(self, function, *args):
        a = function(*args)
        if a() != 0:
            for x in lib('enums', 'QCam_Err'):
                if lib('enums', 'QCam_Err')[x] == a():
                    raise QCamFunctionError(a(), "There was an error running %s. Error code = %s" %(function.name, x))
        else:
            return a

    def open(self): #opens the camera and returns the handle
        """Opens the chosen camera and returns the handle. Takes cameraID parameter."""
        if not self.isOpen: 
            a = self.call(lib.OpenCamera, self.name, lib.Handle())
            self.isOpen = True
            #self.call(lib.SetStreaming, a[1], 1)
            return a[1]   
  
    def __del__(self):
        self.quit()
    
    def quit(self):
        #print "quit() called from QCamCameraClass. self.isOpen: ", self.isOpen
        if not self.isOpen:
            return
        self.call(lib.Abort, self.handle)
        self.call(lib.SetStreaming, self.handle, 0)
        self.call(lib.CloseCamera, self.handle)
        
    def translateToCamera(self, arg):
        return self.userToCameraDict.get(arg, arg)
            
    def translateToUser(self, arg):
        return self.cameraToUserDict.get(arg, arg)
    
    def convertUnitsToCamera(self, param, value):
        if param in self.unitConversionDict:
            if type(value) in [int, float]:
                return value/self.unitConversionDict[param]
            elif type(value) == list:
                for i in range(len(value)):
                    value[i] = value[i]/self.unitConversionDict[param]
                return value
            elif type(value) == tuple:
                return (value[0]/self.unitConversionDict[param], value[1]/self.unitConversionDict[param])
        else: return value
        
    def convertUnitsToAcq4(self, param, value):
        if param in self.unitConversionDict:
            #print "        0 convertUnits: param:", param, "value:", value
            if type(value) in [type(1),type(1.0),type(1L)]:
                #print "        1 convertUnits: param:", param, "value:", value*self.unitConversionDict[param]
                return value*self.unitConversionDict[param]
            elif type(value) == list:
                for i in range(len(value)):
                    value[i] = value[i]*self.unitConversionDict[param]
                #print "        2 convertUnits: param:", param, "value:", value
                return value
            elif type(value) == tuple:
                #print "        3 convertUnits: param:", param, "value:", (value[0]*self.unitConversionDict[param], value[1]*self.unitConversionDict[param])
                return (value[0]*self.unitConversionDict[param], value[1]*self.unitConversionDict[param])  
            else:
                print "qcam.convertUnitsToAcq4 does not know how to convert value of type ", type(value)
        else: 
            #print "%s not in unitConversionDict." %param, "Value = ", value
            return value
    
        
    def readSettings(self):
        s = self.call(lib.ReadSettingsFromCam, self.handle)[1]
        s.size = sizeof(s)
        return s


    
    def listParams(self, param=None, allParams=False):
        if param == None:
            return self.fillParamDict(allParams=allParams)
        else:
            if param in ['binningX', 'binningY']:
                param = 'binning'
            return self.paramAttrs[param]

    def fillParamDict(self, allParams=False):
        """Fills in the 'paramAttrs' dictionary with the state parameters available on the camera.
        The key is the name of the parameter, while the value is a list: [acceptablevalues, isWritable, isReadable, [dependencies]]."""
        #print "QID: fillParamDict() called."
        s = self.readSettings()
        #print "      settings structure read."
        if allParams:
            p = []
            for x in lib('enums', 'QCam_Param').keys():
                p.append(x)
            for x in lib('enums', 'QCam_ParamS32').keys():
                p.append(x)
            for x in lib('enums', 'QCam_Param64').keys():
                p.append(x)
        else:
            p = externalParams
        #for x in lib('enums', 'QCam_Param'):
        for x in p:
            if x == 'ringSize':
                self.paramAttrs[x] = [(2,100), True, True, []]
                continue
            x = self.translateToCamera(x)
            if x not in ['qprmS32AbsoluteOffset', 'qprmS32RegulatedCoolingTemp', 'qprm64Exposure']:
                try:
                    if self.call(lib.GetParam, byref(s), getattr(lib, x))() == 0:
                        try: ###first try to get a SparseTable
                            table = (c_ulong *32)()
                            r = self.call(lib.GetParamSparseTable, byref(s), getattr(lib,x), table, c_long(32))
                            self.paramAttrs[self.translateToUser(x)] = [list(r[2])[:r[3]], True, True, []]
                        except QCamFunctionError, err: ###if sparse table doesn't work try getting a RangeTable
                            if err.value == 1:  
                                min = self.call(lib.GetParamMin, byref(s), getattr(lib,x))[2]
                                max = self.call(lib.GetParamMax, byref(s), getattr(lib,x))[2]
                                self.paramAttrs[self.translateToUser(x)] = [(min, max), True, True, []]
                            else: raise      
                except QCamFunctionError, err:
                    if err.value == 1: pass    
                    else: raise
        #for x in lib('enums', 'QCam_ParamS32'):
            elif x not in ['qprm64Exposure']:
                try:
                    if self.call(lib.GetParamS32, byref(s), getattr(lib, x))() == 0:
                        try:
                            table = (c_long *32)()
                            r = self.call(lib.GetParamSparseTableS32, byref(s), getattr(lib,x), table, c_long(32))
                            self.paramAttrs[self.translateToUser(x)] = [list(r[2])[:r[3]], True, True, []]
                        except QCamFunctionError, err:
                            if err.value == 1:
                                min = self.call(lib.GetParamS32Min, byref(s), getattr(lib,x))[2]
                                max = self.call(lib.GetParamS32Max, byref(s), getattr(lib,x))[2]
                                self.paramAttrs[self.translateToUser(x)] = [(min, max), True, True, []]
                            else: raise
                except QCamFunctionError, err:
                    if err.value == 1: pass
                    else: raise
        #for x in lib('enums', 'QCam_Param64'):
            elif x not in ['qprmS32AbsoluteOffset', 'qprmS32RegulatedCoolingTemp']:
                try:
                    if self.call(lib.GetParam64, byref(s), getattr(lib, x))() == 0:
                        try:
                            table = (c_ulonglong *32)()
                            r = self.call(lib.GetParamSparseTable64, byref(s), getattr(lib,x), table, c_long(32))
                            self.paramAttrs[self.translateToUser(x)] = [list(r[2])[:r[3]], True, True, []]
                        except QCamFunctionError, err:
                            if err.value == 1:
                                min = self.call(lib.GetParam64Min, byref(s), getattr(lib,x))[2]
                                max = self.call(lib.GetParam64Max, byref(s), getattr(lib,x))[2]
                                self.paramAttrs[self.translateToUser(x)] = [(min, max), True, True, []]
                            else: raise
                except QCamFunctionError, err:
                    if err.value == 1:  pass
                    else: raise
        #print "      parameters are retrieved."
        #self.paramAttrs.pop('qprmExposure')
        #self.paramAttrs.pop('qprmOffset')
        ### Replace qcam enum numbers with qcam strings
        #for x in self.paramAttrs: 
        #    if type(self.paramAttrs[x]) == type([]):
        #        if x in self.paramEnums: ## x is the name of the parameter
        #            #print "Param: ", x, self.paramAttrs[x]
        #            for i in range(len(self.paramAttrs[x])): ## i is the index
        #                a = self.paramAttrs[x][i] ## a is the value
        #                for b in lib('enums', self.paramEnums[x]): # b is the name of the parameter option
        #                    if lib('enums', self.paramEnums[x])[b] == a:
        #                        self.paramAttrs[x][i] = self.translateToUser(b)
        for x in self.paramAttrs:
            if type(self.paramAttrs[x][0]) != tuple:
                self.paramAttrs[x][0] = self.getNameFromEnum(x, self.paramAttrs[x][0])
            else:
                self.paramAttrs[x][0] = self.convertUnitsToAcq4(x, self.paramAttrs[x][0])
                
        ## rearrange trigger names
        trigNames = ['Normal', 'Strobe', 'Bulb']
        for n in self.paramAttrs['triggerMode'][0]:
            if n not in trigNames:
                trigNames.append(n)
        self.paramAttrs['triggerMode'][0] = trigNames
                
        
        
        return self.paramAttrs
                                
    def getNameFromEnum(self, enum, value):
        enum = self.translateToCamera(enum)
        if enum in self.paramEnums:
            if isinstance(value, list):
                values = []
                for j in value:
                    for i in lib('enums', self.paramEnums[enum]):
                        if lib('enums', self.paramEnums[enum])[i] == j:
                            values.append(self.translateToUser(i))
                return values
            else:
                for i in lib('enums', self.paramEnums[enum]):
                    if lib('enums', self.paramEnums[enum])[i] == value:
                        return self.translateToUser(i)
        else:
            return value
    
    def getEnumFromName(self, enum, value):
        enum = self.translateToCamera(enum)
        return lib('enums', self.paramEnums[enum])[value]
            
                                #print "old: ", a, "new: ", self.paramAttrs[x][i]
        ##### For camera on rig1, listParams returns: {                       
        ##    'qprmBlackoutMode': [0L, 1L],
        ##    'qprmBinning': [1L, 2L, 4L, 8L],
        ##          'qprmExposureRed': (10L, 1073741823L),
        ##    'qprm64Exposure': (10000L, 1073741823000L),
        ##          'qprmPostProcessBayerAlgorithm': [1L, 2L, 3L, 4L],
        ##    'qprmImageFormat': ['qfmtRaw8', 'qfmtRaw16', 'qfmtMono8', 'qfmtMono16', 'qfmtRgbPlane8', 'qfmtRgbPlane16', 'qfmtBgr24', 'qfmtXrgb32', 'qfmtRgb48', 'qfmtBgrx32', 'qfmtRgb24'],
        ##    'qprmCoolerActive': [0L, 1L], # 0=disable cooler
        ##    'qprmRoiHeight': (1L, 1200L),
        ##          'qprmColorWheel': ['qcWheelRed', 'qcWheelGreen', 'qcWheelBlue'], #color of the RGB filter
        ##          'qprm64ExposureRed': (10000L,1073741823000L),
        ##    'qprmRoiX': (0L, 1599L),
        ##    'qprmRoiY': (0L, 1199L),
        ##    'qprmS32NormalizedGaindB': (-6930000, 26660000),
        ##          'qprmPostProcessGainBlue': (10L, 100000L),
        ##    'qprmTriggerType': ['qcTriggerNone', 'qcTriggerEdgeHi', 'qcTriggerEdgeLow', 'qcTriggerPulseHi', 'qcTriggerPulseLow', 'qcTriggerSoftware', 'qcTriggerStrobeHi', 'qcTriggerStrobeLow'],
        ##          'qprmPostProcessImageFormat': ['qfmtRaw8', 'qfmtRaw16','qfmtMono8', 'qfmtMono16', 'qfmtRgbPlane8', 'qfmtRgbPlane16', 'qfmtBgr24', 'qfmtXrgb32', 'qfmtRgb48', 'qfmtBgrx32', 'qfmtRgb24'],
        ##          'qprm64ExposureBlue': (10000L, 1073741823000L),
        ##          'qprmExposureBlue': (10L, 1073741823L),
        ##    'qprmSyncb': ['qcSyncbOem1', 'qcSyncbExpose'],
        ##    'qprmRoiWidth': (1L, 1600L),
        ##          'qprmPostProcessGainRed': (10L, 100000L),
        ##          'qprmGain': (0L, 4095L), #DEPRECATED
        ##    'qprmS32RegulatedCoolingTemp': (-45, 0),
        ##    'qprmS32AbsoluteOffset': (-2048, 2047),
        ##    'qprmNormalizedGain': (451000L, 21500000L),#default is 1
        ##          'qprmPostProcessGainGreen': (10L, 100000L),
        ##    'qprmReadoutSpeed': ['qcReadout20M', 'qcReadout10M', 'qcReadout5M']}
        

        
                                
    def getCameraInfo(self):
        for x in lib('enums', 'QCam_Info'):
            try:
                a = self.call(lib.GetInfo, self.handle, getattr(lib, x))
                self.cameraInfo[x] = a[2]
            except QCamFunctionError, err:
                if err.value == 1:
                    #print "No info for: ", x
                    pass
                else: raise
    
    def getImageSize(self):
        size = self.call(lib.GetInfo, self.handle, lib.qinfImageSize)[2]
        self.cameraInfo['qinfImageSize'] = size
        #print "Image Size: ", size
        return size

    def getParam(self, param):
        if param == 'ringSize':
            return self.ringSize
        if param in self.groupParams:
            return self.getParams(self.groupParams[param], asList=True)
        s = self.readSettings()
        #s.size = sizeof(s)
        #print "   0 getParam.param:", param
        param = self.translateToCamera(param)
        #print "   1 getParam.param:", param
        if param in lib('enums', 'QCam_Param'):
            value = self.call(lib.GetParam, byref(s), getattr(lib, param))[2]
        elif param in lib('enums', 'QCam_ParamS32'):
            value = self.call(lib.GetParamS32, byref(s), getattr(lib, param))[2]
        elif param in lib('enums', 'QCam_Param64'):
            value = self.call(lib.GetParam64, byref(s), getattr(lib, param))[2]
        elif param in self.cameraInfo:
            value = self.cameraInfo[param]
        else:
            raise Exception("%s is not recognized as a parameter." %param)
        #print "   2 getParam.param:", param, "value:", value
        if param in ['qprmRoiX', 'qprmRoiY', 'qprmRoiWidth', 'qprmRoiHeight']:
            #print param, value, '===>', value*self.getParam('binning')[0] 
            value = value*self.getParam('binning')[0]
        #print "   3 getParam.param:", param, "value:", value
        value = self.getNameFromEnum(param, value)
        #print "   4 getParam.param:", param, "value:", value
        value = self.convertUnitsToAcq4(self.translateToUser(param), value)
        #print "   5 getParam.param:", param, "value:", value
        if param != 'qprmBinning':
            return value
        elif param == 'qprmBinning':
            return (value,value)

    #def setParam(self, param, value, autoRestart=True, autoCorrect=True):
        #if param == 'ringSize':
            #self.ringSize = value
        #if param in self.groupParams:
            #return self.setParams(zip(self.groupParams[param], value))
        #s = self.readSettings()
        #param = self.translateToCamera(param)
        #value = self.translateToCamera(value)
        #if param in self.paramEnums:
            #value = self.getEnumFromName(param, value)
        #if param in lib('enums', 'QCam_Param'):
            #self.call(lib.SetParam, byref(s), getattr(lib, param), c_ulong(value))
        #elif param in lib('enums', 'QCam_ParamS32'):
            #self.call(lib.SetParamS32, byref(s), getattr(lib, param), c_long(value))
        #elif param in lib('enums', 'QCam_Param64'):
            #self.call(lib.SetParam64, byref(s), getattr(lib, param), c_ulonglong(value))
        #with self.mutex:
            #if self.stopSignal == True:
                ##self.mutex.unlock()
                #self.call(lib.SendSettingsToCam, self.handle, byref(s))
            #if self.stopSignal == False:
                ##self.mutex.unlock()
                #self.call(lib.QueueSettings, self.handle, byref(s), null, lib.qcCallbackDone)
        #print "Set param:", param, value
        


    
    def getParams(self, params, asList=False):
        """Get a list of parameter values. Return a dictionary of name: value pairs"""
        if asList:
            return [self.getParam(p) for p in params]
        else:
            return OrderedDict([(p, self.getParam(p)) for p in params])

    def setParams(self, params, autoRestart=True, autoCorrect=True): 
        """Set camera parameters. Options are:
           params: a list of (param, value) pairs to be set. Parameters are set in the order specified.
           autoRestart: If true, restart the camera if required to enact the parameter changes
           autoCorrect: If true, correct values that are out of range to their nearest acceptable value
        
        Return a tuple with: 
           0: dictionary of parameters and the values that were set.
              (note this may differ from requested values if autoCorrect is True)
           1: Boolean value indicating whether a restart is required to enact changes.
              If autoRestart is True, this value indicates whether the camera was restarted."""
        
        #traceback.print_stack()
        ## Convert params to a dictionary:
        if not isinstance(params, type({})):
            params = OrderedDict(params)
            #dict = {}
            #for t in params:
                #dict[t[0]] = t[1]
            #params = dict
        #print "Params to set:", params
        
        s = self.readSettings()
        
        ### Unpack grouped params
        for x in params.keys():
            if x in self.groupParams:
                tuples = zip(self.groupParams[x], params[x])
                #newDict = {}
                for y in tuples:
                    params[y[0]]= y[1]
                del params[x]
                #return self.setParams(newDict)
            
        #changeTuple = {}
        for x in params:
            #print "0 x:", x
            #changeTuple[x] = False
            if x == 'ringSize':
                self.ringSize = params[x]
                value = params[x]
                continue
            if x == 'qprmImageFormat':
                if params[x] != 'qfmtMono16':
                    print "QCam driver currently only supports the 'qfmtMono16' image format."
                    continue
                
            param = self.translateToCamera(x)
            #print "     1 param:", param
            value = params[x]
            #print "     2 value:", value
            
            
            #### sometimes camera code sends in tuples (ie. for binning)
            if type(value) == tuple and value[0]==value[1]:
                #changeTuple[x] = True
                value = value[0]
            #print "     3 value:", value
            
            ### Check that value is allowable:
            if autoCorrect:
                if x in self.paramAttrs.keys():
                    allowableValues = self.paramAttrs[x][0]
                    if type(allowableValues) == tuple:
                        if value < min(allowableValues):
                            value = min(allowableValues)
                        elif value > max(allowableValues):
                            value = max(allowableValues)
                    elif type(allowableValues) == list:
                        if value not in allowableValues:
                            print "%s not an allowable value for QImaging camera. Allowable values are %s" %(value, allowableValues)
            #print "     4 value:", value
            
            
            value = self.convertUnitsToCamera(x, value)
            #print "     5 value:", value
            value = self.translateToCamera(value)
            #print "     6 value:", value
            
            if param in self.paramEnums:
                value = self.getEnumFromName(param, value)
            #print "     7 value:", value
            
            #### Reset region if binning is changed
            if param == 'qprmBinning':
                x = self.getParam('qprmRoiX')
                y = self.getParam('qprmRoiY')
                w = self.getParam('qprmRoiWidth')
                h = self.getParam('qprmRoiHeight')
                #oldBinning = self.getParam('binning')[0]
                self.call(lib.SetParam, byref(s), getattr(lib, 'qprmRoiX'), c_ulong(int(x/value)))
                self.call(lib.SetParam, byref(s), getattr(lib, 'qprmRoiY'), c_ulong(int(y/value)))
                self.call(lib.SetParam, byref(s), getattr(lib, 'qprmRoiWidth'), c_ulong(int(w/value)))
                self.call(lib.SetParam, byref(s), getattr(lib, 'qprmRoiHeight'), c_ulong(int(h/value)))
                
                
            if param in ['qprmRoiX', 'qprmRoiY', 'qprmRoiWidth', 'qprmRoiHeight']:
                value = value/self.getParam('binning')[0]
                
            if param in lib('enums', 'QCam_Param'):
                self.call(lib.SetParam, byref(s), getattr(lib, param), c_ulong(int(value)))
            elif param in lib('enums', 'QCam_ParamS32'):
                self.call(lib.SetParamS32, byref(s), getattr(lib, param), c_long(int(value)))
            elif param in lib('enums', 'QCam_Param64'):
                self.call(lib.SetParam64, byref(s), getattr(lib, param), c_ulonglong(int(value)))
        #self.queueSettingsDict = {}
        #for x in params:
            #self.queueSettingsDict[x] = value
        
        with self.mutex:
            #print "Mutex locked from qcam.setParams()"
            if self.stopSignal == True:
                #self.mutex.unlock()
                self.call(lib.SendSettingsToCam, self.handle, byref(s))

                restart = False
            elif self.stopSignal == False: ##### Can't figure out how to get QueueSettings to work....so we'll just stop and start the camera.
                #try:
                    #print "QCam about to Queue settings. params:", params
                    #s.size = sizeof(s)
                    ##self.mutex.unlock()
                    #var = c_void_p(0)
                    #self.call(lib.QueueSettings, self.handle, byref(s), self.fnpNull, lib.qcCallbackDone, var, 0)
                    #restart = False
                    #print "QCamSettings are queued. Look for message from callback..."
                #except QCamFunctionError:
                #self.stop()
                self.call(lib.SendSettingsToCam, self.handle, byref(s))
                #self.start()
                restart = True
                    

        #print "Mutex released from qcam.setParams()"
        dict = {}
        for x in params:
            dict[x] = self.getParam(x)
        self.getImageSize() ## Run this function to update image size in cameraInfo dictionary
        #print "Set params to:", dict
        #if not autoRestart:
            #autoRestart = restart
            
        return dict, restart
    
    def mkFrame(self):
        #s = self.call(lib.GetInfo, self.handle, lib.qinfImageWidth)[2] * self.call(lib.GetInfo, self.handle, lib.qinfImageHeight)[2]
        imForm = self.getParam('qprmImageFormat')
        #print 'mkFrame: s', s
        

        if imForm in ['qfmtMono16']:
            s = self.getImageSize() ## ImageSize returns the size in bytes
            frame = lib.Frame()
            array = ascontiguousarray(empty(s/2, dtype=uint16))
            #array = ascontiguousarray(empty(s, dtype=uint16))
            frame.bufferSize = s*2
        elif imForm not in ['qfmtMono16']:
            self.setParams([('qprmImageFormat','qfmtMono16')])
            s = self.getImageSize() ## ImageSize returns the size in bytes
            frame = lib.Frame()
            array = ascontiguousarray(empty(s/2, dtype=uint16))
            #array = ascontiguousarray(empty(s, dtype=uint16))
            frame.bufferSize = s*2

        #print "frameshape:", frame.shape
        #print 'size:', s, "height:", self.getParam('regionH'), 'width:', self.getParam('regionW'), 'binning:', self.getParam('binning')[0]
        #array.shape=(self.getParam('regionH'), self.getParam('regionW') )
        array.shape = (self.getParam('regionH')/self.getParam('binning')[0], -1)
        array = array.transpose()
        #print 'array.size', array.size, 'array.shape', array.shape
        frame.pBuffer = array.ctypes.data ###sets the frame buffer pointer to point to the array? So camera writes data directly into the array?
        #for x in array:
            #x = 1000
        #print 'mkFrame: frame.shape', frame.shape
        
        
        return (frame, array)
    
    def grabFrame(self):
        s = self.call(lib.GetInfo, self.handle, lib.qinfImageSize)[2]
        #s = lib.GetInfo(handle, lib.qinfImageSize)[2]
        (f, a) = mkFrame()
        self.call(lib.GrabFrame, self.handle, byref(f))
        #w = self.call(lib.GetInfo, self.handle, lib.qinfCcdWidth)[2]
        #frame.shape = (s/w, w)
        return a

    def start(self):

        #print "QCam.start() called."

        self.frames = []
        self.arrays = []
        self.lastImages = []
        self.frameTimes = [None]*self.ringSize
        #global i, stopsignal
        #self.mutex.lock()
        #self.stopSignal = False
        #self.i = 0
        #self.mutex.unlock()
        #self.setParams({'region':[0,0,self.cameraInfo['qinfCcdWidth'], self.cameraInfo['qinfCcdHeight']]})
        with self.mutex:
            #print "Mutex locked from qcam.start()"
            self.stopSignal = False
            self.i=0
        #print "Mutex released from qcam.start()"
        self.call(lib.SetStreaming, self.handle, 1)
        for x in range(self.ringSize):
            f, a = self.mkFrame()
            self.frames.append(f)
            #print "start: a.shape", a.shape
            self.arrays.append(a)
        #print "Camera started. Frame shape:", self.arrays[0].shape
        #print "Camera region:", self.getParam('region')
        for x in range(2):  ## need 2 frames queued to allow simultaneous exposure and frame transfer
            self.call(lib.QueueFrame, self.handle, self.frames[self.i], self.fnp1, lib.qcCallbackDone|lib.qcCallbackExposeDone, 0, self.i)
            self.mutex.lock()
            self.i += 1
            #self.counter +=1
            self.mutex.unlock()
        #for x in range(1):
        #self.call(lib.QueueFrame, self.handle, self.frames[self.i], self.fnp1, lib.qcCallbackDone, 0, self.i)
        ##self.mutex.lock()
        #with self.mutex:
            #self.i += 1
        #self.counter +=1
        #self.mutex.unlock()
        return self.arrays
    
    def callBack1(self, *args):
        #print "Callback1: args:", args
        if args[3] == lib.qcCallbackExposeDone:
            now = ptime.time()
            self.frameTimes[args[1]] = now
            #print "Exposure done. Time: %f, Duration: %f" %
            return
        if args[2] != 0:
            for x in lib('enums', 'QCam_Err'):
                if lib('enums', 'QCam_Err')[x] == args[2]:
                    raise QCamFunctionError(args[2], "There was an error during QueueFrame/Callback. Error code = %s" %(x))
        #self.mutex.lock()
        with self.mutex:
            #print "Mutex locked from qcam.callBack1()"
            #print "set last index", args[1]
            self.lastImages.append({'id':self.counter, 'data':self.arrays[args[1]].copy(), 'time': self.frameTimes[args[1]], 'exposeDoneTime':self.frameTimes[args[1]]})
            self.counter += 1
            
            if self.stopSignal == False:
                #self.mutex.unlock()
                #size = self.getImageSize()
                #if len(self.arrays[self.i]) != size/2:
                    #self.frames[self.i],self.arrays[self.i] = self.mkFrame()
                #### Need to check that frame is the right size given settings, and if not, make a new frame.
                self.call(lib.QueueFrame, self.handle, self.frames[self.i], self.fnp1, lib.qcCallbackDone|lib.qcCallbackExposeDone, 0, self.i)
                self.i = ( self.i+1) % self.ringSize
                #self.counter +=1
                #if self.i != self.ringSize-1:
                    #self.i += 1
                #else:
                    #self.i = 0
            #else:
            #    self.mutex.unlock()
        #print "Mutex released from qcam.callBack1()"
            
    def doNothing(self, *args):
        #dict = {}
        #for x in args[0]:
            #dict[x] = self.getParam(x)
        #print "Set params to:", dict
        print "Queued settings have been changed. (Message from queueSettings callback). Settings:", args

    def stop(self):

        #print "QCam.stop() called."

        #self.mutex.lock()
        with self.mutex:
            #print "Mutex locked from qcam.stop()"
            #print "stop() 1"
            self.stopSignal = True
            #print "stop() 2, self.stopSignal:", self.stopSignal
        a = self.call(lib.Abort, self.handle)
        #print "stop() 3", a()
        self.call(lib.SetStreaming, self.handle, 0)
        #self.mutex.unlock()

    def newFrames(self):
        with self.mutex:
            #print "Mutex locked from qcam.lastFrame()"
            a = self.lastImages
            self.lastImages = []
            #self.mutex.unlock()
        #print "Mutex released from qcam.lastFrame()"
        return a 
        
    
    
#loadDriver()
#cameras = listCameras()
#handle = openCamera(cameras[0])



#setParam(lib.qprmDoPostProcessing, 0)
#setParams(qprm64Exposure=10000000)
##setParams(qprmExposureRed=0, qprmExposureBlue=0)
#setParams(qprmReadoutSpeed=lib.qcReadout20M)
#
#setParams(qprmTriggerType=lib.qcTriggerFreerun, qprmImageFormat=lib.qfmtMono16)
#
#
#
#getCameraInfo()
#print camerainfo
#
#
#
#n = 0
#
#
#
#
#for i in range(5):
#    f, a = mkFrame()
#    frames.append(f)
#    arrays.append(a)
#    print "Queue frame..", id(f)
#    
#    print "Frame queued."
#   # time.sleep(0.3)

#time.sleep(1.0)
#print "starting app.."
#app = QtGui.QApplication([])
#print "app started."
#print a.shape, (camerainfo['qinfCcdWidth'], camerainfo['qinfCcdHeight'])
#a.shape = (camerainfo['qinfCcdHeight'], camerainfo['qinfCcdWidth'])
#print "create window"
#imw1 = gw.ImageWindow()
#imw1.setImage(a.transpose())
##imw1.setImage(concatenate([a.transpose()[newaxis] for a in arrays]))
#print "show window"
#imw1.show()
#
#print "Done."
#
#app.exec_()

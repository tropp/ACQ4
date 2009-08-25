# -*- coding: utf-8 -*-
from PyQt4 import Qwt5 as Qwt
from PyQt4 import QtCore, QtGui, QtSvg
from lib.util.MetaArray import MetaArray
from numpy import *
from scipy.fftpack import fft
from plotConfigTemplate import Ui_Form
from lib.util.WidgetGroup import WidgetGroup

class PlotWidget(Qwt.QwtPlot):
    def __init__(self, *args):
        Qwt.QwtPlot.__init__(self, *args)
        self.setMinimumHeight(50)
        self.setCanvasBackground(QtGui.QColor(0,0,0))
        self.setAxisFont(self.yLeft, QtGui.QFont("Arial", 7))
        self.setAxisFont(self.xBottom, QtGui.QFont("Arial", 7))
        #self.zoomer = Qwt.QwtPlotZoomer(
            #Qwt.QwtPlot.xBottom,
            #Qwt.QwtPlot.yLeft,
            #Qwt.QwtPicker.DragSelection,
            #Qwt.QwtPicker.AlwaysOff,
            #self.canvas())
        self.plotLayout().setCanvasMargin(0)
        #self.zoomer.setRubberBandPen(QtGui.QPen(QtGui.QColor(250, 250, 200)))
        
        self.grid = Qwt.QwtPlotGrid()
        self.grid.attach(self)
        self.grid.setMinPen(QtGui.QPen(QtGui.QColor(255, 255, 255, 10)))
        self.grid.setMajPen(QtGui.QPen(QtGui.QColor(255, 255, 255, 30)))
        #self.grid.enableXMin(True)
        #self.grid.enableYMin(True)
        
        self.curves = []
        self.paramIndex = {}
        self.avgCurves = {}
        
        self.range = [[0, 1000], [0, 1000]]
        
        ### Set up context menu
        
        w = QtGui.QWidget()
        self.ctrl = c = Ui_Form()
        c.setupUi(w)
        dv = QtGui.QDoubleValidator(self)
        self.ctrlMenu = QtGui.QMenu()
        ac = QtGui.QWidgetAction(self)
        ac.setDefaultWidget(w)
        self.ctrlMenu.addAction(ac)
        
        self.stateGroup = WidgetGroup(self.ctrlMenu)
        
        c.xMinText.setValidator(dv)
        c.yMinText.setValidator(dv)
        c.xMaxText.setValidator(dv)
        c.yMaxText.setValidator(dv)
        
        QtCore.QObject.connect(c.xMinText, QtCore.SIGNAL('editingFinished()'), self.updateManualXScale)
        QtCore.QObject.connect(c.xMaxText, QtCore.SIGNAL('editingFinished()'), self.updateManualXScale)
        QtCore.QObject.connect(c.yMinText, QtCore.SIGNAL('editingFinished()'), self.updateManualYScale)
        QtCore.QObject.connect(c.yMaxText, QtCore.SIGNAL('editingFinished()'), self.updateManualYScale)
        
        QtCore.QObject.connect(c.xManualRadio, QtCore.SIGNAL('toggled(bool)'), self.updateXScale)
        QtCore.QObject.connect(c.yManualRadio, QtCore.SIGNAL('toggled(bool)'), self.updateYScale)
        
        QtCore.QObject.connect(c.xAutoRadio, QtCore.SIGNAL('clicked()'), self.updateXScale)
        QtCore.QObject.connect(c.yAutoRadio, QtCore.SIGNAL('clicked()'), self.updateYScale)

        QtCore.QObject.connect(c.alphaGroup, QtCore.SIGNAL('toggled(bool)'), self.updateAlpha)
        QtCore.QObject.connect(c.alphaSlider, QtCore.SIGNAL('valueChanged(int)'), self.updateAlpha)
        QtCore.QObject.connect(c.autoAlphaCheck, QtCore.SIGNAL('toggled(bool)'), self.updateAlpha)

        QtCore.QObject.connect(c.powerSpectrumGroup, QtCore.SIGNAL('toggled(bool)'), self.updateSpectrumMode)
        
        self.replot()
      
    def widgetGroupInterface(self):
        return (None, PlotWidget.saveState, PlotWidget.restoreState)
      
    def updateSpectrumMode(self, b=None):
        if b is None:
            b = self.ctrl.powerSpectrumGroup.isChecked()
        curves = filter(lambda i: isinstance(i, Qwt.QwtPlotCurve), self.itemList())
        for c in curves:
            c.setSpectrumMode(b)
        self.replot()
            
      
    def updateDecimation(self):
        if self.ctrl.maxTracesCheck.isChecked():
            numCurves = self.ctrl.maxTracesSpin.value()
        else:
            numCurves = -1
            
        #curves = filter(lambda i: isinstance(i, Qwt.QwtPlotCurve), self.itemList())
        curves = self.curves[:]
        split = len(curves) - numCurves
        for i in range(len(curves)):
            if numCurves == -1 or i >= split:
                curves[i].show()
            else:
                if self.ctrl.forgetTracesCheck.isChecked():
                    curves[i].free()
                    self.detachCurve(curves[i])
                else:
                    curves[i].hide()
        
      
    def updateAlpha(self, *args):
        (alpha, auto) = self.alphaState()
        for item in self.itemList():
            if isinstance(item, PlotCurve):
                item.setAlpha(alpha, auto)
                
        self.replot(autoRange=False)
     
    def alphaState(self):
        enabled = self.ctrl.alphaGroup.isChecked()
        auto = self.ctrl.autoAlphaCheck.isChecked()
        alpha = float(self.ctrl.alphaSlider.value()) / self.ctrl.alphaSlider.maximum()
        if auto:
            alpha = 1.0  ## should be 1/number of overlapping plots
        if not enabled:
            auto = False
            alpha = 1.0
        return (alpha, auto)
        
        
    def updateXScale(self, b=False):
        if b:
            self.updateManualXScale()
        else:
            #self.setAxisAutoScale(Qwt.QwtPlot.xBottom)
            self.replot()
        
    def updateYScale(self, b=False):
        if b:
            self.updateManualYScale()
        else:
            #self.setAxisAutoScale(Qwt.QwtPlot.yLeft)
            self.replot()
        
        
    def updateManualXScale(self):
        x1 = float(self.ctrl.xMinText.text())
        x2 = float(self.ctrl.xMaxText.text())
        self.ctrl.xManualRadio.setChecked(True)
        self.setXRange(x1, x2)
        self.replot()
        
    def updateManualYScale(self):
        y1 = float(self.ctrl.yMinText.text())
        y2 = float(self.ctrl.yMaxText.text())
        self.ctrl.yManualRadio.setChecked(True)
        self.setYRange(y1, y2)
        self.replot()
        
    def plotRange(self):
        return self.range
        
    def screenScale(self):
        pr = self.plotRange()
        xd = pr[0][1] - pr[0][0]
        yd = pr[1][1] - pr[1][0]
        
        cs = self.canvas().size()
        return array([cs.width() / xd, cs.height() / yd])

    def map(self, pt):
        return array([self.invTransform(self.xBottom, pt[0]), self.invTransform(self.yLeft, pt[1])], dtype=float)
        

    def scaleBy(self, s, center=None):
        xr, yr = self.plotRange()
        if center is None:
            xc = (xr[1] + xr[0]) * 0.5
            yc = (yr[1] + yr[0]) * 0.5
        else:
            (xc, yc) = center
        
        x1 = xc + (xr[0]-xc) * s[0]
        x2 = xc + (xr[1]-xc) * s[0]
        y1 = yc + (yr[0]-yc) * s[1]
        y2 = yc + (yr[1]-yc) * s[1]
        
        self.setXRange(x1, x2)
        self.setYRange(y1, y2)
        self.replot(autoRange=False)
        
    def translateBy(self, t, screen=False):
        t = t.astype(float)
        if screen:  ## scale from pixels
            t /= self.screenScale()
        xr, yr = self.plotRange()
        #self.setAxisScale(self.xBottom, xr[0] + t[0], xr[1] + t[0])
        #self.setAxisScale(self.yLeft, yr[0] + t[1], yr[1] + t[1])
        self.setXRange(xr[0] + t[0], xr[1] + t[0])
        self.setYRange(yr[0] + t[1], yr[1] + t[1])
        self.replot(autoRange=False)
        
        
    def mouseMoveEvent(self, ev):
        pos = array([ev.pos().x(), ev.pos().y()])
        dif = pos - self.mousePos
        dif[0] *= -1
        self.mousePos = pos
        
        ## Ignore axes if mouse is disabled
        mask = array([1, 1])
        if not self.ctrl.xMouseCheck.isChecked():
            mask[0] = 0
        if not self.ctrl.yMouseCheck.isChecked():
            mask[1] = 0
        
        ## Scale or translate based on mouse button
        if ev.buttons() & QtCore.Qt.LeftButton:
            self.translateBy(dif * mask, screen=True)
        elif ev.buttons() & QtCore.Qt.RightButton:
            s = ((mask * 0.02) + 1) ** dif
            cPos = self.canvas().pos()
            cPos = array([cPos.x(), cPos.y()])
            self.scaleBy(s, self.map(self.pressPos - cPos))
            
        Qwt.QwtPlot.mouseMoveEvent(self, ev)
        
    def mousePressEvent(self, ev):
        self.mousePos = array([ev.pos().x(), ev.pos().y()])
        self.pressPos = self.mousePos.copy()
        Qwt.QwtPlot.mousePressEvent(self, ev)
        
    def mouseReleaseEvent(self, ev):
        pos = array([ev.pos().x(), ev.pos().y()])
        if sum(abs(self.pressPos - pos)) < 3:  ## Detect click
            if ev.button() == QtCore.Qt.RightButton:
                self.ctrlMenu.popup(self.mapToGlobal(ev.pos()))
        self.mousePos = pos
        Qwt.QwtPlot.mouseReleaseEvent(self, ev)
        
    def setYRange(self, min, max):
        self.setAxisScale(self.yLeft, min, max)
        self.range[1] = [min, max]
        self.ctrl.yMinText.setText('%g' % min)
        self.ctrl.yMaxText.setText('%g' % max)
        
    def setXRange(self, min, max):
        self.setAxisScale(self.xBottom, min, max)
        self.range[0] = [min, max]
        self.ctrl.xMinText.setText('%g' % min)
        self.ctrl.xMaxText.setText('%g' % max)

    def replot(self, autoRange=True):
        if autoRange:
            self.autoRange()
        Qwt.QwtPlot.replot(self)

    def autoRange(self):
        if self.ctrl.xAutoRadio.isChecked():
            #self.setAxisAutoScale(Qwt.QwtPlot.xBottom)
            #print "first:", self.plotRange()
            xMin = []
            xMax = []
            for i in self.itemList():
                if isinstance(i, Qwt.QwtPlotCurve):
                    xMin.append(i.minXValue())
                    xMax.append(i.maxXValue())
            if len(xMin) > 0:
                xMin = min(xMin)
                xMax = max(xMax)
                d = (xMax-xMin) * 0.05
                self.setXRange(xMin-d, xMax+d)
            #print "second:", self.plotRange()
        if self.ctrl.yAutoRadio.isChecked():
            #self.setAxisAutoScale(Qwt.QwtPlot.yLeft)
            yMin = []
            yMax = []
            for i in self.itemList():
                if isinstance(i, Qwt.QwtPlotCurve):
                    yMin.append(i.minYValue())
                    yMax.append(i.maxYValue())
            if len(yMin) > 0:
                yMin = min(yMin)
                yMax = max(yMax)
                d = (yMax-yMin) * 0.05
                self.setYRange(yMin-d, yMax+d)

    def setAxisTitle(self, axis, title):
        text = Qwt.QwtText(title)
        text.setFont(QtGui.QFont('Arial', 8))
        Qwt.QwtPlot.setAxisTitle(self, axis, text)
        
    def plot(self, data=None, x=None, clear=False, params=None, pen=None, replot=True):
        if clear:
            self.clear()
        
        if isinstance(data, MetaArray):
            curves = self._plotMetaArray(data)
        elif isinstance(data, ndarray):
            curves = self._plotArray(data, x=x)
        elif isinstance(data, list):
            if x is not None:
                x = array(x)
            curves = self._plotArray(array(data), x=x)
        elif data is None:
            curves = [PlotCurve()]
        else:
            raise Exception('Not sure how to plot object of type %s' % type(data))
            
        for c in curves:
            self.attachCurve(c)
            c.setParams(params)
            if pen is not None:
                c.setPen(pen)
            
            
        if replot:
            self.replot()
        
        #self.indexParams(params, ids)
        
        if data is not None and data.ndim == 2:
            return curves
        else:
            return curves[0]
        
    def attachCurve(self, c, params=None):
        self.curves.append(c)
        Qwt.QwtPlotCurve.attach(c, self)
        
        ## configure curve for this plot
        (alpha, auto) = self.alphaState()
        c.setAlpha(alpha, auto)
        c.setSpectrumMode(self.ctrl.powerSpectrumGroup.isChecked())
        
        ## Hide older plots if needed
        self.updateDecimation()
        
    def detachCurve(self, c):
        try:
            Qwt.QwtPlotCurve.detach(c)
        except:
            pass
        
        if c in self.curves:
            self.curves.remove(c)
        self.updateDecimation()
        
        
    def indexParams(self, params, ids):
        """Add IDs into the parameter index for params"""
        pass
    
    def _plotArray(self, arr, x=None):
        arr = atleast_2d(arr)
        if arr.ndim != 2:
            raise Exception("Array must be 1 or 2D to plot (shape is %s)" % arr.shape)
            
        if x is None:
            x = arange(arr.shape[1])
            
        x = atleast_2d(x)
        if x.ndim != 2:
            raise Exception("X array must be 1 or 2D to plot (shape is %s)" % x.shape)
            
        
        ret = []
        for i in range(arr.shape[0]):
            c = PlotCurve()
            c.setData(x[i%x.shape[0]], arr[i])
            #c.attach(self)
            ret.append(c)
            #self.curves.append(c)
                
        return ret
            
        
        
    def _plotMetaArray(self, arr):
        inf = arr.infoCopy()
        
        if arr.ndim == 1:
            xAxis = 0
            yAxis = 1
            
        elif arr.ndim == 2:
            for i in [0,1]:
                if 'cols' in inf[i]:
                    xAxis = 1-i
                    yAxis = i
        else:
            raise Exception('can only automatically plot 1 or 2 dimensional arrays.')
                    
        titles = ['', '']
        for i in [1,0]:
            t = ''
            if i >= len(inf):
                continue
            
            ## If there are columns, pick title/units from first column
            if 'cols' in inf[i]:
                s = inf[i]['cols'][0]
            else:
                s = inf[i]
                
            if 'name' in s:
                t = s['name']
            if 'units' in s:
                t += ' (%s)' % s['units']
            
        ## Set axis titles
        titles = ['', '']
        for i in [0,1]:
            if 'name' in inf[i]:
                titles[i] = inf[i]['name']
            if 'units' in inf[i]:
                titles[i] = titles[i] + ' (%s)' % inf[i]['units']
        self.setAxisTitle(self.xBottom, titles[0])
        self.setAxisTitle(self.yLeft, titles[1])

        ## create curves
        #curves = []
        try:
            xv = arr.xvals(xAxis)
        except:
            print "Making up xvals"
            print arr
            raise
            xv = range(arr.shape[xAxis])
            
        ret = []
        if arr.ndim == 2:
            for i in range(arr.shape[yAxis]):
                c = PlotCurve()
                c.setData(xv, arr[yAxis:i])
                #c.setPen(QtGui.QPen(QtGui.QColor(200, 200, 200)))
                c.attach(self)
                ret.append(len(self.curves))
                #self.curves.append(c)
        else:
            c = PlotCurve()
            c.setData(xv, arr)
            #c.setPen(QtGui.QPen(QtGui.QColor(200, 200, 200)))
            #c.attach(self)
            ret.append(c)
            #self.curves.append(c)
            
            
        return ret

    def writeSvg(self, fileName=None):
        if fileName is None:
            fileName = str(QtGui.QFileDialog.getSaveFileName())
        self.svg = QtSvg.QSvgGenerator()
        self.svg.setFileName(fileName)
        self.svg.setSize(self.size())
        self.svg.setResolution(600)
        painter = QtGui.QPainter(self.svg)
        self.print_(painter, self.rect())
        
    def writeImage(self, fileName=None):
        if fileName is None:
            fileName = str(QtGui.QFileDialog.getSaveFileName())
        self.png = QtGui.QImage(self.size(), QtGui.QImage.Format_ARGB32)
        painter = QtGui.QPainter(self.png)
        #rh = self.renderHints()
        #self.setRenderHints(QtGui.QPainter.Antialiasing)
        self.print_(painter, self.rect())
        #self.setRenderHints(rh)
        self.png.save(fileName)
        
        
    def clear(self):
        Qwt.QwtPlot.clear(self)
        self.curves = []
        self.paramIndex = {}

    def saveState(self):
        return self.stateGroup.state()
        
    def restoreState(self, state):
        self.stateGroup.setState(state)
        
        
        
class PlotCurve(Qwt.QwtPlotCurve):
    def __init__(self, *args):
        Qwt.QwtPlotCurve.__init__(self, *args)
        self.xData = None
        self.yData = None
        self.xSpecData = None
        self.ySpecData = None
        self.specCurve = None
        #self.currentCurve = None
        #self.plot = None
        pen = QtGui.QPen(QtGui.QColor(255, 255, 255))
        self.setPen(pen)
        self.alpha = 1.0
        self.autoAlpha = True
        self.spectrumMode = False

    def free(self):
        self.xData = None
        self.yData = None
        self.xSpecData = None
        self.xSpecData = None
        self.specCurve = None

    def setSpectrumMode(self, b):
        self.spectrumMode = b
        
    def setAlpha(self, alpha, auto=True):
        self.alpha = alpha
        self.autoAlpha = auto
        
    def draw(self, *args):
        if self.xData is None or len(self.xData) < 2:
            return
        if self.spectrumMode:
            self.generateSpecData()
            xData = self.xSpecData
            yData = self.ySpecData
            drawCurve = self.specCurve
        else:
            xData = self.xData
            yData = self.yData
            drawCurve = self
            
        (p, xsm, ysm, r) = args
        width = xsm.pDist()
        sd = xsm.sDist()
        dx = (xData[-1] - xData[0]) / (len(xData) - 1)
        numPts = sd / dx
        
        if numPts < width:
            ptAlpha = 255 * clip(0.1 * width/numPts, 0, 1)
            alpha = 255
            showPts = True
        else:
            ptAlpha = 0
            showPts = False
            alpha = clip(255 * width / numPts, 1, 255)
        s = Qwt.QwtSymbol(
            Qwt.QwtSymbol.Ellipse, 
            QtGui.QBrush(), 
            QtGui.QPen(QtGui.QColor(200,200,255,ptAlpha)), 
            QtCore.QSize(5,5))
        if not showPts:
            s.setStyle(Qwt.QwtSymbol.NoSymbol)
        drawCurve.setSymbol(s)
        
        penColor = self.pen().color()
            
        if self.autoAlpha:
            penColor.setAlpha(alpha * self.alpha)
        else:
            penColor.setAlpha(int(self.alpha * 255))
        drawCurve.setPen(QtGui.QPen(penColor))
            
        Qwt.QwtPlotCurve.draw(drawCurve, *args)
        
    def setDisplayRange(self, *args, **kargs):
        pass

    def generateSpecData(self):
        if self.ySpecData is None:
            f = fft(self.yData)
            
            self.ySpecData = abs(f[1:len(f)/2])
            
            dt = self.xData[-1] - self.xData[0]
            self.xSpecData = linspace(0, 0.5*len(self.xData)/dt, len(self.ySpecData))
            self.specCurve = Qwt.QwtPlotCurve()
            self.specCurve.setData(self.xSpecData, self.ySpecData)
        
        
    def setParams(self, params):
        self.params = params

    def setData(self, x, y):
        self.xData = x
        self.yData = y
        Qwt.QwtPlotCurve.setData(self, x, y)
        self.generateCurves()
        self.xSpecData = None
        self.ySpecData = None
        self.specCurve = None

    def generateCurves(self):
        pass
    
    def attach(self, plot):
        raise Exception("Use PlotWidget.attachCurve instead.")
        #if self.plot is not None:
            #self.detach()
        #self.plot = plot
        #if hasattr(plot, 'registerItem'):
            #plot.registerItem(self)
        #Qwt.QwtPlotCurve.attach(self, plot)
        
    def detach(self):
        raise Exception("Use PlotWidget.detachCurve instead.")
        ##print 'detach', self
        #if self.plot is not None and hasattr(self.plot, 'unregisterItem'):
            ##print 'unregister', self
            #self.plot.unregisterItem(self)
        #self.plot = None
        #Qwt.QwtPlotCurve.detach(self)
        
    def boundingRect(self):
        if self.spectrumMode:
            self.generateSpecData()
            return Qwt.QwtPlotCurve.boundingRect(self.specCurve)
        else:
            return Qwt.QwtPlotCurve.boundingRect(self)
        
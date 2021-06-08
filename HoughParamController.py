from PyQt5.QtWidgets import QWidget
import functools

class HoughParamController(QWidget):
    def __init__(self, parent):
        super(HoughParamController, self).__init__()
        self.parent=parent

    def gethoughparam(self):
        self.updatehoughparam()
        return  self.pixel, self.threshold, self.minlinelength, self.maxlinegap

    def setparam(self, pixel, threshold, minlinelength, maxlinegap):
        self.pixel = pixel
        self.threshold = threshold 
        self.minlinelength = minlinelength
        self.maxlinegap = maxlinegap  

    def setslider(self, pixel, threshold, minlinelength, maxlinegap):
        # ui obj
        self.HSlider_pixel = pixel
        self.HSlider_thres = threshold 
        self.HSlider_minlen = minlinelength
        self.HSlider_maxgap = maxlinegap  

    def setlineedit(self, pixel, threshold, minlinelength, maxlinegap):    
        # self.lineEdit_pixel.setText(str(pixel)) 
        # self.lineEdit_thres.setText(str(threshold))
        # self.lineEdit_minlen.setText(str(minlinelength))
        # self.lineEdit_maxgap.setText(str(maxlinegap))
        # ui obj
        self.lineEdit_pixel = pixel
        self.lineEdit_thres = threshold
        self.lineEdit_minlen = minlinelength
        self.lineEdit_maxgap = maxlinegap        

    def updatehoughparam(self):
        self.pixel = int(self.lineEdit_pixel.text()) 
        self.threshold = int(self.lineEdit_thres.text())  
        self.minlinelength = int(self.lineEdit_minlen.text())  
        self.maxlinegap = int(self.lineEdit_maxgap.text()) 

    def setup_slider_lineedit_callback(self):
        self.linkSliderLineEdit(self.HSlider_pixel, 10, 1, self.pixel, 1, 100, self.lineEdit_pixel)
        self.linkSliderLineEdit(self.HSlider_thres, 10, 1, self.threshold, 1, 100, self.lineEdit_thres)
        self.linkSliderLineEdit(self.HSlider_minlen, 10, 1, self.minlinelength, 1, 100, self.lineEdit_minlen)
        self.linkSliderLineEdit(self.HSlider_maxgap, 10, 1, self.maxlinegap, 1, 100, self.lineEdit_maxgap)

    def linkSliderLineEdit(self, slider, tickinterval, singlestep, value, minrange, maxrange, lineedit):
        slider.setTickInterval(tickinterval)
        slider.setSingleStep(singlestep)
        slider.setValue(value)
        slider.setMinimum(minrange)    
        slider.setMaximum(maxrange)
        slider.valueChanged.connect(functools.partial(self.slider_changed, slider, lineedit, value))
        lineedit.setText(str(value))
        lineedit.textChanged[str].connect(functools.partial(self.lineedit_changed, slider, lineedit, value))
        #some_action.triggered.connect(functools.partial(callbackfuntion, param1, param2))

    def slider_changed(self, slider, lineedit, itemval):
        itemval = slider.value() #self.pixel = self.HSlider_pixel.value()       
        lineedit.setText(str(itemval))
        self.parent.button_calculate_hough_show() 
        #self.calculatelinesandshow()
        #print(self.imgpath, self.pixel, self.threshold, self.minlinelength, self.maxlinegap)

    def lineedit_changed(self, slider, lineedit, itemval):
        itemval = int(lineedit.text()) #  
        slider.setValue(itemval) 
        self.parent.button_calculate_hough_show() 
        #print(self.imgpath, self.pixel, self.threshold, self.minlinelength, self.maxlinegap)    

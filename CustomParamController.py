from PyQt5.QtWidgets import QWidget
import functools

class CustomParamController(QWidget):
    def __init__(self, parent):
        super(CustomParamController, self).__init__()
        self.parent=parent
    def getcustomparam(self):
        self.updatecustomparam()
        return self.minlinelength, self.maxlinegap

    def setparam(self, minlinelength, maxlinegap):
        self.minlinelength = minlinelength
        self.maxlinegap = maxlinegap  

    def setslider(self, minlinelength, maxlinegap):
        self.HSlider_minlen = minlinelength
        self.HSlider_maxgap = maxlinegap  

    def setlineedit(self, minlinelength, maxlinegap):     
        self.lineEdit_minlen = minlinelength
        self.lineEdit_maxgap = maxlinegap   

    def updatecustomparam(self):
        self.minlinelength = int(self.lineEdit_minlen.text())  
        self.maxlinegap = int(self.lineEdit_maxgap.text()) 

    def setup_slider_lineedit_callback(self):
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
        self.parent.button_calculate_custom_spline_show() 
        #self.parent.button_calculate_custom_mergespline_show() 
        #self.calculatelinesandshow()
        #print(self.imgpath, self.pixel, self.threshold, self.minlinelength, self.maxlinegap)

    def lineedit_changed(self, slider, lineedit, itemval):
        itemval = int(lineedit.text()) #  
        slider.setValue(itemval) 
        self.parent.button_calculate_custom_spline_show()
        #print(self.imgpath, self.pixel, self.threshold, self.minlinelength, self.maxlinegap)    

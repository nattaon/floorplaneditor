from PyQt5.QtWidgets import QWidget
import functools

class MergeParamController(QWidget):
    def __init__(self, parent):
        super(MergeParamController, self).__init__()
        self.parent=parent

    def getmergeparam(self):
        self.updatemergeparam()
        return self.nearby, self.maxspace, self.cornerrad

    def setparam(self, nearby, maxspace, cornerrad):
        self.nearby = nearby 
        self.maxspace = maxspace
        self.cornerrad = cornerrad


    def setslider(self, nearby, maxspace, cornerrad):
        self.HSlider_nearby = nearby 
        self.HSlider_maxspace = maxspace
        self.HSlider_cornerrad = cornerrad

    def setlineedit(self, nearby, maxspace, cornerrad):     
        self.lineEdit_nearby = nearby
        self.lineEdit_maxspace = maxspace
        self.lineEdit_cornerrad = cornerrad

    def updatemergeparam(self):
        self.nearby = int(self.lineEdit_nearby.text())  
        self.maxspace = int(self.lineEdit_maxspace.text())  
        self.cornerrad = int(self.lineEdit_cornerrad.text())  


    def setup_slider_lineedit_callback(self):
        self.linkSliderLineEdit(self.HSlider_nearby, 10, 1, self.nearby, 1, 100, self.lineEdit_nearby)
        self.linkSliderLineEdit(self.HSlider_maxspace, 10, 1, self.maxspace, 1, 100, self.lineEdit_maxspace)
        self.linkSliderLineEdit(self.HSlider_cornerrad, 10, 1, self.cornerrad, 1, 100, self.lineEdit_cornerrad)


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
        #self.parent.button_calculate_custom_spline_show() 
        #self.parent.button_calculate_custom_mergespline_show() 
        #self.calculatelinesandshow()
        #print(self.imgpath, self.pixel, self.threshold, self.minlinelength, self.maxlinegap)

    def lineedit_changed(self, slider, lineedit, itemval):
        itemval = int(lineedit.text()) #  
        slider.setValue(itemval) 
        #self.calculatelinesandshow()
        #print(self.imgpath, self.pixel, self.threshold, self.minlinelength, self.maxlinegap)    

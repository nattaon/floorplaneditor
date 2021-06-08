from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QPushButton, QCheckBox, QLabel, QLineEdit, \
QHBoxLayout, QVBoxLayout

from QTGLWidget2 import QTGLWidget2
from WallPlane import WallPlane

class Widget3Dview2(QWidget):

    def __init__(self, parent):
        print("Widget3Dview2 __init__")
        super(Widget3Dview2, self).__init__()
        self.parent=parent
        
        self.label_img2 = parent.label_img2
        #self.init_3dlayout_window()
        

    # https://www.tutorialspoint.com/pyqt/pyqt_qlineedit_widget.htm
    def init_3dlayout_window(self):
        print("Widget3Dview2 init_3dlayout_window")
 
        # def update_other_param(value, otherparam):
        #     print("before",otherparam)
        #     otherparam = float(value)
        #     self.gl.flashLightPos[0]=otherparam
        #     print("after",otherparam)

        self.gl = QTGLWidget2(self)

        # Sub layout4
        #self.label_flashlight = QLabel('flash light', self)
        self.check_fl = QCheckBox('flash light',self)
        self.check_fl.setChecked(True)
        self.fl_pos0 = QLineEdit('0', self)
        self.fl_pos1 = QLineEdit('0', self)
        self.fl_pos2 = QLineEdit('0', self)  
        
        self.hbox_flashlight = QHBoxLayout()  
        #self.hbox_flashlight.addWidget(self.label_flashlight)   
        self.hbox_flashlight.addWidget(self.check_fl)  
        self.hbox_flashlight.addWidget(self.fl_pos0)  
        self.hbox_flashlight.addWidget(self.fl_pos1)  
        self.hbox_flashlight.addWidget(self.fl_pos2)    

        # Sub layout5
        self.check_gl = QCheckBox('green light',self)
        self.check_gl.setChecked(True)
        self.gl_pos0 = QLineEdit('0', self)
        self.gl_pos1 = QLineEdit('0', self)
        self.gl_pos2 = QLineEdit('0', self) 

        self.hbox_greenlight = QHBoxLayout()    
        self.hbox_greenlight.addWidget(self.check_gl)  
        self.hbox_greenlight.addWidget(self.gl_pos0)  
        self.hbox_greenlight.addWidget(self.gl_pos1)  
        self.hbox_greenlight.addWidget(self.gl_pos2)

        # Sub layout6
        self.check_rl = QCheckBox('red light',self)
        self.check_rl.setChecked(True)
        self.rl_pos0 = QLineEdit('0', self)
        self.rl_pos1 = QLineEdit('0', self)
        self.rl_pos2 = QLineEdit('0', self) 

        self.hbox_redlight = QHBoxLayout()    
        self.hbox_redlight.addWidget(self.check_rl)  
        self.hbox_redlight.addWidget(self.rl_pos0)  
        self.hbox_redlight.addWidget(self.rl_pos1)  
        self.hbox_redlight.addWidget(self.rl_pos2) 

        # Sub layout3
        self.label_campos = QLabel('position (x,y,z)', self)
        self.line_pos0 = QLineEdit('0', self)
        self.line_pos1 = QLineEdit('0', self)
        self.line_pos2 = QLineEdit('0', self)
        self.hbox_campos = QHBoxLayout()
        self.hbox_campos.addWidget(self.label_campos)
        self.hbox_campos.addWidget(self.line_pos0)  
        self.hbox_campos.addWidget(self.line_pos1) 
        self.hbox_campos.addWidget(self.line_pos2) 

        # Sub layout2
        self.label_camrot = QLabel('rotation (x,y,z)', self)
        self.line_rot0 = QLineEdit('0', self)
        self.line_rot1 = QLineEdit('0', self)
        self.line_rot2 = QLineEdit('0', self)
        self.hbox_camrot = QHBoxLayout()
        self.hbox_camrot.addWidget(self.label_camrot)
        self.hbox_camrot.addWidget(self.line_rot0)  
        self.hbox_camrot.addWidget(self.line_rot1) 
        self.hbox_camrot.addWidget(self.line_rot2)   

        # Sub layout1
        self.vbox = QVBoxLayout()
        
        self.vbox.addWidget(self.gl)
        self.vbox.addLayout(self.hbox_flashlight)  
        self.vbox.addLayout(self.hbox_greenlight)  
        self.vbox.addLayout(self.hbox_redlight)  
        self.vbox.addLayout(self.hbox_campos)  
        self.vbox.addLayout(self.hbox_camrot)  

        # Overall layout
        self.widgl = QWidget()
        self.widgl.setWindowTitle("3D layout2") 
        self.widgl.setLayout(self.vbox)
        self.widgl.resize(300, 350)  
        #print("widgl.show")


        self.gl.reinitview()
        self.gl_pos0.textChanged.connect(lambda:self.gl.setgreenlightpos(self.gl_pos0.text(), self.gl_pos1.text(),self.gl_pos2.text()))     
        self.gl_pos1.textChanged.connect(lambda:self.gl.setgreenlightpos(self.gl_pos0.text(), self.gl_pos1.text(),self.gl_pos2.text()))  
        self.gl_pos2.textChanged.connect(lambda:self.gl.setgreenlightpos(self.gl_pos0.text(), self.gl_pos1.text(),self.gl_pos2.text()))  

        self.fl_pos0.textChanged.connect(lambda:self.gl.setflashlightpos(self.fl_pos0.text(), self.fl_pos1.text(),self.fl_pos2.text()))     
        self.fl_pos1.textChanged.connect(lambda:self.gl.setflashlightpos(self.fl_pos0.text(), self.fl_pos1.text(),self.fl_pos2.text()))  
        self.fl_pos2.textChanged.connect(lambda:self.gl.setflashlightpos(self.fl_pos0.text(), self.fl_pos1.text(),self.fl_pos2.text())) 

        self.rl_pos0.textChanged.connect(lambda:self.gl.setredlightpos(self.rl_pos0.text(), self.rl_pos1.text(),self.rl_pos2.text()))     
        self.rl_pos1.textChanged.connect(lambda:self.gl.setredlightpos(self.rl_pos0.text(), self.rl_pos1.text(),self.rl_pos2.text()))  
        self.rl_pos2.textChanged.connect(lambda:self.gl.setredlightpos(self.rl_pos0.text(), self.rl_pos1.text(),self.rl_pos2.text()))  
        
        self.widgl.closeEvent = self.closeEvent
        self.widgl.show()


    ''' 
    called from main.py 
    > self.pushButton_testlight.clicked.connect(self.Widget3Dview2.open_3d_window)
    '''
    def open_3d_window(self):
        print("Widget3Dview2 open_3d_window")
        self.init_3dlayout_window()

        #self.gl.reinitview()   
        #self.draw3Dlayout()

    def closeEvent(self, event):
        print("Widget3Dview2 closeEvent")
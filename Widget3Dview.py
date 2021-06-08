from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QPushButton, QLabel, QLineEdit, QCheckBox, QHBoxLayout, QVBoxLayout

from QTGLWidget import QTGLWidget
from WallPlane import WallPlane

class Widget3Dview(QWidget):
    def __init__(self, parent):
        print("Widget3Dview __init__")
        super(Widget3Dview, self).__init__()
        self.parent=parent
        #self.gl = QTGLWidget(self) # will call it in init_3dlayout_window()
        self.label_img2 = parent.label_img2
        #self.init_3dlayout_window() # wil call it in open_3d_window()
        self.wall_h=200
        self.ground_h=0
        self.ground_grid_size = 50

    def checkfloat(self,value):
        try:
            float(value)
            return True
        except ValueError:
            return False
            
    def setwallheight(self, value):
        
        if (self.checkfloat(value)):
            self.wall_h=float(value)
            self.draw3Dlayout()

    def setgroundgrid(self, value):

        if (self.checkfloat(value)):
            self.ground_grid_size=int(value)
            self.draw3Dlayout()

    def init_3dlayout_window(self):
        print("Widget3Dview init_3dlayout_window")
        # Draw window component
        # opengl
        self.gl = QTGLWidget(self)

        # wall height
        self.label_wallheight = QLabel('wall height (cm)', self)
        self.line_wh = QLineEdit('200', self)
        self.label_groundgrid = QLabel('ground grid size (cm)', self)
        self.line_gg = QLineEdit('50', self)    
        self.label_groundwh = QLabel('w*h', self)
        self.line_ggw = QLineEdit('0', self)    
        #self.line_ggw.setReadOnly(True)
        self.line_ggw.setEnabled(False)
        self.line_ggh = QLineEdit('0', self)  
        #self.line_ggh.setReadOnly(True)
        self.line_ggh.setEnabled(False)

        self.hbox_wallheight = QHBoxLayout()
        self.hbox_wallheight.addWidget(self.label_wallheight)
        self.hbox_wallheight.addWidget(self.line_wh)  
        self.hbox_wallheight.addWidget(self.label_groundgrid)
        self.hbox_wallheight.addWidget(self.line_gg) 
        self.hbox_wallheight.addWidget(self.label_groundwh) 
        self.hbox_wallheight.addWidget(self.line_ggw) 
        self.hbox_wallheight.addWidget(self.line_ggh) 

        # camera perspective
        self.label_fov = QLabel('Fov', self)
        self.line_fov = QLineEdit('0', self) 
        self.label_znear = QLabel('zNear', self)
        self.line_znear = QLineEdit('0', self) 
        self.label_zfar = QLabel('zFar', self)
        self.line_zfar = QLineEdit('0', self) 
        self.hbox_camera = QHBoxLayout()
        self.hbox_camera.addWidget(self.label_fov)
        self.hbox_camera.addWidget(self.line_fov)  
        self.hbox_camera.addWidget(self.label_znear)
        self.hbox_camera.addWidget(self.line_znear)  
        self.hbox_camera.addWidget(self.label_zfar)
        self.hbox_camera.addWidget(self.line_zfar)  

        #light
        self.check_fl = QCheckBox('light',self)
        self.check_fl.setChecked(True)
        self.label_fl_color = QLabel('color', self)
        self.fl_r = QLineEdit('0', self)
        self.fl_g = QLineEdit('0', self)
        self.fl_b = QLineEdit('0', self) 
        self.label_fl_pos = QLabel('position', self)
        self.fl_pos0 = QLineEdit('0', self)
        self.fl_pos1 = QLineEdit('0', self)
        self.fl_pos2 = QLineEdit('0', self) 
        self.hbox_light = QHBoxLayout() 
        self.hbox_light.addWidget(self.check_fl) 
        self.hbox_light.addWidget(self.label_fl_color) 
        self.hbox_light.addWidget(self.fl_r) 
        self.hbox_light.addWidget(self.fl_g) 
        self.hbox_light.addWidget(self.fl_b) 
        self.hbox_light.addWidget(self.label_fl_pos) 
        self.hbox_light.addWidget(self.fl_pos0) 
        self.hbox_light.addWidget(self.fl_pos1) 
        self.hbox_light.addWidget(self.fl_pos2) 

        # buttons
        self.button_captureimage = QPushButton('capture image', self)
        self.button_reset3Dview = QPushButton('default view', self)
        self.button_show3Dlayout = QPushButton('show layout', self) 
        self.hbox_buttons = QHBoxLayout()
        self.hbox_buttons.addWidget(self.button_captureimage)
        self.hbox_buttons.addWidget(self.button_reset3Dview)
        self.hbox_buttons.addWidget(self.button_show3Dlayout)   

        # arrange components vertical stack
        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.gl) 
        self.vbox.addLayout(self.hbox_wallheight) 
        self.vbox.addLayout(self.hbox_camera)   
        self.vbox.addLayout(self.hbox_light)  
        self.vbox.addLayout(self.hbox_buttons)                

        # create a widget to binding all these components
        self.widgl = QWidget()
        self.widgl.setWindowTitle("3D layout")  
        self.widgl.setLayout(self.vbox)
        self.widgl.resize(300, 350)   

        # set up opengl init param
        self.gl.reinitview()       

        # events
        self.button_captureimage.clicked.connect(self.gl.captureview)
        self.button_reset3Dview.clicked.connect(self.gl.reinitview)
        self.button_show3Dlayout.clicked.connect(self.draw3Dlayout)
        self.line_wh.textChanged.connect(lambda value: self.setwallheight(value))
        self.line_gg.textChanged.connect(lambda value: self.setgroundgrid(value))

        self.line_fov.textChanged.connect(lambda:self.gl.setcameraperspective(self.line_fov.text(), self.line_znear.text(),self.line_zfar.text()))     
        self.line_znear.textChanged.connect(lambda:self.gl.setcameraperspective(self.line_fov.text(), self.line_znear.text(),self.line_zfar.text()))  
        self.line_zfar.textChanged.connect(lambda:self.gl.setcameraperspective(self.line_fov.text(), self.line_znear.text(),self.line_zfar.text()))  

        self.fl_pos0.textChanged.connect(lambda:self.gl.setlightpos(self.fl_pos0.text(), self.fl_pos1.text(),self.fl_pos2.text()))     
        self.fl_pos1.textChanged.connect(lambda:self.gl.setlightpos(self.fl_pos0.text(), self.fl_pos1.text(),self.fl_pos2.text()))  
        self.fl_pos2.textChanged.connect(lambda:self.gl.setlightpos(self.fl_pos0.text(), self.fl_pos1.text(),self.fl_pos2.text())) 

        self.fl_r.textChanged.connect(lambda:self.gl.setlightcolor(self.fl_r.text(), self.fl_g.text(),self.fl_b.text()))     
        self.fl_g.textChanged.connect(lambda:self.gl.setlightcolor(self.fl_r.text(), self.fl_g.text(),self.fl_b.text()))  
        self.fl_b.textChanged.connect(lambda:self.gl.setlightcolor(self.fl_r.text(), self.fl_g.text(),self.fl_b.text())) 
        
        self.widgl.closeEvent = self.closeEvent

        self.widgl.show() 


    
    def draw3Dlayout(self):


        def line2wall(line):
            return [line[0],self.ground_h,line[1]],\
                   [line[2],self.ground_h,line[3]],\
                   [line[2],self.wall_h,line[3]],\
                   [line[0],self.wall_h,line[1]]
     
        # convert 2d line to 3d wall..
        corners=[]
        lines = self.parent.LinesWidget.getlines()
        for line in lines:
            corners.extend(line2wall(line))

        wall1 = WallPlane()
        wall1.corners = corners        

        self.gl.walls=wall1
        self.gl.enable_draw_wall=True

        self.gl.set_draw_grid_wh_param(self.label_img2.width(),self.label_img2.height(),self.ground_grid_size)
        
        #print(self.label_img2.width(),self.label_img2.height())        
        #print(wall1.color)
        #print("wall1.corners", len(wall1.corners))

        #self.gl.enable_draw_sample=True




    def open_3d_window(self):
        print("Widget3Dview open_3d_window")
        self.init_3dlayout_window()
        self.draw3Dlayout() # walls and ground grid

    def closeEvent(self, event):
        print("Widget3Dview closeEvent")
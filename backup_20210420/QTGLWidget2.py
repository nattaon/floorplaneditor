from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtOpenGL import *
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtGui import QPixmap

#from WallPlane import *
CUBE_DEG_PER_S = 30.0
LIGHT_DEG_PER_S = 90.0
CUBE_SIZE = 9.0



m_pSphere = gluNewQuadric()
m_cubeAngle = 45.0
m_lightAngle = 0.0
m_flashlightOn = True     

class QTGLWidget2(QGLWidget):

    def __init__(self, parent):
        print("QTGLWidget2 __init__")
        QGLWidget.__init__(self, parent)
        self.parent = parent
        self.setMinimumSize(500, 500)
        #self.reinitview() # called by Widget3Dview2.init_3dlayout_window

    def checkfloat(self,value):
        try:
            float(value)
            return True
        except ValueError:
            return False
        
    def setflashlightpos(self, v0, v1, v2):
        if (self.checkfloat(v0) and self.checkfloat(v1) and self.checkfloat(v2)):
            self.flashLightPos = [float(v0), float(v1), float(v2),1.0]

    def setredlightpos(self, v0, v1, v2):
        if (self.checkfloat(v0) and self.checkfloat(v1) and self.checkfloat(v2)):
            self.redLightPos = [float(v0), float(v1), float(v2),1.0]

    def setgreenlightpos(self, v0, v1, v2):
        if (self.checkfloat(v0) and self.checkfloat(v1) and self.checkfloat(v2)):
            self.greenLightPos = [float(v0), float(v1), float(v2),1.0]

    def reinitview(self):
        print("QTGLWidget2 reinitview")
        #self.initializeGL()
        #self.setMinimumSize(500, 500)
        self.cubeColor = [ 0.3, 0.3, 0.3 ];
        self.cubeSpecular = [ 1.0, 1.0, 1.0 ];
        self.cubeShiness = 10.0;

        self.flashLightPos = [ 0.0, 10.0, 0.0, 1.0];
        self.flashLightDir = [ 0.0, -1.0, 0.0 ];
        self.flashLightColor = [ 0.5, 0.5, 0.5 ];
        self.flashLightCutoff = 12.0
        self.parent.fl_pos0.setText(str(self.flashLightPos[0])) 
        self.parent.fl_pos1.setText(str(self.flashLightPos[1])) 
        self.parent.fl_pos2.setText(str(self.flashLightPos[2]))  

        self.redLightColor = [ 0.5, 0.1, 0.2 ];
        self.redLightPos = [ 10.0, 0.0, 5.0, 1.0 ];
        self.parent.rl_pos0.setText(str(self.redLightPos[0])) 
        self.parent.rl_pos1.setText(str(self.redLightPos[1])) 
        self.parent.rl_pos2.setText(str(self.redLightPos[2]))  

        self.greenLightColor = [ 0.1, 0.6, 0.2 ];
        self.greenLightPos = [ 0.0, 0.0, 10.0, 1.0 ];
        self.parent.gl_pos0.setText(str(self.greenLightPos[0])) 
        self.parent.gl_pos1.setText(str(self.greenLightPos[1])) 
        self.parent.gl_pos2.setText(str(self.greenLightPos[2]))  

        ### trackball
        self.__lastPos = QPoint()

        self.camRot = [0.0, 0.0, 0.0]  
        self.camPos = [0.0, 0.0, 20.0] 

        self.parent.line_rot0.setText(str(self.camRot[0])) 
        self.parent.line_rot1.setText(str(self.camRot[1])) 
        self.parent.line_rot2.setText(str(self.camRot[2])) 

        self.parent.line_pos0.setText(str(self.camPos[0])) 
        self.parent.line_pos1.setText(str(self.camPos[1])) 
        self.parent.line_pos2.setText(str(self.camPos[2]))

        self.update()
        #self.paintGL()

    # def ChangeAngle(self, dt):
    #     global CUBE_DEG_PER_S, LIGHT_DEG_PER_S, m_cubeAngle, m_lightAngle
    #     m_cubeAngle += CUBE_DEG_PER_S * dt;
    #     if (m_cubeAngle > 360.0):
    #         m_cubeAngle = 0.0;
    #     # m_lightAngle += LIGHT_DEG_PER_S * dt;
    #     # if (m_lightAngle > 360.0):
    #     #     m_lightAngle = 0.0;

    def DrawAxis(self):

        glPushMatrix();
        glTranslatef(15, -15, 0);
        glRotated(self.camRot[0], 0.0, 1.0, 0.0)
        glRotated(self.camRot[1], 1.0, 0.0, 0.0) 

        glColor3fv([1.0, 0.0, 0.0]);   #r         
        glBegin(GL_LINES);
        glVertex3f(0.0, 0.0, 0.0);
        glVertex3f(1.0, 0.0, 0.0); #x
        glEnd();  

        glColor3fv([0.0, 1.0, 0.0]);  #g         
        glBegin(GL_LINES);
        glVertex3f(0.0, 0.0, 0.0);
        glVertex3f(0.0, 1.0, 0.0); #y
        glEnd(); 

        glColor3fv([0.0, 0.0, 1.0]);  #b         
        glBegin(GL_LINES);
        glVertex3f(0.0, 0.0, 0.0);
        glVertex3f(0.0, 0.0, 1.0); #z
        glEnd(); 
        glPopMatrix();  

    def paintGL(self):
       
        #global m_cubeAngle, m_flashlightOn, m_lightAngle, m_pSphere, CUBE_SIZE
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT);
        glLoadIdentity();
        # camera setting [eyeX, eyeY, eyeZ,  centerX, centerY, centerZ,  upX, upY, upZ]
        # gluLookAt(0.0, 0.0, 20.0, 
        #           0.0, 0.0, 0.0, 
        #           0.0, 1.0, 0.0);
        gluLookAt(self.camPos[0], self.camPos[1], self.camPos[2],
                  self.camPos[0], self.camPos[1], 0.0,  
                  0.0, 1.0, 0.0)
        glPushMatrix()

        self.DrawAxis()

        glRotated(self.camRot[0], 0.0, 1.0, 0.0)
        glRotated(self.camRot[1], 1.0, 0.0, 0.0)    


        #self.ChangeAngle(0.03)

        # position and draw the flash light
        if (self.parent.check_fl.isChecked()):
            #print(self.flashLightPos)
            glEnable(GL_LIGHT0)
            glPushMatrix();
            glDisable(GL_LIGHTING);
            glLightfv(GL_LIGHT0, GL_POSITION, self.flashLightPos);       
            # glLightfv(GL_LIGHT0, GL_SPOT_DIRECTION, self.flashLightDir);
            # glLightf(GL_LIGHT0, GL_SPOT_CUTOFF, self.flashLightCutoff); 
            glColor3fv(self.flashLightColor);           
            # glBegin(GL_LINES);
            # glVertex3f(self.flashLightPos[0], self.flashLightPos[1], self.flashLightPos[2]);
            # glVertex3f(self.flashLightPos[0]+self.flashLightDir[0]*20, \
            #             self.flashLightPos[1]+self.flashLightDir[1]*20, \
            #             self.flashLightPos[2]+self.flashLightDir[2]*20);
            # glEnd(); 
            glTranslatef(self.flashLightPos[0], self.flashLightPos[1], self.flashLightPos[2]); 
            gluSphere(m_pSphere, 0.2, 10, 10); 
            glEnable(GL_LIGHTING);
            glPopMatrix();                  
        else:
            glDisable(GL_LIGHT0)

        # position and draw the red light
        if (self.parent.check_rl.isChecked()):
            glEnable(GL_LIGHT1)
            glPushMatrix();
            glDisable(GL_LIGHTING);
            glLightfv(GL_LIGHT1, GL_POSITION, self.redLightPos);
            glColor3fv(self.redLightColor); 
            glBegin(GL_LINES);
            glVertex3f(self.redLightPos[0], self.redLightPos[1], self.redLightPos[2]);
            glVertex3f(self.redLightPos[0]+self.flashLightDir[0]*20, \
                        self.redLightPos[1]+self.flashLightDir[1]*20, \
                        self.redLightPos[2]+self.flashLightDir[2]*20);
            glEnd();                         
            glTranslatef(self.redLightPos[0], self.redLightPos[1], self.redLightPos[2]);
            
            gluSphere(m_pSphere, 0.2, 10, 10);
            glEnable(GL_LIGHTING);
            glPopMatrix();

        else:
            glDisable(GL_LIGHT1)


        # position and draw the green light
        if (self.parent.check_gl.isChecked()):
            glEnable(GL_LIGHT2)
            glPushMatrix();
            glDisable(GL_LIGHTING);
            # glRotatef(m_lightAngle, 1.0, 0.0, 0.0);
            # glRotatef(m_lightAngle, 0.0, 1.0, 0.0);
            glLightfv(GL_LIGHT2, GL_POSITION, self.greenLightPos);
            glTranslatef(self.greenLightPos[0], self.greenLightPos[1], self.greenLightPos[2]);
            glColor3fv(self.greenLightColor);
            gluSphere(m_pSphere, 0.2, 10, 10);
            glEnable(GL_LIGHTING);
            glPopMatrix();    

        else:
            glDisable(GL_LIGHT2)           
        
        # set up cube's material
        # glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, self.cubeColor);
        # glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, self.cubeSpecular);
        # glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, self.cubeShiness);        
        # position and draw the cube
        glPushMatrix();
        #glRotatef(m_cubeAngle, 1.0, 1.0, 0.0);
        #glRotatef(m_cubeAngle, 0.0, 0.0, 1.0);
        self.DrawCube(CUBE_SIZE, 1.0);
        glPopMatrix(); 


        glPopMatrix()
        self.update()
            
    def DrawPlane(self, size, step):
        glBegin(GL_QUADS)
        x=0.0
        z=0.0
        while(z < size):
            x = 0.0
            while (x<size):
                glVertex3f(x, 0.0, z)
                glVertex3f(x+step, 0.0, z)
                glVertex3f(x+step, 0.0, z+step)
                glVertex3f(x, 0.0, z+step)
                x += step
            z += step
        glEnd()

    def DrawCube(self, size, resolution=1.0):
        step = size / resolution
        
        glPushMatrix();
        glTranslatef(-size/2, -size/2, -size/2);
        glNormal3f(0.0, -1.0, 0.0);  ##### test
            
            # top
        glPushMatrix();
        glTranslatef(0.0, size, 0.0);
        glScalef(1.0, -1.0, 1.0);
        self.DrawPlane(size, step);
        glPopMatrix();
        
        # bottom
        self.DrawPlane(size, step);
        
        # left
        glPushMatrix();
        glRotatef(90.0, 0.0, 0.0, 1.0);
        glScalef(1.0, -1.0, 1.0);
        self.DrawPlane(size, step);
        glPopMatrix();
        
        # right
        glPushMatrix();
        glTranslatef(size, 0.0, 0.0);
        glRotatef(90.0, 0.0, 0.0, 1.0);
        self.DrawPlane(size, step);
        glPopMatrix();
        
        # front
        glPushMatrix();
        glTranslatef(0.0, 0.0, size);
        glRotatef(90.0, -1.0, 0.0, 0.0);
        self.DrawPlane(size, step);
        glPopMatrix();
        
        # back
        glPushMatrix();
        glRotatef(90.0, -1.0, 0.0, 0.0);
        glScalef(1.0, -1.0, 1.0);
        self.DrawPlane(size, step);
        glPopMatrix();
        
        glPopMatrix();


    def resizeGL(self, width, height):
        if(height == 0):
            height = 1
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        # [float fovy, float aspect, float zNear, float zFar]
        gluPerspective(64.0, float(width)/height, 1.0, 1000.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()




        
    def mousePressEvent(self, event):
        self.setFocus(True)
        self.__lastPos = event.pos()
   
        
    def mouseMoveEvent(self, event):
        #print("point : {0} {1}".format(event.pos().x(), event.pos().y()))
        dx = event.x() - self.__lastPos.x()
        dy = event.y() - self.__lastPos.y()

        #pos_move_mul = 0.02
        pos_move_mul = 1
        if event.buttons() == Qt.LeftButton:
            self.camRot[0] += 0.5 * dx 
            self.camRot[1] += 0.5 * dy 

            self.camRot[0] = self.reRotataionValue(self.camRot[0])
            self.camRot[1] = self.reRotataionValue(self.camRot[1])

            self.parent.line_rot0.setText(str(self.camRot[0])) 
            self.parent.line_rot1.setText(str(self.camRot[1])) 

        elif event.buttons() == Qt.RightButton:
            self.camPos[0] -=  dx * pos_move_mul
            self.camPos[1] +=  dy * pos_move_mul

            self.parent.line_pos0.setText(str(self.camPos[0])) 
            self.parent.line_pos1.setText(str(self.camPos[1])) 

        #print(self.camPos)
        self.__lastPos = event.pos()
        self.update()
    
    def reRotataionValue(self,rot):
        if (rot > 360.0):
            return 0.0
        elif (rot < -360.0):
            return 0.0
        else:
            return rot

    def wheelEvent(self,event):
        
        numAngle = float(event.angleDelta().y()) / 10#120
        self.camPos[2] -= numAngle
        self.parent.line_pos2.setText(str(self.camPos[2])) 

        self.update()

    ''' auto called when new this class'''
    def initializeGL(self):
        print("QTGLWidget2 initializeGL")


        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
        glEnable(GL_DEPTH_TEST)
        #glEnable(GL_LIGHTING)
        glEnable(GL_COLOR_MATERIAL)
        #glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE )
        #glShadeModel(GL_SMOOTH)

        glClearColor(0.0, 0.0, 0.0, 1.0)
        #glClearDepth(1.0)

        glEnable(GL_LIGHT0);
        glLightfv(GL_LIGHT0, GL_AMBIENT, self.flashLightColor);
        glLightfv(GL_LIGHT0, GL_DIFFUSE, self.flashLightColor);
        glLightfv(GL_LIGHT0, GL_SPECULAR, self.flashLightColor);

        
        # set up static red light
        glEnable(GL_LIGHT1);
        glLightfv(GL_LIGHT1, GL_AMBIENT, self.redLightColor);
        glLightfv(GL_LIGHT1, GL_DIFFUSE, self.redLightColor);
        glLightfv(GL_LIGHT1, GL_SPECULAR, self.redLightColor);
        
        # set up moving green light
        glEnable(GL_LIGHT2);
        glLightfv(GL_LIGHT2, GL_AMBIENT, self.greenLightColor);
        glLightfv(GL_LIGHT2, GL_DIFFUSE, self.greenLightColor);
        glLightfv(GL_LIGHT2, GL_SPECULAR, self.greenLightColor);
        
        # get a quadric object for the light sphere
        m_pSphere = gluNewQuadric()

   
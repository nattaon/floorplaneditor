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
m_pSphere = gluNewQuadric()
class QTGLWidget(QGLWidget):


    def __init__(self, parent):
        QGLWidget.__init__(self, parent)
        self.parent = parent
        self.setMinimumSize(500, 500)
        
        self.enable_draw_grid_wh = False
        self.enable_draw_wall = False
        self.walls = None


        #self.reinitview()

    def checkfloat(self,value):
        try:
            float(value)
            return True
        except ValueError:
            return False
        
    def setcameraperspective(self, fov, near, far):
        if (self.checkfloat(fov) and self.checkfloat(near) and self.checkfloat(far)):
            self.fov = float(fov)
            self.zNear = float(near)
            self.zFar = float(far)
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            #print(self.fov, self.aspect, self.zNear, self.zFar)
            gluPerspective(self.fov, self.aspect, self.zNear, self.zFar)
            self.update()
    def setlightpos(self, v0, v1, v2):
        if (self.checkfloat(v0) and self.checkfloat(v1) and self.checkfloat(v2)):
            self.flashLightPos = [float(v0), float(v1), float(v2),1.0]
            print("setlightpos ", v0, v1, v2)
            self.update()

    def setlightcolor(self, v0, v1, v2):
        if (self.checkfloat(v0) and self.checkfloat(v1) and self.checkfloat(v2)):
            self.flashLightColor = [float(v0), float(v1), float(v2)]
            print("setlightcolor ", v0, v1, v2)
            self.update()

    def reinitview(self):
        ### trackball
        self.__lastPos = QPoint()
        self.camRot = [0.0, 90.0, 0.0]
        #self.camPos = [0.0, 0.0, 360.0]  #too near
        self.camPos = [0.0, 0.0, 720.0] 

        self.fov = 60.0
        self.zNear = 1.0
        self.zFar = 1000.0
        self.aspect = 1

        self.parent.line_fov.setText(str(self.fov)) 
        self.parent.line_znear.setText(str(self.zNear)) 
        self.parent.line_zfar.setText(str(self.zFar)) 


        self.flashLightPos = [ 200.0, 1000.0, 200.0, 1.0]
        self.parent.fl_pos0.setText(str(self.flashLightPos[0])) 
        self.parent.fl_pos1.setText(str(self.flashLightPos[1])) 
        self.parent.fl_pos2.setText(str(self.flashLightPos[2]))  

        self.flashLightColor = [ 0.7, 0.7, 0.7 ]
        self.parent.fl_r.setText(str(self.flashLightColor[0])) 
        self.parent.fl_g.setText(str(self.flashLightColor[1])) 
        self.parent.fl_b.setText(str(self.flashLightColor[2])) 

        self.update()

    def DrawAxis(self,xpos,ypos,size=1.0):
        glPushMatrix();
        glTranslatef(xpos, ypos, 0);
        glRotated(self.camRot[0], 0.0, 1.0, 0.0)
        glRotated(self.camRot[1], 1.0, 0.0, 0.0) 

        glColor3fv([1.0, 0.0, 0.0]);   #r         
        glBegin(GL_LINES);
        glVertex3f(0.0, 0.0, 0.0);
        glVertex3f(size, 0.0, 0.0); #x
        glEnd();  

        glColor3fv([0.0, 1.0, 0.0]);  #g         
        glBegin(GL_LINES);
        glVertex3f(0.0, 0.0, 0.0);
        glVertex3f(0.0, size, 0.0); #y
        glEnd(); 

        glColor3fv([0.0, 0.0, 1.0]);  #b         
        glBegin(GL_LINES);
        glVertex3f(0.0, 0.0, 0.0);
        glVertex3f(0.0, 0.0, size); #z
        glEnd(); 
        glPopMatrix(); 

    def drawWallPlane(self, wallPlane):
        glPushMatrix();
        glBegin(GL_QUADS)
        rgb = wallPlane.color
        glColor4f(rgb[0], rgb[1], rgb[2], 0.75)
        glNormal3f(0.0, 0.0, 1.0)
        for p in wallPlane.corners:
            glVertex3f(p[0], p[1], p[2])
        glEnd()

        #wall border line
        
        #print("len wallPlane.corners",len(wallPlane.corners))
        wallPlanequater = int(len(wallPlane.corners)/4)
        glColor4f(0.3, 0.3, 0.3, 0.75)
        glBegin(GL_LINES)
        for i in range(0, wallPlanequater):
            forthindex = i*4
            glVertex(wallPlane.corners[forthindex+0])
            glVertex(wallPlane.corners[forthindex+1])

            glVertex(wallPlane.corners[forthindex+1])
            glVertex(wallPlane.corners[forthindex+2])

            glVertex(wallPlane.corners[forthindex+2])
            glVertex(wallPlane.corners[forthindex+3])
            
            glVertex(wallPlane.corners[forthindex+3])
            glVertex(wallPlane.corners[forthindex+0])
        glEnd()
        glPopMatrix(); 

    def paintGL(self):
        #glClearColor(0.0, 0.0, 0.0, 0.0) # rgba
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # glLoadIdentity()
        # gluLookAt(3.0, 4.0, 5.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        # camera setting [eyeX, eyeY, eyeZ,  centerX, centerY, centerZ,  upX, upY, upZ]
        gluLookAt(self.camPos[0], self.camPos[1], self.camPos[2],
                  self.camPos[0], self.camPos[1], -1.0,  
                  0.0, 1.0, 0.0)

        glPushMatrix()
        self.DrawAxis(-10, 10, self.gridsize*2)
        #self.DrawAxis(self.gridmaxwidth+50, self.gridmaxheight-50, 50.0) 
        
        glRotated(self.camRot[0], 0.0, 1.0, 0.0)
        glRotated(self.camRot[1], 1.0, 0.0, 0.0)

        if (self.parent.check_fl.isChecked()):
            glEnable(GL_LIGHT0)
            glLightfv(GL_LIGHT0, GL_AMBIENT, self.flashLightColor);
            glLightfv(GL_LIGHT0, GL_DIFFUSE, self.flashLightColor);
            glLightfv(GL_LIGHT0, GL_SPECULAR, self.flashLightColor);            
            glPushMatrix()
            glDisable(GL_LIGHTING)
            glLightfv(GL_LIGHT0, GL_POSITION, self.flashLightPos)        
            glColor3fv(self.flashLightColor)       
            glTranslatef(self.flashLightPos[0], self.flashLightPos[1], self.flashLightPos[2])
            gluSphere(m_pSphere, 5, 10, 10)
            glEnable(GL_LIGHTING)
            glPopMatrix();                  
        else:
            glDisable(GL_LIGHT0)

        if self.enable_draw_grid_wh:
            self.draw_grid_wh()

        if self.enable_draw_wall:
            self.drawWallPlane(self.walls)

        glPopMatrix()

        self.update()
        #glFlush()




    def set_draw_grid_wh_param(self,width,height,gridsize):
        print("QTGLWidget set_draw_grid_wh_param")
        glPushMatrix();
        self.gridsize = gridsize
        q, r = divmod(width, gridsize)
        gridmax = q + bool(r) #ceiling
        self.gridmaxwidth = gridmax*gridsize
        self.parent.line_ggw.setText(str(self.gridmaxwidth)) 

        q, r = divmod(height, gridsize)
        gridmax = q + bool(r) #ceiling
        self.gridmaxheight = gridmax*gridsize
        self.parent.line_ggh.setText(str(self.gridmaxheight))         
        #print(self.gridmaxwidth, self.gridmaxheight)

        # set camera do that the layout is center to the screen
        self.camPos[0] = width/2
        self.camPos[1] = -height/2

        self.enable_draw_grid_wh = True
        self.update()
        glPopMatrix();

    def draw_grid_wh(self):
        glPushMatrix();
        glColor3f(0.5,0.5,0.5) # grey
        # horizontal lines
        for i in range(0,self.gridmaxheight+1,self.gridsize):
            glPushMatrix()
            glTranslated(0,0,i)
            glBegin(GL_LINES)
            glVertex3f(0,-0.1,0)
            glVertex3f(self.gridmaxwidth,-0.1,0)
            glEnd()
            glPopMatrix()

        # vertical lines,   self.gridmaxwidth+1 to get the last line  
        for i in range(0,self.gridmaxwidth+1,self.gridsize):
            glPushMatrix()
            glTranslated(i,0,0)
            glRotated(-90, 0.0, 1.0, 0.0)
            glBegin(GL_LINES)
            glVertex3f(0,-0.1,0)
            glVertex3f(self.gridmaxheight,-0.1,0)
            glEnd()
            glPopMatrix()

        glColor4f(0.1, 0.1, 0.1, 0.75)
        glBegin(GL_QUADS)
        glVertex3f(0,-0.15,0)
        glVertex3f(self.gridmaxwidth,-0.15,0)
        glVertex3f(self.gridmaxwidth,-0.15,self.gridmaxheight)
        glVertex3f(0,-0.15,self.gridmaxheight)
        glEnd() 
        glPopMatrix(); 



    def resizeGL(self, width, height):
        #print("resizeGL width, height: ", width, height)
        #print(glutGet(GLUT_WINDOW_WIDTH)) # why got 0?

        # side = min(width, height) # this shink 3d when window_w bigger... - -?
        # glViewport((width - side) // 2, (height - side) // 2, side, side)
        glViewport(0, 0, width, height)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        #gluPerspective(60, width/height, 1.0, 1000)
        # [float fovy, float aspect, float zNear, float zFar]

        
        if height==0:
            self.aspect = 1
        else:
            self.aspect = float(width)/height

        gluPerspective(self.fov, self.aspect, self.zNear, self.zFar)

        #self.update()
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

        elif event.buttons() == Qt.RightButton:
            self.camPos[0] -=  dx * pos_move_mul
            self.camPos[1] +=  dy * pos_move_mul
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
        #print(self.camPos)
        self.update()

    def initializeGL(self):
        print("QTGLWidget initializeGL")
        #glutInit()
        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
        glEnable(GL_DEPTH_TEST)
        # glEnable(GL_LIGHTING)
        # glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        # glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE )
        #glShadeModel(GL_SMOOTH)

        glClearColor(0.0, 0.0, 0.0, 1.0)
        #glClearDepth(1.0)



   
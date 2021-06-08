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

class QTGLWidget(QGLWidget):


    def __init__(self, parent):
        QGLWidget.__init__(self, parent)
        self.setMinimumSize(500, 500)
        
        self.enable_draw_grid_wh = False
        self.enable_draw_sample = False
        self.enable_draw_wall = False
        self.walls = None

        self.reinitview()

    def reinitview(self):
        ### trackball
        self.__lastPos = QPoint()
        self.camRot = [0.0, 90.0, 0.0]
        #self.camPos = [0.0, 0.0, 12.0]  #360
        self.camPos = [0.0, 0.0, 720.0] 
        self.update()

    # def drawEdges(self, wallPlane):
        
    #     glLineWidth(3)
    #     glBegin(GL_LINE_STRIP)
    #     for p in obj.corners:
    #         glVertex3f(p.xyz[0], p.xyz[1], p.xyz[2])
    #     first = obj.corners[0]
    #     glVertex3f(first.xyz[0], first.xyz[1], first.xyz[2])
    #     glEnd()

    def drawWallPlane(self, wallPlane):
        
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

    def paintGL(self):
        #glClearColor(0.0, 0.0, 0.0, 0.0) # rgba
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # glLoadIdentity()
        # gluLookAt(3.0, 4.0, 5.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(self.camPos[0], self.camPos[1], self.camPos[2],
                  self.camPos[0], self.camPos[1], -1.0,  0.0, 1.0, 0.0)

        glPushMatrix()
        
        glRotated(self.camRot[0], 0.0, 1.0, 0.0)
        glRotated(self.camRot[1], 1.0, 0.0, 0.0)

        if self.enable_draw_grid_wh:
            self.draw_grid_wh()
        else:
            self.draw_grid()

        if self.enable_draw_sample:
            self.draw_sample_quad()

        if self.enable_draw_wall:
            self.drawWallPlane(self.walls)

        glPopMatrix()

        glFlush()

    # def resizeGL(self, w, h):
    #     glViewport(0, 0, w, h)
    #     glMatrixMode(GL_PROJECTION)
    #     glLoadIdentity()
    #     gluPerspective(30.0, w/h, 1.0, 100.0)
    #     glMatrixMode(GL_MODELVIEW)
    vertex = [
        [ 0.0, 0.0, 0.0 ],
        [ 1.0, 0.0, 0.0 ],
        [ 1.0, 1.0, 0.0 ],
        [ 0.0, 1.0, 0.0 ],
        [ 0.0, 0.0, 1.0 ],
        [ 1.0, 0.0, 1.0 ],
        [ 1.0, 1.0, 1.0 ],
        [ 0.0, 1.0, 1.0 ]]

    edge = [
        [ 0, 1 ],
        [ 1, 2 ],
        [ 2, 3 ],
        [ 3, 0 ],
        [ 4, 5 ],
        [ 5, 6 ],
        [ 6, 7 ],
        [ 7, 4 ],
        [ 0, 4 ],
        [ 1, 5 ],
        [ 2, 6 ],
        [ 3, 7 ]]

    def draw_sample_line(self):
        # red line cube
        glColor4f(1.0, 0.0, 0.0, 0.75)
        glBegin(GL_LINES)
        for i in range(0, 4):
            glVertex(self.vertex[self.edge[i][0]])
            glVertex(self.vertex[self.edge[i][1]])
        glEnd()
    
    def draw_sample_quad(self):
        glColor4f(1.0, 0.0, 0.0, 0.75)
        glBegin(GL_QUADS)
        glVertex3f(0,0,0)
        glVertex3f(1,0,0)
        glVertex3f(1,1,0)
        glVertex3f(0,1,0)
        glEnd()

        glColor4f(0.0, 0.0, 1.0, 0.75)
        glBegin(GL_QUADS)
        glVertex3f(0,0,1)
        glVertex3f(1,0,1)
        glVertex3f(1,1,1)
        glVertex3f(0,1,1)
        glEnd()    

        glColor4f(0.0, 1.0, 0.0, 0.75)
        glBegin(GL_QUADS)
        glVertex3f(0,0,1)
        glVertex3f(0,0,0)
        glVertex3f(0,1,0)
        glVertex3f(0,1,1)
        glEnd()   

        glColor4f(1.0, 1.0, 0.0, 0.75)
        glBegin(GL_QUADS)
        glVertex3f(1,0,1)
        glVertex3f(1,0,0)
        glVertex3f(1,1,0)
        glVertex3f(1,1,1)
        glEnd() 

    def set_draw_grid_wh_param(self,width,height,gridsize):
        self.gridsize = gridsize
        q, r = divmod(width, gridsize)
        gridmax = q + bool(r) #ceiling
        self.gridmaxwidth = gridmax*gridsize

        q, r = divmod(height, gridsize)
        gridmax = q + bool(r) #ceiling
        self.gridmaxheight = gridmax*gridsize
        #print(self.gridmaxwidth, self.gridmaxheight)

        # set camera do that the layout is center to the screen
        self.camPos[0] = width/2
        self.camPos[1] = -height/2


        self.enable_draw_grid_wh = True
        self.update()

    def draw_grid_wh(self):
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



    def draw_grid(self):
        totalline=100
        grid_size=10
        glColor3f(1,1,1) # white        
        for i in range(0,totalline*2,grid_size): #from 0,0 to t,t
            glPushMatrix()
            if i < totalline:
                glTranslated(0,0,i)
            else:
                glTranslated(i-totalline,0,0)
                glRotated(-90, 0.0, 1.0, 0.0)


            glBegin(GL_LINES)

            #glLineWidth(1)
            glVertex3f(0,-0.1,0)
            glVertex3f(totalline-grid_size,-0.1,0)
            glEnd()

            glPopMatrix()


    def resizeGL(self, width, height):
        #print("width, height: ", width, height)
        side = min(width, height)
        glViewport((width - side) // 2, (height - side) // 2, side, side)
        
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        #gluPerspective(60, width/height, 1.0, 1000)
        if height==0:
            gluPerspective(60, 1, 100.0, 2000)
        else:
            gluPerspective(60, width/height, 100.0, 2000)
        
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

        elif event.buttons() == Qt.RightButton:
            self.camPos[0] -=  dx * pos_move_mul
            self.camPos[1] +=  dy * pos_move_mul
        #print(self.camPos)
        self.__lastPos = event.pos()
        self.update()
    
    def wheelEvent(self,event):
        
        numAngle = float(event.angleDelta().y()) / 10#120
        self.camPos[2] -= numAngle
        #print(self.camPos)
        self.update()

    def initializeGL(self):
        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
        glEnable(GL_DEPTH_TEST)
        # glEnable(GL_LIGHTING)
        # glEnable(GL_LIGHT0)
        # glEnable(GL_COLOR_MATERIAL)
        # glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE )
        #glShadeModel(GL_SMOOTH)

        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClearDepth(1.0)

        
        # glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 1])
        # glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1])          
        #glLightfv(GL_LIGHT0, GL_AMBIENT, [0.5, 0.5, 0.5, 1])
        #glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1])  

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(40.0, 1.0, 1.0, 30.0)

   
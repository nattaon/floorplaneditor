from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtWidgets import  QWidget
from PyQt5.QtCore import Qt, QLineF, QPointF, QRectF
import numpy as np
from math import sqrt

class LabelPixmap(QWidget):
    def __init__(self):
        super(LabelPixmap, self).__init__()
        self.wallcolor = Qt.green

        self.rawimgpixmap = None # keep raw image
        self.imgpixmap = None # keep raw image
        self.currentpixmap = None # keep last stage of drawing
        self.temppixmap = None # keep temp drawing
        self.linetxtpixmap = None

        self.label_img1 = None
        self.label_img2 = None
        #self.setMouseTracking(True)
        self.editmode = None

        self.mergeline =[]

    def onWallLineItemClicked(self, it, col):
        print("click", it, col, it.text(col))
        self.drawtemp_addline(int(it.text(1)), int(it.text(2)), int(it.text(3)), int(it.text(4)), Qt.yellow, self.currentpixmap)


    def set_temppixmap(self):
        # print("rawimgpixmap", 0 if self.rawimgpixmap==None else 1)
        # print("imgpixmap", 0 if self.imgpixmap==None else 1)
        # print("currentpixmap", 0 if self.currentpixmap==None else 1)
        # print("temppixmap", 0 if self.temppixmap==None else 1)
        self.temppixmap=self.currentpixmap.copy()

    def getimgpixmap(self):
        return self.imgpixmap

    def getimgpixmap_wh(self):
        return self.imgpixmap.width(),self.imgpixmap.height()  

    def enter_addline_mode(self):
        self.editmode = "addline"

    def enter_removeline_mode(self):
        self.editmode = "removeline"        

    def enter_mergelines_mode(self):
        self.editmode = "mergelines"

    def enter_joincorner_mode(self):
        self.editmode = "joincorner"

    def exit_mode(self):
        self.editmode = None
        self.mergeline =[]
        self.revert_pixmap(self.currentpixmap)

    def PressMouse(self , event):
        x = event.pos().x()
        y = event.pos().y() 
        print("press ",x,y)
        self.mousestartx=x
        self.mousestarty=y
        self.mergeline =[]
        self.removelines =[]
        self.linesextendinfo=[]

    def MoveMouse(self , event):
        x = event.pos().x()
        y = event.pos().y() 
        #print("move ",x,y)  

        if self.editmode == None:
            pass
        elif self.editmode == "addline":    
            self.drawtemp_addline(self.mousestartx, self.mousestarty, x,y, Qt.magenta, self.currentpixmap)  

        elif self.editmode == "removeline":    
            self.drawtemp_rectangle(self.mousestartx, self.mousestarty, x,y,Qt.yellow)   
            hilightlinesinfo = self.get_hilighlines_in_temprectangle(self.mousestartx,self.mousestarty,x,y,"line")
            if len(hilightlinesinfo)>0:
                self.drawtemp_hilightlinesinfo(hilightlinesinfo, Qt.green, self.temppixmap)
                self.removelines=hilightlinesinfo

        elif self.editmode == "mergelines":   
            self.drawtemp_rectangle(self.mousestartx, self.mousestarty, x,y,Qt.yellow)  
            hilightlinesinfo = self.get_hilighlines_in_temprectangle(self.mousestartx,self.mousestarty,x,y,"line")
            if len(hilightlinesinfo)>0:
                self.drawtemp_hilightlinesinfo(hilightlinesinfo, Qt.green, self.temppixmap)
                mx1,my1,mx2,my2, linescomponent = self.cal_mergealign_hilightlines(hilightlinesinfo)
                self.mergeline = [mx1,my1,mx2,my2]
                #print("draw ",mx1,my1,mx2,my2)
                self.drawtemp_addline(mx1,my1,mx2,my2, Qt.magenta, self.temppixmap) 
                self.linescomponent=linescomponent

        elif self.editmode == "joincorner":   
            self.drawtemp_rectangle(self.mousestartx, self.mousestarty,x,y,Qt.yellow)  
            hilightlinesinfo = self.get_hilighlines_in_temprectangle(self.mousestartx,self.mousestarty,x,y,"part")
            if len(hilightlinesinfo)==2:
                self.drawtemp_hilightlinesinfo(hilightlinesinfo, Qt.green, self.temppixmap)
                linesextendinfo = self.cal_extend_hilightlines(hilightlinesinfo)
                #print(linesextend)
                if(len(linesextendinfo)==2):
                    self.drawtemp_hilightlinesinfo(linesextendinfo, Qt.magenta, self.temppixmap)
                    self.linesextendinfo = linesextendinfo
                    #self.drawtemp_addlines(linesextend, Qt.magenta, self.temppixmap)
                    #self.drawtemp_addline(linesextend[0][0],linesextend[0][1],linesextend[0][2],linesextend[0][3], Qt.magenta, self.temppixmap) 
                    #self.drawtemp_addline(linesextend[1][0],linesextend[1][1],linesextend[1][2],linesextend[1][3], Qt.magenta, self.temppixmap) 
        else:#
            print("error editmode not match")    
        

    def ReleaseMouse(self , event):
        x = event.pos().x()
        y = event.pos().y() 
        print("release ",x,y)


        if self.editmode == None:
            pass
        elif self.editmode == "addline":    
            self.drawnewline(self.mousestartx,self.mousestarty,x,y, self.wallcolor)  
            self.LinesWidget.addnewline([self.mousestartx,self.mousestarty,x,y])

        elif self.editmode == "removeline":  
            self.revert_pixmap(self.currentpixmap)
            self.removelines
            self.LinesWidget.removelines(self.removelines)
            lines = self.LinesWidget.getlines()
            self.drawpermanentlines(lines)            

        elif self.editmode == "mergelines":   
            self.revert_pixmap(self.currentpixmap)
            if(len(self.mergeline)>0):
                self.drawnewline(self.mergeline[0],self.mergeline[1],self.mergeline[2],self.mergeline[3], self.wallcolor) 
                self.LinesWidget.addnewline(self.mergeline)
                #for line in self.linescomponent:
                #    print(line)             
                self.LinesWidget.removelines(self.linescomponent)

                lines = self.LinesWidget.getlines()
                self.drawpermanentlines(lines)

        elif self.editmode == "joincorner":   
            self.revert_pixmap(self.currentpixmap)
            if(len(self.linesextendinfo)==2):
                self.LinesWidget.editlinevalue(self.linesextendinfo)
                lines = self.LinesWidget.getlines()
                self.drawpermanentlines(lines)            
        else:
            print("error editmode not match")   

    def cal_extend_hilightlines(self,hilightlinesinfo):

        l1 = QLineF(hilightlinesinfo[0][1],hilightlinesinfo[0][2],hilightlinesinfo[0][3],hilightlinesinfo[0][4])
        l2 = QLineF(hilightlinesinfo[1][1],hilightlinesinfo[1][2],hilightlinesinfo[1][3],hilightlinesinfo[1][4])  

        

        # p1 = QPointF(mostleft,mosttop) #" along U direction"
        # p2 = QPointF(mostleft,mostdown)
        # p3 = QPointF(mostright,mostdown)
        # p4 = QPointF(mostright,mosttop)

        # p_center_l1 = QPointF((l1.p1().x()+l1.p2().x())/2,(l1.p1().y()+l1.p2().y())/2)
        # p_center_l2 = QPointF((l2.p1().x()+l2.p2().x())/2,(l2.p1().y()+l2.p2().y())/2)

  

        # total_dist_to_p1 = QLineF(p_center_l1, p1).length() + QLineF(p_center_l2, p1).length()
        # total_dist_to_p2 = QLineF(p_center_l1, p2).length() + QLineF(p_center_l2, p2).length()
        # total_dist_to_p3 = QLineF(p_center_l1, p3).length() + QLineF(p_center_l2, p3).length()
        # total_dist_to_p4 = QLineF(p_center_l1, p4).length() + QLineF(p_center_l2, p4).length()

        #print(total_dist_to_p1,total_dist_to_p2,total_dist_to_p3,total_dist_to_p4)

        line1 = [[hilightlinesinfo[0][1],hilightlinesinfo[0][2]],[hilightlinesinfo[0][3],hilightlinesinfo[0][4]]]
        line2 = [[hilightlinesinfo[1][1],hilightlinesinfo[1][2]],[hilightlinesinfo[1][3],hilightlinesinfo[1][4]]]
        ix,iy = self.line_intersection(line1,line2)
        if ix<0 or iy<0:
            return []

        ipoint = QPointF(ix,iy)

        dist_l1_p1= QLineF(ipoint, l1.p1()).length()
        dist_l1_p2= QLineF(ipoint, l1.p2()).length()

        dist_l2_p1= QLineF(ipoint, l2.p1()).length()
        dist_l2_p2= QLineF(ipoint, l2.p2()).length()  

        if dist_l1_p1 >= dist_l1_p2:
            newl1info = [hilightlinesinfo[0][0],l1.p1().x(),l1.p1().y(), ix,iy,hilightlinesinfo[0][5]] # extend p2 by ix,iy
        else:
            newl1info = [hilightlinesinfo[0][0],ix,iy,l1.p2().x(),l1.p2().y(),hilightlinesinfo[0][5] ] # extend p1 by ix,iy

        if dist_l2_p1 >= dist_l2_p2:
            newl2info = [hilightlinesinfo[1][0],l2.p1().x(),l2.p1().y(), ix,iy,hilightlinesinfo[1][5]] # extend p2
        else:
            newl2info = [hilightlinesinfo[1][0],ix,iy,l2.p2().x(),l2.p2().y() ,hilightlinesinfo[1][5]] # extend p1

        return [newl1info,newl2info]

        #QPointF intersect
        #intersectpoint = QPointF()
        #intersectpoint = l1.intersect(l2,intersectpoint) # this return IntersectType(enum) not intersection point
        #print(intersectpoint)
        #return [ix,iy,l1.p1().x(),l1.p1().y() ]

    def line_intersection(self, line1, line2):
        #https://stackoverflow.com/questions/20677795/how-do-i-compute-the-intersection-point-of-two-lines
        xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
        ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

        def det(a, b):
            return a[0] * b[1] - a[1] * b[0]

        div = det(xdiff, ydiff)
        if div == 0:
            #print('lines do not intersect')
            return -1,-1

        d = (det(*line1), det(*line2))
        x = det(d, xdiff) / div
        y = det(d, ydiff) / div
        return x, y

    def cal_mergealign_hilightlines(self,hilightlinesinfo):
        mostleft=999
        mosttop=999
        mostright=0
        mostdown=0
        list_x=[]
        list_y=[]
        for index,lx1,ly1,lx2,ly2,direction in hilightlinesinfo:
            if direction == 'p':
                pass
            elif direction == 'v' or direction == 'nv':
                #num_v=num_v+1
                half_len = int(abs(ly1-ly2)/2)
                list_x.extend([lx1]*half_len)
                list_x.extend([lx2]*half_len)
            elif direction == 'h' or direction == 'nh':
                #num_h=num_h+1
                half_len = int(abs(lx1-lx2)/2)
                list_y.extend([ly1]*half_len)
                list_y.extend([ly2]*half_len)                
            else:
                continue

            mostleft = self.get_lower(mostleft,lx1)
            mostleft = self.get_lower(mostleft,lx2)
            mostright = self.get_higher(mostright,lx1)
            mostright = self.get_higher(mostright,lx2)
            mosttop = self.get_lower(mosttop,ly1)
            mosttop = self.get_lower(mosttop,ly2)
            mostdown = self.get_higher(mostdown,ly1)
            mostdown = self.get_higher(mostdown,ly2)  
  
        avg_x, _ = self.mode1(np.array(list_x))
        avg_y, _ = self.mode1(np.array(list_y))
        # print()
        # print("avg_x,avg_y: ", avg_x,avg_y)
        # print("len list_x,list_y: ", len(list_x),len(list_y))
        # print("left,right: ",mostleft, mostright)
        # print("top,down: ",mosttop, mostdown)

        if(len(list_x) <= len(list_y)): # horizontal line
            #print("horizontal line")
            linescomponent = [line for line in hilightlinesinfo if (line[5]== 'h' or line[5]== 'nh' or line[5]== 'p' or line[5]== 'd')]
            return mostleft,avg_y,mostright,avg_y, linescomponent
            #self.drawtemp_addline(mostleft,avg_y,mostright,avg_y, Qt.magenta)  
            #self.LinesWidget.addnewline([mostleft,avg_y,mostright,avg_y])
        else: #vertical line
            #print("vertical line")
            linescomponent = [line for line in hilightlinesinfo if (line[5]== 'v' or line[5]== 'nv' or line[5]== 'p' or line[5]== 'd')]
            return avg_x,mosttop,avg_x,mostdown, linescomponent
            #self.drawtemp_addline(avg_x,mosttop,avg_x,mostdown, Qt.magenta)  
            #self.LinesWidget.addnewline([avg_x,mosttop,avg_x,mostdown])



    def mode1(self,x):
        if len(x) == 0:
            return 0,0
        values, counts = np.unique(x, return_counts=True)
        m = counts.argmax()
        return values[m], counts[m] 

    def get_lower(self,a,b):
        return a if a <=b else b
    def get_higher(self,a,b):
        return a if a >=b else b

    def get_hilighlines_in_temprectangle(self,rec_x1,rec_y1,rec_x2,rec_y2, mode):
        linesinfo = self.LinesWidget.getlinesindex_position()
        # swap rec position x1,y1 to near origin
        rec_left,rec_right = self.swap_low_to_high(rec_x1,rec_x2) # left is near origin
        rec_top,rec_down = self.swap_low_to_high(rec_y1,rec_y2)   # top is near origin
        #print("rec x",rec_left,rec_right)  
        #print("rec y",rec_top,rec_down)  
        hilightlinesinfo=[]
        if mode =="line":
            for index,lx1,ly1,lx2,ly2,direction in linesinfo:
                if self.check_line_in_rectangle(lx1,ly1,lx2,ly2,rec_left,rec_right,rec_top,rec_down):
                    hilightlinesinfo.append([index,lx1,ly1,lx2,ly2,direction])
        elif mode == "part":
            for index,lx1,ly1,lx2,ly2,direction in linesinfo:
                if self.check_linepart_in_rectangle(lx1,ly1,lx2,ly2,rec_left,rec_right,rec_top,rec_down):
                    hilightlinesinfo.append([index,lx1,ly1,lx2,ly2,direction])
        else:
            print("error don't know mode")   

        return hilightlinesinfo      

    def check_linepart_in_rectangle(self, lx1,ly1,lx2,ly2, rec_left,rec_right,rec_top,rec_down):
        if rec_left <= lx1 and lx1 <= rec_right and rec_top <= ly1 and ly1 <= rec_down:
            return True
        elif rec_left <= lx2 and lx2 <= rec_right and rec_top <= ly2 and ly2 <= rec_down:
            return True
        else:
            return False

    def check_line_in_rectangle(self, lx1,ly1,lx2,ly2, rec_left,rec_right,rec_top,rec_down):
        if lx1 < rec_left or lx2 < rec_left:
            return False
        elif ly1 < rec_top or ly2 < rec_top:
            return False
        elif lx1 > rec_right or lx2 > rec_right:
            return False
        elif ly1 > rec_down or ly2 > rec_down:
            return False
        else:
            return True

    def swap_low_to_high(self,a,b):
        if a<=b:
            return a,b
        else:
            return b,a

    def revert_pixmap(self, refpixmap):
        if refpixmap is None:
            print("please cal hough before select area ")
            return        
        self.label_img2.setPixmap(refpixmap) 

    def setlabelimg(self,label_img1, label_img2):
        self.label_img1 = label_img1
        self.label_img2 = label_img2
        
        # Event register on the 2nd image only
        self.label_img2.mousePressEvent = self.PressMouse 
        self.label_img2.mouseReleaseEvent = self.ReleaseMouse 
        self.label_img2.mouseMoveEvent = self.MoveMouse 

    def setLinesWidget(self, linewidget):
        self.LinesWidget = linewidget


    def loadimage_bothlabels(self, imgpath):
        #print(imgpath)
        self.rawimgpixmap = QPixmap(imgpath)   
        self.imgpixmap = QPixmap(imgpath)  
        self.reloadimage()

    def loadimage_predictlabel(self, imgpath):
        print(imgpath) 
        self.imgpixmap = QPixmap(imgpath)  
        self.currentpixmap = self.imgpixmap
        self.reloadimage()

    def reloadimage(self):
        if self.imgpixmap is None:
            print("Error! self.imgpixmap is None ")
        elif self.label_img1 is None:
            print("Error! self.label_img1 is None ")        
        elif self.label_img2 is None:
            print("Error! self.label_img2 is None ")                    
        else:
            self.label_img1.setPixmap(self.rawimgpixmap)
            self.label_img2.setPixmap(self.imgpixmap)
            #pixelScale=2.0
            #self.imgpixmap = self.imgpixmap.scaled(pixelScale,pixelScale,Qt.KeepAspectRatio)

    def saveimage_currentpixmap(self,outputpath):
        self.currentpixmap.save(outputpath,"PNG",100);
        pass

    def drawlinesforsave(self, lines, img_width, img_height, outputpath):
        savepixmap = QPixmap(img_width,img_height)  
        savepixmap.fill((QColor('black')))

        qp = QPainter(savepixmap)
        pen = QPen(self.wallcolor, 1, Qt.SolidLine) 
        qp.setPen(pen)
        for line in lines:
            if len(line) == 1 :
                qp.drawLine(line[0][0], line[0][1], line[0][2], line[0][3])
            else:
                qp.drawLine(line[0], line[1], line[2], line[3])
        qp.end() 
        savepixmap.save(outputpath,"PNG",100);       

    def drawpermanentlines(self, lines):
        newpixmap = self.imgpixmap.copy()

        qp = QPainter(newpixmap)
        #qp.begin(self)
        pen = QPen(self.wallcolor, 1, Qt.SolidLine)      
        qp.setPen(pen)
        #print(len(lines))
        for line in lines:
            if len(line) == 1 :
                qp.drawLine(line[0][0], line[0][1], line[0][2], line[0][3])
            else:
                qp.drawLine(line[0], line[1], line[2], line[3])

        qp.end()

        self.label_img2.setPixmap(newpixmap)     
        self.currentpixmap = newpixmap

    def drawtemp_hilightlinesinfo(self,linesinfo, color, refpixmap):
        if refpixmap is None:
            print("no refpixmap ")
            return
        pixmaptemp = refpixmap.copy()
        qp = QPainter(pixmaptemp)
        pen = QPen(color, 1, Qt.SolidLine)      
        qp.setPen(pen)
        for index,x1,y1,x2,y2,direction in linesinfo:
            qp.drawLine(x1,y1,x2,y2)
        qp.end()
        self.label_img2.setPixmap(pixmaptemp)   
        self.temppixmap = pixmaptemp

    def drawtemp_addline(self,x1,y1,x2,y2, color, refpixmap):
        if refpixmap is None:
            print("no refpixmap ")
            return
        pixmaptemp = refpixmap.copy()
        qp = QPainter(pixmaptemp)
        pen = QPen(color, 1, Qt.SolidLine)      
        qp.setPen(pen)
        qp.drawLine(x1,y1,x2,y2)
        qp.end()
        self.label_img2.setPixmap(pixmaptemp) 

    def drawtemp_addlines(self,lines, color, refpixmap):
        if refpixmap is None:
            print("no refpixmap ")
            return
        pixmaptemp = refpixmap.copy()
        qp = QPainter(pixmaptemp)
        pen = QPen(color, 1, Qt.SolidLine)      
        qp.setPen(pen)
        for x1,y1,x2,y2 in lines:
            qp.drawLine(x1,y1,x2,y2)
        qp.end()
        self.label_img2.setPixmap(pixmaptemp) 

    def drawnewline(self,x1,y1,x2,y2, color):
        newpixmap = self.currentpixmap.copy()
        qp = QPainter(newpixmap)
        pen = QPen(color, 1, Qt.SolidLine)      
        qp.setPen(pen)
        qp.drawLine(x1,y1,x2,y2)
        qp.end()
        self.label_img2.setPixmap(newpixmap) 
        self.currentpixmap = newpixmap

    def drawtemp_rectangle(self,mousestartx, mousestarty, mouseposx, mouseposy, color):
        if self.currentpixmap is None:
            print("please cal hough before select area ")
            return
        pixmaptemp = self.currentpixmap.copy()
        qp = QPainter(pixmaptemp)
        pen = QPen(color, 1, Qt.DashDotLine)      
        qp.setPen(pen)
        #qp.drawLine(self.mousestartx, self.mousestarty, mouseposx, mouseposy)
        w = mouseposx-mousestartx
        h = mouseposy- mousestarty
        #qp.drawLine(self.mousestartx, self.mousestarty, self.mousestartx, self.mousestarty)
        qp.drawLine(mousestartx, mousestarty, mousestartx+w, mousestarty)
        qp.drawLine(mousestartx, mousestarty, mousestartx, mousestarty+h)
        qp.drawLine(mouseposx, mouseposy, mouseposx-w, mouseposy)
        qp.drawLine(mouseposx, mouseposy, mouseposx, mouseposy-h)
        qp.end()

        self.label_img2.setPixmap(pixmaptemp)     
        self.temppixmap = pixmaptemp

    def cal_line_center(self,x1,y1,x2,y2):
        return (x1+x2)/2, (y1+y2)/2

    def cal_line_length(self,x1,y1,x2,y2):
        sumsquar = (x1-x2)*(x1-x2) + (y1-y2)*(y1-y2)
        return sqrt(sumsquar)   

    def draw_lines_whitebg(self):
        pixmaptemp = QPixmap(self.currentpixmap.width(),self.currentpixmap.height())  
        pixmaptemp.fill((QColor('white')))

        qp = QPainter(pixmaptemp)
        pen = QPen(Qt.black, 1, Qt.SolidLine) 
        qp.setPen(pen)
        lines = self.LinesWidget.getlines()
        for line in lines:
            if len(line) == 1 :
                qp.drawLine(line[0][0], line[0][1], line[0][2], line[0][3])
            else:
                qp.drawLine(line[0], line[1], line[2], line[3])
        qp.end() 
        self.label_img2.setPixmap(pixmaptemp)   
        self.currentpixmap = pixmaptemp

    def draw_lines_length(self):
        self.draw_lines_whitebg()
        #lines = self.LinesWidget.getlines()

        linesinfo = self.LinesWidget.getlinesindex_position()

        pixmaptemp = self.currentpixmap.copy()
        print("image size: ",pixmaptemp.width(),pixmaptemp.height())
        painter = QPainter(pixmaptemp)
        #painter.rotate(-60)
        pen = QPen(self.wallcolor, 1, Qt.DashDotLine)      
        painter.setPen(pen)

        for ind,x1,y1,x2,y2,direction in linesinfo:
            #print(self.cal_line_center(x1,y1,x2,y2), self.cal_line_length(x1,y1,x2,y2))
            xc,yc=self.cal_line_center(x1,y1,x2,y2)
            linelen = self.cal_line_length(x1,y1,x2,y2)/100
            txt_linelen = str(linelen)# + " m."
            print(xc,yc,txt_linelen,len(txt_linelen))
            #rect = QRectF(x1,y1,x2-x1,y2-y1)
            #painter.drawText(rect, Qt.AlignCenter, txt_linelen) # nothingshown because width, height of rec = 1
            
            textwsize=len(txt_linelen)*7

            if direction=="h": # keep text not outbound the top line 
                xc = xc - textwsize/2
                if yc<12:
                    yc=yc+12
                else:
                    yc=yc-1 # move it up 1px to not occlude a line
                
            elif direction=="v": # keep text not outbound the right line
                
                #print("textwsize",textwsize)
                if xc+textwsize > pixmaptemp.width():
                    xc=xc-textwsize 
                else:
                    xc = xc+1 # move it right 1px
            else:
                pass

            if linelen>0.3:
                painter.drawText(xc,yc, txt_linelen)
        #painter.drawText(100,100, "Hello PyQt5 App Development")
        painter.end()
        self.label_img2.setPixmap(pixmaptemp)   
        self.currentpixmap = pixmaptemp
        #self.linetxtpixmap = pixmaptemp


        
  
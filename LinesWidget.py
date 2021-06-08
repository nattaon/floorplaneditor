from PyQt5.QtWidgets import QWidget, QTreeWidgetItem
from PyQt5.QtCore import Qt

class LinesWidget(QWidget):
    def __init__(self):
        super(LinesWidget, self).__init__()
        self.lines_treeWidget = None

    def settreewidget(self, treeWidget):
        self.lines_treeWidget = treeWidget
        self.lines_treeWidget.header().show()
        self.lines_treeWidget.header().resizeSection(0, 30)
        self.lines_treeWidget.header().resizeSection(1, 42)
        self.lines_treeWidget.header().resizeSection(2, 42)
        self.lines_treeWidget.header().resizeSection(3, 42)
        self.lines_treeWidget.header().resizeSection(4, 42)
        self.lines_treeWidget.header().resizeSection(5, 20)
        #self.lines_treeWidget.header().setStretchLastSection(True)

        # uncheck rootIsDecorated in the QTdesigner so that the white space on the fist column gone
    def getlinesindex_position(self):
        linesinfo=[]
        totallines = self.lines_treeWidget.topLevelItemCount()
        for i in range(totallines):
            item = self.lines_treeWidget.topLevelItem(i)
            linesinfo.append([int(item.text(0)),int(item.text(1)),int(item.text(2)),int(item.text(3)),int(item.text(4)),item.text(5)])
        return linesinfo

    def getpoints(self):
        points=[]
        totallines = self.lines_treeWidget.topLevelItemCount()
        for i in range(totallines):
            item = self.lines_treeWidget.topLevelItem(i)
            points.append([int(item.text(1)),int(item.text(2))])
            points.append([int(item.text(3)),int(item.text(4))])
        return points

    def getlines(self):
        lines=[]
        totallines = self.lines_treeWidget.topLevelItemCount()
        for i in range(totallines):
            item = self.lines_treeWidget.topLevelItem(i)
            lines.append([int(item.text(1)),int(item.text(2)),int(item.text(3)),int(item.text(4))])
        return lines


    def removelines(self, linesinfo):
        if len(linesinfo) == 0:
            return
        root = self.lines_treeWidget.invisibleRootItem()

        reverse_linesinfo = linesinfo[::-1] # to delete from the lastest one
        for index,lx1,ly1,lx2,ly2,direction in reverse_linesinfo:
            item = self.lines_treeWidget.topLevelItem(index-1)
            root.removeChild(item)

        #reindex       
        totallines = self.lines_treeWidget.topLevelItemCount()
        for i in range(totallines):
            item = self.lines_treeWidget.topLevelItem(i)
            item.setText(0, "%d" % (i+1))

    def editlinevalue(self, linesinfo):
        if len(linesinfo) == 0:
            return       
        for index,lx1,ly1,lx2,ly2,direction in linesinfo:
            item = self.lines_treeWidget.topLevelItem(index-1)
            item.setText(1, "%d" % lx1)
            item.setText(2, "%d" % ly1)
            item.setText(3, "%d" % lx2)
            item.setText(4, "%d" % ly2)          

    def addlines(self, lines):
        #self.clearlines()
        for id, line in enumerate(lines,1): #start id from 1
            #print(line,len(line))
            if len(line)==1:
                line = line[0] # return from hough function [[  8 812   8 269]] 1
            else:
                pass #return from custom function [850, 567, 850, 570] 4

            currentLine = QTreeWidgetItem(self.lines_treeWidget)
            #currentLine.setChildIndicatorPolicy(QTreeWidgetItem.DontShowIndicator) # help nothing
            #currentLine.setTextAlignment(0,Qt.AlignCenter)
            currentLine.setText(0, "%d" % id)
            
            currentLine.setText(1, "%d" % line[0])
            currentLine.setText(2, "%d" % line[1])
            currentLine.setText(3, "%d" % line[2])
            currentLine.setText(4, "%d" % line[3])
            direction = self.checklinedirection(line[0],line[1],line[2],line[3])            
            currentLine.setText(5, direction)

    def addnewline(self,line):

        totallines = self.lines_treeWidget.topLevelItemCount()
        id=totallines+1     

        currentLine = QTreeWidgetItem(self.lines_treeWidget)
        currentLine.setText(0, "%d" % id)
        currentLine.setText(1, "%d" % line[0])
        currentLine.setText(2, "%d" % line[1])
        currentLine.setText(3, "%d" % line[2])
        currentLine.setText(4, "%d" % line[3])
        direction = self.checklinedirection(line[0],line[1],line[2],line[3])
        
        currentLine.setText(5, direction)                

    def clearlines(self):
        self.lines_treeWidget.clear()

    def checklinedirection(self,x1,y1,x2,y2):

        diffx = abs(x1-x2)
        diffy = abs(y1-y2)
        #print(diffx, diffy)
        if diffx == 0 and diffy == 0:
            return "p" #point
        elif diffx == diffy:
            return "d" # diagonal
        elif diffx == 0:
            return "v" # vertical
        elif diffy == 0:
            return "h" # horizontal
        elif diffx > diffy: # y=0
            #print(diffx, diffy,diffx/diffy,"nh")
            if diffx/diffy <4.0:
                return "d" # diagonal
            else:
                return "nh" # near horizontal
        elif diffy > diffx:
            #print(diffx, diffy,diffy/diffx,"nv")
            if diffy/diffx <4.0:
                return "d" # diagonal
            else:
                return "nv" # near vertical            
        else:
            return "error"



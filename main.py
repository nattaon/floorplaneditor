import sys
from PyQt5 import uic, QtWidgets
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtGui import QPainter, QPen, QPalette
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QProgressDialog, \
        QWidget, QTreeWidgetItem, QPushButton, QHBoxLayout, QVBoxLayout, QSizePolicy,  \
        QFileSystemModel
from PyQt5.QtCore import Qt, QDir 
from PyQt5 import QtCore
import numpy as np

#import cv2

from LineDectection import LineDectection
from LabelPixmap import LabelPixmap
from LinesWidget import LinesWidget
from HoughParamController import HoughParamController
from CustomParamController import CustomParamController
from MergeParamController import MergeParamController
from DragDropImage import DragDropImage
from Widget3Dview import Widget3Dview
from Widget3Dview2 import Widget3Dview2
from BatchProcessing import BatchProcessing
from tfpredict import tfpredict

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__() # Call the inherited classes __init__ method
        uic.loadUi('opencv_py_hough2.ui', self) # Load the .ui file
        self.imgpath = None
        self.predictimgpath = None
      
        # Link scrollarea and label(display pixmap), to be able to move along the whole image area 
        def init_scroll_label(scrolla,label):
            label.setBackgroundRole(QPalette.Base)
            label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
            label.setScaledContents(True)

            scrolla.setBackgroundRole(QPalette.Dark)
            scrolla.setWidget(label)
            scrolla.setVisible(True)
            scrolla.setWidgetResizable(False); #  if set true the image will very small, and no scrollbar appear  

        init_scroll_label(self.scrollArea_img1,self.label_img1)        
        init_scroll_label(self.scrollArea_img2,self.label_img2)    
        ########################################################################################################

        # Link 2 scrollareas, if one changes scroll position, another will follow the same position
        def update_other_scroll(value, otherscroll):
            otherscroll.setValue(value)

        self.scrollArea_img1.verticalScrollBar().valueChanged.connect(lambda value: update_other_scroll(value, self.scrollArea_img2.verticalScrollBar()))
        self.scrollArea_img1.horizontalScrollBar().valueChanged.connect(lambda value: update_other_scroll(value, self.scrollArea_img2.horizontalScrollBar()))
        self.scrollArea_img2.verticalScrollBar().valueChanged.connect(lambda value: update_other_scroll(value, self.scrollArea_img1.verticalScrollBar()))
        self.scrollArea_img2.horizontalScrollBar().valueChanged.connect(lambda value: update_other_scroll(value, self.scrollArea_img1.horizontalScrollBar()))
        ########################################################################################################

        # Enable Drag & Drop Event, to open the image by just droping it to the window
        self.DragDropImage = DragDropImage(self)

        # To keep lines as a list on the rightside widget
        self.LinesWidget = LinesWidget()
        self.LinesWidget.settreewidget(self.lines_treeWidget)
        #self.widget_control.setBackgroundRole(QPalette.Dark)

        # Checking mouse stage and draw,edit,remove lines on the label_img
        self.LabelPixmap = LabelPixmap()
        self.LabelPixmap.setlabelimg( self.label_img1, self.label_img2)
        self.LabelPixmap.setLinesWidget(self.LinesWidget)

        # Automatic line detection functions
        self.LineDectection = LineDectection()     

        # Draw 3D walls from lines
        self.Widget3Dview = Widget3Dview(self)
        self.Widget3Dview2 = Widget3Dview2(self)

        # Convert histogram image input to a wall labeled output
        self.tfpredict = tfpredict()

        # Slidebar for adjusting Hough line detection parameter
        self.HoughParamController = HoughParamController(self)
        self.HoughParamController.setparam(pixel=1, threshold=10, minlinelength=10, maxlinegap=5)
        self.HoughParamController.setslider(self.HSlider_pixel, self.HSlider_thres, self.HSlider_minlen, self.HSlider_maxgap)
        self.HoughParamController.setlineedit(self.lineEdit_pixel, self.lineEdit_thres, self.lineEdit_minlen, self.lineEdit_maxgap)
        self.HoughParamController.setup_slider_lineedit_callback()

        # Slidebar for adjusting Custom line detection parameter
        self.CustomParamController = CustomParamController(self)
        self.CustomParamController.setparam(minlinelength=5, maxlinegap=5)
        self.CustomParamController.setslider(self.HSlider_minlen_custom, self.HSlider_maxgap_custom)
        self.CustomParamController.setlineedit(self.lineEdit_minlen_custom, self.lineEdit_maxgap_custom)
        self.CustomParamController.setup_slider_lineedit_callback()

        self.MergeParamController = MergeParamController(self)
        self.MergeParamController.setparam(nearby=5, maxspace=20, cornerrad=50)
        self.MergeParamController.setslider(self.HSlider_nearby, self.HSlider_maxspace, self.HSlider_cornerrad)
        self.MergeParamController.setlineedit(self.lineEdit_nearby, self.lineEdit_maxspace, self.lineEdit_cornerrad)
        self.MergeParamController.setup_slider_lineedit_callback()


        # Detect line all images in a specify folder
        self.BatchProcessing = BatchProcessing(self)       
        self.actioncalline_save.triggered.connect(self.BatchProcessing.batch_save_calline_folder)
        self.actionmergeline_save.triggered.connect(self.BatchProcessing.batch_save_mergeline_folder)
        self.actionjoincorner_save.triggered.connect(self.BatchProcessing.batch_save_joincorner_folder)
        self.actionlayout_textsize_save.triggered.connect(self.BatchProcessing.batch_save_layouttext_folder)



        # Link menus & buttons to its function
        self.actionLoad_image.triggered.connect(self.pickfile)
        self.actionReset_layout.triggered.connect(self.button_reset)
        self.actionPredict_Layout.triggered.connect(self.predict_layout)

        self.pushButton_houghcal.clicked.connect(self.button_calculate_hough_show)
        self.pushButton_cal_sp_line.clicked.connect(self.button_calculate_custom_spline_show)

        self.pushButton_merge_sp_line.clicked.connect(self.button_calculate_custom_mergespline_show)
        self.pushButton_merge_corner.clicked.connect(self.button_calculate_custom_joincorner_show)

        self.pushButton_saveimage.clicked.connect(self.button_saveimage)
        self.pushButton_resetlines.clicked.connect(self.button_reset)
        self.pushButton_show3D.clicked.connect(self.Widget3Dview.open_3d_window)
        self.pushButton_testlight.clicked.connect(self.Widget3Dview2.open_3d_window)

        # Link a group of buttons, when one is clicked, others toggle off (unclick stage)
        self.pushButton_addline.clicked.connect(lambda:self.set_edit_mode(self.LabelPixmap.enter_addline_mode, self.pushButton_addline))
        self.pushButton_removeline.clicked.connect(lambda:self.set_edit_mode(self.LabelPixmap.enter_removeline_mode, self.pushButton_removeline))
        self.pushButton_mergelines.clicked.connect(lambda:self.set_edit_mode(self.LabelPixmap.enter_mergelines_mode, self.pushButton_mergelines))
        self.pushButton_joincorner.clicked.connect(lambda:self.set_edit_mode(self.LabelPixmap.enter_joincorner_mode, self.pushButton_joincorner))
        
        self.pushButtons_mode = [self.pushButton_addline, self.pushButton_removeline, self.pushButton_mergelines, self.pushButton_joincorner]
        for button in self.pushButtons_mode:
            button.setCheckable(True) # dont know why is command toggle on/off push effect on the button

        self.lines_treeWidget.itemClicked.connect(self.LabelPixmap.onWallLineItemClicked)
        self.pushButton_whitebg.clicked.connect(self.LabelPixmap.draw_lines_whitebg)
        self.pushButton_showlen.clicked.connect(self.LabelPixmap.draw_lines_length)
        self.pushButton_savepixmap.clicked.connect(self.button_savepixmap)
        ####################################################################################################

        # Select showing both or one of img1 and img2 areas
        def toggleMenu_Raw_image(state):
            #print("toggleMenu_actionRaw_image",state)
            if state == True:
                #self.label_img1.show()
                self.scrollArea_img1.show()
            else:
                #self.label_img1.hide()
                self.scrollArea_img1.hide()
            self.update_position()
            #print("self.label_img1.isVisible()",self.label_img1.isVisible()) #False
            #print("self.scrollArea_img1.isVisible()",self.scrollArea_img1.isVisible()) #False
            
        def toggleMenu_2D_layout(state):
            #print("toggleMenu_action2D_layout",state)
            if state == True:
                #self.label_img1.show()
                self.scrollArea_img2.show()
            else:
                #self.label_img1.hide()
                self.scrollArea_img2.hide()
            self.update_position()
        #viewMenu = self.menubar.addMenu('view')
        self.actionRaw_image.triggered.connect(toggleMenu_Raw_image)
        self.action2D_layout.triggered.connect(toggleMenu_2D_layout)
        #toggleMenu_Raw_image(False)
        #self.actionRaw_image.setChecked(False)
        ##################################################################################################

        # Show the MAIN GUI 
        self.show()    

        # Some initialize setup
        self.imgpath = "weights500/005_color_a_00.png"
        #self.imgpath = "../030_color_a_00_w500.png"
        #self.imgpath = "../beike097_a_00.png"
        #self.imgpath = "weights500/InStanford3D_Area1_hallway_5_x01.png"
        self.set_image(self.imgpath)
        # self.LabelPixmap.loadimage_bothlabels(self.imgpath)

        # self.update_position()   # to resize label area      
        #self.button_calculate_custom_mergespline_show() 
        #self.draw3Dlayout()



    # When the window size is changed, this function is triggered
    def resizeEvent(self, event):
        self.update_position()

    # To show image on the label_img area
    def set_image(self, file_path):
        #self.photoViewer.setPixmap(QPixmap(file_path))
        #print("got drop image ",file_path)
        self.imgpath = file_path
        self.LabelPixmap.loadimage_bothlabels(self.imgpath)
        img_w,img_h = self.LabelPixmap.getimgpixmap_wh()
        self.label_imgsize.setText("img size (w*h): "+str(img_w)+" x "+str(img_h))

        self.LinesWidget.clearlines()
        self.update_position()

    def predict_layout(self):
        if self.LabelPixmap.getimgpixmap() is None:
            print("no image loaded")
            return     

        self.predictimgpath = self.tfpredict.predict(self.imgpath)
        self.LabelPixmap.loadimage_predictlabel(self.predictimgpath)
        self.update_position()   # to resize label area  
           
    # Line Edit Mode: add, remove, merge, join lines
    def set_edit_mode(self, func_setmode, button ):
        self.cancel_push_effect(button)
        self.current_button=button
        button.setCheckable(True) # toggle button appearance
        if button.isChecked():
            func_setmode() #self.LabelPixmap.enter_addline_mode or enter_mergelines_mode or enter_joincorner_mode
        else:
            self.LabelPixmap.exit_mode()
        print(self.LabelPixmap.editmode)       

    # Untoggle buttons in the line edit group
    def cancel_push_effect(self, ignorebutton):      
        for button in self.pushButtons_mode:
            if button == ignorebutton:
                #print("the same button, ignore")
                pass
            elif button.isChecked():
                #print("toggle off ",button)
                button.toggle()

    # Capture keyboard pressed key
    def keyPressEvent(self,event):
        if event.key() == Qt.Key_Escape:
            for button in self.pushButtons_mode:
                print(button, button.isChecked())
                if button.isChecked():
                    
                    button.toggle() 

            self.LabelPixmap.exit_mode()
            print(self.LabelPixmap.editmode)     
            #print("close")
            #self.close() #exit program
       
    # Open dialog to pick image to open
    def pickfile(self):
        #QtGui.QFileDialog.getOpenFileName()
        fileDefaultOpenPath = ""
        self.imgpath, _ = QFileDialog.getOpenFileName(self, "open", fileDefaultOpenPath, "Images (*.png *.jpg)")
        #print(self.imgpath)
        if(len(self.imgpath)>0):
            self.LabelPixmap.loadimage_bothlabels(self.imgpath)
            self.update_position()   # to resize label area  
            self.LinesWidget.clearlines()

    # Revert img area to the initial one
    def button_reset(self):
        self.LabelPixmap.reloadimage()
        self.LinesWidget.clearlines()


    def button_calculate_hough_show(self):
        #source_img = cv2.imread(self.imgpath, cv2.IMREAD_COLOR)
        #cv2.imshow("image", source_img)
        if self.LabelPixmap.getimgpixmap() is None:
            print("no image loaded")
            return
        #print(self.imgpath, self.pixel, self.threshold, self.minlinelength, self.maxlinegap)

        pixel, threshold, minlinelength, maxlinegap = self.HoughParamController.gethoughparam()

        if self.predictimgpath is None:
            self.lines = self.LineDectection.detecthoughlines(self.imgpath, pixel, threshold, minlinelength, maxlinegap)
        else: 
            self.lines = self.LineDectection.detecthoughlines(self.predictimgpath, pixel, threshold, minlinelength, maxlinegap)

        self.LabelPixmap.drawpermanentlines(self.lines)
        self.LinesWidget.clearlines()
        self.LinesWidget.addlines(self.lines)


    def get_imgpath_to_cal_lines(self):
        if self.LabelPixmap.getimgpixmap() is None:
            print("no image loaded")
            return None      
        if self.predictimgpath is None:
            return self.imgpath
        else: 
            return self.predictimgpath     

    def get_regtangle_around_point(self,px,py,rad,image_w,image_h):
        rec_x1 = 0 if px-rad < 0 else px-rad 
        rec_y1 = 0 if py-rad < 0 else py-rad 
        rec_x2 = image_w if px+rad > image_w else px+rad
        rec_y2 = image_h if py+rad > image_h else py+rad          
        return rec_x1,rec_y1,rec_x2,rec_y2    

    # Estimate lines in the image
    # 1. calculate line
    def button_calculate_custom_spline_show(self):
        img_path = self.get_imgpath_to_cal_lines()
        if img_path is None:
            return

        minlinelength, maxlinegap = self.CustomParamController.getcustomparam()    

        # vertical line
        line_data_axis_0,_ = self.LineDectection.cal_sum_pixel_v3_lineslice(\
            img_path, axis=0, threshold_minlen=minlinelength, threshold_maxgap=maxlinegap)
        # horizontal line
        line_data_axis_1,_ = self.LineDectection.cal_sum_pixel_v3_lineslice(\
            img_path, axis=1, threshold_minlen=minlinelength, threshold_maxgap=maxlinegap)
        
        # create line items for show in treewidget and draw at pixmap
        self.lines =[]
        for index,sump,p1,p2 in line_data_axis_1: # horizontal line
            self.lines.append([p1, index, p2, index])
        for index,sump,p1,p2  in line_data_axis_0: #vertical line
            self.lines.append([index,p1,index,p2])
        #print(len(self.lines))

        self.LabelPixmap.drawpermanentlines(self.lines)
        self.LinesWidget.clearlines()
        self.LinesWidget.addlines(self.lines)        

    # 2. merge lines
    def button_calculate_custom_mergespline_show(self):#, img_path=None):
        img_path = self.get_imgpath_to_cal_lines()
        if img_path is None:
            return

        nearby, maxspace, _ = self.MergeParamController.getmergeparam()  
        imgpixmap = self.LabelPixmap.getimgpixmap() 
        img_width = imgpixmap.width()
        img_height = imgpixmap.height()
        line_data_axis_0, line_data_axis_1, remain_d_p_linesinfo = self.convert_lines_to_line_data()
        #print("img_path:",img_path)
        # vertical line, pixel_max along vertical 
        #line_data_axis_0, pixel_max = self.LineDectection.cal_sum_pixel_v3_lineslice(img_path, axis=0, threshold=pixelnum)
        #print("line_data_axis_0: pixel_max", pixel_max)
        #print(line_data_axis_0)
        line_group_axis_0 = self.LineDectection.cal_sum_pixel_v4_mergeline(line_data_axis_0,
                                                    total_pixel_along_line = img_height,
                                                    threshold_same_group=nearby,
                                                    max_white_space=maxspace)        
        
        #line_data_axis_1, pixel_max = self.LineDectection.cal_sum_pixel_v3_lineslice(img_path, axis=1, threshold=pixelnum)
        line_group_axis_1 = self.LineDectection.cal_sum_pixel_v4_mergeline(line_data_axis_1,
                                                    total_pixel_along_line = img_width,
                                                    threshold_same_group=nearby,
                                                    max_white_space=maxspace)
        self.lines =[]
        for index,sump,p1,p2 in line_group_axis_1: # horizontal line
            self.lines.append([p1, index, p2, index])
        for index,sump,p1,p2  in line_group_axis_0: #vertical line
            self.lines.append([index,p1,index,p2])
        for x1,y1,x2,y2  in remain_d_p_linesinfo: #vertical line
            self.lines.append([x1,y1,x2,y2])

        #if img_path is False: # draw lines on image
        self.LabelPixmap.drawpermanentlines(self.lines)

        self.LinesWidget.clearlines()
        self.LinesWidget.addlines(self.lines)    

    # 3. merge corners
    def button_calculate_custom_joincorner_show(self):
        img_path = self.get_imgpath_to_cal_lines()
        if img_path is None:
            return
        
        _, _, cornerrad = self.MergeParamController.getmergeparam()  
        print("########################################")
        print("button_calculate_custom_joincorner_show")
        self.LabelPixmap.set_temppixmap()
        linesinfo = self.LinesWidget.getlinesindex_position()
        #print("img w h",self.LineDectection.img.shape[1], self.LineDectection.img.shape[0]) # 512 348
        img_w = self.LineDectection.img.shape[1]-1
        img_h = self.LineDectection.img.shape[0]-1
        # for each in point
        points = self.LinesWidget.getpoints()
        #print(points)
        #print("\n")
        for px,py in points:
            #print(px,py)
            otherlinepoints=[]
            rec_left,rec_top,rec_right,rec_down = self.get_regtangle_around_point(px,py,cornerrad,img_w,img_h)
            #print(rec_x1,rec_y1,rec_x2,rec_y2)
            #check otherpoints in rectangle area
            for index,lx1,ly1,lx2,ly2,direction in linesinfo:
                if self.LabelPixmap.check_linepart_in_rectangle(lx1,ly1,lx2,ly2,rec_left,rec_right,rec_top,rec_down):
                    otherlinepoints.append([index,lx1,ly1,lx2,ly2,direction])
            #for otherlinepoint in otherlinepoints:
            #    print(otherlinepoint)
            print("\npoint ",px,py,"; len(otherlinepoints):",len(otherlinepoints))

            if len(otherlinepoints) == 2: #cal the easy case
                linesextendinfo = self.LabelPixmap.cal_extend_hilightlines(otherlinepoints)
                print("linesextendinfo: len",len(linesextendinfo),". ",linesextendinfo)
                if len(linesextendinfo) != 0:
                    self.LinesWidget.editlinevalue(linesextendinfo)
                    #self.LabelPixmap.drawtemp_hilightlinesinfo(linesextendinfo, Qt.magenta, self.LabelPixmap.temppixmap)

            elif len(otherlinepoints) == 3:
                # remove the "current line point" out from otherlinepoints
                remain_lines = []
                for otherlinepoint in otherlinepoints:
                    if px == otherlinepoint[1] and py == otherlinepoint[2]:
                        current_line = otherlinepoint
                        pass
                    elif px == otherlinepoint[3] and py == otherlinepoint[4]:
                        current_line = otherlinepoint
                        pass
                    else:
                        remain_lines.append(otherlinepoint)                        
                print("current_line:",current_line)
                print("remain_lines:",remain_lines)

                for remainline in remain_lines:
                    # pair each?
                    linesextendinfo = self.LabelPixmap.cal_extend_hilightlines([current_line,remainline])
                    print("linesextendinfo: len",len(linesextendinfo),". ",linesextendinfo)
                    if len(linesextendinfo) != 0:
                        self.LinesWidget.editlinevalue(linesextendinfo)


                pass


        lines = self.LinesWidget.getlines()
        self.LabelPixmap.drawpermanentlines(lines)
            #print()
            #check if same line ignore

    def convert_lines_to_line_data(self):
        linesinfo = self.LinesWidget.getlinesindex_position()
        final_lines_axis0=[]
        final_lines_axis1=[]
        remain_linesinfo =[]

        for index,lx1,ly1,lx2,ly2,direction in linesinfo:

            if direction == "v":# or direction == "nv":
                avg_index = (lx1+lx2)/2
                if ly2>ly1:
                    sum_pixel = ly2-ly1
                    final_lines_axis0.append((avg_index, sum_pixel, ly1, ly2))
                else:
                    sum_pixel = ly1-ly2
                    final_lines_axis0.append((avg_index, sum_pixel, ly2, ly1))                    

            elif direction == "h":# or direction == "nh":
                avg_index = (ly1+ly2)/2
                if lx2>lx1:
                    sum_pixel = lx2-lx1
                    final_lines_axis1.append((avg_index, sum_pixel, lx1, lx2))
                else:
                    sum_pixel = lx1-lx2
                    final_lines_axis1.append((avg_index, sum_pixel, lx2, lx1))
            else:
                remain_linesinfo.append([lx1,ly1,lx2,ly2])


        img_a1_data_axis0 = np.array(final_lines_axis0,dtype={'names':('index', 'sum_pixel', 'p1', 'p2'),
                                    'formats':('i4','i4','i4','i4')})   
        img_a1_data_axis1 = np.array(final_lines_axis1,dtype={'names':('index', 'sum_pixel', 'p1', 'p2'),
                                    'formats':('i4','i4','i4','i4')})  
        img_a1_data_axis0 = np.sort(img_a1_data_axis0, order=['index', 'p1']) 
        img_a1_data_axis1 = np.sort(img_a1_data_axis1, order=['index', 'p1']) 

        return img_a1_data_axis0, img_a1_data_axis1, remain_linesinfo

    # Save lines as an image
    def button_saveimage(self):
        #fileDefaultOpenPath = "./img.png"
        fileDefaultOpenPath=self.imgpath.split("/")[-1]
        image_save_path = QFileDialog.getSaveFileName(self, 'Save image', fileDefaultOpenPath, "Image Files (*.png);;All Files (*)", options=QFileDialog.DontUseNativeDialog)
        # ('/home/nattaon/onz/opencv_pyqt2/layout_detector_tf_custom2/005line1', 'Image Files (*.png)')
        #print("button_saveimage",len(image_save_path),image_save_path)
        if(len(image_save_path[0])>0):
            image_save_path = image_save_path[0]
            print(image_save_path)
            lines = self.LinesWidget.getlines()
            #print(len(lines))
            if len(lines)>0:
                self.LabelPixmap.drawlinesforsave(lines, self.LineDectection.img.shape[1], self.LineDectection.img.shape[0], image_save_path)
            else:
                print("button_saveimage : not save because no lines")

    def button_savepixmap(self):
        fileDefaultOpenPath=self.imgpath.split("/")[-1]
        image_save_path = QFileDialog.getSaveFileName(self, 'Save image', fileDefaultOpenPath, "Image Files (*.png);;All Files (*)", options=QFileDialog.DontUseNativeDialog)
        #print("button_savepixmap",len(image_save_path),image_save_path)
        if(len(image_save_path[0])>0):
            image_save_path = image_save_path[0]
            print(image_save_path)
            #lines = self.LinesWidget.getlines()
            lines = self.LinesWidget.getlines()
            #print(len(lines)) 
            #if len(lines)>0:           
            #    self.LabelPixmap.saveimage_currentpixmap(image_save_path) 
            #else:
            #    print("button_savepixmap : not save because no lines")
            self.LabelPixmap.saveimage_currentpixmap(image_save_path) 

    # Adjust qt ui widget position to match the windows size
    def update_position(self):
        self.label_img1.adjustSize()        
        self.label_img2.adjustSize()  

        self.label_img1.isVisible() 
        self.label_img2.isVisible()
 
        widget_mode_width = self.widget_mode.width()    
        widget_mode_height = self.widget_mode.height()   
        tabwidget_control_width = self.tabWidget_hough_custom.width()
        tabwidget_control_height = self.tabWidget_hough_custom.height()     
        widget_control_width = self.widget_control.width()
        widget_control_height = self.widget_control.height()     
        gap=2

        window_current_width=self.centralwidget.width() #  always change, depend on window size
        window_current_height=self.centralwidget.height() 

        each_scrollarea_width = (window_current_width - widget_control_width)/2 
        each_scrollarea_height = (window_current_height - widget_mode_height)-gap

        if self.label_img1.isVisible() and self.label_img2.isVisible(): # both label is shown

            #print("each_scrollarea ",each_scrollarea_width,each_scrollarea_height)

            self.scrollArea_img1.resize(each_scrollarea_width, each_scrollarea_height)     
            self.scrollArea_img2.resize(each_scrollarea_width, each_scrollarea_height)
            self.scrollArea_img1.move(gap, widget_mode_height+gap)   
            self.scrollArea_img2.move(each_scrollarea_width+gap*2, widget_mode_height+gap) 
            self.statusBar().showMessage("showing: raw_img and 2d_layout")

        elif self.label_img1.isVisible():
            self.scrollArea_img1.resize(each_scrollarea_width*2, each_scrollarea_height)   
            self.scrollArea_img1.move(gap, widget_mode_height+gap)  
            self.statusBar().showMessage("showing: raw_img") 

        elif self.label_img2.isVisible():
            self.scrollArea_img2.resize(each_scrollarea_width*2, each_scrollarea_height)   
            self.scrollArea_img2.move(gap, widget_mode_height+gap)   
            self.statusBar().showMessage("showing: 2d_layout")
        else:
            self.statusBar().showMessage("select item in menubar to show img.")
            pass

        if self.widget_control.x() >= widget_mode_width: # the second label_img can fit the widget_mode
            widget_mode_new_x = self.widget_control.x() - widget_mode_width
        else:
            widget_mode_new_x = 0
        self.widget_mode.move(widget_mode_new_x,self.widget_mode.y())

        # widget control
        self.tabWidget_hough_custom.move(each_scrollarea_width*2+gap*2+10, 0)
        self.widget_control.move(each_scrollarea_width*2+gap*2, tabwidget_control_height+gap)
        self.widget_control.resize(widget_control_width, window_current_height - self.widget_control.y())

        # inside widget control
        self.lines_treeWidget.resize(self.lines_treeWidget.width(), self.widget_control.height() - self.widget_bt_ls.height())
        self.widget_bt_ls.move(self.widget_bt_ls.x(), self.lines_treeWidget.y() + self.lines_treeWidget.height())



app = QtWidgets.QApplication(sys.argv)
window = Ui()
#window.installEventFilter(window)
app.exec_()
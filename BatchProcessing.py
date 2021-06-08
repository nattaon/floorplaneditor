from PyQt5.QtWidgets import QWidget, QFileDialog
from PyQt5.QtCore import Qt, QDir 
import os

class BatchProcessing(QWidget):
    def __init__(self, parent):
        super(BatchProcessing, self).__init__()
        self.parent=parent
        self.LabelPixmap = parent.LabelPixmap
        self.LinesWidget = parent.LinesWidget
        self.LineDectection = parent.LineDectection

    def get_files_open_directory(self, outputfoldername):

        #get directory name
        read_directorypath = QFileDialog.getExistingDirectory(self, "Choose a directory to be read in")
        print("read_directorypath",read_directorypath)
        if len(read_directorypath)==0:
            print("did not select directorypath")
            return None  

        #read image fileds in directory
        directory = QDir(read_directorypath)
        directory.setFilter(QDir.Files | QDir.NoDotAndDotDot)
        files_in_directory = [entry.fileName() for entry in directory.entryInfoList() if entry.fileName().endswith(".png")]
 
        print("files_in_directory ",len(files_in_directory))        
        if len(files_in_directory)==0:
            print(" no images in the directorypath")
            return None     

        # create outputfolder if not exist
        output_directorypath = os.path.join(read_directorypath, outputfoldername)
        if not os.path.exists(output_directorypath):
            os.makedirs(output_directorypath)


        return files_in_directory, read_directorypath, output_directorypath

    def batch_save_calline_folder(self):
        print("no implementation batch_save_calline_folder")
        pass

    def batch_save_mergeline_folder(self):
        # 1. Get directory to open layout images
        files_in_directory, read_directorypath, output_directorypath = self.get_files_open_directory(outputfoldername="output_mergeline")
        if files_in_directory== None:
            return

        for imgname in files_in_directory:
            
            # 1.read path+imagename
            read_image_path = os.path.join(read_directorypath,imgname)

            image_save_path = os.path.join(output_directorypath,imgname) 
            print(image_save_path)

            # 2.calculate linesmerge
            self.parent.set_image(read_image_path)   
            self.parent.button_calculate_custom_spline_show()         
            self.parent.button_calculate_custom_mergespline_show()  
            #print(self.LineDectection.img.shape)  
            #         
            # 3.draw lineonlyimage & save
            lines = self.LinesWidget.getlines()
            self.LabelPixmap.drawlinesforsave(lines, self.LineDectection.img.shape[1], self.LineDectection.img.shape[0], image_save_path)
    
    def batch_save_joincorner_folder(self):
        # 1. Get directory to open layout images
        files_in_directory, read_directorypath, output_directorypath = self.get_files_open_directory(outputfoldername="output_joincorner")
        if files_in_directory== None:
            return
            
        for imgname in files_in_directory:
            
            # 1.read path+imagename
            read_image_path = os.path.join(read_directorypath,imgname)

            image_save_path = os.path.join(output_directorypath,imgname) 
            print(image_save_path)

            # 2.calculate linesmerge
            self.parent.set_image(read_image_path)       
            self.parent.button_calculate_custom_spline_show()         
            self.parent.button_calculate_custom_mergespline_show()  
            self.parent.button_calculate_custom_joincorner_show()  
            #print(self.LineDectection.img.shape)  
            #         
            # 3.draw lineonlyimage & save
            lines = self.LinesWidget.getlines()
            self.LabelPixmap.drawlinesforsave(lines, self.LineDectection.img.shape[1], self.LineDectection.img.shape[0], image_save_path)

    def batch_save_layouttext_folder(self):

        # 1. Get directory to open layout images
        files_in_directory, read_directorypath, output_directorypath = self.get_files_open_directory(outputfoldername="output_layouttext")
        if files_in_directory== None:
            return

        for imgname in files_in_directory:
            
            # 1.read path+imagename
            read_image_path = os.path.join(read_directorypath,imgname)

            image_save_path = os.path.join(output_directorypath,imgname) 
            print(image_save_path)

            # 2.calculate linesmerge
            self.parent.set_image(read_image_path)   
            self.parent.button_calculate_custom_spline_show()             
            self.parent.button_calculate_custom_mergespline_show()  
            self.parent.button_calculate_custom_joincorner_show()  
            self.parent.LabelPixmap.draw_lines_whitebg()    
            self.parent.LabelPixmap.draw_lines_length()    
            #print(self.LineDectection.img.shape)  
            #         
            # 3.draw lineonlyimage & save
            #lines = self.LinesWidget.getlines()
            self.LabelPixmap.saveimage_currentpixmap(image_save_path)
import numpy as np
import cv2
class LineDectection:
    def __init__(self):
        super(LineDectection, self).__init__()
        self.img = None
        self.imgpath = None
    
    def readimage2gray(self):
        self.img = cv2.imread(self.imgpath) # got 3 channels 
        #print(self.img.shape)
        self.img = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY) # convert to 1 channel
      
        #print(self.img.shape)
        #print("min:",self.img.min())
        #print("max",self.img.max())
        #self.edges=cv2.Canny(self.gray,150,200,apertureSize=3)

    def detecthoughlines(self, imagepath, pixel, threshold, minLineLength, maxLineGap):
        #print(imagepath)
        if self.imgpath == imagepath:
            #the same img
            pass
        else:
            #readimg
            self.imgpath = imagepath
            self.readimage2gray()

        # lines	= cv2.HoughLinesP(	image, rho, theta, threshold[, lines[, minLineLength[, maxLineGap]]]	)
        # rho (pixel) = Distance resolution of the accumulator in pixels.
        # theta (np.pi/360) = Angle resolution of the accumulator in radians.
        # thres = the number of vote
        lines = cv2.HoughLinesP(self.img,\
                                     pixel, np.pi/360, threshold, \
                                     minLineLength,  maxLineGap )
        return lines
        
    def get_end_indexs_to_cut(self, arr, maxgap):
        # find slicing index
        indexlist=[]
        for j in range(len(arr)-1):
            if arr[j] + maxgap < arr[j+1]:
                indexlist.append(j) 
        return indexlist

    def get_slice_arrays(self, arr, maxgap):
        
        # find slicing index
        indexlist=self.get_end_indexs_to_cut(arr, maxgap) # min width = maxgap?
    
        # no need to slice        
        if len(indexlist) == 0:
            return [arr]
        
        arraylist=[]
        s=0
        for cutindex in indexlist:
            arraylist.append(arr[s:cutindex+1]) # [s, s+1, s+2, cutindex]
            s = cutindex+1
        arraylist.append(arr[s:])
        return arraylist

    def get_slice_dataarrays(self, indexarr, distance_same_group, dataarray):
        
        # find slicing index
        indexlist=self.get_end_indexs_to_cut(indexarr, distance_same_group)
                
        # no need to slice        
        if len(indexlist) == 0:
            return [dataarray]
        
        arraylist=[]
        s=0
        for cutindex in indexlist:
            arraylist.append(dataarray[s:cutindex+1])
            s = cutindex+1
        arraylist.append(dataarray[s:])
        return arraylist

    def cal_sum_pixel_v3_lineslice(self, imagepath, axis, threshold_minlen, threshold_maxgap):   
        #print("cal_sum_pixel_v3_lineslice")
        if self.imgpath == imagepath:
            #the same img
            pass
        else:
            #readimg
            self.imgpath = imagepath
            self.readimage2gray()    #got 0-255 range    

        img_normalize = self.img/255.0
        #print("min:",img_normalize.min())
        #print("max",img_normalize.max())        
        img_binarise = np.where(img_normalize > 0.3, 1.0, 0.0)
        list_pixel =[]
        if axis == 1: #horizontal
            max_line_per_image = img_binarise.shape[0] 
            max_pixel_per_line = img_binarise.shape[1] 
            for i in range(max_line_per_image):
                # 1.Get indexs of the current row that contain pixel
                haspixel = np.where(img_binarise[i,:]==1)[0]
                # 2.keep the row if the number of pixel > threshold
                if len(haspixel) > 0:
                    #3. slice the current row to lines, if they are separate apart
                    slicearrays = self.get_slice_arrays(haspixel, threshold_maxgap) 
                    # append to list
                    for sa in slicearrays:
                        if len(sa) >= threshold_minlen:
                            list_pixel.append((i, len(sa), sa[0], sa[-1]))                 

        elif axis == 0: #vertical
            max_line_per_image = img_binarise.shape[1] 
            max_pixel_per_line = img_binarise.shape[0]   
            for i in range(max_line_per_image):
                haspixel = np.where(img_binarise[:,i]==1)[0]
                # if there are enough pixels
                if len(haspixel) > 0:
                    slicearrays = self.get_slice_arrays(haspixel, threshold_maxgap) 
                    #4. keep the sliced lines into a list
                    for sa in slicearrays:
                        if len(sa) >= threshold_minlen:
                            list_pixel.append((i, len(sa), sa[0], sa[-1]))
                            
        img_a1_data = np.array(list_pixel,dtype={'names':('index', 'sum_pixel', 'p1', 'p2'),
                                    'formats':('i4','i4','i4','i4')})                        
        return img_a1_data, max_pixel_per_line


    # line_group_axis_0 = self.LineDectection.cal_sum_pixel_v4_mergeline(line_data_axis_0,
    #                                             total_pixel_along_line = img_height,
    #                                             threshold_same_group=nearby,
    #                                             max_white_space=maxspace)  
    def cal_sum_pixel_v4_mergeline(self, img_sum_axis, total_pixel_along_line, threshold_same_group, max_white_space): 
        print("\ncal_sum_pixel_v4_mergeline. line max len",total_pixel_along_line)
        print("lines count:",len(img_sum_axis))
        print(img_sum_axis)
        final_lines=[]
        # 1. group the "nearby lines" top/down or left/right together
        group_slicearrays = self.get_slice_dataarrays(img_sum_axis['index'],
                                                threshold_same_group,
                                                img_sum_axis)
        

        # merge each rows in group to 1 row, then calculate the most occupied index

        # 2. in each group of the nearby line, 
        #    separate subgroup along the line width direction, 
        #    (separate the line that is far away each other)
        for group_id, group in enumerate(group_slicearrays):

            print("------------------------\ngroup #",group_id)
            print(group)
            if len(group)==0: # in case of NO vertical line or horizontal line 
                print("len(group),id,group:",len(group),group_id,group)
                continue


            line_index_l0=group['index'][0]
            line_index_l1=group['index'][-1]
            index_range = line_index_l1 - line_index_l0 +1  
            index_array = np.arange(line_index_l0, line_index_l1+1)    
            # 3. create group_pixel, 2d array, size(index_range,total_pixel_along_line) 
            #    to store pixels from the group
            #print(line_index_l0, line_index_l1,index_range, total_pixel_along_line)
            group_pixel=np.zeros((index_range, total_pixel_along_line))    
            #print("group_pixel",group_pixel.shape)
            #print("index l0,l1:",line_index_l0,line_index_l1)  
  
            # 4. fill 1 on the group_pixel cell that has pixel. (or get it from the raw image?)
            for index,sump,p1,p2 in group:
                group_pixel[index-line_index_l0,p1:p2+1]=1

            # 5. merge the nearby lines, to then find a gap
            merge_index = np.sum(group_pixel,axis=0)
            print("len=",len(merge_index))
            #print("merge_index\n",merge_index) 
            pixel_list = np.where(merge_index>0)[0]  # return a tuple (len=1) of numpy.ndarray, 
            #                                                so select the first index [0]
            #print("index_list_pixel",type(index_list_pixel),len(index_list_pixel),index_list_pixel)
            print("pixel_list\n",pixel_list)   
       
            pixel_p0 = pixel_list[0]
            pixel_p1 = pixel_list[-1]
            #print("pixel p0,p1:",pixel_p0, pixel_p1)


            # 6. get index of the linesgroup gap
            pixel_to_cut_line = self.get_end_indexs_to_cut(pixel_list,max_white_space)
            print("pixel_to_cut_line\n",pixel_to_cut_line) 

            # 7. if there is no gap, find the average index
            if len(pixel_to_cut_line) == 0:

                count_row_pixels = np.sum(group_pixel,axis=1) # size = 1d
                count_all_pixels = np.sum(count_row_pixels) # size = 1d

                # 8. sum up all pixel index value.

                total_index=index_array.dot(count_row_pixels) #get single value
                avg_index = int(round(total_index/count_all_pixels))

                #print("avg_index,p1,p2:",avg_index,pixel_p0, pixel_p1)
                final_lines.append((avg_index, pixel_p1-pixel_p0+1, pixel_p0, pixel_p1))

                # done!

            else:
                # 8. if there are gaps, combine the lines pixel as each block, then find the average index
                #fine lines that can merge, and cannot

                start_pixel=0
                # add the last cut index
                pixel_to_cut_line.append(len(pixel_list)-1)

                for cut_pixel in pixel_to_cut_line:

                    end_pixel = cut_pixel          
                    #print("pixel value:",pixel_list[start_pixel]," to ",pixel_list[end_pixel])

                    # 9. crop the cells of pixel-block 
                    #print("sub_group_pixel")#,group_pixel[:, pixel_list[start_pixel]:pixel_list[end_pixel]+1])
                    sub_group_pixel=group_pixel[:, pixel_list[start_pixel]:pixel_list[end_pixel]+1]
                    print("sub_group_pixel")
                    print(sub_group_pixel)

                    count_row_pixels = np.sum(sub_group_pixel,axis=1) # size = 1d
                    count_all_pixels = np.sum(count_row_pixels) # #get single value

                    total_index=index_array.dot(count_row_pixels) #get single value
                    avg_index=int(round(total_index/count_all_pixels))

                    print(" count_row_pixels=",count_row_pixels," count_all_pixels=",count_all_pixels)
                    #print(" total_index=",total_index," avg_index=",avg_index)
                    print("avg_index,p1,p2:",avg_index,pixel_list[start_pixel], pixel_list[end_pixel])

                    final_lines.append((avg_index, 
                                        pixel_list[end_pixel]-pixel_list[start_pixel]+1, 
                                        pixel_list[start_pixel], pixel_list[end_pixel]))

                    start_pixel = end_pixel+1             
                    #print("---")

        img_a1_data = np.array(final_lines,dtype={'names':('index', 'sum_pixel', 'p1', 'p2'),
                                    'formats':('i4','i4','i4','i4')})                        
        return img_a1_data 

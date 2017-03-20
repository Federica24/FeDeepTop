# Friday 3rd March 2017
# ETH Zurich

import argparse
import numpy as np
import matplotlib
import pandas
matplotlib.use('Agg')
matplotlib.rcParams['text.usetex'] = True
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator
import math
import os
import sys
import h5py

from scipy import ndimage as ndi
from skimage.feature import peak_local_max #pip install scikit-image
from scipy import ndimage

minorLocator = AutoMinorLocator(2)
subminorLocator = AutoMinorLocator(2)

def imager(tablename,mode):

    store = pandas.HDFStore(imager)
    foo = store.select('table')
    foo.columns
    print foo.columns
    foo.reset_index(inplace=True)
    print len(foo['entries'])
    group_matrix = []

    counter = 0
    for k in range(0,len(foo['entries'])):
        plain_matrix = []
        if foo["is_signal_new"][k]!=mode:
            counter = counter+1
            continue
        for n in range(0,1600):
            plain_matrix.append(foo["img_"+ str(n)][k])
        plain_matrix = np.array(plain_matrix)
        matrix = plain_matrix.reshape(40,40)
        matrix = np.array(matrix)

        # LOCAL MAXIMA FINDER
        # Find the coordinates of all the founded local maxima (to be visulised below), and order them so that the first three entris of the "list_peaks" contains the first three local maxima
        coordinates = peak_local_max(matrix, min_distance=3)
        list_peaks = []
        for point in coordinates:
            list_peaks.append([tuple(point), matrix[tuple(point)]])
        list_peaks = np.array(list_peaks)
        if len(list_peaks)<3:
            counter = counter+1
            continue
        list_peaks = list_peaks[list_peaks[:, 1].argsort()][::-1]
    
        # Determine the rotation angle using the original coordinates
        x_max_0 = list_peaks[:,0][0][0]
        y_max_0 = list_peaks[:,0][0][1]
        x_max_1 = list_peaks[:,0][1][0]
        y_max_1 = list_peaks[:,0][1][1]
        delta_x = x_max_1-x_max_0
        delta_y = y_max_1-y_max_0
        phi_rot = math.atan2(delta_x*1.,delta_y*1.)+np.pi/2

        # Define an auxiliary matrix to trace the position of the third local maximum
        x_max_2 = list_peaks[:,0][2][0]
        y_max_2 = list_peaks[:,0][2][1]
        plain_aux_matrix = np.zeros((1600),dtype=int)
        aux_matrix = plain_aux_matrix.reshape(40,40)
        aux_matrix[(x_max_2,y_max_2)]=40
        for j in range(0,(39-x_max_2)):
            aux_matrix[(x_max_2+j+1,y_max_2)]= 40-(j+1)
        for j in range(0,x_max_2+1):
            aux_matrix[(x_max_2-(j+1),y_max_2)] = 40-(j+1)

        # Define the entity of the shift
        c = 20
        s = (int(c-x_max_0),int(c-y_max_0))

        # Shift the image and the auxiliary image so that the local first maximum is at the center
        transformed_matrix = ndimage.interpolation.shift(matrix, s, order=0)
        aux_matrix = ndimage.interpolation.shift(aux_matrix, s, order=0)

        # Traces the third local maximum after the shift
        #print (x_max_2+s[0],y_max_2+s[1]), aux_matrix[(x_max_2+s[0],y_max_2+s[1])]

        # Apply the rotation to the transformed coordinates
        transformed_matrix = ndimage.interpolation.rotate(transformed_matrix, phi_rot*180./np.pi,reshape=False,cval=0,order=0)
        aux_matrix = ndimage.interpolation.rotate(aux_matrix, phi_rot*180./np.pi,reshape=False,cval=0,order=0)

        # Flip the image if needed
        max_tr = np.max(aux_matrix)
        #print max_tr
        new_thirdpeak_coordinates = zip(*np.where(aux_matrix==max_tr))
        new_thirdpeak_coordinates = np.array(new_thirdpeak_coordinates)
        new_thirdpeak_coordinates = new_thirdpeak_coordinates[new_thirdpeak_coordinates[:, 1].argsort()]
        
        newy_max_2 = new_thirdpeak_coordinates[0][1]
    
        if newy_max_2<c:
            #print 'flip', y_max_2
            transformed_matrix = np.fliplr(transformed_matrix)

        group_matrix.append(transformed_matrix)
        counter = counter+1
    
        if counter % 1000 == 0:
            print 'Collecting data,', counter

    group_matrix = np.array(group_matrix)

    aux_list = [0]*1600
    aux_list = np.array(aux_list)
    overlap_img = aux_list.reshape(40,40)

    print ' '
    counter = 0
    for entry in group_matrix:
        overlap_img = overlap_img+entry
        counter = counter+1
        if counter % 100 == 0:
            print 'Overlapping data,', counter

    interpolation_type = 'nearest'
    print interpolation_type

    fig, ax = plt.subplots(1, 1)
    ax.grid(False)
    imres = ax.imshow(overlap_img, norm=matplotlib.colors.LogNorm(), cmap='jet',interpolation=interpolation_type)
    cbar = fig.colorbar(imres, ax=ax, pad = 0.025)
    cbar.set_label(r'$\mathrm{ECal \ E_{T} \ [GeV]}$', fontsize=22)
    cbar.ax.tick_params(labelsize=20)
    ax.set_xlabel("$\mathrm{\phi^{'} \ pixels}$", fontsize=22)
    ax.set_ylabel("$\mathrm{\eta^{'} \ pixels}$", fontsize=22)
    ax.tick_params(axis='x', labelsize=20)
    ax.tick_params(axis='y', labelsize=20)
    #plt.text(.8, .03, ' {:.12s}'.format(nimage), transform=plt.gca().transAxes, fontsize=22, color='black')
    output_imgname = tablename.split('.h5')
    output_imgname  = output_imgname[0] + '_' + str(mode) + '.png'
    plt.savefig(output_imgname, bbox_inches='tight')
    plt.clf()
    #os.system("open " + output_imgname)



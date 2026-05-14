#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 30 11:31:26 2024

@author: khanh
"""

import numpy as np
import tensorflow as tf
import keras
import cv2
from keras.layers import MaxPool2D,Conv2D,UpSampling2D,Input,Dropout
from keras.models import Sequential
from keras.preprocessing.image import img_to_array
import os
from tqdm import tqdm
import re
import matplotlib.pyplot as plt
import netCDF4 as nc
import sklearn
from sklearn import preprocessing
from keras import layers
import geopandas as gpd
from descartes import PolygonPatch
import shapefile
from mpl_toolkits.axes_grid1 import make_axes_locatable
from sklearn.preprocessing import StandardScaler
import datetime as tdelta
from datetime import datetime

#############################################################################################
targetLabel = 'T2'
modDir = '/glade/campaign/univ/uncs0034/kdo/ML/downscale/savedWeights/'
dataDir = '/glade/campaign/univ/uncs0034/kdo/ML/downscale/features_2006/'
metBaseFolder = '/glade/campaign/univ/uncs0034/kdo/ML/downscale/shapefiles_plotformat/'
outFeatureName = 'featuresMetem_d03_'
init = True  #True or False 
startDate = datetime(2006,1,4,0,0,0)  # start date
endDate = datetime(2006,12,31,23,0,0) # end date
numberOfDay = 3
trainPercent = 1.0 # 0.9 = 90% for training and 10 percent for testing
##############################################################################################

while startDate <= endDate:
#if numberOfDay == 1:
    SIZE1 = int(608/1) #d01: 94 #d03 606
    SIZE2 = int(768/1) #d01: 131 #d03 750
    
    label_names = ['LU_INDEX', 'PBLH', 'Q2', 'T2',
                       'U10', 'V10', 'RAINC', 'XLAT', 'XLONG']
    # emission features are anything except met_em_features, wrfout_features, labels, and Timestep
    timestep = 'Timestep'
    
    idxLabel = label_names.index(targetLabel)
    
    # import features
    #file = 'featuresMetem_d03_20060101_20060228.nc' # sample emis file
    file = outFeatureName + str(startDate.year) + str(startDate.month).zfill(2) + str(startDate.day).zfill(2) + '.nc'
    inFile = dataDir + file
    if os.path.exists(inFile):
        print('=====================================================================')
        print(inFile)
        print('=====================================================================')
        ds_in = nc.Dataset(inFile)
        
        xlat = ds_in['XLAT_M'][0,:,:]
        xlong = ds_in['XLONG_M'][0,:,:]
        
        featureVar = list(ds_in.variables.keys())
        features = []
        
        for f in featureVar:
            if f not in label_names and f != timestep:
                 features.append(ds_in[f])
                 print(f)
        
        labels = []
        for l in featureVar:
            if l in label_names:
                labels.append(ds_in[l])  
        
        # resize labels
        reshapeLabel = np.array(labels).transpose(2,3,0,1)
        trainLabels = []
        sc1 = []
        sc2 = []
        
        for i in range(0, np.shape(reshapeLabel)[3]):
            tmp = cv2.resize(reshapeLabel[:,:,:,i], (SIZE2, SIZE1))
            # normalize 0 -> 1
            tmpLabel = []
            for n in range(0, np.shape(tmp)[2]):
                if n == idxLabel:
                    sc1.append(StandardScaler().fit(tmp[:,:,n]))
                else:
                    StandardScaler().fit(tmp[:,:,n])
                # tmpLabel.append(preprocessing.minmax_scale(tmp[:,:,n], feature_range=(0, 1), axis=0, copy=True))
                tmpLabel.append(StandardScaler().fit_transform(tmp[:,:,n]))
                # tmpLabel.append(tmp[:,:,n])
            trainLabels.append(tmpLabel)
            
        trainLabels = np.array(trainLabels).transpose(0,2,3,1)
        trainLabel = trainLabels[:,:,:,idxLabel:idxLabel+1]
        # trainLabel = np.reshape(trainLabel, (np.shape(trainLabel)[0], np.shape(trainLabel)[1], np.shape(trainLabel)[2], 1))
        
        # resize fetures
        reshapeFeture = np.array(features).transpose(2,3,0,1)
        trainFeature = []
        for i in range(0, np.shape(reshapeFeture)[3]):
            tmp = cv2.resize(reshapeFeture[:,:,:,i], (SIZE2, SIZE1))
            # normalize 0 -> 1
            tmpFeature = []
            for n in range(0, np.shape(tmp)[2]):
                StandardScaler().fit(tmp[:,:,n])
                # tmpFeature.append(preprocessing.minmax_scale(tmp[:,:,n], feature_range=(0, 1), axis=0, copy=True))
                tmpFeature.append(StandardScaler().fit_transform(tmp[:,:,n]))
            trainFeature.append(tmpFeature)
            
        trainFeature = np.array(trainFeature).transpose(0,2,3,1)
        
        # defining function to plot images pair
        def plot_images(color,grayscale):
            plt.figure(figsize=(15,15))
            plt.subplot(1,3,1)
            plt.title('Color Image', color = 'green', fontsize = 20)
            plt.imshow(color)
            plt.subplot(1,3,2)
            plt.title('Grayscale Image ', color = 'black', fontsize = 20)
            plt.imshow(grayscale)
           
            plt.show()
        
        train_gray_image = trainFeature[:round(np.shape(trainLabel)[0]*trainPercent)]
        train_color_image = trainLabel[:round(np.shape(trainLabel)[0]*trainPercent)]
        
        test_gray_image = trainFeature[:round(np.shape(trainLabel)[0]*(1-trainPercent))]
        test_color_image = trainLabel[:round(np.shape(trainLabel)[0]*(1-trainPercent))]
        # reshaping
        train_g = np.reshape(train_gray_image,(len(train_gray_image),SIZE1,SIZE2,np.shape(trainFeature)[3]))
        train_c = np.reshape(train_color_image, (len(train_color_image),SIZE1,SIZE2,np.shape(trainLabel)[3]))
        print('Train color image shape:',train_c.shape)
        
        
        test_gray_image = np.reshape(test_gray_image,(len(test_gray_image),SIZE1,SIZE2,np.shape(trainFeature)[3]))
        test_color_image = np.reshape(test_color_image, (len(test_color_image),SIZE1,SIZE2,np.shape(trainLabel)[3]))
        print('Test color image shape',test_color_image.shape)
        
        def down(filters , kernel_size, apply_batch_normalization = True):
            downsample = tf.keras.models.Sequential()
            downsample.add(layers.Conv2D(filters,kernel_size,padding = 'same', strides = 2))
            if apply_batch_normalization:
                downsample.add(layers.BatchNormalization())
            downsample.add(keras.layers.LeakyReLU())
            return downsample
        
        
        def up(filters, kernel_size, dropout = False):
            upsample = tf.keras.models.Sequential()
            upsample.add(layers.Conv2DTranspose(filters, kernel_size,padding = 'same', strides = 2))
            if dropout:
                upsample.dropout(0.2)
            upsample.add(keras.layers.LeakyReLU())
            return upsample
        
        # def model():
        #     inputs = layers.Input(shape= [SIZE1,SIZE2,np.shape(trainFeature)[3]])
        #     d1 = down(128,(3,3),False)(inputs)
        #     d2 = down(128,(3,3),False)(d1)
        #     d3 = down(256,(3,3),True)(d2)
        #     d4 = down(512,(3,3),True)(d3)
            
        #     d5 = down(512,(3,3),True)(d4)
        #     #upsampling
        #     u1 = up(512,(3,3),False)(d5)
        #     u1 = layers.concatenate([u1,d4])
        #     u2 = up(256,(3,3),False)(u1)
        #     u2 = layers.concatenate([u2,d3])
        #     u3 = up(128,(3,3),False)(u2)
        #     u3 = layers.concatenate([u3,d2])
        #     u4 = up(128,(3,3),False)(u3)
        #     u4 = layers.concatenate([u4,d1])
        #     u5 = up(3,(3,3),False)(u4)
        #     u5 = layers.concatenate([u5,inputs])
        #     output = layers.Conv2D(1,(2,2),strides = 1, padding = 'same')(u5)
        #     return tf.keras.Model(inputs=inputs, outputs=output)
        
        # def model():
        #     inputs = layers.Input(shape= [SIZE1,SIZE2,np.shape(trainFeature)[3]])
        #     d1 = down(256,(3,3),False)(inputs)
        #     print(f'd1: {d1.shape}')
        #     d2 = down(256,(3,3),False)(d1)
        #     print(f'd2: {d2.shape}')
        #     d3 = down(512,(3,3),True)(d2)
        #     print(f'd3: {d3.shape}')
        #     d4 = down(1024,(3,3),True)(d3)
        #     print(f'd4: {d4.shape}')
        #     d5 = down(1024,(3,3),True)(d4)
        #     print(f'd5: {d5.shape}')
        #     #upsampling
        #     u1 = up(1024,(3,3),False)(d5)
        #     print(f'u1: {u1.shape}')
        #     u1 = layers.concatenate([u1,d4])
        #     u2 = up(1024,(3,3),False)(u1)
        #     print(f'u2: {u2.shape}')
        #     u2 = layers.concatenate([u2,d3])
        #     u3 = up(512,(3,3),False)(u2)
        #     print(f'u3 {u3.shape}')
        #     u3 = layers.concatenate([u3,d2])
        #     u4 = up(256,(3,3),False)(u3)
        #     print(f'u4: {u4.shape}')
        #     u4 = layers.concatenate([u4,d1])
        #     u5 = up(256,(3,3),False)(u4)
        #     print(f'u5: {u5.shape}')
        #     u5 = layers.concatenate([u5,inputs])
        #     output = layers.Conv2D(1,(2,2),strides = 1, padding = 'same')(u5)
        #     return tf.keras.Model(inputs=inputs, outputs=output)
        
        def model():
            inputs = layers.Input(shape= [SIZE1,SIZE2,np.shape(trainFeature)[3]])
            d1 = down(256,(3,3),False)(inputs)
            print(f'd1: {d1.shape}')
            d2 = down(256,(3,3),False)(d1)
            print(f'd2: {d2.shape}')
            d3 = down(512,(3,3),True)(d2)
            print(f'd3: {d3.shape}')
            d4 = down(1024,(3,3),True)(d3)
            print(f'd4: {d4.shape}')
            #upsampling
            u1 = up(1024,(3,3),False)(d4)
            print(f'u1: {u1.shape}')
            u1 = layers.concatenate([u1,d3])
            u2 = up(512,(3,3),False)(u1)
            print(f'u2: {u2.shape}')
            u2 = layers.concatenate([u2,d2])
            u3 = up(256,(3,3),False)(u2)
            print(f'u3 {u3.shape}')
            u3 = layers.concatenate([u3,d1])
            u4 = up(256,(3,3),False)(u3)
            print(f'u4: {u4.shape}')
            u4 = layers.concatenate([u4,inputs])
            output = layers.Conv2D(1,(2,2),strides = 1, padding = 'same')(u4)
            return tf.keras.Model(inputs=inputs, outputs=output)
        
        if init == True:
            model = model()
            model.summary()
            model.compile(optimizer = tf.keras.optimizers.Adam(learning_rate = 0.001), loss = 'mean_absolute_error', metrics = ['acc'])
            init = False
        else:
            model = model()
            model.summary()
            #model.compile(optimizer = tf.keras.optimizers.Adam(learning_rate = 0.001), loss = 'mean_absolute_error', metrics = ['acc'])
            model.load_weights(modDir + 'checkpoint_T2_v3_run1.weights.h5')
            model.compile(optimizer = tf.keras.optimizers.Adam(learning_rate = 0.001), loss = 'mean_absolute_error', metrics = ['acc'])
        
        #model.compile(optimizer = tf.keras.optimizers.Adam(learning_rate = 0.001), loss = 'mean_absolute_error',
        #              metrics = ['acc'])
        
        model.fit(train_g, train_c, epochs = 50,batch_size = 5,verbose = 1)
        
        #model.evaluate(test_gray_image,test_color_image)
        
        model.save_weights(modDir + 'checkpoint_T2_v3_run1.weights.h5')
    
    startDate = startDate + tdelta.timedelta(days = 1)

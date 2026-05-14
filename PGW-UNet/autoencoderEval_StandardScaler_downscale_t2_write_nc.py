#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 29 21:38:13 2024

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
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import StandardScaler
import datetime as tdelta
from datetime import datetime

targetLabel = 'T2'

modDir = '/glade/campaign/univ/uncs0034/kdo/ML/downscale/'
# feaDir = '/glade/campaign/univ/uncs0034/kdo/ML/downscale/featuresWithoutWind/features_ssp585_2046_2056/'
feaDir = '/glade/campaign/univ/uncs0034/kdo/ML/downscale/features_2006/'
metBaseFolder = '/glade/campaign/univ/uncs0034/kdo/ML/downscale/shapefiles_plotformat/'
outFeatureName = 'featuresMetem_d03_'
startDate = datetime(2006,1,4,0,0,0)  # start date
endDate = datetime(2006,12,31,23,0,0) # end date
numberOfDay = 3
trainPercent = 0.0 # 90 percent for training, 10 percent for testing
##############################################################################################

while startDate <= endDate:
    SIZE1 = 608 # d01 94
    SIZE2 = 768 # d01 131
    
    met_em_features = ['PSFC', 'GHT', 'LANDUSEF', 'ALBEDO12M', 'GREENFRAC',
                       'TT', 'RH', 'CLONG',
                       'CLAT', 'PMSL']
    label_names = ['LU_INDEX', 'PBLH',
                       'Q2', 'T2',
                       'U10', 'V10', 'RAINC', 'XLAT', 'XLONG']
    
    timestep = 'Timestep'
    
    idxLabel = label_names.index(targetLabel)
    
    # import features
    #file = 'featuresWrfonlyMetem_20060101_20060228.nc' # sample emis file
    file = outFeatureName + str(startDate.year) + str(startDate.month).zfill(2) + str(startDate.day).zfill(2) + '.nc'
    inFile = feaDir + file

    if os.path.exists(inFile):
        ds_in = nc.Dataset(inFile)
        xlat = ds_in['XLAT_M'][0,:,:]
        xlong = ds_in['XLONG_M'][0,:,:]
        
        featureVar = list(ds_in.variables.keys())
        # featureVar.remove('PSFC')
        features = []
        
        for f in featureVar:
            if f not in label_names and f != timestep:
                features.append(ds_in[f])
        labels = []
        for l in featureVar:
            if l in label_names:
                labels.append(ds_in[l])
                
        # resize labels
        scaler = MinMaxScaler()
        sc = []
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
        
        train_gray_image = trainFeature[:round(np.shape(trainLabel)[0]*trainPercent)]
        train_color_image = trainLabel[:round(np.shape(trainLabel)[0]*trainPercent)]
        sc_train = sc1[:round(np.shape(sc1)[0]*trainPercent)]
        
        test_gray_image = trainFeature[round(np.shape(trainLabel)[0]*trainPercent):]
        test_color_image = trainLabel[round(np.shape(trainLabel)[0]*(trainPercent)):]
        sc_test = sc1[round(np.shape(sc1)[0]*(trainPercent)):]
        
        # reshaping
        train_g = np.reshape(train_gray_image,(len(train_gray_image),SIZE1,SIZE2,np.shape(trainFeature)[3]))
        train_c = np.reshape(train_color_image, (len(train_color_image),SIZE1,SIZE2,np.shape(trainLabel)[3]))
        print('Train color image shape:',train_c.shape)
        
        
        test_gray_image = np.reshape(test_gray_image,(len(test_gray_image),SIZE1,SIZE2,np.shape(trainFeature)[3]))
        test_color_image = np.reshape(test_color_image, (len(test_color_image),SIZE1,SIZE2,np.shape(trainLabel)[3]))
        print('Test color image shape',test_color_image.shape)
        
        initDate = startDate - tdelta.timedelta(numberOfDay*24)
        dnt = []
        for i in range(0, numberOfDay*24):
            dnt.append(initDate + tdelta.timedelta(hours=i))
            
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

        model = model()
        model.summary()
        
        model.compile(optimizer = tf.keras.optimizers.Adam(learning_rate = 0.001), loss = 'mean_absolute_error',
                      metrics = ['acc'])
        
        # model.fit(train_g, train_c, epochs = 150,batch_size = 50,verbose = 1)
        
        # model.evaluate(test_gray_image,test_color_image)
        
        model.load_weights(modDir + '/savedWeights/checkpoint_T2_v3_run1.weights.h5')
        
        # defining function to plot images pair
        def plot_images(wrf,predicted):
            fig, ax1 = plt.subplots(nrows=1, ncols=2, figsize = (24, 10))
            # plt.figure(figsize=(12,10))
            # plt.subplot(1,2,1)
            #df=gpd.read_file(metBaseFolder + "/shapefiles/test.shp")
            #df.plot(ax=ax1, color="none", edgecolor='black', linewidth=1)
            sf = shapefile.Reader(metBaseFolder + "/States_shapefile.shp")
            for poly in sf.shapes():
                poly_geo=poly.__geo_interface__
                ax1[0].add_patch(PolygonPatch(poly_geo, fc='#ffffff', ec='#000000', alpha=0.5, zorder=2 ))
            im2 = ax1[0].pcolor(xlong, xlat, (wrf), cmap='jet', vmin=np.max(270), vmax=np.max(predicted))
            # im2 = plt.pcolor(xlong, xlat, labels[0][0][:][:], cmap='jet', vmin=0, vmax=np.max(labels[0][0][:][:]))
            # im2 = plt.pcolor(xlong, xlat, a[:,:,0], cmap='jet', vmin=0, vmax=np.max(a[:,:,0]))
            
            ax1[0].set_xlim([-133.5, -62])
            ax1[0].set_ylim([21, 55])
            # plt.text(-18, -5, 'R=' + R[v], size = 20)
            ax1[0].set_title('WRF')
            divider = make_axes_locatable(ax1[0])
            cax = divider.append_axes("right", size="2%", pad=0.2)
            plt.colorbar(im2, cax=cax, label=targetLabel)
            # plt.savefig('_pred.png',bbox_inches='tight', dpi=300)
           
            # fig, (ax2) = plt.subplots(1, 2, figsize = (12, 10))
            #df=gpd.read_file(metBaseFolder + "/shapefiles/test.shp")
            #df.plot(ax=ax2, color="none", edgecolor='black', linewidth=1)
            sf = shapefile.Reader(metBaseFolder + "/States_shapefile.shp")
            for poly in sf.shapes():
                poly_geo=poly.__geo_interface__
                ax1[1].add_patch(PolygonPatch(poly_geo, fc='#ffffff', ec='#000000', alpha=0.5, zorder=2 ))
            im2 = ax1[1].pcolor(xlong, xlat, (predicted), cmap='jet', vmin=np.max(270), vmax=np.max(predicted))
            # im2 = plt.pcolor(xlong, xlat, labels[0][0][:][:], cmap='jet', vmin=0, vmax=np.max(labels[0][0][:][:]))
            # im2 = plt.pcolor(xlong, xlat, a[:,:,0], cmap='jet', vmin=0, vmax=np.max(a[:,:,0]))
            
            ax1[1].set_xlim([-133.5, -62])
            ax1[1].set_ylim([21, 55])
            # plt.text(-18, -5, 'R=' + R[v], size = 20)
            ax1[1].set_title('Autoencoder')
            divider = make_axes_locatable(ax1[1])
            cax = divider.append_axes("right", size="2%", pad=0.2)
            plt.colorbar(im2, cax=cax, label=targetLabel)
            # plt.savefig('_pred.png',bbox_inches='tight', dpi=200)
            # plt.show()
        
        mArray = []
        oArray = []
        m2dArray = []
        o2dArray = []
        for i in range(0, numberOfDay*24):
            predicted = model.predict(test_gray_image[i].reshape(1,SIZE1, SIZE2,np.shape(trainFeature)[3]))[0,:,:,:]
            #plot_images(sc_test[i].inverse_transform(test_color_image[i][:,:,0]), sc_test[i].inverse_transform(predicted[:,:,0]))
            #plt.savefig('timeseries'+str(i)+'.png',bbox_inches='tight', dpi=200)
            
            x = sc_test[i].inverse_transform(predicted[:,:,0])
            y = sc_test[i].inverse_transform(test_color_image[i][:,:,0])
            m2dArray.append(cv2.resize(x, (606, 750)))
            o2dArray.append(y)
            
            m = np.reshape(x, (np.shape(x)[0]*np.shape(x)[1]))
            o = np.reshape(y, (np.shape(y)[0]*np.shape(y)[1])) 
            cc= sum((m-np.mean(m))*(o-np.mean(o)))/(sum((m-np.mean(m))**2)*sum((o-np.mean(o))**2))**0.5
            mb = np.mean(m-o)
            mae = np.mean(np.abs(m-o))
            nmb = sum(m-o)/sum(o)
            print('NMB: ' + str(nmb*100)[0:4])
            print('R2: ' + str(cc**2)[0:4])
            mArray = np.hstack((mArray, m))
            oArray = np.hstack((oArray, o))
            plt.close('all')
        
        mbAll = np.mean(mArray-oArray)
        nmbAll = sum(mArray-oArray)/sum(oArray)
        cc= sum((mArray-np.mean(mArray))*(oArray-np.mean(oArray)))/(sum((mArray-np.mean(mArray))**2)*sum((oArray-np.mean(oArray))**2))**0.5
        rmseAll = np.sqrt(np.mean((mArray - oArray)**2))
        
        print(mbAll)
        print(nmbAll)
        print(cc**2)
        print(rmseAll)

        # creating ds_out file
        p = 't2_ssp585_36_46_d03_' + str(startDate.year) + str(startDate.month).zfill(2) + str(startDate.day).zfill(2)
        ds_out = nc.Dataset(p+'.nc', "w")
       
        # create dimensions
        _ = ds_out.createDimension('time', None)
        _ = ds_out.createDimension('lon', 606)
        _ = ds_out.createDimension('lat', 750)
        
        # m2dArrayResize = cv2.resize(m2dArray[:, :, :], (606, 750))

        v_in = np.array(m2dArray)
        v_in_unit = ds_in.variables['T2']
        v_out = ds_out.createVariable(
            'T2',
            np.float32,
            ("time", "lon", "lat"),
            zlib=True,
            complevel=1,
        )
        # Note: `zlib=True` is deprecated in favor of `compression='zlib'`
        # Note: complevel=4 is default, 0--9 with 9 most compression
        v_out.units = v_in_unit.units.strip()
        v_out[:] = 0
        
        v_out[:] = v_in[:]
        ds_out.close()

    startDate = startDate + tdelta.timedelta(days = 1)

# -*- coding: utf-8 -*-
"""
Created on Mon Jun 19 23:49:39 2017

@author: pasca
"""
from __future__ import print_function
import os
import imageio
import re
import numpy as np
from tqdm import tqdm
import pdb


def ParseVideos(videoPath, imagePath, sampleRate, transformFun=None, 
                overwrite=False, shift=0, suffix='mov'):
    #shift is in seconds
    
    if not os.path.isdir(imagePath):
        os.makedirs(imagePath)
    
    if not overwrite:
        oldVideoIds = [f.split('_')[0] for f in os.listdir(imagePath) if f.endswith('.jpg')]
    
    
    video_names = [f for f in os.listdir(videoPath) if f.endswith(suffix)]
    for file in tqdm(video_names):
        
        filename = os.path.join(videoPath, file)
        print(filename)
        videoId = file.split('.')[0]
        if not overwrite:
            if videoId in oldVideoIds:
                print('skip')
                continue
        
        try:
            reader = imageio.get_reader(filename)
        except OSError:
            with open("errors.txt", "a") as myfile:
                myfile.write(videoId+'\n')
            continue
        
        fps = reader.get_meta_data()['fps']
        duration = reader.get_meta_data()['duration']
        nFrame = reader.get_meta_data()['nframes']
        
        
        if sampleRate is not None:
            #calculate the time points in ms to sample frames
            timePoints = np.arange(shift*1000, duration*1000, 1000.0/sampleRate)
            timePoints = np.floor(timePoints).astype(int)
            #calculate the frame indexes
            frameIndexes = (np.floor(timePoints/1000.0*fps)).astype(int)
            nSample = len(frameIndexes)
        else:
            frameIndexes = np.arange(nFrame)
            timePoints = (frameIndexes*1000/fps).astype(int)
            nSample = nFrame
        
        for i in tqdm(range(nSample)):
            #make output file name
            imageName = os.path.join(imagePath, videoId+'_'+\
                str(timePoints[i]).zfill(5)+'.jpg')
                
            if os.path.isfile(imageName):
                print('Already exist.')
                continue
          
            #read image
            try:
                image = reader.get_data(frameIndexes[i])
            except:
                print('Can\'t read this frame. Skip')
                continue
            
            #apply transformation
            if transformFun is not None:
                image = transformFun(image)
            
            #write image
            imageio.imwrite(imageName, image)
        
    
            
#set parameters
sampleRate = 10
suffix = '.mov'
#sampleRate is in Hz. sampleRate needs to be an integer


predictionRate = 3
#predictionRate should be set to 3

videoFolder = 'data/application/camera_videos/'
imageFolder = 'data/application/camera_images/'


#parse videos
if sampleRate % predictionRate == 0:
    ParseVideos(videoFolder, imageFolder, sampleRate=sampleRate)
else:
    for i in range(predictionRate):
        ParseVideos(videoFolder, imageFolder, sampleRate=sampleRate, 
                    shift=i*1.0/sampleRate/predictionRate,
                    overwrite=True)
        




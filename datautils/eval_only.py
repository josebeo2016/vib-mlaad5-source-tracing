import os
import numpy as np
import torch
import torch.nn as nn
from torch import Tensor
import librosa
from torch.utils.data import Dataset
from datautils.RawBoost import ISD_additive_noise,LnL_convolutive_noise,SSI_additive_noise,normWav
from random import randrange
import random
import logging

logging.basicConfig(filename='errors.log', level=logging.DEBUG)

__credits__ = ["Hemlata Tak", "Xin Wang"]
__authors__ = ["Josebeo2016", "Thien-Phuc Doan"]

'''
datapath should has:
- protocol.txt
- wavdir
protocol.txt: <relative path to audio from the datapath> <subset> <label>
'''
def genList(dir_meta, is_train=False, is_eval=True, is_dev=False):
    
    d_meta = {}
    file_list=[]
    with open(dir_meta, 'r') as f:
         l_meta = f.readlines()
    
    if (is_eval):
        for line in l_meta:
            key = line.strip().split()[0]
            file_list.append(key)
        return [], file_list


def pad(x:np.ndarray, padding_type:str='zero', max_len=64000, random_start=False) -> np.ndarray:
        '''
        pad audio signal to max_len
        x: audio signal
        padding_type: 'zero' or 'repeat' when len(X) < max_len, default 'zero'
            zero: pad with zeros
            repeat: repeat the signal until it reaches max_len
        max_len: max length of the audio, default 64000
        random_start: if True, randomly choose the start point of the audio
        '''
        x_len = x.shape[0]
        padded_x = None
        if max_len == 0:
            # no padding
            padded_x = x
        elif max_len > 0:
            if x_len >= max_len:
                if random_start:
                    start = np.random.randint(0, x_len - max_len+1)
                    padded_x = x[start:start + max_len]
                    # logger.debug("padded_x1: {}".format(padded_x.shape))
                else:
                    padded_x = x[:max_len]
                    # logger.debug("padded_x2: {}".format(padded_x.shape))
            else:
                if random_start:
                    start = np.random.randint(0, max_len - x_len+1)
                    if padding_type == "repeat":
                        num_repeats = int(max_len / x_len) + 1
                        padded_x = np.tile(x, (1, num_repeats))[:, start:start + max_len][0]

                    elif padding_type == "zero":
                        padded_x = np.zeros(max_len)
                        padded_x[start:start + x_len] = x
                else:
                    if padding_type == "repeat":
                        num_repeats = int(max_len / x_len) + 1
                        padded_x = np.tile(x, (1, num_repeats))[:, :max_len][0]

                    elif padding_type == "zero":
                        padded_x = np.zeros(max_len)
                        padded_x[:x_len] = x

        else:
            raise ValueError("max_len must be >= 0")
        # logger.debug("padded_x: {}".format(padded_x.shape))
        return padded_x
			
class Dataset_for(Dataset):
    def __init__(self,args,list_IDs, labels, base_dir, algo):
        self.list_IDs = list_IDs
        self.labels = labels
        self.base_dir = base_dir
        self.algo=algo
        self.args=args
        self.cut=64600 # take ~4 sec audio (64600 samples)
    
    def __len__(self):
        return len(self.list_IDs)
    
    def __getitem__(self, index):
        utt_id = self.list_IDs[index]
        X, fs = librosa.load(self.base_dir + "/" + utt_id, sr=16000)
        # Y=process_Rawboost_feature(X,fs,self.args,self.algo)
        X_pad= pad(X,utt_id,self.cut)
        x_inp= Tensor(X_pad)
        target = self.labels[utt_id]
            
        return x_inp, target
            
            
class Dataset_for_eval(Dataset):
    def __init__(self, list_IDs, base_dir, max_len=64600, padding_type="zero", **kwargs):
        self.list_IDs = list_IDs
        self.base_dir = os.path.join(base_dir)
        self.cut=max_len # take ~4 sec audio (64600 samples)
        self.padding_type = padding_type
    def __len__(self):
        return len(self.list_IDs)
    
    def __getitem__(self, index):
            
        utt_id = self.list_IDs[index]
        X, fs = librosa.load(self.base_dir + "/" + utt_id, sr=16000)
        X_pad = pad(X,self.padding_type,self.cut)
        x_inp = Tensor(X_pad)
        return x_inp, utt_id


#--------------RawBoost data augmentation algorithms---------------------------##

def process_Rawboost_feature(feature, sr,args,algo):
    
    # Data process by Convolutive noise (1st algo)
    if algo==1:

        feature =LnL_convolutive_noise(feature,args.N_f,args.nBands,args.minF,args.maxF,args.minBW,args.maxBW,args.minCoeff,args.maxCoeff,args.minG,args.maxG,args.minBiasLinNonLin,args.maxBiasLinNonLin,sr)
                            
    # Data process by Impulsive noise (2nd algo)
    elif algo==2:
        
        feature=ISD_additive_noise(feature, args.P, args.g_sd)
                            
    # Data process by coloured additive noise (3rd algo)
    elif algo==3:
        
        feature=SSI_additive_noise(feature,args.SNRmin,args.SNRmax,args.nBands,args.minF,args.maxF,args.minBW,args.maxBW,args.minCoeff,args.maxCoeff,args.minG,args.maxG,sr)
    
    # Data process by all 3 algo. together in series (1+2+3)
    elif algo==4:
        
        feature =LnL_convolutive_noise(feature,args.N_f,args.nBands,args.minF,args.maxF,args.minBW,args.maxBW,
                 args.minCoeff,args.maxCoeff,args.minG,args.maxG,args.minBiasLinNonLin,args.maxBiasLinNonLin,sr)                         
        feature=ISD_additive_noise(feature, args.P, args.g_sd)  
        feature=SSI_additive_noise(feature,args.SNRmin,args.SNRmax,args.nBands,args.minF,
                args.maxF,args.minBW,args.maxBW,args.minCoeff,args.maxCoeff,args.minG,args.maxG,sr)                 

    # Data process by 1st two algo. together in series (1+2)
    elif algo==5:
        
        feature =LnL_convolutive_noise(feature,args.N_f,args.nBands,args.minF,args.maxF,args.minBW,args.maxBW,
                 args.minCoeff,args.maxCoeff,args.minG,args.maxG,args.minBiasLinNonLin,args.maxBiasLinNonLin,sr)                         
        feature=ISD_additive_noise(feature, args.P, args.g_sd)                
                            

    # Data process by 1st and 3rd algo. together in series (1+3)
    elif algo==6:  
        
        feature =LnL_convolutive_noise(feature,args.N_f,args.nBands,args.minF,args.maxF,args.minBW,args.maxBW,
                 args.minCoeff,args.maxCoeff,args.minG,args.maxG,args.minBiasLinNonLin,args.maxBiasLinNonLin,sr)                         
        feature=SSI_additive_noise(feature,args.SNRmin,args.SNRmax,args.nBands,args.minF,args.maxF,args.minBW,args.maxBW,args.minCoeff,args.maxCoeff,args.minG,args.maxG,sr) 

    # Data process by 2nd and 3rd algo. together in series (2+3)
    elif algo==7: 
        
        feature=ISD_additive_noise(feature, args.P, args.g_sd)
        feature=SSI_additive_noise(feature,args.SNRmin,args.SNRmax,args.nBands,args.minF,args.maxF,args.minBW,args.maxBW,args.minCoeff,args.maxCoeff,args.minG,args.maxG,sr) 
   
    # Data process by 1st two algo. together in Parallel (1||2)
    elif algo==8:
        
        feature1 =LnL_convolutive_noise(feature,args.N_f,args.nBands,args.minF,args.maxF,args.minBW,args.maxBW,
                 args.minCoeff,args.maxCoeff,args.minG,args.maxG,args.minBiasLinNonLin,args.maxBiasLinNonLin,sr)                         
        feature2=ISD_additive_noise(feature, args.P, args.g_sd)

        feature_para=feature1+feature2
        feature=normWav(feature_para,0)  #normalized resultant waveform
 
    # original data without Rawboost processing           
    else:
        
        feature=feature
    
    return feature

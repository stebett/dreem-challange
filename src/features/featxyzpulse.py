import numpy as np
import h5py
import matplotlib.pyplot as plt
import scipy.stats as scs
from scipy.signal import butter, lfilter, freqz

#first run pulse,x,y,z,mode=read(mode='train' or 'test')


pathtosave="../../data/interim/"


def read(mode='train'):
    filename = "../../data/raw/X_"+str(mode)+".h5"
    pulse = np.array(h5py.File(filename, mode='r')['pulse'])
    x = np.array(h5py.File(filename, mode='r')['x'])
    y = np.array(h5py.File(filename, mode='r')['y'])
    z =np.array(h5py.File(filename, mode='r')['z'])
    return pulse,x,y,z,mode


def extractall(save=True):
    a=extractpulse(save=save)[0]
    b=extractentropy(save=save)[0]
    c=extractbreath(save=save)[0]
    d=extractagitation(save=save)[0]
    return a,b,c,mode

def extractpulse(save=True):
    Lpulse=[]
    product=pulse[:,1:]*pulse[:,:-1]
    for i in range (product.shape[0]):
        Lpulse.append((np.where(product[i]<0))[0].shape)
    Lpulse=np.array(Lpulse)
    if save==True:
         np.save(pathtosave+'lpulse'+str(mode)+'.npy',Lpulse)
    return Lpulse,mode


def extractentropy(save=True,bins=100):
    entrpulse=entropyarray(pulse,bins)
    entrx=entropyarray(x,bins)
    entry=entropyarray(y,bins)
    entrz=entropyarray(z,bins)
    out= np.transpose(np.array([entrpulse,entrx,entry,entrz]))
    if save==True:
         np.save(pathtosave+'entropy'+str(mode)+'.npy',out)
    return out,mode



def extractbreath(save=True):
    '''
    extracts breathing freq from z 
    pb tp save
    '''
    fs = 10
    lowcut = 0.2
    highcut = 0.5
    n=z.shape[0]
    zmstd=(z-np.reshape(z.mean(axis=1),(n,1)))
    zmstd=(zmstd/np.reshape(z.std(axis=1),(n,1)))
    Lbreath,count=[],[]
    for x in zmstd:
        Lbreath.append(butter_bandpass_filter(x, lowcut, highcut, fs, order=2))
    Lbreath=np.array(Lbreath)
    productb=Lbreath[:,1:]*Lbreath[:,:-1]
    for i in range (productb.shape[0]):
        count.append((np.where(productb[i]<0))[0].shape)
    count=np.array(count)
    if save==True:
        np.save(pathtosave+'breath'+str(mode)+'.npy',count)
    return count,mode
    

def extractagitation(save=True):
    agx=np.sum(abs(x),axis=1)
    agy=np.sum(abs(y),axis=1)
    agz=np.sum(abs(z),axis=1)
    ag=np.array([agx,agy,agz]).T
    print(ag.shape)
    if save==True:
         np.save(pathtosave+'agitation'+str(mode)+'.npy',ag)
    return ag,mode



#--------------------------------------------------------------------------------------------#


def entropyarray(x,bins):
    L=list()
    for elt in x:
        L.append(entropySignal(elt,bins))
    return np.array(L)

def entropySignal(x,bins):
    hist=np.histogram(x,bins=bins,density=True)[0]
    return scs.entropy(hist)



def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a


def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y

if __name__ == "__main__":
    pulse, x, y, z, mode = read(mode='train')
    extractagitation()
    pulse, x, y, z, mode = read(mode='test')
    extractagitation()


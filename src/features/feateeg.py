import numpy as np
import h5py
import matplotlib.pyplot as plt
import scipy.stats as scs
from RC import scale

pathtosave="../../data/interim/"

def read(mode='train'):
    filename = "../../data/raw/X_"+str(mode)+".h5"
    eegs = []
    for i in range(1, 8):
        np_array = np.array(h5py.File(filename, mode='r')['eeg_'+str(i)])
        eegs.append(np_array)
    eegs=np.array(eegs)
    return eegs,mode


def extractall(save=True):
    a=extractfbandsfull(save=save)[0]
    b=extractentropeeg(save=save)[0]
    c=extractvar(save=save)[0]
    d=extractMMD(save=save)[0]
    e=extractfreqmax(save=save)[0]
    f=extractPFD(save=save)[0]
    return a,b,c,d,e,f,mode

def extractfbandsfull(save=True,cuts=1):
    L=list()
    for i in range(7):
        L.append(extractfbands(eegs[i],cuts))
    L=np.array(L)
    s=L.shape
    L=L.reshape((s[0],s[1],s[2],s[3]))
    L=np.moveaxis(L,[3],[0])
    s=L.shape
    print(s)
    L=np.reshape(L,(s[0],L[0].size))
    if save==True:
        np.save(pathtosave+"fbands"+str(mode)+".npy", L)
    return L,mode


def extractentropeeg(save=True,bins=1000):
    entreegs=np.array([entropyarray(eegs[i],bins) for i in range(7)])
    if save==True:
        np.save(pathtosave+'entreeg'+str(mode)+'.npy',entreegs.T)
    return entreegs.T,mode



def old_extractvar(save=True):
    varray=np.array([np.log(np.var(eegs[i],axis=1)) for i in range(7)])
    minmax=np.array([(np.max(eegs[i],axis=1)-np.min(eegs[i],axis=1)) for i in range(7)])
    minmaxvarray=np.array([minmax.T,varray.T])    
    minmaxvarray= np.moveaxis(minmaxvarray,[1],[0])
    s=minmaxvarray.shape
    minmaxvarray=minmaxvarray.reshape((s[0],s[1]*s[2]))
    if save==True:
        np.save(pathtosave+'minmaxvarray'+str(mode)+'.npy',minmaxvarray)

    return minmaxvarray,mode


def extractvar(save=True):
    varray = np.log(np.var(eegs, axis=2))
    minmax = np.max(eegs, axis=2) - np.min(eegs,axis=2)
    minmax_norm = np.max(scale(eegs), axis=2) - np.min(scale(eegs),axis=2)
    full_array = np.concatenate([varray, minmax, minmax_norm.T]).T
    if save==True:
        np.save(pathtosave+'minmaxvarray'+str(mode)+'.npy',full_array)

    return full_array,mode



def extractMMD(save=True):
    MMD=np.array([np.log(partitionsum(eegs[i],3)) for i in range(7)])
    if save==True:
        np.save(pathtosave+'MMD'+str(mode)+'.npy',MMD.T)
    return MMD.T,mode



def extractfreqmax(save=True,cuts=1):
    fmax=np.squeeze(np.array([extractfmax(eegs[i],cuts) for i in range(7)]).T)
    if save==True:
        np.save(pathtosave+'fmax'+str(mode)+'.npy',fmax)
    return fmax,mode



def extractPFD(save=True):
    '''Petrosian Fractal Dimension
    '''
    listPFD=[]
    for i in range (7):
        dif=eegs[i,:,1:]-eegs[i,:,:-1]
        PFD=computePFD(dif)
        listPFD.append(PFD)
    listPFD=np.array(listPFD)
    listPFD=listPFD.T
    print(listPFD.shape)
    if save==True:
        np.save(pathtosave+'PFD'+str(mode)+'.npy',listPFD)
    return listPFD,mode

#--------------------------------------------------------------------------------------------#


def computePFD(dif):
    chsidif=dif[:,1:]*dif[:,:-1]
    truefalse=chsidif<0
    ndel=np.sum(truefalse*1,axis=1)
    n=dif.shape[1]
    lo=np.log10(n)
    londel=np.log10(n/(n+0.4*ndel))
    print(dif.shape,truefalse.shape,ndel,n,lo.shape,londel.shape)
    return lo/(lo+londel)



def d(epochs):
    '''epochs an array of time series cut in time the way you want
    output is a distance d
    '''
    dx=abs(np.argmax(epochs,axis=1)-np.argmin(epochs,axis=1)) 
    dy=np.max(epochs,axis=1)-np.min(epochs,axis=1)
    return np.sqrt(dx**2+dy**2)
    
def partitionsum(ts,lepoch=10,lts=30):
    '''ts : array of time series
    lepoch :duration of epoch
    lts = duration of time series
    '''
    if lts%lepoch!=0:
        print('lts must be a multiple of lepoch')
        
    indexts=ts.shape[1]    
    nepoch=int(lts/lepoch)
    indexepoch=int(indexts/nepoch)
    sum=0
    for i in range (nepoch):
        sum+=d(ts[:,i*indexepoch:(i+1)*indexepoch])
    return sum





def entropyarray(x,bins):
    L=list()
    for elt in x:
        L.append(entropySignal(elt,bins))
    return np.array(L)


def entropySignal(x,bins):
    hist=np.histogram(x,bins=bins,density=True)[0]
    return scs.entropy(hist)

def extractfbands(eeg,cuts):
    L=list()
    s=eeg.shape
    idcut=int(s[1]/cuts)
    freq=np.fft.fftfreq(idcut,1/50)[:int(idcut/2)]
    plt.plot(freq)
    for i in range(cuts):
        print(i)
        FFT=np.fft.fft(eeg[:,i*idcut:(i+1)*idcut],axis=1)[:,:int(idcut/2)]
        FFT=abs(FFT)
        delta=np.sum(FFT[:,np.where((freq<4)*(freq>0))],axis=2)
        theta=np.sum(FFT[:,np.where((freq>4)* (freq<8))],axis=2)
        alpha=np.sum(FFT[:,np.where((freq>8)* (freq<13))],axis=2)
        beta=np.sum(FFT[:,np.where((freq>13 )* (freq<22))],axis=2)
        gamma=np.sum(FFT[:,np.where(freq>22)],axis=2)
        L.append( np.array([delta,theta,alpha,beta,gamma]))
    return np.array(L)


def extractfmax(eeg,cuts):
    L=list()
    s=eeg.shape
    idcut=int(s[1]/cuts)
    freq=np.fft.fftfreq(idcut,1/50)[:int(idcut/2)]
    for i in range(cuts):
        FFT=np.fft.fft(eeg[:,i*idcut:(i+1)*idcut],axis=1)[:,:int(idcut/2)]
        FFT=abs(FFT)
        f=np.sum(FFT*freq,axis=1)/np.sum(FFT,axis=1)
        L.append(f)
    return np.array(L)

if __name__ == "__main__":
    eegs, mode = read("train")
    extractvar()
    eegs, mode = read("test")
    extractvar()


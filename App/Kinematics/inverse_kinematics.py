from sklearn.metrics import mean_squared_error
import numpy as np
from .forward_kinematics import forward_kinematics

def cos(t):
    return np.cos(np.deg2rad(t))
def sin(t):
    return np.sin(np.deg2rad(t))
from sklearn.metrics import mean_absolute_error
def finder(fk, i):
    dx,dy,dz=fk
    eT2=(90-i)
    l1=104.
    l2=89.
    l3=175.
    r = np.sqrt(dx**2+dy**2)
    r1 = cos(eT2)*l1
    r2 = r-r1
    t = sin(eT2)*l1
    t1=t-(dz-95)
    if(t1!=0):        
        alpha1=np.arctan(r2/t1)
        alpha1=np.degrees(alpha1)
    else:
        alpha1=0
    b=np.sqrt(t1**2+r2**2)
    operation1=(l2**2+b**2-l3**2)/(2*l2*b)
    operation2=(l2**2+l3**2-b**2)/(2*l2*l3)
    if(int(operation1*100)>100 or int(operation1*100)<-100):
        raise Exception() 
    if(int(operation1*100)==100 or int(operation1*100)==-100):
        operation1=np.round(operation1)
        
    if(int(operation2*100)>100 or int(operation2*100)<-100):
        raise Exception() 
    if(int(operation2*100)==100 or int(operation2*100)==-100):
        operation2=np.round(operation2)

    alpha2=np.arccos(operation1)
    alpha2=np.degrees(alpha2)
    if(t1>0):
        T3=180-(alpha1+alpha2+i)
        T3=np.round(T3)
    else:
        T3=alpha1+alpha2+i
        T3=abs(np.round(T3))
    T4=np.arccos(operation2)

    T4=np.degrees(T4)
    T4=180-T4
    T4=np.round(T4)

    if T3>90 or T4>90:
        raise Exception()
    return T3, T4

def find_T2(T1,fk_true):

    mse={}

    for i in range(91):
        try:
            T3, T4 = finder(fk_true, i)
            fk =forward_kinematics(T1,i,T3,T4)[:3,3]
            if (np.array_equal(fk_true,fk) and np.isclose(180,(i+T3+T4),atol=5)):
                return i, T3, T4
            mse[i]=[mean_absolute_error(np.append(fk_true,180),np.append(fk,i+T3+T4)),T3,T4]
        except:
            pass
    else:
        T2 =min(mse,key=mse.get)
        T3, T4 = mse[T2][1:]
        return T2,T3,T4
def calculate_inverse_kinematics(fk):
    dx,dy,dz=fk
    #if(np.sqrt(dx**2+dy**2)-dz<64):
       # raise Exception("It was entered lower value than arm can reach")
    # Find T1
    if(dx==0.):
        T1=90
    else:
        T1= np.arctan(dy/dx)
        T1=np.degrees(-T1)
        T1=np.round(T1)
    #Find T3
    T2, T3, T4=find_T2(T1,fk)
    eT2=(90-T2)
    eT3=(90-T3)+eT2
    eT4=(90-T4)+eT3
   # print(T2+T3+T4)
    return float(T1), float(T2), float(T3), float(T4)
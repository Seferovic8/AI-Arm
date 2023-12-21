import numpy as np
from numpy import cos, sin
def create_dh_parameters_table(T1,T2,T3,T4):
    T1=(-T1/180.0)*np.pi
    T2=((-T2+90)/180.0)*np.pi
    T3=(-T3/180.0)*np.pi
    T4=(-T4/180.0)*np.pi
    return np.array([[0, 0., 0.   ,95.],
              [T1, (90/180.0)*np.pi, 0.   ,0.],
              [T2, 0., 104. ,0.],
              [T3, 0., 89.  ,0.],
              [T4, 0., 175. ,0.],
              ])
def create_dh_matrix(n,dh):
    return [
    [cos(dh[n][0]), -sin(dh[n][0])*cos(dh[n][1]), sin(dh[n][0])*sin(dh[n][1]),dh[n][2]*cos(dh[n][0])],
    [sin(dh[n][0]), cos(dh[n][0])*cos(dh[n][1]), -cos(dh[n][0])*sin(dh[n][1]),dh[n][2]*sin(dh[n][0])],
    [0, sin(dh[n][1]), cos(dh[n][1]),dh[n][3]],
    [0,0,0,1]]

def forward_kinematics(T1,T2,T3,T4):
    result=1.
    dh_table=create_dh_parameters_table(T1,T2,T3,T4)
    for i in range(len(dh_table)):
        result=np.dot(result, create_dh_matrix(i,dh_table))
    return np.round(result)
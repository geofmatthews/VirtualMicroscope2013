
import numpy as N

def identity():
    return N.array(((1,0,0,0),
                    (0,1,0,0),
                    (0,0,1,0),
                    (0,0,0,1)), dtype=N.float32)

def projection(n,f,r,t):
    return N.array(((n/float(r), 0, 0, 0),
                    (0, n/float(t), 0, 0),
                    (0, 0, -(f+n)/float(f-n), -2*f*n/(float(f-n))),
                    (0, 0, -1.0, 0)), dtype=N.float32)

def translation(x,y,z):
    return N.array(((1,0,0,x),
                    (0,1,0,y),
                    (0,0,1,z),
                    (0,0,0,1)), dtype=N.float32)

def scale(x,y,z):
    return N.array(((x,0,0,0),
                    (0,y,0,0),
                    (0,0,z,0),
                    (0,0,0,1)),dtype=N.float32)

def scaleU(x):
    return scale(x,x,x)

def rotationZ(angle):
    sina = N.sin(angle)
    cosa = N.cos(angle)
    return N.array(((cosa, -sina,    0, 0),
                    (sina,  cosa,    0, 0),
                    (0   ,     0,    1, 0),
                    (0   ,     0,    0, 1)), dtype=N.float32)

def rotationY(angle):
    sina = N.sin(angle)
    cosa = N.cos(angle)
    return N.array(((cosa,     0, -sina, 0),
                    (0   ,     1,     0, 0),
                    (sina,     0,  cosa, 0),
                    (0   ,     0,     0, 1)), dtype=N.float32)

def rotationX(angle):
    sina = N.sin(angle)
    cosa = N.cos(angle)
    return N.array(((    1,    0,     0, 0),
                    (    0, cosa, -sina, 0),
                    (    0, sina,  cosa, 0),
                    (    0,     0,    0, 1)), dtype=N.float32)

def rotationAxis(angle, axis):
    sina = N.sin(angle)
    cosa = N.cos(angle)
    cosa1 = 1.0 - cosa
    x,y,z = axis
    mag = N.sqrt(x*x+y*y+z*z)
    x /= mag
    y /= mag
    z /= mag
    return N.array(((   cosa+x*x*cosa1, x*y*cosa1-z*sina,  y*sina+x*z*cosa1, 0),
                    ( z*sina+x*y*cosa1,   cosa+y*y*cosa1, -x*sina+y*z*cosa1, 0),
                    (-y*sina+x*z*cosa1, x*sina+y*z*cosa1,    cosa+z*z*cosa1, 0),
                    (                0,                0,                 0, 1)),dtype=N.float32)


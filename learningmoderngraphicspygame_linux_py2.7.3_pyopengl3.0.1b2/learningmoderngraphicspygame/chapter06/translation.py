

from ctypes import c_void_p

from OpenGL.GL import *
from OpenGL.GL.ARB.vertex_array_object import *
from OpenGL.GL.shaders import compileShader, compileProgram

import pygame
from pygame.locals import *
import numpy as N

from transform import *

null = c_void_p(0)

# This is lame. What's the right way to get the sizeof(GLfloat) ?
# Tried sys.getsizeof(GLfloat), sys.getsizeof(GLfloat()),
# GLfloat().__sizeof__(). All give different wrong answers (size of python
# objects, not of underlying C 'float' type)
sizeOfFloat = 4
sizeOfShort = 2

GREEN_COLOR = [0.0, 1.0, 0.0, 1.0]
BLUE_COLOR  = [0.0, 0.0, 1.0, 1.0]
RED_COLOR  = [1.0, 0.0, 0.0, 1.0]
GREY_COLOR  = [0.8, 0.8, 0.8, 1.0]
BROWN_COLOR  = [0.5, 0.5, 0.0, 1.0]

numberOfVertices = 8
vertexData = [
    1,1,1,
    -1,-1,1,
    -1,1,-1,
    1,-1,-1,

    -1,-1,-1,
    1,1,-1,
    1,-1,1,
    -1,1,1]

vertexData += GREEN_COLOR+BLUE_COLOR+RED_COLOR+BROWN_COLOR
vertexData += GREEN_COLOR+BLUE_COLOR+RED_COLOR+BROWN_COLOR

vertexData = N.array(vertexData, dtype=N.float32)

indexData = N.array((0,1,2,
                     1,0,3,
                     2,3,0,
                     3,2,1,

                     5,4,6,
                     4,5,7,
                     7,6,4,
                     6,7,5), dtype=N.uint16)

def CalcFrustumScale(fFovDeg):
    degToRad = 3.14159 * 2.0 / 360.0
    fFovRad = fFovDeg * degToRad
    return 1.0/N.tan(fFovRad/2.0)

fFrustumScale = CalcFrustumScale(45.0)

theProgram = None

def loadFile(filename):
    with open(filename) as fp:
        return fp.read()
strVertexShader = loadFile('PosColorLocalTransform.vert')
strFragmentShader = loadFile('ColorPassthrough.frag')

theProgram = None

modelToCameraMatrixUnif = None
cameraToClipMatrixUnif = None

def InitializeProgram():
    global modelToCameraMatrixUnif, cameraToClipMatrixUnif, fFrustumScale, theProgram
    theProgram = compileProgram(
        compileShader(strVertexShader, GL_VERTEX_SHADER),
        compileShader(strFragmentShader, GL_FRAGMENT_SHADER)
    )
    modelToCameraMatrixUnif = glGetUniformLocation(theProgram, "modelToCameraMatrix")
    cameraToClipMatrixUnif = glGetUniformLocation(theProgram, "cameraToClipMatrix")
    fzNear = 1.0
    fzFar = 45.0

    theMatrix = projection(fzNear, fzFar, fzNear/fFrustumScale, fzNear/fFrustumScale)

    glUseProgram(theProgram)
    glUniformMatrix4fv(cameraToClipMatrixUnif, 1, True, theMatrix)
    glUseProgram(0);

vertexBufferObject = None
indexBufferObject = None

def InitializeVertexBuffer():
    global vertexBufferObject, indexBufferObject
    
    vertexBufferObject = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vertexBufferObject)
    glBufferData(
        GL_ARRAY_BUFFER, len(vertexData) * sizeOfFloat,
        vertexData, GL_STATIC_DRAW
    )
    glBindBuffer(GL_ARRAY_BUFFER, 0)

    indexBufferObject = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, indexBufferObject)
    glBufferData(
        GL_ELEMENT_ARRAY_BUFFER, len(indexData) * sizeOfShort,
        indexData, GL_STATIC_DRAW
        )
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

def StationaryOffset(fElapsedTime):
    return N.array((0.0, 0.0, -20.0), dtype=N.float32)

def OvalOffset(fElapsedTime):
    fLoopDuration = 3.0
    fScale = 3.14159 * 2.0 / fLoopDuration
    fCurrTimeThroughLoop = N.mod(fElapsedTime, fLoopDuration)
    return N.array((N.cos(fCurrTimeThroughLoop * fScale) * 4.0,
                    N.sin(fCurrTimeThroughLoop * fScale) * 6.0,
                    -20.0), dtype=N.float32)

def BottomCircleOffset(fElapsedTime):
    fLoopDuration = 3.0
    fScale = 3.14159 * 2.0 / fLoopDuration
    fCurrTimeThroughLoop = N.mod(fElapsedTime, fLoopDuration)
    return N.array((N.cos(fCurrTimeThroughLoop * fScale) * 5.0,
                    -3.5,
                    N.sin(fCurrTimeThroughLoop * fScale) * 5.0 - 20.0), dtype=N.float32)
    
class Instance():
    def __init__(self, CalcOffset):
        self.CalcOffset = CalcOffset

    def ConstructMatrix(self, fElapsedTime):
        x,y,z = self.CalcOffset(fElapsedTime)
        return translation(x,y,z)

g_instanceList = [Instance(StationaryOffset),
                  Instance(OvalOffset),
                  Instance(BottomCircleOffset)]

vao = None

# Called once at application start-up.
# Must be called after we have an OpenGL context, i.e. after the pyglet
# window is created
def init():
    global vao, vertexBufferObject, indexBufferObject
    InitializeProgram()
    InitializeVertexBuffer()
    
    n = 1
    vao = arrays.GLuintArray.zeros((n,))
    glBindVertexArray( vao )
    
    colorDataOffset = sizeOfFloat * 3 * numberOfVertices
    glBindBuffer(GL_ARRAY_BUFFER, vertexBufferObject)
    glEnableVertexAttribArray(0)
    glEnableVertexAttribArray(1)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, c_void_p(0))
    glVertexAttribPointer(1, 4, GL_FLOAT, GL_FALSE, 0, c_void_p(colorDataOffset))
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, indexBufferObject)

    glBindVertexArray(0)

    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)
    glFrontFace(GL_CW)
    
    glEnable(GL_DEPTH_TEST)
    glDepthMask(GL_TRUE)
    glDepthFunc(GL_LEQUAL)
    glDepthRange(0.0, 1.0)
	
# Called to redraw the contents of the window
def display():
    global vao, theProgram, modelToCameraMatrixUnif

    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClearDepth(1.0)
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

    glUseProgram(theProgram)

    glBindVertexArray(vao)
    
    fElapsedTime = pygame.time.get_ticks()/1000.0
    
    for iLoop in range(len(g_instanceList)):
        currInst = g_instanceList[iLoop]
        transformMatrix = currInst.ConstructMatrix(fElapsedTime)
        glUniformMatrix4fv(modelToCameraMatrixUnif, 1, True, transformMatrix)
        glDrawElements(GL_TRIANGLES, len(indexData)*sizeOfShort,
                       GL_UNSIGNED_SHORT, c_void_p(0))
    
    glBindVertexArray(0)
    glUseProgram(0)

screen = None
SCREENSIZE = (512,512)

def main():
    global screen,clock,SCREENSIZE
    pygame.init()
    screen = pygame.display.set_mode(SCREENSIZE, OPENGL|DOUBLEBUF)
    
    clock = pygame.time.Clock()
    init()
    while True:     
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            if event.type == KEYUP and event.key == K_ESCAPE:
                return               
        display()
        pygame.display.flip()

if __name__ == '__main__':
    try:
        main()
    finally:
        pygame.quit()


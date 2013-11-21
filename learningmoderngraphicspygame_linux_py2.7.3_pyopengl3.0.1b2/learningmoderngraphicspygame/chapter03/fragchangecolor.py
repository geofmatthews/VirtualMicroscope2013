

from ctypes import c_void_p

import OpenGL.GL as GL
import OpenGL.GL.ARB.vertex_array_object as GLARBVAO

for name in dir(GLARBVAO):
    GL.__setattr__(name, GLARBVAO.__getattribute__(name))

from OpenGL.GL.shaders import compileShader, compileProgram

import pygame
from pygame.locals import *
import numpy as N

null = c_void_p(0)

# This is lame. What's the right way to get the sizeof(GLfloat) ?
# Tried sys.getsizeof(GLfloat), sys.getsizeof(GLfloat()),
# GLfloat().__sizeof__(). All give different wrong answers (size of python
# objects, not of underlying C 'float' type)
sizeOfFloat = 4

# Three vertices, with an x,y,z & w for each.
vertexPositions = N.array([
	0.25, 0.25, 0.0, 1.0,
	0.25, -0.25, 0.0, 1.0,
	-0.25, -0.25, 0.0, 1.0
],dtype = N.float32)
vertexComponents = 4

def loadFile(filename):
    with open(filename) as fp:
        return fp.read()

strVertexShader = loadFile('calcOffset.vert')
strFragmentShader = loadFile('calcColor.frag')

# Integer handle identifying our compiled shader program
theProgram = None

# Integer handle identifying the GPU memory storing our vertex position array
positionBufferObject = None
elapsedTimeUniform = None
loopDurationUnf = None
fragLoopDurUnf = None

def initialize_program():
    global theProgram, elapsedTimeUniform, loopDurationUnf, fralLoopDurUnf
    """
    Instead of calling OpenGL's shader compilation functions directly
    (glShaderSource, glCompileShader, etc), we use PyOpenGL's wrapper
    functions, which are much simpler to use.
    """
    global theProgram
    theProgram = compileProgram(
        compileShader(strVertexShader, GL.GL_VERTEX_SHADER),
        compileShader(strFragmentShader, GL.GL_FRAGMENT_SHADER)
    )
    elapsedTimeUniform = GL.glGetUniformLocation(theProgram, 'time')
    loopDurationUnf = GL.glGetUniformLocation(theProgram, 'loopDuration')
    fragLoopDurUnf = GL.glGetUniformLocation(theProgram, 'fragLoopDuration')
    GL.glUseProgram(theProgram)
    GL.glUniform1f(loopDurationUnf, 5.0)
    GL.glUniform1f(fragLoopDurUnf, 10.0)
    GL.glUseProgram(0)

def initialize_vertex_buffer():
    global positionBufferObject
    positionBufferObject = GL.glGenBuffers(1)
    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, positionBufferObject)
    GL.glBufferData(
        GL.GL_ARRAY_BUFFER, len(vertexPositions) * sizeOfFloat,
        vertexPositions, GL.GL_STREAM_DRAW
    )
    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)

def ComputePositionOffsets():
    fLoopDuration = 5.0
    fScale = 3.14159*2.0/fLoopDuration
    fElapsedTime = pygame.time.get_ticks()/1000.0
    fCurrTimeThroughLoop = N.mod(fElapsedTime, fLoopDuration)
    xoffset = N.cos(fCurrTimeThroughLoop * fScale) * 0.5
    yoffset = N.sin(fCurrTimeThroughLoop * fScale) * 0.5
    return (xoffset, yoffset)

def AdjustVertexData(fXOffset, fYOffset):
    global vertexPositions
    n = len(vertexPositions)
    fNewData = N.copy(vertexPositions)
    # do this with slices!
    for iVertex in N.arange(0,n,4):
        fNewData[iVertex] += fXOffset
        fNewData[iVertex+1] += fYOffset
    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, positionBufferObject)
    GL.glBufferSubData(GL.GL_ARRAY_BUFFER, 0, fNewData)
    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
    
# Called once at application start-up.
# Must be called after we have an OpenGL context, i.e. after the pyglet
# window is created
def init():
    initialize_program()
    initialize_vertex_buffer()
    
    n = 1
    vao_array = GL.arrays.GLuintArray.zeros((n,))
    GL.glBindVertexArray( vao_array )


# Called to redraw the contents of the window
def display():
    global offsetLocation
    fXOffset, fYOffset = ComputePositionOffsets()
    
    GL.glClearColor(0.0, 0.0, 0.0, 0.0)
    GL.glClear(GL.GL_COLOR_BUFFER_BIT)

    GL.glUseProgram(theProgram)

    GL.glUniform1f(elapsedTimeUniform, pygame.time.get_ticks()/1000.0)
    
    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, positionBufferObject)
    GL.glEnableVertexAttribArray(0)
    GL.glVertexAttribPointer(0, vertexComponents, GL.GL_FLOAT, False, 0, null)

    GL.glDrawArrays(GL.GL_TRIANGLES, 0, len(vertexPositions) / vertexComponents)

    GL.glDisableVertexAttribArray(0)
    GL.glUseProgram(0)

    # equivalent of glutSwapBuffers and glutPostRedisplay is done for us by
    # pygame


# Called when the window is resized, including once at application start-up
def reshape(width, height):
    GL.glViewport(0, 0, width, height)

screen = None

def main():
    global screen,clock
    pygame.init()
    screen = pygame.display.set_mode((640,480), OPENGL|DOUBLEBUF)
    clock = pygame.time.Clock()
    init()
    while True:
        clock.tick(30)
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


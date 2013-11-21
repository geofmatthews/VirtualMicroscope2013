
from ctypes import c_void_p
from os.path import dirname, join

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
     0.75,  0.75,  0.0,  1.0,
     0.75, -0.75,  0.0,  1.0,
    -0.75, -0.75,  0.0,  1.0,
],dtype=N.float32)
vertexComponents = 4

# the Pyglet window object
window = None

# Integer handle identifying our compiled shader program
theProgram = None

# Integer handle identifying the GPU memory storing our vertex position array
positionBufferObject = None


def loadFile(filename):
    with open(filename) as fp:
        return fp.read()


def initialize_program():
    """
    Instead of calling OpenGL's shader compilation functions directly
    (glShaderSource, glCompileShader, etc), we use PyOpenGL's wrapper
    functions, which are much simpler to use.
    """
    global theProgram
    theProgram = compileProgram(
        compileShader(
            loadFile('fragposition.vert'), GL.GL_VERTEX_SHADER),
        compileShader(
            loadFile('fragposition.frag'), GL.GL_FRAGMENT_SHADER)
    )


def initialize_vertex_buffer():
    global positionBufferObject
    positionBufferObject = GL.glGenBuffers(1)
    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, positionBufferObject)
    array_type = (GL.GLfloat * len(vertexPositions))
    GL.glBufferData(
        GL.GL_ARRAY_BUFFER, len(vertexPositions) * sizeOfFloat,
        array_type(*vertexPositions), GL.GL_STATIC_DRAW
    )
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
    GL.glClearColor(0.0, 0.0, 0.0, 0.0)
    GL.glClear(GL.GL_COLOR_BUFFER_BIT)

    GL.glUseProgram(theProgram)
    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, positionBufferObject)
    GL.glEnableVertexAttribArray(0)
    GL.glVertexAttribPointer(0, vertexComponents, GL.GL_FLOAT, False, 0, null)

    GL.glDrawArrays(GL.GL_TRIANGLES, 0, len(vertexPositions) / vertexComponents)

    GL.glDisableVertexAttribArray(0)
    GL.glUseProgram(0)


# Called when the window is resized, including once at application start-up
def reshape(width, height):
    GL.glViewport(0, 0, width, height)


screen = None

def main():
    global screen
    pygame.init()
    screen = pygame.display.set_mode((640,480), OPENGL|DOUBLEBUF)
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


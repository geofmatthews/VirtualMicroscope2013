

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
vertexData = N.array([
	 0.25,  0.25, 0.75, 1.0,
	 0.25, -0.25, 0.75, 1.0,
	-0.25,  0.25, 0.75, 1.0,

	 0.25, -0.25, 0.75, 1.0,
	-0.25, -0.25, 0.75, 1.0,
	-0.25,  0.25, 0.75, 1.0,

	 0.25,  0.25, -0.75, 1.0,
	-0.25,  0.25, -0.75, 1.0,
	 0.25, -0.25, -0.75, 1.0,

	 0.25, -0.25, -0.75, 1.0,
	-0.25,  0.25, -0.75, 1.0,
	-0.25, -0.25, -0.75, 1.0,

	-0.25,  0.25,  0.75, 1.0,
	-0.25, -0.25,  0.75, 1.0,
	-0.25, -0.25, -0.75, 1.0,

	-0.25,  0.25,  0.75, 1.0,
	-0.25, -0.25, -0.75, 1.0,
	-0.25,  0.25, -0.75, 1.0,

	 0.25,  0.25,  0.75, 1.0,
	 0.25, -0.25, -0.75, 1.0,
	 0.25, -0.25,  0.75, 1.0,

	 0.25,  0.25,  0.75, 1.0,
	 0.25,  0.25, -0.75, 1.0,
	 0.25, -0.25, -0.75, 1.0,

	 0.25,  0.25, -0.75, 1.0,
	 0.25,  0.25,  0.75, 1.0,
	-0.25,  0.25,  0.75, 1.0,

	 0.25,  0.25, -0.75, 1.0,
	-0.25,  0.25,  0.75, 1.0,
	-0.25,  0.25, -0.75, 1.0,

	 0.25, -0.25, -0.75, 1.0,
	-0.25, -0.25,  0.75, 1.0,
	 0.25, -0.25,  0.75, 1.0,

	 0.25, -0.25, -0.75, 1.0,
	-0.25, -0.25, -0.75, 1.0,
	-0.25, -0.25,  0.75, 1.0,




	0.0, 0.0, 1.0, 1.0,
	0.0, 0.0, 1.0, 1.0,
	0.0, 0.0, 1.0, 1.0,

	0.0, 0.0, 1.0, 1.0,
	0.0, 0.0, 1.0, 1.0,
	0.0, 0.0, 1.0, 1.0,

	0.8, 0.8, 0.8, 1.0,
	0.8, 0.8, 0.8, 1.0,
	0.8, 0.8, 0.8, 1.0,

	0.8, 0.8, 0.8, 1.0,
	0.8, 0.8, 0.8, 1.0,
	0.8, 0.8, 0.8, 1.0,

	0.0, 1.0, 0.0, 1.0,
	0.0, 1.0, 0.0, 1.0,
	0.0, 1.0, 0.0, 1.0,

	0.0, 1.0, 0.0, 1.0,
	0.0, 1.0, 0.0, 1.0,
	0.0, 1.0, 0.0, 1.0,

	0.5, 0.5, 0.0, 1.0,
	0.5, 0.5, 0.0, 1.0,
	0.5, 0.5, 0.0, 1.0,

	0.5, 0.5, 0.0, 1.0,
	0.5, 0.5, 0.0, 1.0,
	0.5, 0.5, 0.0, 1.0,

	1.0, 0.0, 0.0, 1.0,
	1.0, 0.0, 0.0, 1.0,
	1.0, 0.0, 0.0, 1.0,

	1.0, 0.0, 0.0, 1.0,
	1.0, 0.0, 0.0, 1.0,
	1.0, 0.0, 0.0, 1.0,

	0.0, 1.0, 1.0, 1.0,
	0.0, 1.0, 1.0, 1.0,
	0.0, 1.0, 1.0, 1.0,

	0.0, 1.0, 1.0, 1.0,
	0.0, 1.0, 1.0, 1.0,
	0.0, 1.0, 1.0, 1.0,

],dtype = N.float32)
vertexComponents = 4

def loadFile(filename):
    with open(filename) as fp:
        return fp.read()
strVertexShader = loadFile('ManualPerspective.vert')
strFragmentShader = loadFile('StandardColors.frag')

# Integer handle identifying our compiled shader program
theProgram = None

# Integer handle identifying the GPU memory storing our vertex position array
offsetUniform = None
frustumScaleUnif = None
zNearUnif = None
zFarUnif = None

def initialize_program():
    global offsetUniform, frustrumScaleUnif, zNearUnif, zFarUnif
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
    offsetUniform = GL.glGetUniformLocation(theProgram, 'offset')

    frustumScaleUnif = GL.glGetUniformLocation(theProgram, 'frustumScale')
    zNearUnif = GL.glGetUniformLocation(theProgram, 'zNear')
    zFarUnif = GL.glGetUniformLocation(theProgram, 'zFar')

    GL.glUseProgram(theProgram)
    GL.glUniform1f(frustumScaleUnif, 1.0)
    GL.glUniform1f(zNearUnif, 0.5)
    GL.glUniform1f(zFarUnif, 3.0)
    GL.glUseProgram(0);
    
def initialize_vertex_buffer():
    global vertexBufferObject
    vertexBufferObject = GL.glGenBuffers(1)
    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, vertexBufferObject)
    GL.glBufferData(
        GL.GL_ARRAY_BUFFER, len(vertexData) * sizeOfFloat,
        vertexData, GL.GL_STATIC_DRAW
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

    GL.glEnable(GL.GL_CULL_FACE)
    GL.glCullFace(GL.GL_BACK)
    GL.glFrontFace(GL.GL_CW)


# Called to redraw the contents of the window
def display():
    global offsetUniform, theProgram

    GL.glClearColor(0.0, 0.0, 0.0, 0.0)
    GL.glClear(GL.GL_COLOR_BUFFER_BIT)

    GL.glUseProgram(theProgram)

    GL.glUniform2f(offsetUniform, 0.5, 0.5)

    colorData = sizeOfFloat*len(vertexData)/2
    
    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, vertexBufferObject)   
    positionLocation = GL.glGetAttribLocation(theProgram, 'position')
    colorLocation = GL.glGetAttribLocation(theProgram, 'color')
    GL.glEnableVertexAttribArray(positionLocation)
    GL.glVertexAttribPointer(positionLocation,
                             4,
                             GL.GL_FLOAT, False, 0, null)
    GL.glEnableVertexAttribArray(colorLocation)
    GL.glVertexAttribPointer(colorLocation,
                             4,
                             GL.GL_FLOAT, False, 0, c_void_p(colorData))

    GL.glDrawArrays(GL.GL_TRIANGLES, 0, 36)

    GL.glDisableVertexAttribArray(positionLocation)
    GL.glDisableVertexAttribArray(colorLocation)
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
    screen = pygame.display.set_mode((512,512), OPENGL|DOUBLEBUF)
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




from ctypes import c_void_p

from OpenGL.GL import *
from OpenGL.GL.ARB.vertex_array_object import *
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
sizeOfShort = 2

vertexData = N.array([
        #points
	 0.25,  0.25,  0.75, 1.0,
	 0.25,  0.25, -0.75, 1.0,
	 0.25, -0.25,  0.75, 1.0,
	 0.25, -0.25, -0.75, 1.0,
	-0.25,  0.25,  0.75, 1.0,
	-0.25,  0.25, -0.75, 1.0,
	-0.25, -0.25,  0.75, 1.0,
	-0.25, -0.25, -0.75, 1.0,
        #colors
	0.0, 0.0, 1.0, 1.0,
	0.8, 0.8, 0.8, 1.0,
	0.0, 1.0, 0.0, 1.0,
	0.5, 0.5, 0.0, 1.0,
	1.0, 0.0, 0.0, 1.0,
	0.0, 1.0, 1.0, 1.0
        ],dtype = N.float32)
numberOfVertices = 8
vertexComponents = 4

indexData = N.array([
    # points
    0,2,4,2,6,4,
    1,5,3,3,5,7,
    4,6,7,4,7,5,
    0,3,2,0,1,3,
    1,0,4,1,4,5,
    3,6,2,3,7,6,
    # colors
    0,0,0,0,0,0,
    1,1,1,1,1,1,
    2,2,2,2,2,2,
    3,3,3,3,3,3,
    4,4,4,4,4,4,
    5,5,5,5,5,5
    ],dtype=N.uint16)


def loadFile(filename):
    with open(filename) as fp:
        return fp.read()
strVertexShader = loadFile('MatrixPerspective.vert')
strFragmentShader = loadFile('StandardColors.frag')

# Integer handle identifying our compiled shader program
theProgram = None

# Integer handle identifying the GPU memory storing our vertex position array
offsetUniform = None

perspectiveMatrixUnif = None

def projectionMatrix(n,f,r,t):
    m = N.zeros((4,4),dtype=N.float32)
    m[0,0] = n/float(r)
    m[1,1] = n/float(t)
    m[2,2] = -(f+n)/float(f-n)
    m[2,3] = -2*f*n/float(f-n)
    m[3,2] = -1.0
    return m

def initialize_program():
    global offsetUniform, perspectiveMatrixUnif, SCREENSIZE
    """
    Instead of calling OpenGL's shader compilation functions directly
    (glShaderSource, glCompileShader, etc), we use PyOpenGL's wrapper
    functions, which are much simpler to use.
    """
    global theProgram
    theProgram = compileProgram(
        compileShader(strVertexShader, GL_VERTEX_SHADER),
        compileShader(strFragmentShader, GL_FRAGMENT_SHADER)
    )
    offsetUniform = glGetUniformLocation(theProgram, 'offset')
    perspectiveMatrixUnif = glGetUniformLocation(theProgram, 'perspectiveMatrix')
    fFrustumScale = 1.0
    fzNear = 0.5
    fzFar = 3.0

    w,h = SCREENSIZE
    theMatrix = N.zeros(16, dtype=N.float32)
    theMatrix[0] = fFrustumScale*float(h)/float(w)
    theMatrix[5] = fFrustumScale
    theMatrix[10] = (fzFar + fzNear) / (fzNear - fzFar)
    theMatrix[14] = (2 * fzFar * fzNear) / (fzNear - fzFar)
    theMatrix[11] = -1.0

    theMatrix = projectionMatrix(fzNear, fzFar,
                                 fzNear*w/float(h), fzNear)

    glUseProgram(theProgram)
    glUniformMatrix4fv(perspectiveMatrixUnif, 1, True, theMatrix)
    glUseProgram(0);

vertexBufferObject = None
indexBufferObject = None

def initialize_vertex_buffer():
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

# Called once at application start-up.
# Must be called after we have an OpenGL context, i.e. after the pyglet
# window is created
def init():
    initialize_program()
    initialize_vertex_buffer()
    
    n = 1
    vao_array = arrays.GLuintArray.zeros((n,))
    glBindVertexArray( vao_array )

    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)
    glFrontFace(GL_CW)


# Called to redraw the contents of the window
def display():
    global offsetUniform, vertexBufferObject, indexBufferObject

    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClear(GL_COLOR_BUFFER_BIT)

    glUseProgram(theProgram)
    
    glUniform2f(offsetUniform, 0.5, 0.5)

    colorData = sizeOfFloat*numberOfVertices
    
    glBindBuffer(GL_ARRAY_BUFFER, vertexBufferObject)   
    positionLocation = glGetAttribLocation(theProgram, 'position')
    colorLocation = glGetAttribLocation(theProgram, 'color')
    glEnableVertexAttribArray(positionLocation)
    glVertexAttribPointer(positionLocation,
                             4,
                             GL_FLOAT, False, 0, null)
    glEnableVertexAttribArray(colorLocation)
    glVertexAttribPointer(colorLocation,
                             4,
                             GL_FLOAT, False, 0, c_void_p(colorData))
    
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, indexBufferObject)

    glDrawElements(GL_TRIANGLES, len(indexData)/2,
                   GL_UNSIGNED_SHORT, c_void_p(0))

    glDisableVertexAttribArray(positionLocation)
    glDisableVertexAttribArray(colorLocation)
    glUseProgram(0)

    # equivalent of glutSwapBuffers and glutPostRedisplay is done for us by
    # pygame


# Called when the window is resized, including once at application start-up
def reshape(width, height):
    glViewport(0, 0, width, height)

screen = None
SCREENSIZE1 = (512,512)
SCREENSIZE2 = (1024,512)
SCREENSIZE = SCREENSIZE1

def main():
    global screen,clock,SCREENSIZE
    pygame.init()
    screen = pygame.display.set_mode(SCREENSIZE, OPENGL|DOUBLEBUF)
    pygame.display.set_caption("Press S to change window size.")
    clock = pygame.time.Clock()
    init()
    while True:     
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            if event.type == KEYUP and event.key == K_ESCAPE:
                return
            if event.type == KEYDOWN and event.key==K_s:
                if SCREENSIZE == SCREENSIZE1:
                    SCREENSIZE = SCREENSIZE2
                else:
                    SCREENSIZE = SCREENSIZE1
                screen = pygame.display.set_mode(SCREENSIZE, OPENGL|DOUBLEBUF)
                init()
                
                
        display()
        pygame.display.flip()


if __name__ == '__main__':
    try:
        main()
    finally:
        pygame.quit()


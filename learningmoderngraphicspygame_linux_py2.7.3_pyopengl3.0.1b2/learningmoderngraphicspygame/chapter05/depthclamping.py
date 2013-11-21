

from ctypes import c_void_p

from OpenGL.GL import *
from OpenGL.GL.ARB.vertex_array_object import *
from OpenGL.GL.ARB.draw_elements_base_vertex import *
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

numberOfVertices = 36;

RIGHT_EXTENT = 0.8
LEFT_EXTENT = -RIGHT_EXTENT
TOP_EXTENT = 0.20
MIDDLE_EXTENT = 0.0
BOTTOM_EXTENT = -TOP_EXTENT
FRONT_EXTENT = -1.25
REAR_EXTENT = -1.75

GREEN_COLOR = [0.75, 0.75, 1.0, 1.0]
BLUE_COLOR = [	0.0, 0.5, 0.0, 1.0]
RED_COLOR = [1.0, 0.0, 0.0, 1.0]
GREY_COLOR = [0.8, 0.8, 0.8, 1.0]
BROWN_COLOR = [0.5, 0.5, 0.0, 1.0]

vertexData = [
	#//Object 1 positions
	LEFT_EXTENT,	TOP_EXTENT,		REAR_EXTENT,
	LEFT_EXTENT,	MIDDLE_EXTENT,	FRONT_EXTENT,
	RIGHT_EXTENT,	MIDDLE_EXTENT,	FRONT_EXTENT,
	RIGHT_EXTENT,	TOP_EXTENT,		REAR_EXTENT,

	LEFT_EXTENT,	BOTTOM_EXTENT,	REAR_EXTENT,
	LEFT_EXTENT,	MIDDLE_EXTENT,	FRONT_EXTENT,
	RIGHT_EXTENT,	MIDDLE_EXTENT,	FRONT_EXTENT,
	RIGHT_EXTENT,	BOTTOM_EXTENT,	REAR_EXTENT,

	LEFT_EXTENT,	TOP_EXTENT,		REAR_EXTENT,
	LEFT_EXTENT,	MIDDLE_EXTENT,	FRONT_EXTENT,
	LEFT_EXTENT,	BOTTOM_EXTENT,	REAR_EXTENT,

	RIGHT_EXTENT,	TOP_EXTENT,		REAR_EXTENT,
	RIGHT_EXTENT,	MIDDLE_EXTENT,	FRONT_EXTENT,
	RIGHT_EXTENT,	BOTTOM_EXTENT,	REAR_EXTENT,

	LEFT_EXTENT,	BOTTOM_EXTENT,	REAR_EXTENT,
	LEFT_EXTENT,	TOP_EXTENT,		REAR_EXTENT,
	RIGHT_EXTENT,	TOP_EXTENT,		REAR_EXTENT,
	RIGHT_EXTENT,	BOTTOM_EXTENT,	REAR_EXTENT,

	#//Object 2 positions
	TOP_EXTENT,		RIGHT_EXTENT,	REAR_EXTENT,
	MIDDLE_EXTENT,	RIGHT_EXTENT,	FRONT_EXTENT,
	MIDDLE_EXTENT,	LEFT_EXTENT,	FRONT_EXTENT,
	TOP_EXTENT,		LEFT_EXTENT,	REAR_EXTENT,

	BOTTOM_EXTENT,	RIGHT_EXTENT,	REAR_EXTENT,
	MIDDLE_EXTENT,	RIGHT_EXTENT,	FRONT_EXTENT,
	MIDDLE_EXTENT,	LEFT_EXTENT,	FRONT_EXTENT,
	BOTTOM_EXTENT,	LEFT_EXTENT,	REAR_EXTENT,

	TOP_EXTENT,		RIGHT_EXTENT,	REAR_EXTENT,
	MIDDLE_EXTENT,	RIGHT_EXTENT,	FRONT_EXTENT,
	BOTTOM_EXTENT,	RIGHT_EXTENT,	REAR_EXTENT,
					
	TOP_EXTENT,		LEFT_EXTENT,	REAR_EXTENT,
	MIDDLE_EXTENT,	LEFT_EXTENT,	FRONT_EXTENT,
	BOTTOM_EXTENT,	LEFT_EXTENT,	REAR_EXTENT,
					
	BOTTOM_EXTENT,	RIGHT_EXTENT,	REAR_EXTENT,
	TOP_EXTENT,		RIGHT_EXTENT,	REAR_EXTENT,
	TOP_EXTENT,		LEFT_EXTENT,	REAR_EXTENT,
	BOTTOM_EXTENT,	LEFT_EXTENT,	REAR_EXTENT]

#//Object 1 colors
vertexData += 4*GREEN_COLOR + 4*BLUE_COLOR + 3*RED_COLOR + 3*GREY_COLOR + 4*BROWN_COLOR

#//Object 2 colors
vertexData += 4*RED_COLOR + 4*BROWN_COLOR + 3*BLUE_COLOR + 3*GREEN_COLOR + 4*GREY_COLOR

vertexData = N.array(vertexData, dtype=N.float32)

indexData = N.array((

	0, 2, 1,
	3, 2, 0,

	4, 5, 6,
	6, 7, 4,

	8, 9, 10,
	11, 13, 12,

	14, 16, 15,
	17, 16, 14), dtype=N.uint16)


vertexComponents = 4
theProgram = None

def loadFile(filename):
    with open(filename) as fp:
        return fp.read()
strVertexShader = loadFile('Standard.vert')
strFragmentShader = loadFile('Standard.frag')

# Integer handle identifying our compiled shader program
theProgram = None

# Integer handle identifying the GPU memory storing our vertex position array
offsetUniform = None

perspectiveMatrixUnif = None
perspectiveMatrix = None
fFrustumScale = 1.0


def projectionMatrix(n,f,r,t):
    m = N.zeros((4,4),dtype=N.float32)
    m[0,0] = n/float(r)
    m[1,1] = n/float(t)
    m[2,2] = -(f+n)/float(f-n)
    m[2,3] = -2*f*n/float(f-n)
    m[3,2] = -1.0
    return m

def InitializeProgram():
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

    fzNear = 1.0
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
        

vao = None

# Called once at application start-up.
# Must be called after we have an OpenGL context, i.e. after the pyglet
# window is created
def init():
    global vao
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
    global offsetUniform, vao

    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClearDepth(1.0)
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

    glUseProgram(theProgram)

    glBindVertexArray(vao)
    glUniform3f(offsetUniform, 0.0, 0.0, 0.5)
    glDrawElements(GL_TRIANGLES, len(indexData)*sizeOfShort,
                      GL_UNSIGNED_SHORT, c_void_p(0))

    glUniform3f(offsetUniform, 0.0, 0.0, -1.0)
    glDrawElementsBaseVertex(GL_TRIANGLES, len(indexData)*sizeOfShort,
                      GL_UNSIGNED_SHORT, c_void_p(0), numberOfVertices/2)
    
    glBindVertexArray(0)
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
    bDepthClampingActive = False
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
            if event.type == KEYDOWN and event.key == K_SPACE:
                if bDepthClampingActive:
                    glDisable(GL_DEPTH_CLAMP)
                else:
                    glEnable(GL_DEPTH_CLAMP)
                bDepthClampingActive = not bDepthClampingActive
                
                
        display()
        pygame.display.flip()


if __name__ == '__main__':
    try:
        main()
    finally:
        pygame.quit()


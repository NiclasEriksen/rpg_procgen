import pyglet
from pyglet.gl import *
from gletools import ShaderProgram, FragmentShader, VertexShader

window = pyglet.window.Window()

positionBufferObject = GLuint()

vertexPositions = [0.75, 0.75, 0.0, 1.0,
                   0.75, -0.75, 0.0, 1.0,
                   -0.75, -0.75, 0.0, 1.0]
vertexPositionsGl = (GLfloat * len(vertexPositions))(*vertexPositions)

program = ShaderProgram(
    FragmentShader('''
    #version 330
    out vec4 outputColor;
    void main()
    {
       outputColor = vec4(1.0f, 1.0f, 1.0f, 1.0f);
    }'''),
    VertexShader('''
    #version 330
    layout(location = 0) in vec4 position;
    void main()
    {
        gl_Position = position;
    }''')
)

@window.event
def on_draw():
    with program:
        glBindBuffer(GL_ARRAY_BUFFER, positionBufferObject)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 4, GL_FLOAT, GL_FALSE, 0, 0)
        glDrawArrays(GL_TRIANGLES, 0, 3)
        glDisableVertexAttribArray(0)

glGenBuffers(1, positionBufferObject)
glBindBuffer(GL_ARRAY_BUFFER, positionBufferObject)
glBufferData(GL_ARRAY_BUFFER, len(vertexPositionsGl)*4, vertexPositionsGl, GL_STATIC_DRAW)
glBindBuffer(GL_ARRAY_BUFFER, 0)

pyglet.app.run()
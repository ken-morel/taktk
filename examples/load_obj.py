import tkinter
from tkinter_gl import GLCanvas
import pywavefront
try:
    from OpenGL import GL
except ImportError:
    raise ImportError(
        """
        This example requires PyOpenGL.

        You can install it with "pip install PyOpenGL".
        """)

"""
Shows a square that can be moved with the cursor keys and whose size
can be controlled by a slider.

Shows how to do "animation", that is repeatedly calling draw using the
elapsed time to compute how far the square has moved. Also tests that
we correctly update the GLCanvas to slider events.
"""


class ObjView(GLCanvas):
    profile = 'legacy'

    def __init__(self, parent):
        super().__init__(parent, width=500, height=500)

        self.size = 0.5

        # Position of square.
        self.x = 0.0
        self.y = 0.0
        self.scene = pywavefront.Wavefront('noseman.obj', collect_faces=True)


    def draw(self):
        self.make_current()

        GL.glViewport(0, 0, self.winfo_width(), self.winfo_height())
        GL.glClearColor(0, 0, 0, 1)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        GL.glRotatef(5, 1, 1, 1)

        GL.glBegin(GL.GL_TRIANGLES)
        for face in self.scene.meshes['Quad_Sphere'].faces:
            for vertex in face:
                vertex = self.scene.vertices[vertex]
                x, y, z = vertex
                GL.glVertex3f(z / 5, y / 5, z / 5)
        print("showing your model...")
        GL.glEnd()
        # GL.glTranslate(0, 0, 0.1)

        while True:
            err = GL.glGetError()
            if err == GL.GL_NO_ERROR:
                break
            print("Error: ", err)

        self.swap_buffers()



if __name__ == '__main__':

    root = tkinter.Tk()
    view = ObjView(root)
    view.pack()


    root.columnconfigure(1, weight=1)

    print("Using OpenGL", view.gl_version())

    def update():
        view.draw()
        root.after(1, update)

    root.after(1, update)
    root.mainloop()


"""
Modern OpenGL Renderer for the Pop-Art AR Application.
Handles GLFW window lifecycle, shader compilation, camera texture uploading,
and drawing the 2D pop-art quadrilateral panel and background quad.
"""
import logging
import os
import numpy as np
import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

logger = logging.getLogger("Renderer")


def read_shader_source(filepath: str) -> str:
    with open(filepath, 'r') as f:
        return f.read()


class OpenGLRenderer:
    """Manages the GLFW context, texture uploads, shaders, and rendering pipeline."""

    def __init__(self, width: int = 1280, height: int = 720, title: str = "AR Hand Panel - Pop-Art"):
        self.width = width
        self.height = height
        self.title = title
        self.window = None
        
        # Shader programs
        self.bg_program = None
        self.panel_program = None
        
        # Texture handle
        self.camera_tex_id = 0
        
        # VAOs and VBOs
        self.bg_vao = 0
        self.bg_vbo = 0
        
        self.panel_vao = 0
        self.panel_vbo = 0
        
        self.border_vao = 0
        self.border_vbo = 0

    def initialize(self) -> bool:
        """Initialize GLFW, create window, and set up OpenGL state."""
        if not glfw.init():
            logger.error("Failed to initialize GLFW!")
            return False

        # Request core profile OpenGL 3.3
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL_TRUE)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

        self.window = glfw.create_window(self.width, self.height, self.title, None, None)
        if not self.window:
            logger.error("Failed to create GLFW window!")
            glfw.terminate()
            return False

        glfw.maximize_window(self.window) # Maximize to fill the screen
        glfw.make_context_current(self.window)
        glfw.swap_interval(1)  # Enable V-Sync

        # Set up viewport based on actual size
        fb_w, fb_h = glfw.get_framebuffer_size(self.window)
        glViewport(0, 0, fb_w, fb_h)

        # Set up shaders
        try:
            self._compile_shaders()
        except Exception as e:
            logger.error(f"Shader compilation failed: {e}")
            return False

        # Create buffers
        self._setup_buffers()
        
        # Create camera texture
        self._setup_texture()

        # OpenGL global states
        glEnable(GL_MULTISAMPLE)  # Anti-aliasing

        logger.info("OpenGL initialization completed successfully.")
        return True

    def _compile_shaders(self):
        """Compile vert and frag shaders."""
        shader_dir = os.path.join(os.path.dirname(__file__), "shaders")
        
        # Compile background shader
        bg_vert_src = read_shader_source(os.path.join(shader_dir, "background.vert"))
        bg_frag_src = read_shader_source(os.path.join(shader_dir, "background.frag"))
        
        self.bg_program = compileProgram(
            compileShader(bg_vert_src, GL_VERTEX_SHADER),
            compileShader(bg_frag_src, GL_FRAGMENT_SHADER)
        )
        
        # Compile panel shader
        panel_vert_src = read_shader_source(os.path.join(shader_dir, "panel.vert"))
        panel_frag_src = read_shader_source(os.path.join(shader_dir, "panel.frag"))
        
        self.panel_program = compileProgram(
            compileShader(panel_vert_src, GL_VERTEX_SHADER),
            compileShader(panel_frag_src, GL_FRAGMENT_SHADER)
        )

    def _setup_buffers(self):
        """Allocate VBOs and VAOs for background quad, panel quad, and borders."""
        # --- Background Quad Setup ---
        # 4 vertices: positions (2D) and texture coords (2D)
        # We invert Y mapping so OpenCV image reads top-down
        bg_data = np.array([
            -1.0,  1.0,   0.0, 0.0,
            -1.0, -1.0,   0.0, 1.0,
             1.0, -1.0,   1.0, 1.0,
             1.0,  1.0,   1.0, 0.0
        ], dtype=np.float32)

        self.bg_vao = glGenVertexArrays(1)
        self.bg_vbo = glGenBuffers(1)

        glBindVertexArray(self.bg_vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.bg_vbo)
        glBufferData(GL_ARRAY_BUFFER, bg_data.nbytes, bg_data, GL_STATIC_DRAW)

        # Positions (location = 0)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 4 * 4, ctypes.c_void_p(0))
        # TexCoords (location = 1)
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 4 * 4, ctypes.c_void_p(2 * 4))
        glBindVertexArray(0)

        # --- Panel Quad Setup (separate VAO) ---
        self.panel_vao = glGenVertexArrays(1)
        self.panel_vbo = glGenBuffers(1)

        glBindVertexArray(self.panel_vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.panel_vbo)
        # 6 vertices, each having 5 floats (X, Y, Z, U, V)
        glBufferData(GL_ARRAY_BUFFER, 6 * 5 * 4, None, GL_DYNAMIC_DRAW)

        # Positions (location = 0)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 5 * 4, ctypes.c_void_p(0))
        # TexCoords (location = 1)
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 5 * 4, ctypes.c_void_p(3 * 4))
        glBindVertexArray(0)

        # --- Border Lines Setup (separate VAO, position only) ---
        self.border_vao = glGenVertexArrays(1)
        self.border_vbo = glGenBuffers(1)

        glBindVertexArray(self.border_vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.border_vbo)
        # 8 vertices (4 line segments), each having 3 floats (X, Y, Z)
        glBufferData(GL_ARRAY_BUFFER, 8 * 3 * 4, None, GL_DYNAMIC_DRAW)

        # Positions only (location = 0)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * 4, ctypes.c_void_p(0))
        # TexCoords NOT enabled for border VAO
        glBindVertexArray(0)

    def _setup_texture(self):
        """Generate texture ID for webcam frame upload."""
        self.camera_tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.camera_tex_id)
        
        # Texture parameters
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        
        glBindTexture(GL_TEXTURE_2D, 0)

    def upload_camera_frame(self, frame_bgr: np.ndarray):
        """Upload an OpenCV frame as a 2D OpenGL texture."""
        h, w = frame_bgr.shape[:2]
        
        # In OpenCV, pixels are in BGR format
        glBindTexture(GL_TEXTURE_2D, self.camera_tex_id)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, w, h, 0, GL_BGR, GL_UNSIGNED_BYTE, frame_bgr)
        glBindTexture(GL_TEXTURE_2D, 0)

    def render(self, frame_bgr: np.ndarray, panels: list, time_sec: float):
        """Perform the actual rendering pipeline."""
        # Query current window size to support dynamic resizing
        fb_w, fb_h = glfw.get_framebuffer_size(self.window)
        glViewport(0, 0, fb_w, fb_h)

        # 1. Clear screen
        glClearColor(0.05, 0.05, 0.08, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # 2. Upload frame texture to GPU
        self.upload_camera_frame(frame_bgr)

        # 3. Draw Background Quad (no depth test — always behind everything)
        glDisable(GL_DEPTH_TEST)
        glUseProgram(self.bg_program)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.camera_tex_id)
        glUniform1i(glGetUniformLocation(self.bg_program, "u_camera_texture"), 0)

        glBindVertexArray(self.bg_vao)
        glDrawArrays(GL_TRIANGLE_FAN, 0, 4)
        glBindVertexArray(0)

        # 4. Draw Pop-Art Panels (no depth test needed for 2D overlay)
        if panels:
            glUseProgram(self.panel_program)

            # Bind camera texture
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, self.camera_tex_id)
            glUniform1i(glGetUniformLocation(self.panel_program, "u_camera_texture"), 0)
            glUniform1f(glGetUniformLocation(self.panel_program, "u_time"), time_sec)
            glUniform2f(glGetUniformLocation(self.panel_program, "u_resolution"), float(fb_w), float(fb_h))

            for panel in panels:
                p_verts = panel.get("vertices")
                p_borders = panel.get("borders")
                p_mode = panel.get("mode", 0)

                p_glitch_factor = panel.get("glitch_factor", 0.0)

                if p_verts is not None:
                    glUniform1i(glGetUniformLocation(self.panel_program, "u_effect_mode"), p_mode)
                    glUniform1f(glGetUniformLocation(self.panel_program, "u_glitch_factor"), float(p_glitch_factor))

                    # --- Draw Panel Fill ---
                    glUniform1i(glGetUniformLocation(self.panel_program, "u_draw_border"), 0)
                    glBindVertexArray(self.panel_vao)
                    glBindBuffer(GL_ARRAY_BUFFER, self.panel_vbo)
                    glBufferSubData(GL_ARRAY_BUFFER, 0, p_verts.nbytes, p_verts)
                    glDrawArrays(GL_TRIANGLES, 0, 6)
                    glBindVertexArray(0)

                    # --- Draw Borders ---
                    if p_borders is not None:
                        glUniform1i(glGetUniformLocation(self.panel_program, "u_draw_border"), 1)
                        try:
                            glLineWidth(3.0)
                        except Exception:
                            pass
                        glBindVertexArray(self.border_vao)
                        glBindBuffer(GL_ARRAY_BUFFER, self.border_vbo)
                        glBufferSubData(GL_ARRAY_BUFFER, 0, p_borders.nbytes, p_borders)
                        glDrawArrays(GL_LINES, 0, len(p_borders) // 3)
                        glBindVertexArray(0)

        glUseProgram(0)

    def cleanup(self):
        """Release OpenGL and GLFW resources."""
        for vbo in [self.bg_vbo, self.panel_vbo, self.border_vbo]:
            if vbo:
                glDeleteBuffers(1, [vbo])
        for vao in [self.bg_vao, self.panel_vao, self.border_vao]:
            if vao:
                glDeleteVertexArrays(1, [vao])
        if self.camera_tex_id:
            glDeleteTextures(1, [self.camera_tex_id])
        if self.bg_program:
            glDeleteProgram(self.bg_program)
        if self.panel_program:
            glDeleteProgram(self.panel_program)

        glfw.terminate()
        logger.info("OpenGL resources cleaned up.")

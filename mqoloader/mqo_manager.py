from OpenGL.GL import *

class MQOManager:
    def __init__(self, max_textures):
        textures = (GLuint * (max_textures + 1)) ()        
        glGenTextures (max_textures, textures)
        self.texture_count = 0

    def generateTextureID(self):
        self.texture_count = self.texture_count + 1
        return self.texture_count

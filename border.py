
import numpy as np
import pygame
import math

from fpvector import FPDecPoint3
from fpvector import FPDecVec3
from fpmatrix import FPDecMtx44
from fpquaternion import FPQuaternion

# Eight corners of the border as points
_verts = [FPDecPoint3( 11, -9, -1),
          FPDecPoint3( 11,  9, -1),
          FPDecPoint3(-11,  9, -1),
          FPDecPoint3(-11, -9, -1),
          FPDecPoint3( 11, -9, 21),
          FPDecPoint3( 11,  9, 21),
          FPDecPoint3(-11, -9, 21),
          FPDecPoint3(-11,  9, 21)]
# Six sides of the border as indexes into the list of _verts
_surfaces = [(0,1,2,3),
             (3,2,7,6),
             (6,7,5,4),
             (4,5,1,0),
             (1,5,7,2),
             (4,0,3,6)]

class Border:
    def __init__(self):
        pass

    def ProcessEvent(self, event):
        return False

    def GetZPos(self):
        return _verts[0][2]

    def Update(self, deltaTime):
        pass

    def BGRender(self, perspective, modelview, camVec, screen):
        global _verts
        global _surfaces
        global _colors

        m = perspective * modelview

        for i in range(1, len(_surfaces)):
            # Apply the new position to each vertex of this face of the cube
            fppoints = []
            for vert in _surfaces[i]:
                v = _verts[vert] * m
                fppoints.append(v)

            # Draw this face of the cube (to do that we first convert our fixed-point numbers to regular integers which pygame.draw requires)
            points = []
            for j in range(len(fppoints)):
                points.append([int(fppoints[j][d]) for d in range(2)])
            pygame.draw.lines(screen, (255, 255, 255), True, points)

    def Render(self, perspective, modelview, camVec, screen):
        global _verts
        global _surfaces

        m = perspective * modelview

        for i in range(1):
            # Apply the new position to each vertex of this face of the cube
            fppoints = []
            for vert in _surfaces[i]:
                v = _verts[vert] * m
                fppoints.append(v)

            # Draw this face of the cube (to do that we first convert our fixed-point numbers to regular integers which pygame.draw requires)
            points = []
            for j in range(len(fppoints)):
                points.append([int(fppoints[j][d]) for d in range(2)])
            pygame.draw.lines(screen, (255, 255, 255), True, points)

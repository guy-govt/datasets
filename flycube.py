
import numpy as np
import pygame
import math

from fpdecimal import FPDecimal
from fpvector import FPDecPoint3
from fpvector import FPDecVec3
from fpmatrix import FPDecMtx44
from fpquaternion import FPQuaternion

# Eight corners of the cube as points
_verts = [FPDecPoint3( 1, -1, -1),
          FPDecPoint3( 1,  1, -1),
          FPDecPoint3(-1,  1, -1),
          FPDecPoint3(-1, -1, -1),
          FPDecPoint3( 1, -1,  1),
          FPDecPoint3( 1,  1,  1),
          FPDecPoint3(-1, -1,  1),
          FPDecPoint3(-1,  1,  1)]
# Six sides of the cube as indexes into the list of _verts
_surfaces = [(0,1,2,3),
             (3,2,7,6),
             (6,7,5,4),
             (4,5,1,0),
             (1,5,7,2),
             (4,0,3,6)]
# A different color for each side of the cube
_colors = [(  0,   0, 255),
           (255,   0,   0),
           (  0, 255,   0),
           (  0, 255, 255),
           (255, 255,   0),
           (255,   0, 255)]

_speed = 10.0

class Cube:
    def __init__(self):
        self.mtx = FPDecMtx44()
        self.aply = FPDecMtx44.GetRotateMtx(3.14/-1.25, [3.0,1.0,1.0])
        self.trns = FPDecMtx44()

        self.moveX = 0
        self.moveY = 0
        self.moveZ = 0

        self.minX = FPDecimal(-10)
        self.maxX = FPDecimal(10)
        self.minY = FPDecimal(-8)
        self.maxY = FPDecimal(8)
        self.minZ = FPDecimal(0)
        self.maxZ = FPDecimal(20)

    def ProcessEvent(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w: # Move Away
                self.moveZ += 1
                return True
            if event.key == pygame.K_s: # Move Near
                self.moveZ -= 1
                return True
            if event.key == pygame.K_UP:
                self.moveY += 1
                return True
            if event.key == pygame.K_DOWN:
                self.moveY -= 1
                return True
            if event.key == pygame.K_LEFT:
                self.moveX -= 1
                return True
            if event.key == pygame.K_RIGHT:
                self.moveX += 1
                return True
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_w: # Move Away
                self.moveZ -= 1
                return True
            if event.key == pygame.K_s: # Move Near
                self.moveZ += 1
                return True
            if event.key == pygame.K_UP:
                self.moveY -= 1
                return True
            if event.key == pygame.K_DOWN:
                self.moveY += 1
                return True
            if event.key == pygame.K_LEFT:
                self.moveX += 1
                return True
            if event.key == pygame.K_RIGHT:
                self.moveX -= 1
                return True
        return False

    def GetZPos(self):
        return self.trns[2][3]

    def GetPos(self):
        return FPDecPoint3(self.trns[0][3], self.trns[1][3], self.trns[2][3])

    def Update(self, deltaTime):
        global _speed

        x = FPDecimal(self.moveX * deltaTime * _speed)
        dx = self.trns[0][3] + x
        if dx > self.maxX: x -= dx - self.maxX
        if dx < self.minX: x += self.minX - dx
        self.trns[0][3] += x
        
        y = FPDecimal(self.moveY * deltaTime * _speed)
        dy = self.trns[1][3] + y
        if dy > self.maxY: y -= dy - self.maxY
        if dy < self.minY: y += self.minY - dy
        self.trns[1][3] += y

        z = FPDecimal(self.moveZ * deltaTime * _speed)
        dz = self.trns[2][3] + z
        if dz > self.maxZ: z -= dz - self.maxZ
        if dz < self.minZ: z += self.minZ - dz
        self.trns[2][3] += z

        self.mtx = self.trns * self.aply

    def Render(self, perspective, modelview, camVec, screen):
        global _verts
        global _surfaces
        global _colors

        m = perspective * modelview * self.mtx

        for i in range(len(_surfaces)):
            # Apply the new position to each vertex of this face of the cube
            fppoints = []
            for vert in _surfaces[i]:
                v = _verts[vert] * m
                fppoints.append(v)

            # Cull backfaces
            v1 = fppoints[1] - fppoints[0]
            v2 = fppoints[2] - fppoints[1]
            vc = FPDecVec3.Cross(v1, v2)
            if FPDecVec3.Dot(vc, camVec) <= 0:
                continue

            # Draw this face of the cube (to do that we first convert our fixed-point numbers to regular integers which pygame.draw requires)
            points = []
            for j in range(len(fppoints)):
                points.append([int(fppoints[j][d]) for d in range(2)])
            pygame.draw.polygon(screen, _colors[i], points)

import numpy as np
import pygame
import math

from fpdecimal import FPDecimal
from fpvector import FPDecPoint3
from fpvector import FPDecVec3
from fpmatrix import FPDecMtx44
from fpquaternion import FPQuaternion

# Eight corners of the rocket as points
_verts = [FPDecPoint3(     0,    0, -1),
          FPDecPoint3(     0,    1,  1),
          FPDecPoint3(-0.866, -0.5,  1),
          FPDecPoint3( 0.866, -0.5,  1)]
# Six sides of the rocket as indexes into the list of _verts
_surfaces = [(0,1,2),
             (0,2,3),
             (0,3,1),
             (1,3,2)]
# A different color for each side of the rocket
_colors = [(255, 128, 128),
           (255, 255,   0),
           (255,   0, 255),
           (255,   0,   0)]

_speed = 10.0
_turnSpeed = 2.0

class Rocket:
    def __init__(self):
        self.mtx = FPDecMtx44()
        self.aply = FPDecMtx44()

        self.minX = FPDecimal(-20)
        self.maxX = FPDecimal(20)
        self.minY = FPDecimal(-18)
        self.maxY = FPDecimal(18)
        self.minZ = FPDecimal(-10)
        self.maxZ = FPDecimal(30)

        self.Reset()

    def ProcessEvent(self, event):
        return False

    def GetZPos(self):
        return self.trns[2][3]

    def SetTarget(self, pos):
        self.target = pos

    def Reset(self):
        self.trns = FPDecMtx44.GetTranslateMtx(-10, -8, 20)
        self.move = FPDecVec3(0, 0, -1)

    def Update(self, deltaTime):
        global _speed
        global _turnSpeed

        maxRadiansToTurn = deltaTime * _turnSpeed

        # Assignment #3
        # The goal is to make the rocket chase the cube
        #   Modify only the code in this section to do so
        # Review what you have learned about vectors (especially dot and cross), and quaternions and use them to solve this problem
        #   You can also use a (rotation) matrix to do this if you want instead of a quaternion
        # The rocket MUST NOT turn to the direction of the target instantly, but only gradually
        # You MUST use the variable maxRadiansToTurn (shown above) to set the turn speed of the rocket
        #   I.e. make maxRadiansToTurn the value you use for how much to turn each frame
        # You must only rotate the rocket by rotating the self.move vector which represents the direction the rocket is facing
        # When running the code you can use the arrow keys and "w" and "s" to move the cube around to see how the rocket chases it
        # You may not import any module except the ones imported above
        # You may not use any code copied from the internet (write your own code so you become a better programmer)
        # You may not modify any code outside of this section
        
        # BEGIN section
        
        # Find direction vector to the target
        # Find direction vector to the target
        # rocket_position = FPDecPoint3(self.trns[0][3], self.trns[1][3], self.trns[2][3])
        # direction_to_target = self.target - rocket_position
        # direction_to_target.Normalize()

        # Get vector that is perpendicular to target vector and direction vector
        # rotation_axis = FPDecVec3.Cross(self.move, direction_to_target)

        # Rotate around the resulting vector to aim more towards the target
        # rotation_quaternion = FPQuaternion(maxRadiansToTurn, rotation_axis)

        # Apply the rotation to the direction vector
        #self.move = ?
        # Rotate around the resulting vector to aim more towards the target
        # rotation_quaternion = FPQuaternion(maxRadiansToTurn, rotation_axis, _normalized=True)
        # self.move = rotation_quaternion * self.move

        
        # END section

        if self.move.IsZero(): self.Reset()
        self.move.Normalize()

        self.trns[0][3] += self.move[0] * (deltaTime * _speed)
        self.trns[1][3] += self.move[1] * (deltaTime * _speed)
        self.trns[2][3] += self.move[2] * (deltaTime * _speed)

        if self.trns[0][3] > self.maxX: self.Reset()
        elif self.trns[0][3] < self.minX: self.Reset()
        elif self.trns[1][3] > self.maxY: self.Reset()
        elif self.trns[1][3] < self.minY: self.Reset()
        elif self.trns[2][3] > self.maxZ: self.Reset()
        elif self.trns[2][3] < self.minZ: self.Reset()

        q = FPQuaternion(self.move, FPDecVec3(0, 0, -1))

        self.mtx = self.trns * q.GetMatrix() * self.aply

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

            # Draw this face of the rocket (to do that we first convert our fixed-point numbers to regular integers which pygame.draw requires)
            points = []
            for j in range(len(fppoints)):
                points.append([int(fppoints[j][d]) for d in range(2)])
            pygame.draw.polygon(screen, _colors[i], points)

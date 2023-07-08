
import pygame

from flycube import Cube
from border import Border
from rocket import Rocket

import fputility3d
from fpvector import FPDecVec3
from fpmatrix import FPDecMtx44

pygame.init()
_size = 640, 480
_screen = pygame.display.set_mode(_size)

# Set screen scale (y-positive is up)
_scale = 1
_modelView = FPDecMtx44.GetScaleMtx(-_scale, _scale, _scale)

# set camera position
_modelView = FPDecMtx44.GetTranslateMtx(0, 0, 20) * _modelView

#_perspective = fputility3d.GetOrthoMatrix(1, 100, _size[0], _size[1])
_perspective = fputility3d.GetPerspMatrix(1, 100, _size[0], _size[1])

_cube = Cube()
_rocket = Rocket()
_border = Border()
_objects = [_border, _rocket, _cube]

def _SortObjects(o):
    return int(o.GetZPos())

def Update(deltaTime):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        for o in _objects:
            if o.ProcessEvent(event):
                break

    _rocket.SetTarget(_cube.GetPos())

    for o in _objects:
        o.Update(deltaTime)

    _objects.sort(key=_SortObjects)

    return True

def Render():
    _screen.fill((0,0,0))

    # Get the vector that is pointing in the direction of the camera
    c = FPDecMtx44(_modelView)
    c.Inverse()
    c.Transpose()
    cam = FPDecVec3(0, 0, -1) * c
    cam.Normalize()

    _border.BGRender(_perspective, _modelView, cam, _screen)
    for o in reversed(_objects):
        o.Render(_perspective, _modelView, cam, _screen)

    pygame.display.flip()

_gTickLastFrame = pygame.time.get_ticks()
_gDeltaTime = 0.0
while Update(_gDeltaTime):
    Render()
    t = pygame.time.get_ticks()
    _gDeltaTime = (t - _gTickLastFrame) / 1000.0
    _gTickLastFrame = t
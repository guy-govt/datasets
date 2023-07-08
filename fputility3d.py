
from fpmatrix import FPDecMtx44
import math

def GetOrthoMatrix(near, far, width, height):
    rml = height / -50    # right - left --> both are based on height so things stay square
    tmb = height / -50    # top - bottom
    nrml = 0              # -right - left = centered
    ntmb = 0              # -top - bottom = centered
    fmn = far - near
    o = FPDecMtx44([[             2/rml,                 0,                 0,          nrml/rml],
                    [                 0,             2/tmb,                 0,          ntmb/tmb],
                    [                 0,                 0,            -2/fmn,   (-far-near)/fmn],
                    [                 0,                 0,                 0,                 1]])
    t = FPDecMtx44.GetTranslateMtx(width*0.5, height*0.5)
    return t * o

def GetPerspMatrix(near, far, width, height):
    p = FPDecMtx44([[            height,                 0,                 0,                 0],
                    [                 0,            height,                 0,                 0],
                    [                 0,                 0,                -1,            -2*far],
                    [                 0,                 0,                -1,                 0]])
    t = FPDecMtx44.GetTranslateMtx(width*0.5, height*0.5, 0)
    return t * p

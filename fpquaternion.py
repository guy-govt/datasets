
import numpy as np
import fpdecimal as fpd
from fpvector import FPDecPoint3
from fpvector import FPDecVec3
from fpmatrix import FPDecMtx44
import math

# Fixed-Point Quaternion Class
class FPQuaternion:
    # Input Options
    #   None: identity
    #   FPQuaternion: copy
    #
    #  FROM ANGLE/AXIS
    #   angle (radians), tuple/list/ndarray/FPDecVec3 (arg[1]): copy 1 to 3 elements
    #   angle (radians), tuple/list/ndarray/FPDecVec3 (arg[1:]): copy 1 to 3 elements
    #
    #  FROM TWO VECTORS
    #   tuple/list/ndarray/FPDecVec3 (arg[0] = destination), tuple/list/ndarray/FPDecVec3 (arg[1] = source)
    #   tuple/list/ndarray/FPDecVec3 (arg[0] = destination), tuple/list/ndarray/FPDecVec3 (arg[1:] = source)
    #
    #   _converted - True means don't convert it to fixed-point if the type is np.longlong because it was already converted
    #   _normalized - True means don't normalize the axis because it was already normalized
    def __init__(self, *args, _converted = False, _normalized = False):
        self.Assign(*args, _converted=_converted, _normalized=_normalized)

    def Assign(self, *args, _converted = False, _normalized = False):
        if len(args) == 0:
            self.q = np.array([0, 0, 0, fpd.gDecMult], dtype=np.longlong)
            return
        if len(args) == 1 and isinstance(args[0], FPQuaternion):
            self.q = args[0].q.copy()
            return

        angle = None
        first = None
        _c1 = _converted
        _c2 = _converted
        if len(args) >= 2:
            if isinstance(args[0], float) or isinstance(args[0], int) or isinstance(args[0], np.longlong):
                angle = args[0]
            elif isinstance(args[0], tuple) or isinstance(args[0], list) or isinstance(args[0], np.ndarray):
                first = args[0]
            elif isinstance(args[0], FPDecVec3):
                first = args[0].v
                _c1 = True
            args = args[1:]

            if len(args) == 1:
                if isinstance(args[0], tuple) or isinstance(args[0], list) or isinstance(args[0], np.ndarray):
                    vec = args[0]
                elif isinstance(args[0], FPDecVec3):
                    vec = args[0].v
                    _c2 = True
                else:
                    vec = args
            else:
                vec = args
        else:
            raise NotImplementedError

        axis = FPDecVec3(*vec, _converted=_c2)
        if axis.IsZero():
            raise NotImplementedError

        if first is not None:
            axis0 = FPDecVec3(*first, _converted=_c1)
            if axis0.IsZero():
                raise NotImplementedError
            if not _normalized:
                axis0.Normalize()
            axis1 = FPDecVec3(axis)
            if not _normalized:
                axis1.Normalize()
            
            axis = FPDecVec3.Cross(axis1, axis0)
            dot = FPDecVec3.Dot(axis0, axis1)
            dot = min(max(dot, -1), 1)
            angle = math.acos(float(dot))

            _normalized = False
            _converted = False

        if angle is not None:
            # quaternion from angle and axis
            if not _normalized and not axis.IsZero():
                axis.Normalize()
            elif axis.IsZero():
                angle = math.fmod(angle, math.pi * 2)
                if angle > math.pi / 2 and angle <= math.pi * 3 / 2:
                    self.q = np.array([0, fpd.gDecMult, 0, 0], dtype=np.longlong)
                else:
                    self.q = np.array([0, 0, 0, fpd.gDecMult], dtype=np.longlong)
                return
            aa = float(fpd.FPDecimal(angle, _converted=_converted) / 2)
            axis2 = axis * math.sin(aa)
            self.q = np.array([*axis2.v[0:3], math.cos(aa) * fpd.gDecMult], dtype=np.longlong)
            self.Normalize()
            return

        raise NotImplementedError

    #
    # Overrides to support list indexing: getitem returns FPDecimal
    #

    def __getitem__(self, key):
        if isinstance(key, int):
            if key < -4 or key > 3:
                raise IndexError
            return fpd.FPDecimal(self.q[key], _converted=True)
        raise TypeError

    def __setitem__(self, key, value):
        if isinstance(key, int):
            if key < -4 or key > 3:
                raise IndexError
            self.q[key] = fpd.FPDecFromAny(value)
            return
        raise TypeError

    def GetAxis(self):
        return FPDecVec3(self.q, _converted=True)

    def GetAngle(self): # angle is in radians
        a = self.q[3] / fpd.gDecMult
        if a > 1: a = 1
        if a < -1: a = -1
        return fpd.FPDecimal(math.acos(a) * 2)

    #
    # Overrides to support list() and tuple() for this type: returns lists of FPDecimal
    #

    def __list__(self):
        return [fpd.FPDecimal(self.q[i], _converted=True) for i in range(4)]

    def __tuple__(self):
        return tuple([fpd.FPDecimal(self.q[i], _converted=True) for i in range(4)])

    def __len__(self):
        return 4

    #
    # Overrides to support str() and repr() for this type
    #

    def __str__(self):
        s = "{"
        for i in range(4):
            s += str(float(self.q[i]) / fpd.gDecMult)
            if i < 3:
                s += ("ijk")[i]
                s += " + "
        s += "}"
        return s

    def __repr__(self):
        s = "{<"
        for i in range(4):
            s += fpd.FPDecToStr(self.q[i])
            if i == 2:
                s += "> "
            elif i < 3:
                s += ", "
        s += "}"
        return s

    #
    # Overrides to support basic math operations on this type
    #

    @staticmethod
    def _mulHelper(d, other):
        if isinstance(other, FPQuaternion):
            s = d.q // fpd.gDecHalfMult
            o = other.q // fpd.gDecHalfMult
            d.q[0] = s[3]*o[0] + s[0]*o[3] + s[1]*o[2] - s[2]*o[1]
            d.q[1] = s[3]*o[1] - s[0]*o[2] + s[1]*o[3] + s[2]*o[0]
            d.q[2] = s[3]*o[2] + s[0]*o[1] - s[1]*o[0] + s[2]*o[3]
            d.q[3] = s[3]*o[3] - s[0]*o[0] - s[1]*o[1] - s[2]*o[2]
            d.Normalize()
            return d
        return None

    def __mul__(self, other):
        d = FPQuaternion._mulHelper(FPQuaternion(self), other)
        if d is None:
            return NotImplemented
        return d

    def __imul__(self, other):
        d = FPQuaternion._mulHelper(self, other)
        if d is None:
            return NotImplemented
        return d

    def __rmul__(self, other):
        if isinstance(other, FPDecPoint3) or isinstance(other, FPDecVec3):
            s = self.q // fpd.gDecHalfMult
            o = other.v // fpd.gDecHalfMult
            ss = s * s
            ss //= fpd.gDecHalfMult
            xy = s[0]*s[1] // fpd.gDecHalfMult
            xz = s[0]*s[2] // fpd.gDecHalfMult
            xa = s[0]*s[3] // fpd.gDecHalfMult
            yz = s[1]*s[2] // fpd.gDecHalfMult
            ya = s[1]*s[3] // fpd.gDecHalfMult
            za = s[2]*s[3] // fpd.gDecHalfMult
            m = [
                np.longlong((ss[3]+ss[0]-ss[1]-ss[2]) * o[0] + ((xy-za) * o[1] + (xz+ya) * o[2]) * 2),
                np.longlong((ss[3]-ss[0]+ss[1]-ss[2]) * o[1] + ((xy+za) * o[0] + (yz-xa) * o[2]) * 2),
                np.longlong((ss[3]-ss[0]-ss[1]+ss[2]) * o[2] + ((xz-ya) * o[0] + (yz+xa) * o[1]) * 2)
            ]
            if isinstance(other, FPDecVec3):
                v = FPDecVec3(m, _converted = True)
            else:
                v = FPDecPoint3(m, _converted = True)
            return v
        return NotImplemented

    #
    # Overrides to support conditional operations == != on this type
    #

    def __eq__(self, other):
        if isinstance(other, FPQuaternion):
            return np.all(np.equal(self.q, other.q)) or np.all(np.equal(self.q, other.q * -1))
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, FPQuaternion):
            return np.any(np.not_equal(self.q, other.q)) and np.any(np.not_equal(self.q, other.q * -1))
        return NotImplemented

    #
    # Common Quaternion operations
    #

    def Invert(self):
        if self.q[3] == 0:
            self.q = np.negative(self.q)
        else:
            self.q[3] = -self.q[3]

    def Normalize(self):
        q = self.q // fpd.gDecHalfMult
        d = np.sum(q * q, dtype=np.longlong)
        ll = np.longlong(math.sqrt(d / fpd.gDecMult) * fpd.gDecHalfMult)
        s = self.q.copy()
        self.q *= fpd.gDecHalfMult
        if np.any(np.not_equal(self.q // fpd.gDecHalfMult, s)):
            # it overflowed past the max size of the integer, so calculate a different way
            self.q = np.longlong(s // (ll / fpd.gDecHalfMult))
        else:
            self.q //= ll

    #https://www.euclideanspace.com/maths/geometry/rotations/conversions/quaternionToMatrix/index.htm
    #https://www.euclideanspace.com/maths/geometry/rotations/conversions/quaternionToMatrix/jay.htm
    def GetMatrix(self):
        m1 = FPDecMtx44([[ self.q[3],-self.q[2], self.q[1], self.q[0]],
                         [ self.q[2], self.q[3],-self.q[0], self.q[1]],
                         [-self.q[1], self.q[0], self.q[3], self.q[2]],
                         [-self.q[0],-self.q[1],-self.q[2], self.q[3]]], _converted = True)
        m2 = FPDecMtx44([[ self.q[3],-self.q[2], self.q[1],-self.q[0]],
                         [ self.q[2], self.q[3],-self.q[0],-self.q[1]],
                         [-self.q[1], self.q[0], self.q[3],-self.q[2]],
                         [ self.q[0], self.q[1], self.q[2], self.q[3]]], _converted = True)
        return m1 * m2

#q = FPQuaternion(math.radians(90), 1, 0, 0, _normalized = True)
#print(q)
#print(repr(q))
#q2 = q * q
#print(q2)
#print(repr(q2))
#v = FPDecVec3(1, 2, 3)
#print(v)
#v2 = v * q
#print(v2)
#v3 = v * q2
#print(v3)
#m = q.GetMatrix()
#v4 = v * m
#print(v4)
#q3 = FPQuaternion((0, 1, 0), (1, 0, 0), _normalized = True)
#print(q3)
#print(repr(q3))
#v5 = FPDecVec3(1, 0, 0)
#v6 = v5 * q3
#print(v6)

import numpy as np
import fpdecimal as fpd
from fpvector import FPDecPoint3
from fpvector import FPDecVec3
import math

# Fixed-Point 4x4 Matrix Class
class FPDecMtx44:
    # Input Options
    #   None: identity
    #   FPDecMtx44: copy
    #   4x4 tuple, list, ndarray: copy
    #   _converted - True means don't convert it to fixed-point if the type is np.longlong because it was already converted
    def __init__(self, value = None, _converted = False):
        self.Assign(value=value, _converted=_converted)
        
    def Assign(self, value = None, _converted = False):
        if value is None:
            self.m = np.identity(4, dtype=np.longlong) * fpd.gDecMult
            return
        if isinstance(value, FPDecMtx44):
            self.m = value.m.copy()
            return
        if isinstance(value, np.ndarray) and value.shape == (4, 4):
            self.m = value.astype(np.longlong) * fpd.gDecMult
            return
        if (isinstance(value, tuple) or isinstance(value, list)) and len(value) == 4:
            for i in range(4):
                if not (isinstance(value[i], tuple) or isinstance(value[i], list)):
                    break
                if len(value[i]) != 4:
                    break
            else:
                self.m = np.array([[value[y][x] if _converted and isinstance(value[y][x], np.longlong) else fpd.FPDecFromAny(value[y][x]) for x in range(4)] for y in range(4)], dtype=np.longlong)
                return
        raise NotImplementedError

    #
    # Overrides to support list indexing: getitem returns FPDecimal
    #

    class __getsetHelper():
        def __init__(self, vw): self.vw = vw
        def __getitem__(self, key):
            if isinstance(key, int):
                if key < -4 or key > 3: raise IndexError
                return fpd.FPDecimal(self.vw[key], _converted=True)
            raise TypeError
        def __setitem__(self, key, value):
            if isinstance(key, int):
                if key < -4 or key > 3: raise IndexError
                self.vw[key] = fpd.FPDecFromAny(value)
                return
            raise TypeError

    def __getitem__(self, key):
        if isinstance(key, int):
            if key < -4 or key > 3:
                raise IndexError
            return FPDecMtx44.__getsetHelper(self.m[key])
        if isinstance(key, tuple) and len(key) == 2:
            if key[0] < -4 or key[0] > 3 or key[1] < -4 or key[1] > 3:
                raise IndexError
            return fpd.FPDecimal(self.m[key], _converted=True)
        raise TypeError

    def __setitem__(self, key, value):
        if isinstance(key, tuple) and len(key) == 2:
            if key[0] < -4 or key[0] > 3 or key[1] < -4 or key[1] > 3:
                raise IndexError
            self.m[key] = fpd.FPDecFromAny(value)
            return
        raise TypeError

    #
    # Overrides to support list() and tuple() for this type: returns 4x4 lists of FPDecimal
    #

    def __list__(self):
        return [[fpd.FPDecimal(self.m[y,x], _converted=True) for x in range(4)] for y in range(4)]

    def __tuple__(self):
        return tuple([[fpd.FPDecimal(self.m[y,x], _converted=True) for x in range(4)] for y in range(4)])

    #
    # Overrides to support str() and repr() for this type
    #

    def __toStrHelper(self, cb):
        width = 1
        lst = []
        for y in range(4):
            for x in range(4):
                q = cb(y,x)
                lst.append(q)
                if len(q) > width:
                    width = len(q)
        s = ""
        lp = 0
        for y in range(4):
            s += "["
            for x in range(4):
                q = lst[lp]
                lp += 1
                if len(q) < width:
                    q = (" " * (width - len(q))) + q
                s += q
                if x < 3:
                    s += ", "
            s += "]"
            if y < 3:
                s += "\n"
        return s

    def __str__(self):
        return self.__toStrHelper(lambda y,x: "%0.3f" % (float(self.m[y,x]) / fpd.gDecMult, ))

    def __repr__(self):
        return self.__toStrHelper(lambda y,x: fpd.FPDecToStr(self.m[y,x]))

    #
    # Overrides to support basic math operations on this type
    #

    def __mul__(self, other):
        m = FPDecMtx44(self)
        if isinstance(other, FPDecMtx44):
            m.m //= fpd.gDecHalfMult
            m.m = np.matmul(m.m, other.m // fpd.gDecHalfMult, dtype=np.longlong)
            return m
        return NotImplemented

    def __imul__(self, other):
        if isinstance(other, FPDecMtx44):
            self.m //= fpd.gDecHalfMult
            self.m = np.matmul(self.m, other.m // fpd.gDecHalfMult, dtype=np.longlong)
            return self
        return NotImplemented

    def __rmul__(self, other):
        if isinstance(other, FPDecPoint3) or isinstance(other, FPDecVec3):
            m = np.matmul(self.m // fpd.gDecHalfMult, other.v // fpd.gDecHalfMult, dtype=np.longlong)
            if isinstance(other, FPDecVec3):
                v = FPDecVec3(m, _converted = True)
            else:
                v = FPDecPoint3(m, _converted = True)
                if m[3] == -0:
                    v /= -0.00001
                elif m[3] == 0:
                    v /= 0.00001
                else:
                    v /= fpd.FPDecimal(m[3], _converted=True)
            return v
        return NotImplemented

    #
    # Overrides to support conditional operations == != on this type
    #

    def __eq__(self, other):
        if isinstance(other, FPDecMtx44):
            return np.all(np.equal(self.m, other.m))
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, FPDecMtx44):
            return np.any(np.not_equal(self.m, other.m))
        return NotImplemented

    #
    # Common Matrix operations
    #

    def Transpose(self):
        self.m = np.transpose(self.m)

    def Inverse(self):
        m = np.hstack((self.m, np.identity(4, dtype=np.longlong) * fpd.gDecMult))
        for j in range(4):

            bk = j
            best = abs(m[bk,j])
            for k in range(j+1, 4):
                a = abs(m[k,j])
                if a > best:
                    best = a
                    bk = k
            if best == 0:
                raise NotImplementedError

            if bk != j:
                m[[j,bk]] = m[[bk,j]]

            v = m[j,j]
            if v != fpd.gDecMult:
                s = m[j].copy()
                m[j] *= fpd.gDecHalfMult
                if np.any(np.not_equal(m[j] // fpd.gDecHalfMult, s)): # overflow
                    m[j] = np.longlong(s // (v / fpd.gDecMult))
                else:
                    m[j] //= v // fpd.gDecHalfMult

            for k in range(4):
                if k == j or m[k,j] == 0: continue
                r = m[j].copy() // fpd.gDecHalfMult
                r *= -m[k,j] // fpd.gDecHalfMult
                m[k] += r

        self.m = m[:,4:].copy()

    #   _converted - True means don't convert it to fixed-point if the type is np.longlong because it was already converted
    @staticmethod
    def GetTranslateMtx(*args, _converted = False):
        v = FPDecVec3(*args, _converted=_converted)
        m = FPDecMtx44()
        m.m[:3,3] = v.v[:3].copy()
        return m

    #   _converted - True means don't convert it to fixed-point if the type is np.longlong because it was already converted
    @staticmethod
    def GetScaleMtx(*args, _converted = False):
        v = FPDecVec3(*args, _converted=_converted)
        m = FPDecMtx44()
        for i in range(3):
            m.m[i,i] = v.v[i]
        return m

    #   _converted - True means don't convert it to fixed-point if the type is np.longlong because it was already converted
    #   _normalized - True means don't normalize the axis because it was already normalized
    @staticmethod
    def GetRotateMtx(angle, *args, _converted = False, _normalized = False): # angle is in radians
        v = FPDecVec3(*args, _converted=_converted)
        if not _normalized:
            v.Normalize()
        m = FPDecMtx44()
        aa = fpd.FPDecimal(angle, _converted=_converted)
        a = float(aa)
        co = math.cos(a)
        co1 = 1.0 - co
        co = int(co * fpd.gDecMult)
        sn = math.sin(a)
        fun = lambda a,b: int(co1 * (v.v[a] // fpd.gDecHalfMult) * (v.v[b] // fpd.gDecHalfMult))
        xy = fun(0, 1)
        xz = fun(0, 2)
        yz = fun(1, 2)
        x = int(sn * v.v[0])
        y = int(sn * v.v[1])
        z = int(sn * v.v[2])
        m.m[0,0] = co + fun(0, 0)
        m.m[0,1] = xy - z
        m.m[0,2] = xz + y
        m.m[1,0] = xy + z
        m.m[1,1] = co + fun(1, 1)
        m.m[1,2] = yz - x
        m.m[2,0] = xz - y
        m.m[2,1] = yz + x
        m.m[2,2] = co + fun(2, 2)
        return m


#mt1 = FPDecMtx44.GetTranslateMtx(1,2,3)
#mt2 = FPDecMtx44.GetTranslateMtx(1,2,3)
#print(mt2)
#mt2.Inverse()
#print(mt2)
#print(mt1 * mt2)
#mt2 = FPDecMtx44.GetTranslateMtx(4,5,6)
#mt3 = FPDecMtx44.GetScaleMtx(7,8,9)
#mt4 = FPDecMtx44.GetRotateMtx(3.14, 0, 1, 0)
#print(mt3)
#print(repr(mt3))
#vt = FPDecVec3(1,1,1)
#vt *= mt3
#print(vt)
#pt = FPDecPoint3(1,1,1)
#print(pt * mt2)
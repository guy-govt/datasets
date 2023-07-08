
import numpy as np
import fpdecimal as fpd
import math
import warnings

warnings.filterwarnings("error")

# Fixed-Point 3D Point Class
class FPDecPoint3:
    # Input Options
    #   None: (0,0,0)
    #   FPDecPoint3: copy
    #   tuple, list, ndarray (arg[0]): copy 1 to 3 elements
    #   tuple, list, ndarray (*arg): copy 1 to 3 elements
    #   _converted - True means don't convert it to fixed-point if the type is np.longlong because it was already converted
    def __init__(self, *args, _converted = False):
        self.Assign(*args, _converted = _converted)
        
    def Assign(self, *args, _converted = False):
        if len(args) == 1 and isinstance(args[0], FPDecPoint3):
            self.v = args[0].v.copy()
            return
        self.v = self._initHelper(*args, _converted=_converted)
        if self.v is None:
            raise NotImplementedError
        self.v[3] = fpd.gDecMult

    def _initHelper(self, *args, _converted = False):
        if len(args) == 0:
            return np.array([0, 0, 0, 0], dtype=np.longlong)
        if len(args) == 1 and (isinstance(args[0], tuple) or isinstance(args[0], list) or isinstance(args[0], np.ndarray)):
            args = args[0]
        if (isinstance(args, tuple) or isinstance(args, list) or (isinstance(args, np.ndarray) and args.ndim == 1)) and len(args) <= 4:
            return np.array([((args[i] if _converted and isinstance(args[i], np.longlong) else fpd.FPDecFromAny(args[i])) if i < len(args) and i < 3 else 0) for i in range(4)], dtype=np.longlong)
        return None

    #
    # Overrides to support list indexing: getitem returns FPDecimal
    #

    def __getitem__(self, key):
        if isinstance(key, int):
            if key < -4 or key > 3:
                raise IndexError
            return fpd.FPDecimal(self.v[key], _converted=True)
        raise TypeError

    def __setitem__(self, key, value):
        if isinstance(key, int):
            if key < -4 or key > 3:
                raise IndexError
            self.v[key] = fpd.FPDecFromAny(value)
            return
        raise TypeError

    #
    # Overrides to support list() and tuple() for this type: returns lists of FPDecimal
    #

    def __list__(self):
        return [fpd.FPDecimal(self.v[i], _converted=True) for i in range(4)]

    def __tuple__(self):
        return tuple([fpd.FPDecimal(self.v[i], _converted=True) for i in range(4)])

    def __len__(self):
        return 4

    #
    # Overrides to support str() and repr() for this type
    #

    def __str__(self):
        s = "("
        for i in range(4):
            s += str(float(self.v[i]) / fpd.gDecMult)
            if i < 2:
                s += ", "
            elif i == 2:
                s += "; "
        s += ")"
        return s

    def __repr__(self):
        s = "("
        for i in range(4):
            s += fpd.FPDecToStr(self.v[i])
            if i < 2:
                s += ", "
            elif i == 2:
                s += "; "
        s += ")"
        return s

    #
    # Overrides to support basic math operations on this type
    #

    def __add__(self, other):
        d = FPDecPoint3(self)
        if isinstance(other, FPDecVec3):
            d.v += other.v
            return d
        if isinstance(other, FPDecPoint3):
            d.v[0:3] += other.v[0:3]
            return d
        return NotImplemented

    def __iadd__(self, other):
        if isinstance(other, FPDecVec3):
            self.v += other.v
            return self
        if isinstance(other, FPDecPoint3):
            self.v[0:3] += other.v[0:3]
            return self
        return NotImplemented

    def __radd__(self, other):
        return NotImplemented

    def __sub__(self, other):
        if isinstance(other, FPDecVec3):
            d = FPDecPoint3(self)
            d.v -= other.v
            return d
        if isinstance(other, FPDecPoint3):
            d = FPDecVec3(self.v, _converted = True)
            d.v[:3] -= other.v[:3]
            return d
        return NotImplemented

    def __isub__(self, other):
        if isinstance(other, FPDecVec3):
            self.v -= other.v
            return self
        return NotImplemented

    def __rsub__(self, other):
        return NotImplemented

    @staticmethod
    def _mulHelper(d, other):
        if isinstance(other, fpd.FPDecimal):
            d.v[:3] //= fpd.gDecHalfMult
            d.v[:3] *= other.d // fpd.gDecHalfMult
            return d
        if isinstance(other, int) or isinstance(other, float):
            d.v[:3] //= fpd.gDecHalfMult
            d.v[:3] *= np.longlong(other * fpd.gDecHalfMult)
            return d
        if isinstance(other, FPDecVec3):
            v = other.v[:3].copy()
            d.v[:3] //= fpd.gDecHalfMult
            d.v[:3] *= v // fpd.gDecHalfMult
            return d
        return None

    def __mul__(self, other):
        d = FPDecPoint3._mulHelper(FPDecPoint3(self), other)
        if d is None:
            return NotImplemented
        return d

    def __imul__(self, other):
        d = FPDecPoint3._mulHelper(self, other)
        if d is None:
            return NotImplemented
        return d

    def __rmul__(self, other):
        return NotImplemented

    @staticmethod
    def _divHelper(d, other):
        if isinstance(other, fpd.FPDecimal):
            s = d.v[:3].copy()
            try:
                d.v[:3] *= fpd.gDecHalfMult
            except:
                d.v[:3] = s // (other.d // fpd.gDecMult)
                return d
            d.v[:3] //= other.d // fpd.gDecHalfMult
            return d
        if isinstance(other, int) or isinstance(other, float):
            d.v[:3] //= np.longlong(other * fpd.gDecHalfMult)
            d.v[:3] *= fpd.gDecHalfMult
            return d
        if isinstance(other, FPDecVec3):
            v = other.v[:3].copy()
            s = d.v[:3].copy()
            try:
                d.v[:3] *= fpd.gDecHalfMult
            except:
                d.v[:3] = s // (v // fpd.gDecMult)
                return d
            d.v[:3] //= v // fpd.gDecHalfMult
            return d
        return None

    def __truediv__(self, other):
        d = FPDecPoint3._divHelper(FPDecPoint3(self), other)
        if d is None:
            return NotImplemented
        return d

    def __itruediv__(self, other):
        d = FPDecPoint3._divHelper(self, other)
        if d is None:
            return NotImplemented
        return d

    def __rtruediv__(self, other):
        return NotImplemented

    def __floordiv__(self, other):
        return NotImplemented

    def __ifloordiv__(self, other):
        return NotImplemented

    def __rfloordiv__(self, other):
        return NotImplemented

    #
    # Overrides to support conditional operations == != on this type
    #

    def __eq__(self, other):
        if isinstance(other, FPDecPoint3) and not isinstance(other, FPDecVec3):
            return np.all(np.equal(self.v, other.v))
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, FPDecPoint3) and not isinstance(other, FPDecVec3):
            return np.any(np.not_equal(self.v, other.v))
        return NotImplemented

    def IsZero(self):
        return not np.any(self.v[0:3])




# Fixed-Point 3D Vector Class
class FPDecVec3(FPDecPoint3):
    # Input Options
    #   None: (0,0,0)
    #   FPDecPoint3: copy
    #   tuple, list, ndarray (arg[0]): copy 1 to 3 elements
    #   tuple, list, ndarray (*arg): copy 1 to 3 elements
    #   _converted - True means don't convert it to fixed-point if the type is np.longlong because it was already converted
    def __init__(self, *args, _converted = False):
        self.Assign(*args, _converted=_converted)
        
    def Assign(self, *args, _converted = False):
        if len(args) == 1 and isinstance(args[0], FPDecVec3):
            self.v = args[0].v.copy()
            return
        self.v = self._initHelper(*args, _converted=_converted)
        if self.v is None:
            raise NotImplementedError

    #
    # Overrides to support str() and repr() for this type
    #

    def __str__(self):
        s = "<"
        for i in range(4):
            s += str(float(self.v[i]) / fpd.gDecMult)
            if i < 2:
                s += ", "
            elif i == 2:
                s += "; "
        s += ">"
        return s

    def __repr__(self):
        s = "<"
        for i in range(4):
            s += fpd.FPDecToStr(self.v[i])
            if i < 2:
                s += ", "
            elif i == 2:
                s += "; "
        s += ">"
        return s

    #
    # Overrides to support basic math operations on this type
    #

    def __add__(self, other):
        d = FPDecVec3(self)
        if isinstance(other, FPDecVec3):
            d.v += other.v
            return d
        return NotImplemented

    def __sub__(self, other):
        d = FPDecVec3(self)
        if isinstance(other, FPDecVec3):
            d.v -= other.v
            return d
        return NotImplemented

    def __neg__(self):
        return FPDecVec3(np.negative(self.v), _converted = True)

    def __mul__(self, other):
        d = FPDecPoint3._mulHelper(FPDecVec3(self), other)
        if d is None:
            return NotImplemented
        return d

    def __truediv__(self, other):
        d = FPDecPoint3._divHelper(FPDecVec3(self), other)
        if d is None:
            return NotImplemented
        return d

    #
    # Overrides to support conditional operations == != > < >= <= on this type
    # These compare vector lengths with both scalars and other vectors
    # Exception: == and != between two vectors will just compare the numbers
    #

    def __eq__(self, other):
        if isinstance(other, FPDecVec3):
            return np.all(np.equal(self.v, other.v))
        if isinstance(other, int) or isinstance(other, float) or isinstance(other, fpd.FPDecimal):
            return self.SqrLength() == other * other
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, FPDecVec3):
            return np.any(np.not_equal(self.v, other.v))
        if isinstance(other, int) or isinstance(other, float) or isinstance(other, fpd.FPDecimal):
            return self.SqrLength() != other * other
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, FPDecVec3):
            return self.SqrLength() < other.SqrLength()
        if isinstance(other, int) or isinstance(other, float) or isinstance(other, fpd.FPDecimal):
            return self.SqrLength() < other * other
        return NotImplemented

    def __gt__(self, other):
        if isinstance(other, FPDecVec3):
            return self.SqrLength() > other.SqrLength()
        if isinstance(other, int) or isinstance(other, float) or isinstance(other, fpd.FPDecimal):
            return self.SqrLength() > other * other
        return NotImplemented

    def __le__(self, other):
        if isinstance(other, FPDecVec3):
            return self.SqrLength() <= other.SqrLength()
        if isinstance(other, int) or isinstance(other, float) or isinstance(other, fpd.FPDecimal):
            return self.SqrLength() <= other * other
        return NotImplemented

    def __ge__(self, other):
        if isinstance(other, FPDecVec3):
            return self.SqrLength() >= other.SqrLength()
        if isinstance(other, int) or isinstance(other, float) or isinstance(other, fpd.FPDecimal):
            return self.SqrLength() >= other * other
        return NotImplemented

    #
    # Common Vector operations
    #

    def SqrLength(self):
        return FPDecVec3.Dot(self, self)

    def Length(self):
        d = self.SqrLength()
        if d < 0: # backup if there is an overflow
            v = self.v / fpd.gDecMult
            d.d = np.longlong(math.sqrt(np.sum(v * v)) * fpd.gDecMult)
            return d
        d.d = np.longlong(math.sqrt(d.d / fpd.gDecMult) * fpd.gDecMult)
        return d

    def Normalize(self):
        l = self.Length()
        if l == 0:
            return
        self /= l

    @staticmethod
    def Dot(a, b):
        if (isinstance(a, FPDecVec3) and isinstance(b, FPDecVec3)) or \
           (isinstance(a, FPDecPoint3) and isinstance(b, FPDecVec3)):
            return fpd.FPDecimal(np.sum((a * b).v[:3], dtype=np.longlong), _converted=True)
        if isinstance(a, FPDecVec3) and isinstance(b, FPDecPoint3):
            return fpd.FPDecimal(np.sum((b * a).v[:3], dtype=np.longlong), _converted=True)
        raise NotImplementedError

    @staticmethod
    def Cross(a, b):
        if isinstance(a, FPDecVec3) and isinstance(b, FPDecVec3):
            return FPDecVec3(np.cross(a.v[:3] // fpd.gDecHalfMult, b.v[:3] // fpd.gDecHalfMult).astype(np.longlong), _converted=True)
        raise NotImplementedError

#a = FPDecVec3(0,0,2)
#b = FPDecVec3(0,2,0)
#c = FPDecVec3.Cross(a, b)
#print(c.Length())
#print(repr(c))
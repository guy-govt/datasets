
import numpy as np

# Decimal type is 64 bit size int with 32 base-2 digits for the right of the decmal point
gDecDigits = int(32)
gDecMult = int(2 ** gDecDigits)
gDecHalfMult = int(2 ** (gDecDigits/2))

# Helper function to convert many types of variables to an int in the form for fix point decimal
def FPDecFromAny(value):
    if isinstance(value, int) or isinstance(value, float):
        a = np.longlong(value * gDecMult)
        return a
    if isinstance(value, FPDecimal):
        return value.d
    raise NotImplementedError

def FPDecSqrt(value):
    if isinstance(value, FPDecimal):
        if value < 0:
            raise NotImplementedError
        if value == 0 or value == 1:
            return value

        if value > 1:
            start = FPDecimal(1)
            end = value / 2
        else:
            start = FPDecimal(value)
            start.d += 1
            end = FPDecimal(1)

        ans = start
        while (start <= end):
            mid = (start + end) / 2
            mm = mid * mid
            if (mm == value):
                return mid
            if (mm < value):
                start.d = mid.d + 1
                ans = mid
            else:
                end.d = mid.d - 1
        return ans
        
    raise NotImplementedError

# Helper function to convert an int in the form for fix point decimal to a string
def FPDecToStr(dec):
    s = ""
    m = abs(dec // gDecMult)
    n = dec < 0
    dd = 0xFFFFFFFF & dec
    if dd != 0:
        val = 0
        mul = 1
        smul = 1
        stp = 1
        for i in range(31, -1, -1):
            mul *= 10
            smul *= 10
            stp *= 10
            stp //= 2
            if (1 << i) & dd != 0:
                val *= mul
                val += stp
                mul = 1
        smul //= 10 * mul
        if n:
            m -= 1
            val = (smul * 10) - val
        s = "."
        sv = str(val)
        for _ in range(len(str(smul)) - len(sv)):
            s += '0'
        s += sv
    s = str(m) + s
    if n: s = "-" + s
    return s

# Fixed-Point Decimal Class
class FPDecimal:
    # Input Options
    #   _converted - True means don't convert it to fixed-point if the type is np.longlong because it was already converted
    def __init__(self, value, _converted = False):
        self.Assign(value, _converted=_converted)
        
    def Assign(self, value, _converted = False):
        if _converted and isinstance(value, np.longlong):
            self.d = value # Don't convert if it is already converted
        else:
            self.d = FPDecFromAny(value)

    #
    # Overrides to support int(), float(), str(), repr() on this type
    #

    def __int__(self):
        return int(self.d // gDecMult)

    def __float__(self):
        return float(self.d / gDecMult)

    def __str__(self):
        return str(float(self.d) / gDecMult)

    def __repr__(self):
        return FPDecToStr(self.d)

    #
    # Overrides to support basic math operations on this type
    #

    def __add__(self, other):
        d = FPDecimal(self)
        if isinstance(other, int) or isinstance(other, float):
            d.d += np.longlong(other * gDecMult)
            return d
        if isinstance(other, FPDecimal):
            d.d += other.d
            return d
        return NotImplemented

    def __iadd__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            self.d += np.longlong(other * gDecMult)
            return self
        if isinstance(other, FPDecimal):
            self.d += other.d
            return self
        return NotImplemented

    def __radd__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            d = FPDecimal(self)
            d.d += np.longlong(other * gDecMult)
            return d
        return NotImplemented

    def __sub__(self, other):
        d = FPDecimal(self)
        if isinstance(other, int) or isinstance(other, float):
            d.d -= np.longlong(other * gDecMult)
            return d
        if isinstance(other, FPDecimal):
            d.d -= other.d
            return d
        return NotImplemented

    def __isub__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            self.d -= np.longlong(other * gDecMult)
            return self
        if isinstance(other, FPDecimal):
            self.d -= other.d
            return self
        return NotImplemented

    def __rsub__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            d = FPDecimal(self)
            d.d = np.longlong(other * gDecMult) - d.d
            return d
        return NotImplemented

    def __neg__(self):
        return FPDecimal(-self.d, _converted = True)

    def __mul__(self, other):
        d = FPDecimal(self)
        if isinstance(other, int) or isinstance(other, float):
            d.d //= gDecHalfMult
            d.d *= np.longlong(other * gDecHalfMult)
            return d
        if isinstance(other, FPDecimal):
            od = other.d
            d.d //= gDecHalfMult
            d.d *= od // gDecHalfMult
            return d
        return NotImplemented

    def __imul__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            self.d //= gDecHalfMult
            self.d *= np.longlong(other * gDecHalfMult)
            return self
        if isinstance(other, FPDecimal):
            d = other.d
            self.d //= gDecHalfMult
            self.d *= d // gDecHalfMult
            return self
        return NotImplemented

    def __rmul__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            d = FPDecimal(self)
            d.d //= gDecHalfMult
            d.d *= np.longlong(other * gDecHalfMult)
            return d
        return NotImplemented

    def __pow__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            return FPDecimal((self.d / gDecMult) ** (other))
        if isinstance(other, FPDecimal):
            return FPDecimal((self.d / gDecMult) ** (other.d / gDecMult))
        return NotImplemented

    def __truediv__(self, other):
        d = FPDecimal(self)
        if isinstance(other, int) or isinstance(other, float):
            d.d //= np.longlong(other * gDecHalfMult)
            d.d *= gDecHalfMult
            return d
        if isinstance(other, FPDecimal):
            od = other.d
            s = d.d
            d.d *= gDecHalfMult
            if d.d // gDecHalfMult != s: # overflow
                d.d = np.longlong(s / (od / gDecMult))
                return d
            d.d //= od // gDecHalfMult
            return d
        return NotImplemented

    def __itruediv__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            self.d //= np.longlong(other * gDecHalfMult)
            self.d *= gDecHalfMult
            return self
        if isinstance(other, FPDecimal):
            d = other.d
            s = self.d
            self.d *= gDecHalfMult
            if self.d // gDecHalfMult != s: # overflow
                self.d = np.longlong(s / (d / gDecMult))
                return d
            self.d //= d // gDecHalfMult
            return self
        return NotImplemented

    def __rtruediv__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            d = FPDecimal(self)
            d.d //= gDecHalfMult
            d.d = np.longlong(other * gDecMult) // d.d
            d.d *= gDecHalfMult
            return d
        return NotImplemented

    def __floordiv__(self, other):
        return NotImplemented

    def __ifloordiv__(self, other):
        return NotImplemented

    def __rfloordiv__(self, other):
        return NotImplemented

    #
    # Overrides to support conditional operations == != > < >= <= on this type
    #

    def __eq__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            return self.d == int(other * gDecMult)
        if isinstance(other, FPDecimal):
            return self.d == other.d
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            return self.d != int(other * gDecMult)
        if isinstance(other, FPDecimal):
            return self.d != other.d
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            return self.d < int(other * gDecMult)
        if isinstance(other, FPDecimal):
            return self.d < other.d
        return NotImplemented

    def __gt__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            return self.d > int(other * gDecMult)
        if isinstance(other, FPDecimal):
            return self.d > other.d
        return NotImplemented

    def __le__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            return self.d <= int(other * gDecMult)
        if isinstance(other, FPDecimal):
            return self.d <= other.d
        return NotImplemented

    def __ge__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            return self.d >= int(other * gDecMult)
        if isinstance(other, FPDecimal):
            return self.d >= other.d
        return NotImplemented

#d1 = FPDecimal(-10)
#d2 = FPDecimal(7)
#d3 = d1 / d2
#print(str(d3))
#print(repr(d3))
#d4 = FPDecimal(-0.123)
#print(str(d4))
#print(repr(d4))
#print(repr(FPDecSqrt(FPDecimal(0))))
#print(repr(FPDecSqrt(FPDecimal(1))))
#print(repr(FPDecSqrt(FPDecimal(4))))
#print(repr(FPDecSqrt(FPDecimal(10))))
#print(repr(FPDecSqrt(FPDecimal(0.9))))
#print(repr(FPDecSqrt(FPDecimal(0.1))))
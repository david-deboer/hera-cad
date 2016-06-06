import math
import numpy as np

class Dims:
    def __init__(self,loc='sa'):
        """Dimensions for hardware lengths of HERA antennas."""
        self.loc = loc
        if loc=='?' or loc=='help':
            print 'Input parameters are (need all in consistent units):'
            print '\trn: distance from center to nail'
            print '\tb:  distance from hub top to sleeve top'
            print '\ts:  outer diameter of sleeve'
            print '\td:  distance from nail to inner edge of sleeve'
            print '\tt:  wall thickness of sleeve'
            print '\tp:  spar pipe outer diameter'
            print '\te:  sleeve spacer size'
            print '\tg:  distance between bottom of sleeve and top of horiz support spar'
            print '\tq:  90deg coupler offset'
            print '\tLh: horizontal support spar length'
            print '\trh: location of inner edge of horizontal support spar'
            print '\tF:  focal length'
            print '\tD:  diameter'
            print '\tri: inner hub diameter'
            print '\tro: outer hub diameter'
            print '\tintermediateSparOffset:  offset of intermediate spar T'
            print "\tpanel['A-E']: length of panel A-E"
            print "\tpanel['Overlap']:  panel overlap"
        else:
            self.precision = None
            self.panel = {}
            self.panel['A'] = 1616.0  # x 1220.0 mm
            self.panel['B'] = 2250.0  # x 1220.0 mm
            self.panel['C'] = 1220.0  # x 1515.0 mm
            self.panel['D'] = 1220.0  # x 1810.0 mm
            self.panel['E'] = 1220.0  # x 2105.0 mm
            self.panel['Overlap'] = 100.0  # mm
            self.mm2unit = {'in':1.0/25.4, 'cm':1.0/10.0}
            if loc=='uk':
                self.units = 'mm'
                self.rn = 240.0
                self.b  = 55.0
                self.s  = 96.0
                self.d  = 30.0
                self.t  = 3.0
                self.p  = 54.0
                self.e  = 'find'
                self.Ls = 300.0
                self.g  = 40.0
                self.q  = 40.0
                self.Lh = 3010.0
                self.rh = 210.0
                self.F  = 4500.0
                self.D  = 14000.0
                self.ri = 230.0
                self.ro = 450.0
                self.intermediateSparOffset = 20.0
            elif loc=='sa':
                self.units = 'mm'
                self.nh = 8.9      #nailhead
                self.dctr = 20.0
                self.d = self.dctr-self.nh/2.0  
                self.ri = 458.0/2.0
                self.ro = 916/2.0
                self.rn = self.ri  #could put half the hub wall thickness if picky
                self.rh = self.rn - self.d
                self.b  = 59.0
                self.s  = 90.0
                self.t  = 3.9      #90 class 9 UPVC
                self.p  = 63.0
                self.e  = 0.0
                self.Ls = 'find'
                self.g  = 38.5
                self.q  = 6.0      #From internet
                self.Lh = 2720.0
                self.F  = 4500.0
                self.D  = 14000.0
                self.intermediateSparOffset = 6.0  #From internet
            elif loc=='us':
                self.units = 'in'
                self.rn = 1.0
                self.b  = 1.0
                self.s  = 1.0
                self.d  = 1.0
                self.t  = 1.0
                self.p  = 1.0
                self.g  = 1.0
                self.q  = 1.0
                self.Lh = 1.0
                self.rh = 1.0
                self.F  = 1.0
                self.D  = 1.0
            if self.precision is None:
                if self.units == 'mm':
                    self.precision = 0
                elif self.units == 'cm':
                    self.precision = 1
                elif self.units == 'in':
                    self.precision = 1
            if self.units != 'mm':
                for k in self.panel.keywords():
                    self.panel[k] = self.panel[k]*self.mm2unit[self.units]
            self.calc()
    def calc(self):
        self.sleeve()
        self._vo()
        self._Lv()
        self.angle_Lv()
        self.fullSpar()
        self.crossLength()
        self._sparMarks()
        self.show()
    def show(self):
        print 'vo = %.*f %s' % (self.precision,self.vo,self.units)
        print 'Sleeve'
        print '\tLs = %.*f %s' % (self.precision,self.Ls,self.units)
        print '\te  = %.*f %s' % (self.precision,self.e,self.units)
        print '\trs = %.*f %s' % (self.precision,self.rs,self.units)
        print '\t(s,t = %.*f, %.*f %s)' % (self.precision,self.s,self.precision,self.t,self.units)
        print 'Support spar'
        print '\tLv = %.*f %s' % (self.precision,self.Lv,self.units)
        print '\trv = %.*f %s' % (self.precision,self.rv,self.units)
        print '\tangle at vertical support = %.1f' % (self.av)
        print '\t(Lh,rh,q = %.*f, %.*f, %.*f %s)' % (self.precision,self.Lh,self.precision,self.rh,self.precision,self.q,self.units)
        print 'fullSpar = %.*f %s' % (self.precision,self.fullSpar,self.units)
        print '\tp = %.*f %s' % (self.precision,self.p,self.units)
        print 'Cross spar'
        print '\tradius for cross piece = %.*f %s' % (self.precision,self.crossRadius,self.units)
        print '\tlength of cross piece = %.*f %s' % (self.precision,self.crossLength,self.units)
        print 'Spar marks:'
        mskeys = sorted(self.sparMarks.keys())
        for m in mskeys:
            pm = m.split(':')
            print '\t%-18s (%-5s): %.*f %s' % (pm[1],pm[0][1:],self.precision,self.sparMarks[m],self.units)
        print 'Metal strip lengths:'
        print '\tBC: = %.*f %s' % (self.precision,self.mBC,self.units)
        print '\tCD: = %.*f %s' % (self.precision,self.mCD,self.units)
        print '\tDE: = %.*f %s' % (self.precision,self.mDE,self.units)
        print 'Panel E ends at r=%.*f %s' % (self.precision,self.r_end_of_E,self.units)
    def _vo(self):
        self.vo = self.b+self.t + self.e + self.zparab(self.rs)
    def zparab(self,r):
        return r**2/(4.0*self.F)
    def theta(self,r):
        return math.atan(r/(2.0*self.F))
    def _zt(self,r):
        """Distance from top of hub to top of spar"""
        zt = self.zparab(r) - self.vo
        return zt
    def _zb(self,r):
        """Distance from top of hub to bottom of spar"""
        costh = math.cos(self.theta(r))
        zt = self._zt(r)
        zb = zt - self.p/costh
        return zb
    def _Lv(self):
        """Length of vertical support spar"""
        self.rv = self.rh + self.Lh + self.q + self.p
        zb = self._zb(self.rv)
        self.Lv = zb + self.b + self.s + self.g - self.q
    def angle_Lv(self):
        av = self.theta(self.rv)
        self.av = av*180.0/math.pi
    def sleeve(self):
        """Sleeve calcs:  Ls, rs, e"""
        a = self.s - 2.0*self.t - self.p
        if type(self.e) is str:
	    self.rs = self.rn - self.d + self.Ls
	    self.e  = a - self.rs*(self.rs-self.rn)/(2.0*self.F)
	else:
	    self.e = 0.0
	    self.rs = (self.rn + math.sqrt(self.rn**2 + 8.0*a*self.F))/2.0
            self.Ls = self.rs - self.rn + self.d
    def arclength(self,r):
        """Arclength of parabola radius r (with given focal length)"""
        t = 2.0*self.F
        p = r
        q = math.sqrt(t**2 + p**2)
        sig = (p*q/t + t*math.log((p+q)/t))/2.0
        return sig
    def s2r(self,s,precision=None):
        """Find r given s"""
        r_start = s/2.0
        r_stop  = 2.0*s
        if precision is None:
	    precision  = (r_stop - r_start)/10000.0
        for r in np.arange(r_start,r_stop,precision):
            s1 = self.arclength(r)
            if s1> s:
                break
        return r
    def fullSpar(self):
        """Length of the full spar"""
        s1 = self.arclength(self.D/2.0)
        s2 = self.arclength(self.rn)
        self.fullSpar = s1-s2
    def crossRadius(self):
        """Find radial position of the cross spar"""
        s2 = self.arclength(self.ro)
        cosa = math.cos(math.pi/12.0)
        s = s2 + (self.panel['A'] - self.panel['Overlap']/2.0+self.p/2.0)/cosa
        self.crossRadius = self.s2r(s)  #This is at center of the long spar for outer edge of cross-piece spar
    def crossLength(self):
        self.crossRadius()
        cosa = math.cos(math.pi/12.0)
        self.crossLength = 2.0*self.crossRadius*math.sin(math.pi/12.0) - self.p/cosa
    def _sparMarks(self):
        s1 = self.arclength(self.crossRadius) - (self.p/2.0)*math.tan(math.pi/12.0)
        s2 = self.arclength(self.rn)
        sCross = s1-s2
        self.sparMarks = {'1Spar:Cross-Piece':sCross}
        self.metalStrips()
        if self.loc == 'uk':  #These are those 'check' distances near end of spars
	    rD = 6820.0
            s1 = self.arclength(rD)
            s2 = self.arclength(self.rn)
            fullSparDmark = s1-s2
            self.sparMarks['3Guide:Full-Spar']=fullSparDmark
            #print 'full spar length to Dmark = ',fullSparDmark
            rI = 6750.0
            s1 = self.arclength(rI)
            s2 = self.arclength(self.crossRadius*math.cos(math.pi/12.0)) + self.intermediateSparOffset
            intermediateSparDmark = s1-s2
            #print 'intermediate spar length to Dmark = ',intermediateSparDmark
            self.sparMarks['3Guide:Intermediate-Spar'] = intermediateSparDmark
    def metalStrips(self):
        """Calculate spar marks for metal strips"""
        cosa1 = math.cos(math.pi/12.0)
        cosa2 = math.cos(math.pi/24.0)
        snail = self.arclength(self.rn)
        shub = self.arclength(self.ro)
        sintermediate = self.arclength(self.crossRadius*cosa1) + self.intermediateSparOffset
        sAB = shub + (self.panel['A'] - self.panel['Overlap']/2.0)/cosa1  #This is the cross-piece (to center of cross, not outer)
        sBC = sAB + (self.panel['B']-self.panel['Overlap'])/cosa2
        self.sparMarks['2Metal:BC-long'] = sBC - snail
        self.sparMarks['2Metal:BC-inter'] = sBC - sintermediate
        sCD = sBC + (self.panel['C']-self.panel['Overlap'])/cosa2
        self.sparMarks['2Metal:CD-long'] = sCD - snail
        self.sparMarks['2Metal:CD-inter'] = sCD - sintermediate
        sDE = sCD + (self.panel['D']-self.panel['Overlap'])/cosa2
        self.sparMarks['2Metal:DE-long'] = sDE - snail
        self.sparMarks['2Metal:DE-inter'] = sDE - sintermediate
        self.mBC = 2.0*self.s2r(sBC)*math.sin(math.pi/24.0) + self.p/cosa2
        self.mCD = 2.0*self.s2r(sCD)*math.sin(math.pi/24.0) + self.p/cosa2
        self.mDE = 2.0*self.s2r(sDE)*math.sin(math.pi/24.0) + self.p/cosa2
        sE = sDE + self.panel['E']/cosa2
        self.r_end_of_E = self.s2r(sE)
             
    ######TEST STUFF
    def alphaCompare(self,rs=None):
        if rs is None:
	        rs = 300.+ 260.0
        b = rs-self.rn
        c = self.s - 2.0*self.t - self.p
        n = (b - math.sqrt(b**2 - 4.0*self.p*c))/(2.0*self.p)
        print math.tan(n), c/b
        print 180.0*n/math.pi, 180.0*math.atan(c/b)/math.pi
    def adjust(self):
        roff = 95.0
        znew = self._zt(self.rD)
        hnew = znew - roff
        print hnew
    def straightLine(self,r):
        dr = r - self.ri
        dz = self._zt(r)
        d = math.sqrt(dr**2 + dz**2)
        print 'Straight line distance from hub inner ',d
        

        
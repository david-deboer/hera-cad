import numpy as np
import math
import matplotlib.pyplot as plt
#import gisout as ge

class HeraConfig:
    ########USER DEFINED ARRAYS AND SUBARRAYS############
    hera = {}
    hera[19] = [0,1,2,11,12,13,14,23,24,25,26,27,37,38,39,40,52,53,54]
    hera[350] = range(350)
    hera[18] = [3,15,28,36,41,42,51,55,56,67,68,69,70,71,84,85,86,87]
    hera['block1-19-18'] = [4,5,6,7,8,9,10, 16,17,18,19,20,21,29,30,31,32,33,43,44,45,46,
                            50,57,58,59,60,65,66,72,73,74,75,81,82,83,88,89,90,91,
                            98,99,100,101,102,103,104,105,106,107,108,116,117,118,
                            119,120,121,122,123,124,125,126, 135,136,137,138,139,140,141,142,143,144,145]
    hera['block1'] = [0,1,2,11,12,13,14,23,24,25,26,27,37,38,39,40,52,53,54,3,15,28,36,41,42,51,55,56,67,68,69,70,71,84,85,86,87,
    4,5,6,7,8,9,10, 16,17,18,19,20,21,29,30,31,32,33,43,44,45,46, 50,57,58,59,60,65,66,72,73,74,75,81,82,83,88,89,90,91,98,
    99,100,101,102,103,104,105,106,107,108,116,117,118,119,120,121,122,123,124,125,126, 135,136,137,138,139,140,141,142,143,144,145]
    useConfigFile = 'SplitCore_HERA-350.txt'
    D = 14.0
    rim2rim = 0.6
    spacing = D + rim2rim
    maxCoreSpacing = 1.5*spacing
    h19ll = [540901.6000, 6601070.7407]    ###Location of existing HERA-19 lower left antenna
    longlat = [21.+(25.+42./60.)/60., -1.*(30.+(43.+17./60)/60)]  
    #-1-#schll = [-80.3,-113.795738]
    #-1-#offset = np.array([schll[0]-h19ll[0],schll[1]-h19ll[1]])

    def __init__(self,array=350,config=None):
        """Produces class with HERA configuration parameters.
           Defaults are defined under class designator.
           Inputs are:
               array:  several options
                            type int or string:  entry in 'hera' dictionary as defined above
                            type list: int list of station #'s to use for desired subarray
               config:  filename with center positions of elements (string)
                            default set above
                            format:  station#, E-W, N-S
            Outputs are:
                N:  number of antennas (int)
                ants:   list of UTM center positions ordered by station# (numpy array)
                core:  list of core UTM center positions ordered by station#: set by maxCoreSpacing (numpy array)
                outriggers: ... 
                poles:  list of all big pole locations (numpy array)
                posts:  list of all intermediate post locations (numpy array)
                polesByAnt:  list of poles by antenna ordered by station#:  duplication of poles (numpy array)
                postsByAnt:   ...
            Other info:
                arrayFileName is the name of the config file (set by 'config')
                stations is the list of used stations from config file (set by 'array')
                allAntsInFile is a dictionary with all the positions in the file with number as key"""
        ###Set input variables
        if config == None:
            self.arrayFileName = self.useConfigFile
        else:
            self.arrayFileName = config
        if type(array) == list:
            self.stations = array
        else:
            self.stations = self.hera[array]
            
        ###Get antenna locations from file
        hsc = np.loadtxt(self.arrayFileName,usecols=(0,1,2))
        self.ants = []
        self.allAntsInFile = {}
        for i,h in enumerate(hsc):
            npos = np.array([h[1],h[2]])#-1-# - self.offset
            self.allAntsInFile[int(h[0])] = [npos]
            
        #This puts then into ants in number order
        for i in self.stations:
            s = [self.allAntsInFile[i][0][0],self.allAntsInFile[i][0][1]]
            self.ants.append(s)
        self.ants = np.array(self.ants)
        self.N = len(self.ants)
        self._getCoreOutriggers()
        self._correctForRefOffset()
        self._getPolesPosts()
    
    def _close(self,a,b,colocatedDistance=1.0):
        ae = False
        dist = math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)
        if  dist < colocatedDistance:
            ae = True
        return ae
        
    def _getCoreOutriggers(self):
        ###Find core antennas
        core=[]
        self.foundCore = False
        for coreTrial in self.ants:
            for a in self.ants:
                if self._close(coreTrial,a,0.1):
                    continue
                elif self._close(coreTrial,a,self.maxCoreSpacing):
                    self.core=True
                    core.append(coreTrial)
                    break
        self.core = np.array(core)
        ###Find outrigger antennas
        outriggers = []
        self.foundOutriggers = False
        for outTrial in self.ants:
            minDist = 1E9
            for a in self.ants:
                if self._close(outTrial,a,0.1):
                    continue
                dist = math.sqrt((outTrial[0]-a[0])**2 + (outTrial[1]-a[1])**2)
                if dist<minDist:
                    minDist = dist
            if minDist>self.maxCoreSpacing:
                self.foundOutriggers
                outriggers.append(outTrial)
        self.outriggers = np.array(outriggers)

    def _correctForRefOffset(self,refType='LL'):
        if refType=='LL':
            refVal=[1E9,1E9]
            for c in self.core:
                if c[0]<refVal[0] and c[1]<refVal[1]:
                    refVal[0]=c[0]
                    refVal[1]=c[1]
        else:
            print 'Invalid refType'
            refVal=[-1E6,-1E6]
        self.offset = np.array([refVal[0]-self.h19ll[0],refVal[1]-self.h19ll[1]])
        print 'Offset to type '+refType,
        print self.offset
        self.ants = self.ants - self.offset
        if self.foundCore:
	    self.core = self.core - self.offset
	if self.foundOutriggers:
	    self.outriggers = self.outriggers - self.offset
        return refVal
        
    def _getPolesPosts(self):
    ###Install poles/posts
        numPolesPerAnt = 3
        numPostsBetween = 3
        totalPerAnt = numPolesPerAnt*(1 + numPostsBetween)
        print 'number of poles per antenna = ',totalPerAnt
        bigPoleDistance = self.spacing/(2.0*math.cos(30.0*math.pi/180.0))
        intermediatePoleDistance = self.spacing/2.0
        iBigPole = range(0,totalPerAnt,numPostsBetween+1)
        print 'iBigPole = ',iBigPole

        poles = []
        posts = []
        polesByAnt = []
        postsByAnt = []
        usedAnts = self.ants
        bigPole = True
        for iant,ant in enumerate(usedAnts):
            polesThisAnt = []
            postsThisAnt = []
            for i in range(totalPerAnt):
                angle = ( i*(360.0/totalPerAnt) - 0.0)
                angle*=(math.pi/180.0)
                if i in iBigPole:
                    poleDistance = bigPoleDistance
                    bigPole = True
                else:
                    poleDistance = intermediatePoleDistance
                    bigPole = False
                poleTrial = [ant[0] + poleDistance*math.sin(angle), ant[1] + poleDistance*math.cos(angle)]
                use = True
                if bigPole:
                    polesThisAnt.append(poleTrial)
                    for p in poles:
                        if self._close(p,poleTrial,0.2):
                            use = False
                else:
                    postsThisAnt.append(poleTrial)
                    for p in posts:
                        if self._close(p,poleTrial,0.2):
                            use = False
                if use:
                    if bigPole == True:
                        poles.append(poleTrial)
                    else:
                        posts.append(poleTrial)
            polesByAnt.append(polesThisAnt)
            postsByAnt.append(postsThisAnt)
        self.poles = np.array(poles)
        self.posts = np.array(posts)
        self.polesByAnt = np.array(polesByAnt)
        self.postsByAnt = np.array(postsByAnt)
        
        print 'number of big poles = ',len(poles)
        print 'number of intermediate posts = ',len(posts)

    def plot(self,incrementFigure=True):
        infi = 0
        if incrementFigure:
            infi = 1
        listOfFigs = plt.get_fignums()
        if len(listOfFigs)>0:
            fignum = listOfFigs[-1]+infi
        else:
            fignum = 0

        plt.figure(fignum)
        plt.plot(self.ants[:,0],self.ants[:,1],'wo',markersize=11)
        plt.plot(self.poles[:,0],self.poles[:,1],'o')
        plt.plot(self.posts[:,0],self.posts[:,1],'x')
        if self.foundCore:
	    plt.plot(self.core[:,0],self.core[:,1],'ro',markersize=10)
	if self.foundOutriggers:
	    plt.plot(self.outriggers[:,0],self.outriggers[:,1],'go',markersize=10)
        plt.axis('image')
        
    def scr(self,filePrefix=None):
        if filePrefix is None:
            filePrefix = self.useConfigFile.split('.')[0]
        fp_ant = open(filePrefix+'.scr','w')
        for a in self.ants:
            fp_ant.write('CIRCLE %.4f,%.4f\n' % (a[0],a[1]))
            fp_ant.write('%.2f\n'%(self.D/2.0))
        fp_ant.close()

    def iAntConfig(self):
        iacf = 'hera.enu.%.0fx4.txt' % (len(self.ants))
        fp = open(iacf,'w')
        print 'Writing '+iacf
        for h in self.ants:
            s = '14 %.4f %.4f 0.0000\n' % (h[0],h[1])
            fp.write(s)
        s = '0 %.4f %.4f 0\n' % (self.longlat[0], self.longlat[1])
        fp.write(s)
        fp.close()

    #def kml(self,filePrefix=None,cofa_zone=34,psc=0.4):
    #    if filePrefix is None:
    #        filePrefix = self.useConfigFile.split('.')[0]
    #    kfn = filePrefix+'.kml'
    #    print 'Writing '+kfn
    #    kmlfp = open(kfn,'w')
    #    gfn = filePrefix+'.gpx'
    #    gfp = open(gfn,'w')
    #    print 'Writing '+gfn
    #
    #    kmlfp.write(ge.kmlhdr('HERA',psc))
    #    gfp.write(ge.garhdr('HERA'))
    #    for ihc,hc in enumerate(self.ants):
    #        x = hc[0]
    #        y = hc[1]
    #        kmlfp.write(ge.kmlplcmk(str(ihc),x,y,'utm',cofa_zone))
    #        gfp.write(ge.garwypt(str(ihc),x,y,'utm',cofa_zone))
    #    kmlfp.write(ge.kmltrlr())
    #    gfp.write(ge.gartrlr())
    #    kmlfp.close()
    #    gfp.close()

    def output21cmSenseAntposDict(self,fnout='hera_split_dict.txt'):
        print 'Writing '+fnout
        xmean = self.ants[:,0].mean()
        ymean = self.ants[:,1].mean()
        zmean = 0.0
        fp = open(fnout,'w')
        s = 'xmean,ymean,zmean = %.3f,%.3f,%.3f\n' % (xmean,ymean,zmean)
        fp.write(s)
        s = 'antpos_dict = {\n'
        for i,a in enumerate(self.ants):
            fp.write(s)
            z = 0.0
            s = "   'hera%03d': [%.3f-xmean,%.3f-ymean,%.3f-zmean],\n" % (i,a[0],a[1],z)
        s = '   '+s.strip().strip(',')+'\n}\n'
        fp.write(s)
        fp.close()

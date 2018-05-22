#from __future__ import print_function

import numpy as np
import math
import matplotlib.pyplot as plt
import gisout as ge

def Nodes(node_filename='nodes.txt'):
    fp = open(node_filename,'r')
    nodes = {}
    check_ants = []
    for line in fp:
        data = line.split(':')
        node_number = int(data[0].strip())
        if node_number in nodes.keys():
            print 'node', node_number, 'already found'
        node_position = data[1].split(',')
        node_position = [float(x) for x in node_position]
        node_antennas = data[2].split(',')
        nodes[node_number] = [int(x) for x in node_antennas]
        for a in node_antennas:
            if a in check_ants:
                print 'antenna', a, 'already found'
                return 0
        check_ants+=node_antennas
    fp.close()
    print 'Total number of antennas found is',len(check_ants)
    skeys = sorted(nodes.keys())
    total_snaps = 0
    print 'Core nodes'
    for k in skeys:
        if k==30:
            print "Outrigger nodes"
        num_ants = len(nodes[k])
        num_snaps = int(math.ceil(num_ants/3.0))
        total_snaps+=num_snaps
        print '\tNode %2d has %2d antennas and needs %d snap boards' % (k,num_ants,num_snaps)
    print 'Need a total of',total_snaps,'snap boards'
    return nodes

class HeraConfig:
    ########USER DEFINED ARRAYS AND SUBARRAYS############
    hera = {}
    hera[19] = [0,1,2,11,12,13,14,23,24,25,26,27,37,38,39,40,52,53,54]
    hera[37] = [0,1,2,3,11,12,13,14,15,23,24,25,26,27,28,36,37,38,39,40,41,42,51,52,53,54,55,56,67,68,69,70,71,84,85,86,87]
    hera[350] = range(350)
    hera[243] = range(22)+range(23,35)+range(36,49)+range(50,64)+range(65,80)+range(81,97)+range(98,115)+range(116,134)+range(135,153)
    hera[243]+= range(156,173)+range(177,193)+range(197,212)+range(216,230)+range(234,247)+range(251,263)+range(267,278)
    hera[257] = range(134)+range(135,153)
    hera[257]+= range(155,173)+range(176,193)+range(196,212)+range(215,230)+range(233,247)+range(250,263)+range(266,278)
    hera[18] = [3,15,28,36,41,42,51,55,56,67,68,69,70,71,84,85,86,87]
    hera['block1-19-18'] = [4,5,6,7,8,9,10, 16,17,18,19,20,21,29,30,31,32,33,43,44,45,46,
                            50,57,58,59,60,65,66,72,73,74,75,81,82,83,88,89,90,91,
                            98,99,100,101,102,103,104,105,106,107,108,116,117,118,
                            119,120,121,122,123,124,125,126, 135,136,137,138,139,140,141,142,143,144,145]
    hera['block1'] = [0,1,2,11,12,13,14,23,24,25,26,27,37,38,39,40,52,53,54,3,15,28,36,41,42,51,55,56,67,68,69,70,71,84,85,86,87,
    4,5,6,7,8,9,10, 16,17,18,19,20,21,29,30,31,32,33,43,44,45,46, 50,57,58,59,60,65,66,72,73,74,75,81,82,83,88,89,90,91,98,
    99,100,101,102,103,104,105,106,107,108,116,117,118,119,120,121,122,123,124,125,126, 135,136,137,138,139,140,141,142,143,144,145]
    hera['core'] = range(320)
    hera['outriggers'] = range(320,350)
    useConfigFile = 'SplitCore_HERA-350_v3.txt'
    D = 14.0
    rim2rim = 0.6
    spacing = D + rim2rim
    maxCoreSpacing = 1.8*spacing
    h19ll = [540901.6000, 6601070.7407]    ###Location of existing HERA-19 lower left antenna
    longlat = [21.+(25.+42./60.)/60., -1.*(30.+(43.+17./60)/60)]  

    def __init__(self,array=None,config=None,offset=None):
        """Produces class with HERA configuration parameters.
           Defaults are defined under class designator.
           Inputs are:
                array:  several options
                            type int or string:  entry in 'hera' dictionary as defined above
                            type list: int list of station #'s to use for desired subarray
                            default:  [None], which uses all in file
                config:  filename with center positions of elements (string)
                            format:  station#, E-W, N-S
                            default:  [None], which uses self.useConfigFile
                offset: 3-element array with type and reference position for applying offset, LL or a##
                            default:  [None], which sets to antenna 0 and self.h19ll
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
                stations:  list of used stations from config file (set by 'array')
                allants:   dictionary with all the positions in the file with number as key"""
        #Get config filename
        if config == None:
            self.arrayFileName = self.useConfigFile
        else:
            self.arrayFileName = config

        ###Get antenna locations from file and default stations to all
        print '\nGetting antennas from '+self.arrayFileName
        hsc = np.loadtxt(self.arrayFileName,usecols=(0,1,2))
        self.allants = {}
        self.stations = []
        for i,h in enumerate(hsc):
            npos = [h[1],h[2]]
            self.allants[int(h[0])] = npos
            self.stations.append(int(h[0]))
        if type(array) == list:
            self.stations = array
        elif array is not None:
            self.stations = self.hera[array]
        print 'Using '+str(len(self.stations))+' stations'
            
        #Pick the desired stations and put ants in listed station order
        self.ants = []
        for i in self.stations:
            s = [self.allants[i][0],self.allants[i][1]]
            self.ants.append(s)
        self.ants = np.array(self.ants)
        self.N = len(self.ants)

        #Get offset parameters and apply
        if offset is None:
            offset = ['a0',self.h19ll[0],self.h19ll[1]]
        elif type(offset) is str:
            offset = [offset,self.h19ll[0],self.h19ll[1]]
        self.applyOffset(offset)

        #Split out core and locate poles/posts
        self._getCoreOutriggers() 
        self._getPolesPosts()
    
    def _close(self,a,b,colocatedDistance=1.0):
        ae = False
        dist = math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)
        if  dist < colocatedDistance:
            ae = True
        return ae
        
    def _getCoreOutriggers(self):
        """Locate core antennas by simple distance method"""
        core=[]
        self.foundCore = False
        for coreTrial in self.ants:
            for a in self.ants:
                if self._close(coreTrial,a,0.1):
                    continue
                elif self._close(coreTrial,a,self.maxCoreSpacing):
                    self.foundCore=True
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
                self.foundOutriggers=True
                outriggers.append(outTrial)
        self.outriggers = np.array(outriggers)

    def applyOffset(self,offset,apply2allants=True):
        refType = offset[0]
        refLoc = [offset[1],offset[2]]
        if refType=='LL':                  #lower left
            refVal=[1E9,1E9]
            for c in self.ants:            #find southernmost
                if c[1]<refVal[1]:
                    refVal[1] = c[1]
            for c in self.ants:            #find westernmost in that row
                if abs(c[1]-refVal[1])<0.1:
                    if c[0]<refVal[0]:
                        refVal[0]=c[0]
        elif refType[0].lower()=='a':
            try:
                refAntNo = int(refType[1:])
            except ValueError:
                print str(offset)+' not valid'
                return None
            refVal = self.allants[refAntNo]
        else:
            print 'Invalid refType'
            refVal=[-1E6,-1E6]
        self.offset = np.array([refVal[0]-refLoc[0],refVal[1]-refLoc[1]])
        print 'Offset to type '+refType,
        print self.offset
        self.ants = self.ants - self.offset
        if apply2allants:
            for i in self.allants.keys():
                self.allants[i][0] = self.allants[i][0]-self.offset[0]
                self.allants[i][1] = self.allants[i][1]-self.offset[1]
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

    def plot(self,coreColor='r',outColor='g',onlyAnts=True,fignum=False):
        if fignum:
            plt.figure(fignum)
        plt.plot(self.ants[:,0],self.ants[:,1],'wo',markersize=11)
        if not onlyAnts:
            plt.plot(self.poles[:,0],self.poles[:,1],'o')
            plt.plot(self.posts[:,0],self.posts[:,1],'x')
        if self.foundCore:
	       plt.plot(self.core[:,0],self.core[:,1],'o',color=coreColor,markersize=10)
        if self.foundOutriggers:
            plt.plot(self.outriggers[:,0],self.outriggers[:,1],'o',color=outColor,markersize=10)
        plt.axis('image')
        
    def plotNumbered(self,fignum=False):
        if fignum:
            plt.figure(fignum)
        for k in self.allants.keys():
            plt.plot(self.allants[k][0],self.allants[k][1],'ko')
            plt.text(self.allants[k][0],self.allants[k][1],str(k))

    def scr(self,filePrefix=None):
        """autocad file script"""
        if filePrefix is None:
            filePrefix = self.arrayFileName.split('.')[0]
        fn = filePrefix+'.scr'
        fp = open(fn,'w')
        for a in self.ants:
            fp.write('CIRCLE %.4f,%.4f\n' % (a[0],a[1]))
            fp.write('%.2f\n'%(self.D/2.0))
        fp.write('\n')
        fp.close()
        fn = filePrefix+'_poles.scr'
        fp = open(fn,'w')
        for h in self.poles:  #pick one format below
            s = 'CIRCLE %.4f,%.4f\n0.2\n' % (h[0],h[1])
            #s = '%.2f\t%.2f\n' % (h[0]+center_of_array[0],h[1]+center_of_array[1])
            #s = 'CIRCLE %.2f,%.2f\n0.2\n' % (h[0]+center_of_array[0],h[1]+center_of_array[1])
            fp.write(s)
        fp.write('\n')
        fp.close()
        fn = filePrefix+'_posts.scr'
        fp = open(fn,'w')
        for h in self.posts:  #pick one format below
            s = 'CIRCLE %.4f,%.4f\n0.1\n' % (h[0],h[1])
            #s = '%.2f\t%.2f\n' % (h[0]+center_of_array[0],h[1]+center_of_array[1])
            #s = 'CIRCLE %.2f,%.2f\n0.2\n' % (h[0]+center_of_array[0],h[1]+center_of_array[1])
            fp.write(s)
        fp.write('\n')
        fp.close()

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

    def antennaConfigTxtfile(self,fn='HERA_350.txt'):
        fp = open(fn,'w')
        for i,a in enumerate(self.ants):
            s = "HH%d\t%.2f\t%.2f\n" % (self.stations[i],a[0],a[1])
            fp.write(s)
        fp.close()
        
    def kml(self,filePrefix=None,cofa_zone=34,psc=0.4):
        if filePrefix is None:
            filePrefix = self.arrayFileName.split('.')[0]
        kfn = filePrefix+'.kml'
        print 'Writing '+kfn
        kmlfp = open(kfn,'w')
        gfn = filePrefix+'.gpx'
        gfp = open(gfn,'w')
        print 'Writing '+gfn
    
        kmlfp.write(ge.kmlhdr('HERA',psc))
        gfp.write(ge.garhdr('HERA'))
        for ihc,hc in enumerate(self.ants):
            x = hc[0]
            y = hc[1]
            kmlfp.write(ge.kmlplcmk(str(ihc),x,y,'utm',cofa_zone))
            gfp.write(ge.garwypt(str(ihc),x,y,'utm',cofa_zone))
        kmlfp.write(ge.kmltrlr())
        gfp.write(ge.gartrlr())
        kmlfp.close()
        gfp.close()

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

    def transferAntNumbers(self,unnumberedFile,numberedFile=False,outFile='numbered.txt'):
        """Takes antenna numberings/locations from numberedFile and finds nearest antenna location in unnumberedFile
           Write new file with numberings and locations to outFile (default='numbered.txt')"""
        if not numberedFile:
            numberedFile = self.arrayFileName
        numbered   = np.loadtxt(numberedFile,usecols=(0,1,2))
        unnumbered = np.loadtxt(unnumberedFile,usecols=(0,1))
        orderedNumbers = []
        for unloc in unnumbered:
            dmin = 1.0E6
            nearest = -1
            for loc in numbered:
                d = math.sqrt( (loc[1] - unloc[0])**2 + (loc[2]-unloc[1])**2 )
                if d < dmin:
                    dmin = d
                    nearest=int(loc[0])
            orderedNumbers.append(nearest)
        i=0
        fpIn = open(unnumberedFile,'r')
        fpOut = open(outFile,'w')
        for line in fpIn:
            s = '%3s  %s' % (str(orderedNumbers[i]),line)
            i+=1
            fpOut.write(s)
        fpIn.close()
        fpOut.close()
        return

    def remove(self,arr,instruct=None):
        """Removes arr values (ants, poles, posts) from self.ants, poles, posts
        and stores in dants, dpoles and dposts"""
        dants = []
        dpoles = []
        dposts = []
        for a1 in self.ants:
            in2 = False
            for a2 in arr.ants:
                if self._close(a1,a2,0.1):
                    in2 = True
                    break
            if not in2:
                dants.append(a1)
        for p1 in self.poles:
            in2 = False
            for p2 in arr.poles:
                if self._close(p1,p2,0.1):
                    in2 = True
                    break
            if not in2:
                dpoles.append(p1)
        for p1 in self.posts:
            in2 = False
            for p2 in arr.posts:
                if self._close(p1,p2,0.1):
                    in2 = True
                    break
            if not in2:
                dposts.append(p1)
        self.dants = np.array(dants)
        self.dpoles = np.array(dpoles)
        self.dposts = np.array(dposts)
        print '\nSubtracting %d from %d.  Need the following:' % (len(arr.stations),len(self.stations))
        print '\t'+str(len(self.dants))+' more antennas (dants)'
        print '\t'+str(len(self.dpoles))+' more poles (dpoles)'
        print '\t'+str(len(self.dposts))+' more posts (dposts)'

        if instruct=='plotit':
            plt.figure('subtracted')
            plt.plot(self.dants[:,0],self.dants[:,1],'wo',markersize=11)
            plt.plot(self.dpoles[:,0],self.dpoles[:,1],'o')
            plt.plot(self.dposts[:,0],self.dposts[:,1],'x')
            plt.axis('image')


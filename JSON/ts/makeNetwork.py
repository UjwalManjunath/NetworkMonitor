import sys, random, operator
from device import Device
from location import Location

args = sys.argv

NumOffices = int(args[1])
NumDataCenters = int(args[2])
NumComputers = int(args[3])
outFile = args[4]

with open("citynames.txt", "r") as f:
	cityNames = f.readlines()

with open("computerlocations.txt", "r") as f:
	computerLocations = f.readlines()

with open("networklocations.txt", "r") as f:
	networkLocations = f.readlines()

sites = []


print "Building a network with " +str(NumComputers)+ " computers, across " +str(NumOffices)+ " offices and " +str(NumDataCenters)+ " data centers and HQ." 

print "Creating HQ"
sites.append(Location("HQ",NumComputers));

print "Creating data centers"
dataCenters = []
options = list(cityNames)

random.shuffle(options)
while(len(dataCenters) < NumDataCenters):
	nc = sites[0].numComputers/3
	sites[0].numComputers -= nc
	dc = options.pop().strip()
	print "New Data Center in "+str(dc)+" created."
	dataCenters.append(dc)
	sites.append(Location(dc+" Data Center",nc))
	sites.sort(key=operator.attrgetter('numComputers'), reverse = True)

print "Creating offices" 
offices= []
options = list(cityNames)

random.shuffle(options)
while(len(offices) < NumOffices):
	nc = sites[0].numComputers/3
	sites[0].numComputers -= nc
	o = options.pop().strip()
	print "New Office in "+str(o)+" created."
	offices.append(o)
	sites.append(Location(o+ " Office",nc))
	sites.sort(key=operator.attrgetter('numComputers'), reverse = True)

print "Building Site topology"

master_id = 0

for s in sites:
	for i in range(0, s.numComputers):
		master_id += 1
		c = Device("Computer",master_id, 1)
		if(s.activeSwitch == None):
			master_id += 1
			sw = Device("Switch",master_id, 38)
			if(s.activeRouter == None):
				master_id += 1
				ar = Device("Router",master_id, 10)
				s.routers.append(ar)
				s.activeRouter = ar
				master_id += 1
				br = Device("Router",master_id, 10)
				s.routers.append(br)
				s.backupRouter = br
			sw.addConnection(s.activeRouter.id)
			s.activeRouter.numPorts -= 1
			sw.addConnection(s.backupRouter.id)
			s.backupRouter.numPorts -= 1
			if(s.activeRouter.numPorts == 0):
				s.activeRouter = None
				s.backupRouter = None
			s.switches.append(sw)
			s.activeSwitch = sw
		c.addConnection(s.activeSwitch.id)
		s.activeSwitch.numPorts -= 1
		if(s.activeSwitch.numPorts == 0):
			s.activeSwitch = None
		s.computers.append(c)

print "Building Core Routing"
for s in sites:
	numCore = len(s.routers)/8 + 1
	for i in range(0, numCore*2):
		master_id += 1
		cr = Device("Router",master_id,0)
		s.core.append(cr)
	for ri,r in enumerate(s.routers):
		r.addConnection(s.core[(ri/8)+(ri%2)].id)
	for cri,cr in enumerate(s.core):
		if(len(s.core) > cri+2):
			cr.addConnection(s.core[cri+2].id)
		elif(cri>1):
			cr.addConnection(s.core[cri%2].id)
if(len(sites)==2):
	lcr = random.randint(0,len(sites[0].core)-1)
	rcr = random.randint(0,len(sites[1].core)-1)
	sites[0].core[lcr].addConnection(sites[1].core[rcr].id)
elif(len(sites)>2):
	min = len(sites)-1
	max = 2*len(sites)


def printComputer(d,s,f,cv):
	f.write('{"id":'+str(d.id)+',"type":"'+d.type+'","location":"'+s.location+'","locationDetail":"'+random.choice(computerLocations).strip()+'","criticalness":'+str(cv)+'}')
def printNetworkDevice(d,s,f,cv):
	f.write('{"id":'+str(d.id)+',"type":"'+d.type+'","location":"'+s.location+'","locationDetail":"'+random.choice(networkLocations).strip()+'","criticalness":'+str(cv)+'}')
def printConnection(s,t,f,bw,cv):
	f.write('{"devicePair":['+str(s)+','+str(t)+'],"bandwidth":'+str(bw)+',"criticalness":'+str(cv)+'}')

f = open(outFile, 'w')
f.write('{"devices":[')
firstPrint = True
for s in sites:
	if s.computers:
		for c in s.computers:
			if(firstPrint == True):
				firstPrint = False
			else:
				f.write(',')
			cv = random.randint(4,5)
			printComputer(c,s,f,cv)
	if s.switches:
		for sw in s.switches:
			if(firstPrint == True):
				firstPrint = False
			else:
				f.write(',')
			cv = random.randint(3,4)
			printNetworkDevice(sw,s,f,cv)
	if s.routers:
		for r in s.routers:
			if(firstPrint == True):
				firstPrint = False
			else:
				f.write(',')
			cv = random.randint(2,3)
			printNetworkDevice(r,s,f,cv)
	if s.core:
		for cr in s.core:
			if(firstPrint == True):
				firstPrint = False
			else:
				f.write(',')
			cv = random.randint(1,2)
			printNetworkDevice(cr,s,f,cv)
f.write(']')
firstPrint = True
f.write(',"connections":[')
for s in sites:
	if s.computers:
		for c in s.computers:
			if c.ports:
				for p in c.ports:
					if(firstPrint == True):
						firstPrint = False
					else:
						f.write(',')
					cv = random.randint(4,5)
					printConnection(c.id,p,f,1000000,cv)
	if s.switches:
		for sw in s.switches:
			if sw.ports:	
				for p in sw.ports:
					if(firstPrint == True):
						firstPrint = False
					else:
						f.write(',')
					cv = random.randint(3,4)
					printConnection(sw.id,p,f,100000000,cv)
	if s.routers:	
		for r in s.routers:
			if r.ports:
				for p in r.ports:
					if(firstPrint == True):
						firstPrint = False
					else:
						f.write(',')
					cv = random.randint(2,3)
					printConnection(r.id,p,f,1000000000,cv)
	if s.core:	
		for cr in s.core:
			if cr.ports:
				for p in cr.ports:
					if(firstPrint == True):
						firstPrint = False
					else:
						f.write(',')
					cv = random.randint(1,2)
					printConnection(cr.id,p,f,1000000000,cv)
f.write(']}')
f.close()

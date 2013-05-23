class Location:
	def __init__(self, name, numComputers):
		self.location = name
		self.numComputers = numComputers	
		self.computers = []
		self.switches = []
		self.routers = []
		self.core = []
		self.activeSwitch = None
		self.activeRouter = None
		self.backupRouter = None
		self.activeCore = None

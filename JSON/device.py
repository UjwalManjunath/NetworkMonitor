class Device:
	def __init__(self, type, id, numPorts):
		self.type = type
		self.id = id
		self.numPorts = numPorts
		self.ports = []
	
	def addConnection(self, id):
		self.ports.append(id)

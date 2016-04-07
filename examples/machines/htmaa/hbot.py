# Hbot virtual machine file
# Can be used with core xy or hbot stages
# nadya peek 2016

#------IMPORTS-------
from pygestalt import nodes
from pygestalt import interfaces
from pygestalt import machines
from pygestalt import functions
from pygestalt.machines import elements
from pygestalt.machines import kinematics
from pygestalt.machines import state
from pygestalt.utilities import notice
from pygestalt.publish import rpc	#remote procedure call dispatcher
import time
import io


#------VIRTUAL MACHINE------
class virtualMachine(machines.virtualMachine):
	
	def initInterfaces(self):
		if self.providedInterface: self.fabnet = self.providedInterface		#providedInterface is defined in the virtualMachine class.
		else: self.fabnet = interfaces.gestaltInterface('FABNET', interfaces.serialInterface(baudRate = 115200, interfaceType = 'ftdi', portName = '/dev/ttyUSB0'))
		
	def initControllers(self):
		print "init controllers, x and y"
		self.xAxisNode = nodes.networkedGestaltNode('A axis', self.fabnet, filename = '086-005a.py', persistence = self.persistence)
		self.yAxisNode = nodes.networkedGestaltNode('B axis', self.fabnet, filename = '086-005a.py', persistence = self.persistence)
		self.xyNode = nodes.compoundNode(self.xAxisNode, self.yAxisNode)


	def initCoordinates(self):
		self.position = state.coordinate(['mm', 'mm'])
	
	def initKinematics(self):
    		# drive components of h-bot. Inputs are A/B stepper motors, outputs are X/Y in machine coordinates.
    		# elements.elementChain.forward(
        	# microstep => input microstepcount -> 1/microstepCount -> steps 
        	# stepper =>   input stepAngle (degrees) -> stepAngle/360 -> revolutions
        	# pulley =>    input pitchDiameter (mm)
        	# invert =>    if it is inputted backwards. false = its correct connection])
    		self.xAxis = elements.elementChain.forward([elements.microstep.forward(1), elements.stepper.forward(1.8), elements.pulley.forward(2.03), elements.invert.forward(False)])
    		self.yAxis = elements.elementChain.forward([elements.microstep.forward(1), elements.stepper.forward(1.8), elements.pulley.forward(2.03), elements.invert.forward(False)])

    		# define an H-BOT configuration
    		self.stageKinematics = kinematics.hbot()        # add invertX = True, invertY = True if needed
	
	def initFunctions(self):
		self.move = functions.move(virtualMachine = self, virtualNode = self.xyNode, axes = [self.xAxis, self.yAxis], kinematics = self.stageKinematics, machinePosition = self.position,planner = 'null')
		self.jog = functions.jog(self.move)	#an incremental wrapper for the move function
		pass
		
	def initLast(self):
		#self.machineControl.setMotorCurrents(aCurrent = 0.8, bCurrent = 0.8, cCurrent = 0.8)
		#self.xNode.setVelocityRequest(0)	#clear velocity on nodes. Eventually this will be put in the motion planner on initialization to match state.
		pass
	
	def publish(self):
		#self.publisher.addNodes(self.machineControl)
		pass
	
	def getPosition(self):
		return {'position':self.position.future()}
	
	def setPosition(self, position  = [None]):
		self.position.future.set(position)

	def setSpindleSpeed(self, speedFraction):
		#self.machineControl.pwmRequest(speedFraction)
		pass

#------IF RUN DIRECTLY FROM TERMINAL------
if __name__ == '__main__':
	# The persistence file remembers the node you set. It'll generate the first time you run the
	# file. If you are hooking up a new node, delete the previous persistence file.
	stages = virtualMachine(persistenceFile = "test.vmp")

	# You can load a new program onto the nodes if you are so inclined. This is currently set to 
	# the path to the 086-005 repository on Nadya's machine. 
	#stages.xyNode.loadProgram('../../../086-005/086-005a.hex')
	
	# This is a widget for setting the potentiometer to set the motor current limit on the nodes.
	# The A4982 has max 2A of current, running the widget will interactively help you set. 
	#stages.xyNode.setMotorCurrent(0.7)

	# This is for how fast the 
	stages.xyNode.setVelocityRequest(2)	
	
	# Some random moves to test with
	moves = [[10,10],[0,0]]
	
	# Move!
	for move in moves:
		stages.move(move, 0)
		status = stages.xAxisNode.spinStatusRequest()
		# This checks to see if the move is done.
		while status['stepsRemaining'] > 0:
			time.sleep(0.001)
			status = stages.xAxisNode.spinStatusRequest()	
	



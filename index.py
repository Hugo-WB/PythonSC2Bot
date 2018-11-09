import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import NEXUS,PROBE,PYLON, ASSIMILATOR, CYBERNETICSCORE, ROBOTICSBAY, ROBOTICSFACILITY,STARGATE,FLEETBEACON,TWILIGHTCOUNCIL,GATEWAY
from sc2.constants import *
print("hi")
global tech
global nexuses
global cheese
global pylon
#gateway:1 cyber:2 twilight/robot/stargate:3 roboBay/fleetBeacon:4
class WorkerRushBot(sc2.BotAI):
	buildLocation=None
	blink = False
	async def on_step(self, iteration):
		# print("                             ",self.supply_used/self.workers.amount)
		tech = await self.techCheck()
		nexuses = self.units(NEXUS).ready
		cheese = False
		techChoice = TWILIGHTCOUNCIL
		techChoice2 = ROBOTICSBAY
		await self.distribute_workers()
		await self.build_workers()
		await self.buildPylon()
		await self.techCheck()
		await self.upgrade(tech)
		await self.techUp(tech,techChoice,techChoice2)
		await self.expand(tech)
		await self.getGas(tech,nexuses)
		await self.getProduction(tech,techChoice,techChoice2)
		await self.buildArmy(tech,techChoice,techChoice2)
		await self.researchUpgrades(tech,techChoice,techChoice2)
		await self.findPosition()
	async def build_workers(self):
		for nexus in self.units(NEXUS).ready.noqueue:
			if self.can_afford(PROBE) and self.units(PROBE).amount < 70 and self.units(PROBE).amount<(self.units(NEXUS).amount*24):
				await self.do(nexus.train(PROBE))
				print("Worker")

	async def buildPylon(self):
		if (self.supply_left/self.supply_used)<0.2 and not self.already_pending(PYLON):
			nexuses = self.units(NEXUS).ready
			if nexuses.exists:
				if self.can_afford(PYLON):
					await self.build(PYLON, near=self.buildLocation)
					print("Building Pylon")

	async def expand(self,tech):
		if self.can_afford(NEXUS) and (self.units(PROBE).amount)/(self.units(NEXUS).ready.amount)>16 and self.units(NEXUS).amount < 3 and not self.already_pending(NEXUS):
				await self.expand_now()
				print("tech:",tech)
	async def techCheck(self):
		if (self.units(ROBOTICSBAY).amount >0 or self.units(FLEETBEACON).amount >0):
			# print("tech = 5")
			return 4
		elif ((self.units(ROBOTICSFACILITY).amount > 0) or (self.units(STARGATE).amount >0) or (self.units(TWILIGHTCOUNCIL).amount>0)):
			# print("tech =3")
			return 3
		elif self.units(CYBERNETICSCORE).amount >0:
			# print("tech =2 ")
			return 2
		elif self.units(GATEWAY).amount>0:
			# print("tech = 1")
			return 1
		else:
			return 0
		
		
		
	async def upgrade(self,tech):
		if self.units(FORGE).amount < 0 and tech >2 and self.can_afford(FORGE):
			pylon = self.units(PYLON).ready.random
			await self.build(FORGE, near=pylon)
		# elif tech >2 and self.can_afford()
	
	async def techUp(self,tech,techChoice,techChoice2):
		if self.units(PYLON).ready.exists:
			pylon = self.units(PYLON).ready.random
			if tech == 0 and self.can_afford(GATEWAY):
				print("current tech is:",tech)
				await self.build(GATEWAY, near=pylon)
				tech = 1
				print("tech =1, gateway on way	")
			if tech == 1 and self.can_afford(CYBERNETICSCORE):
				await self.build(CYBERNETICSCORE, near=pylon)
				print("Tech = 2, cyber core on way")
				tech = 2
			if tech == 2 and self.can_afford(techChoice):
				await self.build(techChoice, near=pylon)
				print("Tech = 3, ",techChoice,"is on the way")
				tech = 3
			if tech == 4 and self.can_afford(techChoice2) and self.supply_used>170:
				await self.build(techChoice2, near=pylon)
				print("tech = 4,",techChoice2,"is on the way")

	async def buildArmy(self,tech,techChoice,techChoice2):
		gateways = self.units(GATEWAY)
		wrokerToArmyRatio =(self.supply_used-self.workers.amount)/self.workers.amount
		for gw in gateways:
			if (self.can_afford(STALKER) and self.units(CYBERNETICSCORE).amount > 0) and ((self.workers.amount<35 and wrokerToArmyRatio<0.3) or (34<self.workers.amount<60 and wrokerToArmyRatio<0.4) or (self.workers.amount>59)) and (gw.noqueue):
				print("Stalker!!!")
				await self.do(gw.train(STALKER))

	async def getGas(self,tech,nexuses):
		gas = 0
		if tech ==0:
			pass
		elif tech == 1:
			gas = 1 * self.units(NEXUS).ready.amount
		elif tech == 2:
			gas = 1.5 * self.units(NEXUS).ready.amount
		elif tech >=3:
			gas = 2 * self.units(NEXUS).ready.amount
		while self.units(ASSIMILATOR).amount<gas:
			if not self.can_afford(ASSIMILATOR):
				break
			
			geyser = self.state.vespene_geyser.closer_than(25.0, nexuses.random).random
			worker = self.select_build_worker(geyser.position,force = True)
			await self.do(worker.build(ASSIMILATOR,geyser))
	async def getProduction(self,tech,techChoice,techChoice2):
		totalProduction = self.units(GATEWAY).amount+self.units(ROBOTICSFACILITY).amount+self.units(STARGATE).amount
		if (totalProduction/self.units(NEXUS).amount)<3 and tech >= 2:
			pylon = self.units(PYLON).ready.random
			if (self.units(GATEWAY).amount/self.units(NEXUS).amount)<=2 and tech ==2 and self.can_afford(GATEWAY):
				await self.build(GATEWAY, near=pylon)
			if tech ==3 and techChoice == TWILIGHTCOUNCIL and (self.units(GATEWAY).amount/self.units(NEXUS).amount)<3 and self.can_afford(GATEWAY):
				await self.build(GATEWAY, near=pylon)
			elif tech ==3 and (self.units(techChoice).amount/self.units(NEXUS).amount)<=1 and self.can_afford(techChoice):
				await self.build(techChoice,near=pylon)
		else:
			pass

	async def researchUpgrades(self,tech,techChoice,techChoice2):
		twilight = self.units(TWILIGHTCOUNCIL).ready
		print(twilight)
		if twilight.amount>0 and self.can_afford(RESEARCH_BLINK) and twilight.noqueue and self.blink == False:
			await self.do(twilight(RESEARCH_BLINK))
			self.blink = True

	async def findPosition(self):
		target = self.start_location
		approach_from = self.enemy_start_locations[0]
		self.buildLocation = target.towards(approach_from,8)

run_game(maps.get("(2)CatalystLE"), [
	Bot(Race.Protoss, WorkerRushBot()),
	Computer(Race.Random, Difficulty.Easy)
], realtime=False)

	
from functions import get_rID, get_directions, get_time, get_oven, get_stove
import copy

min_time = str("inf")
Best = None

class Direction():
	def __init__(self,dictionary):
		self.text = dictionary['text']
		self.time = dictionary['time']
		self.oven = dictionary['oven']
		self.stove = dictionary['stove']
		self.start = dictionary['start']
		self.end = dictionary['end']
		self.scheduled = dictionary['scheduled']
	def set_end_time(self, end_time):
		self.end = end_time
		self.start = self.end - self.time
		self.scheduled = True
	def export(self):
		dictionary = {
			'text': self.text,
			'time': self.time,
			'oven': self.oven,
			'stove': self.stove,
			'start': self.start,
			'end': self.end,
			'scheduled': self.scheduled
		}
		return dictionary

class DirectionCreator():
	def create_direction(self,text,time,oven,stove):
		dictionary = {}
		dictionary['text'] = text
		dictionary['time'] = time
		dictionary['oven'] = oven
		dictionary['stove'] = stove
		dictionary['start'] = 0
		dictionary['end'] = 0
		dictionary['scheduled'] = False
		return Direction(dictionary)

class Recipe():
	def __init__(self,dictionary):
		self.rID = dictionary['rID']
		self.directions = [Direction(d) for d in dictionary['directions']]
	def earliest_stove(self):
		return_time = 0
		for direction in self.directions:
			if direction.stove:
				return_time = min(return_time, direction.start)
		return return_time
	def earliest_oven(self):
		return_time = 0
		for direction in self.directions:
			if direction.stove:
				return_time = min(return_time, direction.start)
		return return_time
	def last_unscheduled(self):
		for i in xrange(len(self.directions) - 1, -1, -1):
			if not self.directions[i].scheduled:
				return self.directions[i]
		return None
	def first_scheduled(self):
		for direction in self.directions:
			if direction.scheduled:
				return direction
		return None
	def export(self):
		dictionary = {
			'rID': self.rID,
			'directions': [direction.export() for direction in self.directions],
		}
		return dictionary

class RecipeCreator():
	def create_recipe(self, url):
		dictionary = {}
		dictionary['rID'] = get_rID(url)
		direx = get_directions(url)
		dictionary['directions'] = []
		for d in direx:
			dictionary['directions'].append(
				DirectionCreator().create_direction(d, get_time(d), get_oven(d), get_stove(d)).export()
				)
		return Recipe(dictionary)

class Schedule():
	def __init__(self, dictionary):
		self.recipes = [Recipe(recipe_dictionary) for recipe_dictionary in dictionary['recipes']]
		self.stoves = dictionary['stoves']
		self.ovens = dictionary['ovens']
	def set(self, dictionary):
		self.recipes = [Recipe(recipe_dictionary) for recipe_dictionary in dictionary['recipes']]
		self.stoves = dictionary['stoves']
		self.ovens = dictionary['ovens']
	def push_down(self,recipe):
		if recipe.first_scheduled():
			end_time = recipe.first_scheduled().start
		else:
			end_time = 0
		if recipe.last_unscheduled():
			if recipe.last_unscheduled().stove and len(self.recipes)>self.stoves:
				last_stove_times = []
				for neighbor in self.recipes:
					if neighbor != recipe:
						last_stove_times.append(neighbor.earliest_stove())
				last_stove_times.sort()
				try:
					end_time = min(end_time, last_stove_times[self.stoves - 1])
				except KeyError, IndexError:
					pass
			if recipe.last_unscheduled().oven and len(self.recipes)>self.ovens:
				last_oven_times = []
				for neighbor in self.recipes:
					if neighbor != recipe:
						last_oven_times.append(neighbor.earliest_oven())
				last_oven_times.sort()
				try:
					end_time = min(end_time, last_oven_times[self.ovens - 1])
				except KeyError, IndexError:
					pass
			recipe.last_unscheduled().set_end_time(end_time)
	def unoptimized_recipes(self):
		unoptimized_recipes = []
		for recipe in self.recipes:
			if recipe.last_unscheduled():
				unoptimized_recipes.append(recipe)
		return unoptimized_recipes
	def conflict(self,argv):
		oven_recipes = []
		stove_recipes = []
		for recipe in argv:
			if recipe.last_unscheduled():
				if recipe.last_unscheduled().stove:
					stove_recipes.append(recipe)
				if recipe.last_unscheduled().oven:
					oven_recipes.append(recipe)
		if len(oven_recipes) > self.ovens:
			return oven_recipes
		elif len(stove_recipes) > self.stoves:
			return stove_recipes
		else:
			return None
	def total_time(self):
		ret_val = 0
		if self.unoptimized_recipes():
			return str("inf") 
		for recipe in self.recipes:
			ret_val = min(ret_val, recipe.directions[0].start)
		return ret_val
	def optimize(self):
		while self.unoptimized_recipes():
			if self.conflict(self.unoptimized_recipes()):
				best_time = str('inf')
				for recipe in self.conflict(self.unoptimized_recipes()):
					rID = recipe.rID
					A = Schedule(self.export())
					for rec in A.recipes:
						if rec.rID == rID:
							A.push_down(rec)
					test_time, export = A.optimize()
					if test_time < best_time:
						best_time = test_time
						best_export = export
					self.set(best_export)
			else:
				for recipe in self.unoptimized_recipes():
					self.push_down(recipe)
				best_time = self.total_time
		if not 'best_time' in locals():
			best_time = self.total_time()
		return [best_time, self.export()]
	def export(self):
		dictionary = {
			'stoves': self.stoves,
			'ovens': self.ovens,
			'recipes': [recipe.export() for recipe in self.recipes]
		}
		return dictionary

class ScheduleCreator():
	def create_schedule(self, stoves, ovens, *argv):
		dictionary = {}
		dictionary['stoves'] = stoves
		dictionary['ovens'] = ovens
		dictionary['recipes'] = []
		for url in argv:
			dictionary['recipes'].append(
				RecipeCreator().create_recipe(url).export()
				)
		self.S = Schedule(dictionary)
		self.S.optimize()
import urllib2
from bs4 import BeautifulSoup
import string
import copy

def get_rID(url):
	url = url.lower()
	start_index = url.find('allrecipes.com/recipe')
	rID = url[start_index + len('allrecipes.com/recipe') + 1:]
	end_index = rID.find('/')
	if end_index != -1:
		rID = rID[:end_index]
	return rID

def get_soup(url):
	response = urllib2.urlopen(url)
	html = response.read()
	soup = BeautifulSoup(html)
	return soup

def get_directions(rID):
	url = 'http://allrecipes.com/recipe/' + rID
	soup = get_soup(url)
	directions = soup.find('div',{"class": "directions"}).find_all('li')
	for i, direction in enumerate(directions):
		directions[i] = direction.string
	return directions

def get_time(direction):
	default_time = 3
	time_in_minutes = 0
	exclude = set([a+' ' for a in set(string.punctuation)])
	direction = list(direction)
	for i in xrange(len(direction) - 1):
		if direction[i]+direction[i+1] in exclude:
			direction[i]=' '
	direction = ''.join(direction)
	# check last charater
	if direction[-1] in string.punctuation:
		direction = direction[:-1]
	direction = direction.lower().split()
	minute_keyword = ['minutes','minute','min','mins']
	for keyword in minute_keyword:
		while (keyword in direction):
			index = direction.index(keyword)
			try:
				time_in_minutes += int(direction[index - 1])
			except ValueError:
				time_in_minutes += default_time
			del direction[index]
	hour_keyword = ['hours','hour','hr','hrs']
	for keyword in minute_keyword:
		while (keyword in direction):
			index = direction.index(keyword)
			try:
				time_in_minutes += 60 * int(direction[index - 1])
			except ValueError:
				time_in_minutes += 60
			del direction[index]	
	return time_in_minutes or default_time

def get_oven(direction):
	exclude = string.punctuation
	direction = ''.join([ch for ch in direction if ch not in exclude])
	direction = direction.lower().split()
	oven_keyword = ['oven', 'ovens', 'broil', 'broiler', 'preheat']
	for keyword in oven_keyword:
		if (keyword in direction):
			return True
	return False

def get_stove(direction):
	exclude = string.punctuation
	direction = ''.join([ch for ch in direction if ch not in exclude])
	direction = direction.lower().split()
	stove_keyword = ['stove', 'stoves', 'boil', 'sear', 'pan', 'skillet', 'simmer', 'cook']
	for keyword in stove_keyword:
		if (keyword in direction):
			return True
	return False

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
	def __str__(self):
		return 'start: ' + str(self.start) + ' end: ' + str(self.end)
	def dict(self):
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

class DirectionHelper():
	def create_direction(self,text,time,oven,stove):
		dictionary = {}
		dictionary['text'] = text
		dictionary['time'] = time
		dictionary['oven'] = oven
		dictionary['stove'] = stove
		dictionary['start'] = 0
		dictionary['end'] = 0
		dictionary['scheduled'] = False
		self.direction = Direction(dictionary)
		return self

class Recipe():
	def __init__(self, dictionary):
		self.rID = dictionary['rID']
		directions = dictionary['directions']
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
	def __str__(self):
		return self.rID + ' '.join([str(direction) for direction in self.directions])
	def dict(self):
		dictionary = {
			'rID': self.rID,
			'directions': [direction.dict() for direction in self.directions],
		}
		return dictionary	

class RecipeHelper():
	def create_recipe(self, url):
		dictionary = {}
		dictionary['rID'] = get_rID(url)
		directions = get_directions(dictionary['rID'])
		dictionary['directions'] = []
		for direct in directions:
			dictionary['directions'].append(DirectionHelper().create_direction(direct,get_time(direct),
				get_oven(direct),get_stove(direct)).direction)
		self.recipe = Recipe(dictionary)
		return self

class Schedule():
	def __init__(self, dictionary):
		self.recipes = dictionary['recipes']
		self.stoves = dictionary['stoves']
		self.ovens = dictionary['ovens']
		self.optimize()
	def push_down(self,recipe):
		if recipe.first_scheduled():
			end_time = recipe.first_scheduled().start
		else:
			end_time = 0
		if recipe.last_unscheduled():
			if recipe.last_unscheduled().stove:
				last_stove_times = []
				for neighbor in self.recipes:
					if neighbor != recipe:
						last_stove_times.append(neighbor.earliest_stove())
				last_stove_times.sort()
				try:
					end_time = min(end_time, last_stove_times[self.stoves - 1])
				except KeyError:
					pass
			if recipe.last_unscheduled().oven:
				last_oven_times = []
				for neighbor in self.recipes:
					if neighbor != recipe:
						last_oven_times.append(neighbor.earliest_oven())
				last_oven_times.sort()
				try:
					end_time = min(end_time, last_oven_times[self.ovens - 1])
				except KeyError:
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
		for recipe in self.recipes:
			ret_val = min(ret_val, recipe.directions[0].start)
		return ret_val
	def optimize(self):
		while self.unoptimized_recipes():
			if not self.conflict(self.unoptimized_recipes()):
				for recipe in self.unoptimized_recipes():
					print str(self)
					self.push_down(recipe)
			else: #conflict
				min_time = str("inf")
				for recipe in self.conflict(self.unoptimized_recipes()):
					A_dictionary = copy.copy({
						'stoves': self.stoves,
						'ovens': self.ovens,
						'recipes': self.recipes,
						})
					A = Schedule(A_dictionary)
					A.push_down(recipe)
					A.optimize()
					if A.total_time < min_time:
						Best = copy.copy({
						'stoves': A.stoves,
						'ovens': A.ovens,
						'recipes': A.recipes,
						})
						min_time = A.total_time()
				self = copy.copy(Schedule(Best))
				break
	def dict(self):
		dictionary = {
			'stoves': self.stoves,
			'ovens': self.ovens,
			'recipes': [recipe.dict() for recipe in recipes],
		}
		return dictionary

	def __repr__(self):
		return "Schedule()"
	def __str__(self):
		return ' '.join([str(recipe) for recipe in self.recipes])

class ScheduleHelper():
	def create_schedule(self, stoves, ovens, *argv):
		dictionary = {}
		dictionary['stoves'] = stoves
		dictionary['ovens'] = ovens
		dictionary['recipes'] = []
		for url in argv:
			dictionary['recipes'].append(RecipeHelper().create_recipe(url).recipe)
		print dictionary
		self.schedule = Schedule(dictionary)

###
# Testing
###

A = ScheduleHelper()
A.create_schedule(1,1,'http://allrecipes.com/Recipe/Easy-Chicken-Pasta/Detail.aspx?prop24=RD_RelatedRecipes','http://allrecipes.com/Recipe/Steak-Soup/Detail.aspx?event8=1&prop24=SR_Thumb&e11=steak&e8=Quick%20Search&event10=1&e7=Recipe&soid=sr_results_p1i2')







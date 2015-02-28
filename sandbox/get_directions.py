import urllib2
from bs4 import BeautifulSoup
import string

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
	def __init__(self,text,time,oven,stove):
		self.text = text
		self.time = time
		self.oven = oven
		self.stove = stove
		self.start = 0
		self.end = 0
		self.scheduled = False

class Recipe():
	def __init__(self, url):
		self.rID = get_rID(url)
		directions = get_directions(self.rID)
		self.directions = []
		for direction in directions:
			self.directions.append(Direction(direction,get_time(direction),
				get_oven(direction),get_stove(direction)))
	def earliest_stove(self):
		return_time = float("inf")
		for direction in self.directions:
			if direction.stove:
				return_time = min(return_time, direction.start)
		return return_time
	def earliest_oven(self):
		return_time = float("inf")
		for direction in self.directions:
			if direction.stove:
				return_time = min(return_time, direction.start)
		return return_time
	def last_unscheduled(self):
		for i in xrange(len(self.directions) - 1, -1, -1):
			if not self.directions[i].scheduled:
				return self.directions[i]

class Schedule():
	def __init__(self, *argv):
		self.recipes = []
		for url in argv:
			self.recipes.append(Recipe(url))
		self.optimize_time()
	# def optimize_time(self):
	# 	while r_1.last_unscheduled and r_2.last_unscheduled:
	# 		if (r_1.last_unscheduled.oven and r_2.last_unscheduled.oven) or (r_1.last_unscheduled.stove and r_2.last_unscheduled.stove):
	# 			# conflict
	# 		else:
				

###
# Testing
###

url = 'http://allrecipes.com/Recipe/Easy-Chicken-Pasta/Detail.aspx?prop24=RD_RelatedRecipes'
url2 = 'http://allrecipes.com/Recipe/Steak-Soup/Detail.aspx?event8=1&prop24=SR_Thumb&e11=steak&e8=Quick%20Search&event10=1&e7=Recipe&soid=sr_results_p1i2'

r_1 = Recipe(url)
r_2 = Recipe(url2)

# for i, direction in enumerate(r_1.directions):
# 	print "%s: %s Stove: %s, Oven: %s, Time: %s" %(i,direction.text,direction.stove,direction.oven,direction.time)
# print r_1.earliest_oven()
# print r_1.earliest_stove()
# print r_1.last_unscheduled().text


def get_rID(url):
	url = url.lower()
	start_index = url.find('allrecipes.com/recipe')
	rID = url[start_index + len('allrecipes.com/recipe') + 1:]
	end_index = rID.find('/')
	if end_index != -1:
		rID = rID[:end_index]
	return rID

import urllib2
from bs4 import BeautifulSoup

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

import string

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

class Directions():
	def __init__(self, url):
		self.rID = get_rID(url)
		directions = get_directions(self.rID)
		self.directions = []
		for direction in directions:
			self.directions.append(Direction(direction,get_time(direction),
				get_oven(direction),get_stove(direction)))






import sys
import re
from collections import defaultdict
from math import sqrt
from random import randint

HEIGHT = WIDTH = T = 0
poz_i = poz_f = (0,0)
portals = {}
labyrinth = None
count = 0
visited_Portals = {}

def readInputs(file_name):
	global labyrinth, HEIGHT, WIDTH, T, poz_i, poz_f

	file = open(file_name, "r")
	line = re.split(' |\n',file.readline())
	HEIGHT = int(line[0])
	WIDTH = int(line[1])
	T = int(line[2])

	line = re.split(' |\n',file.readline())
	poz_i = (int(line[1]), int(line[0]))

	line = re.split(' |\n',file.readline())
	poz_f = (int(line[1]), int(line[0]))

	for poarta in range(T):
		line = re.split(' |\n',file.readline())
		poarta_crt = (int(line[1]),int(line[0]))
		no_destinatii = int(line[2])
		destinatii = []

		for i in range(1,no_destinatii+1):
			dest_crt = ((int(line[3*i+1]), int(line[3*i])), float(line[3*i+2]))
			destinatii.append(dest_crt)

		portals[poarta_crt] = destinatii

	# initialize labyrinth
	labyrinth = [[0 for c in range(WIDTH)] for r in range(HEIGHT)]
	for i in range(HEIGHT):
		line = file.readline()
		for cell in range(len(line[:-1])):
			if line[cell] == "X":
				labyrinth[i][cell] = 1
	
def euclidean_distance(a, b):
	return sqrt((a[0] - b[0])**2 +(a[1] - b[1])**2)

def manhattan_distance(a, b):
	return abs(b[0] - a[0]) + abs(b[1] - a[1])

def A_star1(start, goal):
	global count

	# list of nodes fully evaluated
	closedSet = []

	# list of nodes not fully evaluated
	openSet = [start]

	# parents list
	parent = {}

	# distance from start to current node
	g = defaultdict(lambda: sys.maxint, {}) # default este infinit
	g[start] = 0

	# f = g + h (h=heuristic)
	f = defaultdict(lambda: sys.maxint, {}) # default este infinit
	f[start] = euclidean_distance(start, goal)

	while openSet != []:
		# current node is the one with biggest value for f
		crtScore = sys.maxint
		current = None
		for node in openSet:
			if crtScore > f[node]:
				crtScore = f[node]
				current = node

		# final node -> reconstruct the path
		if current == goal:
			return reconstruct_path(parent, current)
		else:
			count += 1

		# current node is completely evaluated => remove from openSet and add to closedSet
		openSet.remove(current)
		closedSet.append(current)

		# get neighbours of current node
		neighbors = getneighbors2(current)
		for neighbor in neighbors:
			# ignore neighmors already explored
			if neighbor in closedSet:
				continue

			# ignore current node if it is a wall
			if is_wall(current):
				continue

			# add the neighbour into the openSet
			if neighbor not in openSet:
				openSet.append(neighbor)
			
			# distance from start node to current node is 1 + distance of previous node
			g_crt = g[current] + 1
			# if the score is not better than previous, go to the next neighbor
			if g_crt >= g[neighbor]:
				continue

			# score is good, we save it
			parent[neighbor] = current
			g[neighbor] = g_crt
			# f = g + h
			f[neighbor] = g[neighbor] + euclidean_distance(neighbor, goal)

	return False

def A_star2(start, goal, debug):
	global count

	# list of nodes fully evaluated
	closedSet = []

	# list of nodes not fully evaluated
	openSet = [start]

	# distance from start to current node
	g = defaultdict(lambda: sys.maxint, {}) # default este infinit
	g[start] = 0

	# f = g + h (h=heuristic)
	f = defaultdict(lambda: sys.maxint, {}) # default este infinit
	f[start] = euclidean_distance(start, goal)

	while openSet != []:
		# current node is the one with biggest value for f
		crtScore = sys.maxint
		current = None
		for node in openSet:
			if crtScore > f[node]:
				crtScore = f[node]
				current = node

		if debug:
			auxx = "--------WALL--------" if is_wall(current) else "--------------------"
			print
			print("------" + str(count) + "----" + str(current) + auxx + str(f[current]) + "------")

		# we found the goal, return the count
		if current == goal:
			return count
		else:
			count += 1

		# current node is completely evaluated => remove from openSet and add to closedSet
		openSet.remove(current)
		closedSet.append(current)

		# ignore current node if it is a wall
		if is_wall(current):
			continue

		# get neighbours of current node
		neighbors = getneighbors(current)

		# current node is a portal -> reset openSet, closeSet, g, f
		if labyrinth[current[0]][current[1]] == 2:
			openSet = [neighbors[0]]
			closedSet = []
			# "current" is the new root -> set g
			aux = g[current]
			g = defaultdict(lambda: sys.maxint, {})
			g[current] = aux
			# set f
			aux = f[current]
			f = defaultdict(lambda: sys.maxint, {})
			f[current] = aux

			if debug:
				print("       ************* " + str(current) + " is portal; openset: " + str(openSet) + "   closedSet: " + str(closedSet) + " *************")
						
		for neighbor in neighbors:
			# ignore neighbor already evaluated
			if neighbor in closedSet:
				continue

			# add neighbor unexplored into openSet
			if neighbor not in openSet:
				openSet.append(neighbor)
			
			# distance from start node to current node is 1 + distance of previous node
			g_crt = g[current] + 1
			# if the score is not better than previous, go to the next neighbor
			if g_crt >= g[neighbor]:
				continue

			# score is good, we save it
			g[neighbor] = g_crt

			# compute heuristic: 
			# 	H_val 			for using portals
			# 	eucledian_val	for normal crossing to the goal
			H_val = H(current, neighbor)
			eucledian_val = euclidean_distance(neighbor, goal)

			# f = g + h    (we choose h with the smallest value)
			if H_val < eucledian_val:
				f[neighbor] = g[neighbor] + H_val
				if debug:
					print("H = " + '%4.3f' % H_val + " < " + '%4.3f' % eucledian_val + " = eucl" + '\t\t\t' + str(neighbor) + "   =>  " + str(f[neighbor]))
			else:
				f[neighbor] = g[neighbor] + eucledian_val
				if debug:
					print("H = " + '%4.3f' % H_val + " > " + '%4.3f' % eucledian_val + " = eucl" + '\t\t\t' + str(neighbor) + "   =>  " + str(f[neighbor]))
	return False

def A_star3(start, goal):
	global count

	# list of nodes fully evaluated
	closedSet = []

	# list of nodes not fully evaluated
	openSet = [start]

	# parents list
	parent = {}

	# distance from start to current node
	g = defaultdict(lambda: sys.maxint, {}) # default is infiny
	g[start] = 0

	# f = g + h (h=heuristic)
	f = defaultdict(lambda: sys.maxint, {}) # default este infiny
	f[start] = euclidean_distance(start, goal)

	while openSet != []:
		# current node is the one with biggest value for f
		crtScore = sys.maxint
		current = None
		for node in openSet:
			if crtScore > f[node]:
				crtScore = f[node]
				current = node

		# final node -> reconstruct the path
		if current == goal:
			return True
		else:
			count += 1

		# current node is completely evaluated => remove from openSet and add to closedSet
		openSet.remove(current)
		closedSet.append(current)

		# get neighbours of current node
		neighbors = getneighbors2(current)
		for neighbor in neighbors:
			# ignore neighmors already explored
			if neighbor in closedSet:
				continue

			# ignore current node if it is a wall
			if is_wall(neighbor):
				continue

			# add the neighbour into the openSet
			if neighbor not in openSet:
				openSet.append(neighbor)
			
			# distance from start node to current node is 1 + distance of previous node
			g_crt = g[current] + 1
			# if the score is not better than previous, go to the next neighbor
			if g_crt >= g[neighbor]:
				continue

			# score is good, we save it
			parent[neighbor] = current
			g[neighbor] = g_crt
			# f = g + h
			f[neighbor] = g[neighbor] + euclidean_distance(neighbor, goal)

	return False

# find the closest portal to a node, using the eucledian distance
def closestPortal(node):
	minDist = sys.maxint
	minDistPortal = None
	for portal in portals:
		crtDist = euclidean_distance(portal,node)
		if crtDist < minDist:
			minDist = crtDist
			minDistPortal = portal

	return minDistPortal

def getNextPortal(node):
	global visited_Portals

	countVisitedPortals = []
	# find the minimum nuber of destinations from portals
	minDestinations = sys.maxint
	for portal in visited_Portals:
		destinations = visited_Portals[portal].keys()
		total = 0
		for dest in destinations:
			total += visited_Portals[portal][dest]
		countVisitedPortals.append((portal,total))
		if total < minDestinations:
			minDestinations = total

	min_distance = sys.maxint
	min_distance_portal = None

	# find in the portals the closest portal from the current point
	#  with the minimum number of visits
	for portal in countVisitedPortals:
		if portal[1] == minDestinations:
			crt_distance = euclidean_distance(node, portal[0])
			if crt_distance < min_distance:
				min_distance = crt_distance
				min_distance_portal = portal[0]
	return min_distance_portal

def exploreMap(maxCount):
	global poz_i, portals, count, visited_Portals
	count = 0
	# visited_Portals === {portal1: {dest1: 2, dest2: 3}, portal2: {dest1: 3, dest2: 5}}...
	visited_Portals = {}
	for portal in portals:
		visited_Portals[portal] = {}

	nextPortal = closestPortal(poz_i)
	poz_crt = poz_i
	while count < maxCount:
		# apply A_star3 to arrive to "nextPortal"
		A_star3(poz_crt, nextPortal)

		# from nextPortal, teleport "random" to a "destination"
		destination = getneighbors(nextPortal)[0] # 
		# increment "destination" in visited_portals list
		if destination in visited_Portals[nextPortal]:
			visited_Portals[nextPortal][destination] += 1
		else:
			visited_Portals[nextPortal][destination] = 1

		# advance the current position
		poz_crt = destination
		# find the next portal: the closest or the one with fewest data
		nextPortal = getNextPortal(destination)

	# compute probabilities for the data found
	newPortals = {}
	for portal in visited_Portals:
		destinatii = visited_Portals[portal]
		sumaDest = 0
		for dest in destinatii:
			sumaDest += destinatii[dest]
		newPortals[portal] = []
		for dest in destinatii:
			newPortals[portal].append((dest,round(1.0 * destinatii[dest] / sumaDest, 3)))

	# save the probabilities with 0 for destinations not already found
	for portal in portals:
		for dest in portals[portal]:
			# if the destination from "portals[portal]" does not exist in newPortals[portal],
			ok = False
			for newPort in newPortals[portal]:
				if newPort[0] == dest[0]:
					ok = True
					break
			# add the destination with cost 0
			if ok == False:
				newPortals[portal].append((dest[0],0))

	# update the portals dictionary with the new values
	portals = newPortals

def H(crt, neighbor):
	global poz_f

	minDist = sys.maxint
	# for each portal, apply the next formula
	# dist = dist(neighbor, portal) + probl_1 * dist(dest1, poz_f)
	# 								+ probl_2 * dist(dest2, poz_f)
	# 								+ ...
	for portal in portals:
		dist_crt = euclidean_distance(neighbor, portal)
		for destL in portals[portal]:
			dest = destL[0]
			prob = destL[1]
			dist_crt += prob * euclidean_distance(dest, poz_f)

		# pick the smallest value
		if dist_crt < minDist:
			minDist = dist_crt

	return minDist

# reconstruct the path from a current node, given its parents
def reconstruct_path(parent, current):
	total_path = [current]
	while current in parent:
		current = parent[current]
		total_path.append(current)
	return total_path

# get a random destination 
def getRandomDest(node):
	global portals

	destinations = []
	
	# save the probabilities of destinations * 100 into a list
	probabilities = []
	for dest in portals[node]:
		probabilities.append(dest[1] * 100)
	
	crt = 0
	# pick a random number between 0 and 100
	random = randint(0, 99)
	for i in range(len(probabilities)):
		# if it is smaller than the first probability, 
		# 	return the first probability
		# 	else, add the current probability and check the next one
		crt += probabilities[i]
		if random < crt:
			return portals[node][i][0]

# check if this node is part of a wall
def is_wall(node):
	global labyrinth
	return labyrinth[node[0]][node[1]] == 1

def getneighbors(node):
	global labyrinth, portals, WIDTH, HEIGHT

	neighbors = []

	# if it is a portal, return a random destination, 
	#	depending on the distribution of probabilities for the destinations
	if labyrinth[node[0]][node[1]] == 2:
		randomDest = getRandomDest(node)
		neighbors.append(randomDest)
		return neighbors

	# add neighbors from within the map to the neighbor list
	if node[1] - 1 >= 0:
		neighbors.append((node[0], node[1] - 1)) #sus
	if node[1] + 1 < WIDTH:
		neighbors.append((node[0], node[1] + 1)) #jos
	if node[0] - 1 >= 0:
		neighbors.append((node[0] - 1, node[1])) #stanga
	if node[0] + 1 < HEIGHT:
		neighbors.append((node[0] + 1, node[1])) #dreapta

	return neighbors

# get the neighbors without using portals
def getneighbors2(node):
	global labyrinth, portals, WIDTH, HEIGHT

	neighbors = []

	# add neighbors from within the map to the neighbor list
	if node[1] - 1 >= 0:
		neighbors.append((node[0], node[1] - 1)) #up
	if node[1] + 1 < WIDTH:
		neighbors.append((node[0], node[1] + 1)) #down
	if node[0] - 1 >= 0:
		neighbors.append((node[0] - 1, node[1])) #left
	if node[0] + 1 < HEIGHT:
		neighbors.append((node[0] + 1, node[1])) #right

	return neighbors

# print the labyrinth to console
def printLabyrinth():
	for row in labyrinth:
		for val in row:
			print '{:2}'.format(val),
		print
	print

# set portals in labyrinth with the given value: "val"
def setPortals(val):
	global portals, labyrinth
	for portal in portals:
		labyrinth[portal[0]][portal[1]] = int(val)

def cerinta1():
	global count
	# deactivate portals (set with "1" in the labyrinth)
	# 	portals not used -> they are considered walls
	setPortals("1")

	count = 0
	# use A* to get the count 
	rezultat = A_star1(poz_i, poz_f)

	return count

def cerinta2():
	global count
	
	# activate portals (set portals with number "2" in labyrinth)
	setPortals("2")

	total = 0
	for i in range(1000):
		count = 0
		# use A* modified to get the total 
		total += A_star2(poz_i, poz_f, False)

	return 1.0 * total / 1000

def cerinta3():
	global portals, poz_f

	# activate portals (set portals with number "2" in labyrinth)
	setPortals("2")

	for maxCount in [100,1000,10000]:
		# explore the map to find probabilities of portal destinations
		exploreMap(maxCount)
		# solve solve non deterministic with the probabilities found
		print("Task 3, N=" + str(maxCount) + ", Average number of actions = " + str(cerinta2()))

def main():
	if (len(sys.argv) < 2):
		print("Trebuie specificat fisierul din care se face citirea labirintului!")
		return

	# read inputs from file received as parameter
	readInputs(sys.argv[1])

	# solve deterministic
	print("Task 1, Average number of actions = " + str(cerinta1()))
	
	# solve non deterministic
	print("Task 2, Average number of actions = " + str(cerinta2()))

	# solve with no previous knowledge
	cerinta3()

if __name__ == "__main__":
	main()
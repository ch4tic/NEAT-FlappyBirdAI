#!/usr/bin/python3 

# importing modules 
import pygame 
import pickle
import os 
import random 
import time 
import neat 

# Author: ch4tic 
# Date: 3.07.2020 

gen = 0 
pygame.font.init() # initializing the font for the score 
HEIGHT = 800 # height of the screen  
WIDTH = 500 # width of the screen 
BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird1.png'))),pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird2.png'))),pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird3.png'))) ] # loading bird images 
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'pipe.png'))) # pipe image load 
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'base.png'))) # ground image load 
BACKGROUND_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bg.png'))) # background image load 
FONT = pygame.font.SysFont('comicsansms', 30) # setting the score font, comicsansms 
class Bird(): 
	IMGS = BIRD_IMGS # bird images 
	MAX_ROTATION = 25 # maximum bird tilt 
	ROT_VEL = 20 # how much we will rotate in each frame 
	ANIMATION_TIME = 5 # how long we will show the bird animation 
	
	def __init__(self, x, y): 
		self.x = x 
		self.y = y 
		self.tilt = 0
		self.tick_count = 0 
		self.velocity = 0 
		self.height = self.y 
		self.img_count = 0 
		self.img = self.IMGS[0]
	def jump(self): 
		self.velocity = -10.5
		self.tick_count = 0 
		self.height = self.y 
	# function for moving the bird and keeping track of its placement 
	def move(self): 
		self.tick_count += 1 
		displacement = self.velocity * self.tick_count + 1.5 * self.tick_count ** 2 # this variable keeps track of where we change the direction
		if displacement >= 16: 
			displacement = 16 
		if displacement < 0: 
			displacement -= 2 
		self.y = self.y + displacement
		if displacement < 0 or self.y < self.height + 50: 
			if self.tilt < self.MAX_ROTATION: 
				self.tilt = self.MAX_ROTATION
		else: 
			if self.tilt > -90: 
				self.tilt -= self.ROT_VEL
	def draw(self, window): 
		self.img_count += 1 # keeping track of the animation  
		# ---- ANIMATING THE BIRD ----
		if self.img_count < self.ANIMATION_TIME: 
			self.img = self.IMGS[0]
		elif self.img_count < self.ANIMATION_TIME*2: 
			self.img = self.IMGS[1]
		elif self.img_count < self.ANIMATION_TIME*3: 
			self.img = self.IMGS[2]
		elif self.img_count < self.ANIMATION_TIME*4: 
			self.img = self.IMGS[1]
		elif self.img_count == self.ANIMATION_TIME*4 + 1: 
			self.img = self.IMGS[0]
			self.img_count = 0 
		if self.tilt <= -80: 
			self.img = self.IMGS[1]
			self.img_count = self.ANIMATION_TIME * 2 

		rotated_image = pygame.transform.rotate(self.img, self.tilt)
		new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft=(self.x, self.y)).center)
		window.blit(rotated_image, new_rect.topleft)
	def get_mask(self): 
		return pygame.mask.from_surface(self.img)

class Pipe(): 
	GAP = 200 # gap 
	VEL = 5 # velocity 

	def __init__(self, x): 
		self.x = x 
		self.height = 0 
		self.gap = 100 
		
		self.top = 0 
		self.bottom = 0 
		self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
		self.PIPE_BOTTOM = PIPE_IMG
		
		self.passed = False # did the bird pass the pipe? 
		self.set_height() # function for setting the pipe 
		
	def set_height(self): 
		# determining the height of the pipe 
		self.height = random.randrange(50, 450)
		self.top = self.height - self.PIPE_TOP.get_height() # setting the top of the pipe 
		self.bottom = self.height + self.GAP # setting the bottom of the pipe 
	# moving the pipe 
	def move(self): 
		self.x -= self.VEL
	# drawing the pipe 
	def draw(self, window):
		window.blit(self.PIPE_TOP, (self.x, self.top)) # drawing the pipe top 
		window.blit(self.PIPE_BOTTOM, (self.x, self.bottom)) # drawing the pipe bottom 
	def collide(self, bird): 
		birdMask = bird.get_mask() # setting the bird mask 
		topMask = pygame.mask.from_surface(self.PIPE_TOP) # setting a mask for the top of the pipe 
		bottomMask = pygame.mask.from_surface(self.PIPE_BOTTOM) # setting a mask for the bottom of the pipe 
		top_offset = (self.x - bird.x, self.top - round(bird.y)) # setting the offset for keeping track of how far away are masks from each other 
		bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

		bPoint = birdMask.overlap(bottomMask, bottom_offset) # finding the point of collision/overlap of the bottom 
		tPoint = birdMask.overlap(topMask, top_offset) # finding the point of collision/overlap of the top 

		if tPoint or bPoint: 
			return True # the collision happened
		return False # the collision didn't happen 
class Base: 
	VEL = 5 # velocity 
	WIDTH = BASE_IMG.get_width() # getting the width of the base/ground 
	IMG = BASE_IMG # ground images 

	def __init__(self, y): 
		self.y = y 
		self.x1 = 0 
		self.x2 = self.WIDTH 

	# moving the base/ground 
	def move(self): 
		self.x1 -= self.VEL 
		self.x2 -= self.VEL 

		# infinitely moving the images to the left 
		if self.x1 + self.WIDTH < 0: 
			self.x1 = self.x2 + self.WIDTH
		if self.x2 + self.WIDTH < 0: 
			self.x2 = self.x1 + self.WIDTH
	def draw(self, window): 
		window.blit(self.IMG, (self.x1, self.y)) # drawing the base 
		window.blit(self.IMG, (self.x2, self.y)) # drawing the base 

def draw_window(window, birds, pipes, base, score, gen): 
	window.blit(BACKGROUND_IMG, (0, 0)) # drawing the background
	for pipe in pipes: 
		pipe.draw(window)
	text = FONT.render('Score: ' + str(score), 1, (255, 255, 255))
	window.blit(text, (WIDTH - 10 - text.get_width(), 10))
	base.draw(window) 
	for bird in birds: 
		bird.draw(window)
	pygame.display.update() # updating the display 

def main(genomes, config): 
	global gen
	gen += 1 
	nets = [] 
	ge = [] 
	birds = []

	for _, g in genomes: 
		net = neat.nn.FeedForwardNetwork.create(g, config) 
		nets.append(net)
		birds.append(Bird(230, 350))
		g.fitness = 0 
		ge.append(g)
	
	pipes = [Pipe(700)] # setting the pipes variable 
	base = Base(730) # setting the base variable 
	framerate = pygame.time.Clock() # setting the framerate   
	window = pygame.display.set_mode((WIDTH, HEIGHT)) # displaying the game 
	run = True # is the game running 
	score = 0 # score 
	while run: 
		framerate.tick(30) # fps is 30 
		for event in pygame.event.get(): 
			# if the user turns off the game it quits 
			if event.type == pygame.QUIT: 
				run = False # game is no longer running 
				pygame.quit() 
				quit() 
		pipe_ind = 0
		# if we passed the pipes we change what pipe we look at :) 
		if len(birds) > 0: 
			if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width(): 
				pipe_ind = 1 
		else:
			# if there are no birds left we break  
			run = False 
			break 

		for x, bird in enumerate(birds): 
			bird.move() 
			ge[x].fitness += 0.1
			output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom))) 
			if output[0] > 0.5: 
				bird.jump() 

		base.move() # moving the base
		rem = [] # array for pipes to be removed 
		addPipe = False 
		
		for pipe in pipes: 
			pipe.move() # moving the pipes
			# checking if every bird collides with a pipe 
			for x, bird in enumerate(birds): 
				# if the bird collides we remove one point from their fitness score 
				if pipe.collide(bird):  
					ge[x].fitness -= 1
					birds.pop(x)
					nets.pop(x)
					ge.pop(x)

				# checking if the bird passed the pipe 
				if not pipe.passed and pipe.x < bird.x: 
					pipe.passed = True # did the pipe pass the screen 
					addPipe = True # adding apipe

			if pipe.x + pipe.PIPE_TOP.get_width() < 0:
				rem.append(pipe) # if the pipe passed the screen it is added to the remove array to be removed 
		
		if addPipe: 
			score += 1 # adding score after the bird passes a pipe 
			for genome in ge: 
				genome.fitness += 5 # adding more fitness score to birds that got through the pipe 
			pipes.append(Pipe(700)) # appending another pipe to be displayed 
			if score >= 20: 
				pickle.dump(nets[0], open('model.pickle', 'wb')) 
				pygame.quit() 
				quit() 
		# for every pipe in the remove array it gets removed 
		for r in rem: 
			pipes.remove(r)# removing the pipes that passed the screen 
		# checking if every bird hit the ground 
		for x, bird in enumerate(birds): 
			if bird.y + bird.img.get_height() >= 730 or bird.y < 0: 
				birds.pop(x)
				nets.pop(x)
				ge.pop(x) 
		if score > 25:
		    pickle.dump(nets[0],open("bestModel.pickle", "wb"))
		    pygame.quit() 
		    quit() 
		base.move() 
		draw_window(window, birds, pipes, base, score, gen) # displaying the screen, bird, pipes, base/ground and the score  
	
def run(config_path): 
	# loading in the config fie 
	config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)
	population = neat.Population(config) # setting a population based on the config file 
	
	#---- Setting an output ---- 
	population.add_reporter(neat.StdOutReporter(True))
	stats = neat.StatisticsReporter() 
	population.add_reporter(stats) 
	winner = population.run(main, 15)
	with open('bestModel.pickle', 'rb') as file: 
		genome = pickle.load(file)
	genomes = [(1, genome)]
	main(genomes, config)

if  __name__ == '__main__': 
	local_dir = os.path.dirname(__file__)
	config_path = os.path.join(local_dir, 'config.txt')
	run(config_path)

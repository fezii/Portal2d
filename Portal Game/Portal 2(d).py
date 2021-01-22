import pygame
import pickle # module used for translating serialized data
from pygame.locals import *

pygame.init()

clock = pygame.time.Clock() # used to run main loop at a consistent rate
fps = 30

# screen setup
screen_width = 600
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))

pygame.display.set_caption('Portal 2(d)')
tile_size = 30 								# to be used as the height and width of every tile in the map, resulting in squares
bg_image = pygame.image.load('images/background.jpg')
bg_image = pygame.transform.scale(bg_image,(600, 600))

class Player(): # Player class, contains all information required to create player, as well as the methods for moving, teleporting, and creating portals
	def __init__(self, x = 100, y = screen_height - 130): 								# default spawn location
		self.imgNum = 0
		image = pygame.image.load("images/player{}.png".format(self.imgNum)) 								# variable to store sprite graphic
		self.image = pygame.transform.scale(image, (tile_size, 2*tile_size)) 								# scales player character to 2 tiles tall, 1 tile wide
		self.rect = self.image.get_rect() 								# creates rectangle object around player, will be used for coordinates, positioning, and collisions
		self.width = self.image.get_width()
		self.height = self.image.get_height()
		self.rect.x = x 								# x coordinate of player
		self.rect.y = y 								# y coordinate of player
		self.vel_y = 0 								# vertical velocity of player, initially zero
		self.grounded = False								# bug fix - without a condition checking if players have jumped already, it was possible to infinite jump in mid-air
		self.direction = 0
		self.clicked = False
		self.portal_list = [0,0]


	def update(self): 								# constantly running method in main loop
		# out of bounds enforcement
		if self.rect.y < 0:
			self.rect.y = 35
		if self.rect.y > 600:
			self.rect.y = 565
		
		dx = 0 								# proposed change in x distance, added to x coordinate of player
		dy = 0 								# proposed change in y distance, added to y coordinate of player

		key = pygame.key.get_pressed() 								# identifies which key has been pressed, if any
		if (key[pygame.K_SPACE] == True or key[pygame.K_UP] == True) and self.grounded == True: 								# jump 
			self.vel_y = -20 								# sets an instantaneous upwards vertical velocity of 10, which will be added to player coordinates later (not too high so as to increase use of portal gun)
			self.grounded = False								# bug fix - without a condition checking if players have jumped already, it was possible to infinite jump in mid-air 
		if key[pygame.K_a] or key[pygame.K_LEFT]:
			dx -= 5 								# change in x distance of 5 units, not added to player coordinates yet
			self.imgNum = (self.imgNum + 1)%6
		if key[pygame.K_d] or key[pygame.K_RIGHT]:
			dx += 5 								# change in x distance of 5 units, not added to player coordinates yet
			self.imgNum = (self.imgNum + 1)%6

		# Gravity
		self.vel_y += 1 								# constant pull of 1 down
		dy += self.vel_y 								# adds y velocity to change in y coordinates for this cycle (doesn't change actual y coordinates yet)

		# Collision with World
		for tile in world.tile_list:
			if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height): # if a tile will be colliding with the player above or below them
				self.grounded = True
				if self.vel_y < 0: # if player is jumping
					dy = tile[1].bottom - self.rect.top 								# dy = 0 also works, but then the player will not travel right to the edge of the tile, instead they will be stopped a little early
					self.vel_y = 0 								# kills y momentum on collision
				elif self.vel_y >= 0: # if player is falling
					dy = tile[1].top - self.rect.bottom 								# dy = 0 also works, but then the player will not travel right to the edge of the tile, instead they will be stopped a little early
					self.vel_y = 0 								# kills y momentum on collision
			if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height): # if something horizontally will be colliding with player after this cycle, the player will not be able to move there
				dx = 0
		
		# Teleporting player
			# portal_list[0] = Red portal, and portal_list[1] = Blue portal
			if self.portal_list[0] != 0 and self.portal_list[1] != 0:				
				if self.rect.colliderect(self.portal_list[0]): # if player is colliding with the portal, they will be teleported to the other portal
					if self.rect.x < self.portal_list[0].rect.x:
						offset = 50	# offset so that player does not become automatically stuck in the portal
					else:
						offset = -50	# offset so that player does not become automatically stuck in the portal
					self.rect.x, self.rect.y = self.portal_list[1].rect.x + offset, self.portal_list[1].rect.bottom # teleporting (coordinate reassignment)
					
				elif self.rect.colliderect(self.portal_list[1]):# if player is colliding with the portal, they will be teleported to the other portal
					if self.rect.x < self.portal_list[1].rect.x:
						offset = 50	# offset so that player does not become automatically stuck in the portal
					else:
						offset = -50	# offset so that player does not become automatically stuck in the portal
					self.rect.x, self.rect.y = self.portal_list[0].rect.x + offset, self.portal_list[0].rect.bottom # teleporting (coordinate reassignment)
		
		# Updating player coordinates with the sum coordinate change this cycle
		self.rect.x += dx
		self.rect.y += dy

		# Drawing player and portals
		image = pygame.image.load("images/player{}.png".format(self.imgNum)) # assigns the image in the cycles through each image of the player as they walk
		self.image = pygame.transform.scale(image, (tile_size, 2*tile_size)) # scales the player image to 1 tile wide, 2 tiles tall
		screen.blit(self.image, self.rect) # draws the player image
		# pygame.draw.rect(screen, (0,255,0), self.rect, 2)  								# uncomment to view player rect (hitbox)
		for x in range(len(self.portal_list)):	# draws all portals in player's list of portals
			if self.portal_list[x] != 0:
				self.portal_list[x].draw()

	def create_portal(self): # Method to check if portal can be placed, as well as what color portal needs to be placed
		# Creating Portal
		pos = pygame.mouse.get_pos()
		valid = False
		for tile in world.tile_list:
			if tile[1].collidepoint(pos) == True and tile[2] == 1:
				valid = True
				break # saves proccessing power by not iterating through remaining tiles after the target tile has been identified
		if valid:
			# Red Portal (left click)
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				self.portal_list[0] = Portal(pos[0], pos[1] - 25) # -25 offset to stop player clpping through walls
			if pygame.mouse.get_pressed()[0] == 0:
				self.clicked = False # resets clicked condition, disallowing player from infinite clicking
			
			# Blue Portal(right click)
			if pygame.mouse.get_pressed()[2] == 1 and self.clicked == False:
				self.portal_list[1] = Portal(pos[0], pos[1] - 25, "blue") # -25 offset to stop player clpping through walls
			if pygame.mouse.get_pressed()[2] == 0:
				self.clicked = False # resets clicked condition, disallowing player from infinite clicking

class Portal(): # Portal class, contains all information required for creating a portal
	def __init__(self, x = 100, y = screen_height - 130, color = "red"):
		# Portal images
		if color == "red": # loads image based on given color
			Portal_image = pygame.image.load('images/redPort.png')
		else:
			Portal_image = pygame.image.load('images/bluePort.png')
		# defining portal properties
		self.color = color
		self.image = pygame.transform.scale(Portal_image, (tile_size, 2*tile_size)) # transforms portal to 1 tile wide, 2 tiles tall
		self.rect = self.image.get_rect()
		self.width = self.image.get_width()
		self.height = self.image.get_height()
		self.rect.x = x
		self.rect.y = y
	
	def draw(self): # method to draw the portal
		screen.blit(self.image, self.rect)
		# pygame.draw.rect(screen, (255,0,0), self.rect, 2) # uncomment to view portal rect (hitbox)


class World(): # creates the map as an object 
	def __init__(self, data): # takes in an array, and assigns tile properties based on each value in the nested list
		self.tile_list = [] # list of all tiles on the map

		# Tile images
		noPortal_image = pygame.image.load('images/noPortal.png')
		yesPortal_image = pygame.image.load('images/yesPortal.png')

		rowCount = 0 # counter for rows in the world data
		for row in data:
			colCount = 0 # counter for columns in every row
			for tile in row: # iterates through each individual value in the world_data array 
				if tile == 1: # if indiv array value = 1, then:
					image = pygame.transform.scale(noPortal_image, (tile_size, tile_size)) # scales graphic image to a square
					image_rect = image.get_rect()
					image_rect.x = colCount * tile_size # assigns x coord of tile
					image_rect.y = rowCount * tile_size # assigns y coord of tile
					tile = (image, image_rect, 0) # saves each tile as a tuple, with the image, rectangle, and portal state
					self.tile_list.append(tile) # adds tile to list of all tiles in world
				if tile == 2:
					image = pygame.transform.scale(yesPortal_image, (tile_size, tile_size)) # scales graphic image to a square
					image_rect = image.get_rect()
					image_rect.x = tile_size * colCount # assigns x coord of tile
					image_rect.y = tile_size * rowCount # assigns y coord of tile
					tile = (image, image_rect, 1) # saves each tile as a tuple, with the image, rectangle, and portal state
					self.tile_list.append(tile) # adds tile to list of all tiles in world
				colCount += 1
			rowCount += 1

	def draw(self): # draw method for drawing each tile
		for tile in self.tile_list:
			screen.blit(tile[0], tile[1])
			# pygame.draw.rect(screen, (255, 0, 255), tile[1], 2) # uncomment to view tile rects

# using pickle module to read serialized map file
pickle_in = open(f'level1_data', 'rb') 
world_data = pickle.load(pickle_in)

world = World(world_data) # creating instance of world before main loop
player = Player() # creating instance of player before main loop stars
run = True # main loop variable
while run:
	clock.tick(fps)
	screen.blit(bg_image, (0, 0)) # draws onto the screen
	world.draw() # draws all tiles in the map
	player.update() # constantly updates player
	for event in pygame.event.get():
		if event.type == pygame.QUIT: # quit conditional
			run = False
		if event.type == pygame.MOUSEBUTTONDOWN: # portal placement conditional
			player.create_portal()
	pygame.display.update() # updates display

pygame.quit() # quits pygame after run has been declared False

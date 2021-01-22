import pygame
import pickle
from pygame.locals import *

pygame.init()

clock = pygame.time.Clock()
fps = 30

# screen setup
screen_width = 600
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))

pygame.display.set_caption('Portal 2(d)')
tile_size = 30 								# to be used as the height and width of every tile in the map, resulting in squares
bg_image = pygame.image.load('images/background.jpg')
bg_image = pygame.transform.scale(bg_image,(600, 600))


class Player():
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
		self.inPortal = False


	def update(self): 								# constantly running method in main loop
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

		# Collision
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
			# portal_list 0 = Red portal, and portal_list 1 = Blue portal
			if self.portal_list[0] != 0 and self.portal_list[1] != 0 and self.inPortal == False:
				self.inPortal = True				
				if self.rect.colliderect(self.portal_list[0]):
					self.rect.x = self.portal_list[1].rect.x
					# self.rect.y = self.portal_list[1].rect.y
					# self.inPortal = True
					
				if self.rect.colliderect(self.portal_list[1]):
					self.rect.x = self.portal_list[0].rect.x
					# self.rect.y = self.portal_list[0].rect.y
					# self.inPortal = True
				
			else: 
				self.inPortal = False
		
		# Updating player coordinates with the sum coordinate change this cycle
		self.rect.x += dx
		self.rect.y += dy

		# Creating Portal
		pos = pygame.mouse.get_pos()
		
		# Red Portal (left click)
		for tile in world.tile_list:
			if tile[1].collidepoint(pos):
				pass
		if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
			self.portal_list[0] = Portal(pos[0], pos[1])
		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False
		
		# Blue Portal(right click)
		if pygame.mouse.get_pressed()[2] == 1 and self.clicked == False:
			self.portal_list[1] = Portal(pos[0], pos[1], "blue")
		if pygame.mouse.get_pressed()[2] == 0:
			self.clicked = False
		

		# Drawing player and portals
		image = pygame.image.load("images/player{}.png".format(self.imgNum))
		self.image = pygame.transform.scale(image, (tile_size, 2*tile_size))
		screen.blit(self.image, self.rect)
		pygame.draw.rect(screen, (0,255,0), self.rect, 2)  								# uncomment to view player rect (hitbox)
		for x in range(len(self.portal_list)):
			if self.portal_list[x] != 0:
				self.portal_list[x].draw()


class Portal():
	def __init__(self, x = 100, y = screen_height - 130, color = "red"):
		# Portal images
		if color == "red":
			Portal_image = pygame.image.load('images/redPort.png')
		else:
			Portal_image = pygame.image.load('images/bluePort.png')
		self.color = color
		self.image = pygame.transform.scale(Portal_image, (tile_size, 2*tile_size))
		self.rect = self.image.get_rect()
		self.width = self.image.get_width()
		self.height = self.image.get_height()
		self.rect.x = x
		self.rect.y = y
	
	def draw(self):
		screen.blit(self.image, self.rect)
		pygame.draw.rect(screen, (255,0,0), self.rect, 2) # uncomment to view portal rect (hitbox)


class World(): # creates the map as an object 
	def __init__(self, data): # takes in an array, and assigns tile properties based on each value in the nested list
		self.tile_list = []

		# Tile images
		noPortal_image = pygame.image.load('images/noPortal.png')
		yesPortal_image = pygame.image.load('images/yesPortal.png')

		rowCount = 0
		for row in data:
			colCount = 0
			for tile in row:
				if tile == 1:
					image = pygame.transform.scale(noPortal_image, (tile_size, tile_size)) # scales graphic image to a square
					image_rect = image.get_rect()
					image_rect.x = colCount * tile_size
					image_rect.y = rowCount * tile_size
					tile = (image, image_rect)
					self.tile_list.append(tile)
				if tile == 2:
					image = pygame.transform.scale(yesPortal_image, (tile_size, tile_size)) # scales graphic image to a square
					image_rect = image.get_rect()
					image_rect.x = tile_size * colCount
					image_rect.y = tile_size * rowCount
					tile = (image, image_rect)
					self.tile_list.append(tile)
				colCount += 1
			rowCount += 1

	def draw(self):
		for tile in self.tile_list:
			screen.blit(tile[0], tile[1])
			pygame.draw.rect(screen, (255, 0, 255), tile[1], 2) # uncomment to view tile rects

pickle_in = open(f'level1_data', 'rb')
world_data = pickle.load(pickle_in)
world = World(world_data)

player = Player()
run = True
while run:

	clock.tick(fps)

	screen.blit(bg_image, (0, 0))

	world.draw()

	player.update()

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False

	pygame.display.update()

pygame.quit()
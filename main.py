'''

lage hotbar, holde items, building tool # FERDIG

types = {"campfire": campfireImage} (dette er jo allerede gjort med assetManager, bare gjør tileTypes = game.AssetManager.GetImages("./Tiles/Placables")

def campfireCallback():
   print("i am a campfire)

types = {
   "campfire": {
      image: campfireImage,
      callback: campfireCallback
   }
}

class Tile: # dette vil være ansvarlig for alle placables, som cooking pot, campfire, sail, etc.

   def __init__(self, x, y, type):
      self.type = type
      self.image = types[self.type]["image"]
      self.rect = self.image.get_rect()
      self.rect.x, self.rect.y = x, y
   
   def callback(self):
      callback = types[self.type]["callback"]()
   

# ting å gjøre
item callbacks
fix stack på items i hotbar, og da må du endre måten du sjekker hvor mange du har i crafting, bør egentlig gjøre det lettere men litt styr å få gjort unna.
fiskestang
fisker
campfire callback, lighte den og plassere fisk på den
      
'''


import pygame
from pygame.locals import *
import sys
import colorama
from colorama import Fore
from pathlib import Path
import math
import random
import os
from datetime import datetime

colorama.init(autoreset=True)

lg = Fore.LIGHTGREEN_EX

class spawnableTile(pygame.sprite.Sprite):

   def __init__(self, x, y, type):
      pass

class PlankTile(pygame.sprite.Sprite):

    def __init__(self, x, y):
        super().__init__()
        self.position = pygame.Vector2(x * game.TILE_SIZE, y * game.TILE_SIZE)
        self.velocity = 5
        self.type = type
        self.image = game.AssetManager.plankSprites["plank"]
        self.rect = self.image.get_rect()
        self.rect.x = x * game.TILE_SIZE
        self.rect.y = y * game.TILE_SIZE

class WaterTile(pygame.sprite.Sprite):
   def __init__(self, x, y):
      super().__init__() 
      self.start = pygame.Vector2(x, y)
      self.position = pygame.Vector2(x * game.TILE_SIZE, y * game.TILE_SIZE)
      self.velocity = 1
      self.type = type
      self.current_sprite = 0
      self.image = game.AssetManager.waterSprites[self.current_sprite]
      self.rect = self.image.get_rect()
      self.rect.x = x * game.TILE_SIZE
      self.rect.y = y * game.TILE_SIZE
      self.spawnable = True
   
   def spawnPlank(self):
      if self.spawnable:
         tile = PlankTile(0, 0)
         tile.rect.topleft = self.rect.topleft
         game.AssetManager.plank_tiles.add(tile)
         game.log(self, f"Created PlankTile at {tile.rect.topleft}", "info", "TileManager")
         self.spawnable = False

   def update(self, mousePosition, selectivePlank):

      self.current_sprite += 0.05
      if self.current_sprite >= 4:  # 4 frames i alle animations
         self.current_sprite = 0
      
      self.image = game.AssetManager.waterSprites[int(self.current_sprite)]

      '''self.rect.y += self.velocity
      self.rect.x -= self.velocity'''

      if self.rect.collidepoint(mousePosition):
         if not self in selected:
            selected.append(self)
      else:
         if self in selected:
            selected.remove(self)

class Shark:

   def __init__(self):
      self.image = game.AssetManager.nonSpawnable["shark"]
      self.rect = self.image.get_rect()
      self.rect.x = random.randint(30, game.SCREEN_SIZE.x - 30)
      self.rect.y = game.SCREEN_SIZE.y + self.image.get_height() * 4
      self.speed = 2.5
      self.damage = 0.5
      self.health = 100
      self.spawned = False
      self.angle = 0
      game.log(self, f"Created shark at {self.rect.topleft}", "info", "SharkManager")

   def collidingWithPlayer(self):
    # Calculate the center of the player's rectangle
    player_center_x = player.rect.centerx
    player_center_y = player.rect.centery

    # Check if the shark's rectangle collides with the player's center
    return self.rect.collidepoint(player_center_x, player_center_y)
   
   def attack(self):
      hud.stats.health -= self.damage
      #game.sharkInstance = None # remove instance from screen, which means you have to make an new shark instance for each time player goes in water.

   def update(self):
      dx2 = player.position.x - self.rect.x
      dy2 = player.position.y - self.rect.y
      angle2 = math.atan2(dy2, dx2)
      angle_degrees2 = -(math.degrees(angle2) + 90)  # Use the negative and add 90 degrees

      # Ensure the angle is within the range [0, 360)
      angle_degrees2 %= 360

      self.angle = angle_degrees2

      # Rotate the image around its center
      rotated_image, new_rect = game.rotate_image(self.image, angle_degrees2, self.rect.center)
      self.rect = new_rect

      # Calculate the components of the movement vector
      dy = self.speed * math.cos(math.radians(angle_degrees2))
      dx = self.speed * math.sin(math.radians(angle_degrees2))

      if not self.collidingWithPlayer():
        self.rect.x -= dx
        self.rect.y -= dy
      else:
         self.attack()

      game.render(rotated_image, self.rect.topleft)

def campfireCallback():
   print("i am a campfire")

placableCallbacks = {
   "campfire": campfireCallback # when selecting something in hotbar, if it is in this dict then set its selecting to true
}

class Game:

   class assetManager:

      class Object:

         def __init__(self, x, y, image, type, velocity):
            self.position = pygame.Vector2(x, y)
            self.type = type
            self.velocity = 0.4
            self.image = image
            self.rect = self.image.get_rect()
            self.rect.x, self.rect.y = x, y
            self.flippedImage = pygame.transform.flip(self.image, True, False)
            self.inventoryMode = False
            self.inventoryImage = pygame.transform.scale(self.image, (self.image.get_width() * 0.5, self.image.get_height() * 0.5))
            self.regularImage = self.image # FIKS AT DEN IKKE ER TRANSFORMEMD
            self.stack = 1
            self.font = pygame.font.Font(None, 36)
         
         def drawStack(self):
            if self.inventoryMode:
               sprite_to_draw = self

               # Extract the rect attribute from the sprite
               rect_to_draw = sprite_to_draw.rect

               # Set the thickness of the outline (width) to a value greater than 0
               outline_thickness = 20  # Adjust this value according to your preference

               # Draw the outline of the rect on the screen
               pygame.draw.rect(game.screen, (255, 0, 0), rect_to_draw, outline_thickness)

               # Create a font object
               font = pygame.font.Font(None, 36)  # You can replace None with a specific font file path

               # Create a text surface
               text_surface = font.render("Tile", True, (255, 255, 255))  # Replace (255, 255, 255) with the text color

               # Get the center position for the text
               text_rect = text_surface.get_rect(center=rect_to_draw.center)

               # Blit the text surface onto the screen
               game.screen.blit(text_surface, text_rect)

         
         def update(self):
            self.rect.x, self.rect.y = self.position
            if self.inventoryMode:
               self.drawStack()

         def toggleInventoryMode(self):
            self.inventoryMode = not self.inventoryMode
            if self.inventoryMode:
               self.image = self.inventoryImage
            else:
               self.image = self.regularImage
         
      # -- end of object class --

      # -- asset manager below -- 

      def __init__(self):
         self.waterSprites = self.getImages("./Tiles/Water", transform=True, list=True)
         self.plankSprites = self.getImages("./Tiles/Plank", transform=False, list=False)
         # tiles
         self.water_tiles = pygame.sprite.Group()
         self.underTiles = pygame.sprite.Group()
         self.plank_tiles = pygame.sprite.Group()
         self.placableTiles = pygame.sprite.Group()
         # idk
         self.HUDObjects = self.getImages("./HUD", transform=False)
         Game.log(self, self.HUDObjects, "info", "HUDObjects")
         self.spawnable = self.getImages("./SpawnableObjects", transform=True)
         Game.log(self, self.spawnable, "info", "SpawnableObjects")
         self.nonSpawnable = self.getImages("./NonSpawnableObjects", transform=True)
         Game.log(self, self.nonSpawnable, "info", "NonSpawnable")

      def getImages(self, path, transform=True, list=False):
         os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"
         new_map = {}
         newList = []
         Game.log(self, f"Loading files for {path}..", "warn", "AssetManager")
         
         for fileName in os.listdir(path):
            if fileName.endswith(".png"):
                  filePath = os.path.join(path, fileName)
                  image = pygame.image.load(filePath).convert_alpha()
                  name = fileName.split(".")[0]

                  if transform:
                     image = pygame.transform.scale(image, (64, 64))

                  if not list:
                     new_map[name] = image
                  else: # its a list
                     newList.append(image)

                  Game.log(self, f"loaded {fileName} with transform {transform}", "info", "AssetManager")

         Game.log(self, f"loaded all files from {path}", "success", "AssetManager")

         if not list:
            return new_map
         else:
            return newList

   # -- end of asset manager, game clas below

   def __init__(self):
      pygame.init()
      self.SCREEN_SIZE = pygame.Vector2(1000, 650)
      self.screen = pygame.display.set_mode((self.SCREEN_SIZE))
      self.clock = pygame.time.Clock()
      self.TILE_SIZE = 32
      self.tiles = []
      self.AssetManager = self.assetManager()
      self.activeObjects = []
      self.spawnObjectChanceRange = 200
      self.spawnableObjectSize = (45, 45)
      self.sharkInstance = None

   def click(self, rect):
      keys = pygame.mouse.get_pressed()
      if keys[0]:
         pos = pygame.mouse.get_pos()

         if not isinstance(rect, pygame.Rect) :
            print("rect is not rect")
            return

         if rect.collidepoint(pos):
            return True
         else:
            return False

   def spawnObject(self, x, y):
      type = random.choice(list(self.AssetManager.spawnable))
      image = pygame.transform.scale(self.AssetManager.spawnable[type], self.spawnableObjectSize)
      newObject = self.AssetManager.Object(x, y, image, type, 1)
      self.activeObjects.append(newObject)
      self.log(self, f"Created object {type} at {x}, {y}", "info", "ObjectHandler")

   def handleObjects(self):
      if random.randint(1, self.spawnObjectChanceRange) == 1:
         x = random.randint(500, 1070)
         y_range = int(x * 316 / 1070) - 200
         y = random.randint(0, max(0, y_range))  # Ensure y is not negative
         self.spawnObject(x, y)

   def updateObjects(self):
      self.handleObjects()
      for object in self.activeObjects:
         object.position.y += object.velocity
         object.position.x -= object.velocity
         object.update()

         if self.click(object.rect):
            if object in self.activeObjects:
               hud.hotbar.add_item(object)
               self.log(self, f"Picked up {object.type}", "info", "AssetManager")
            
         if object.position.y > self.SCREEN_SIZE.y:
            self.activeObjects.remove(object)
            self.log(self, f"Removed {object.type} from scren", "info", "AssetManager")

         self.render(object.image, object.position)

   @staticmethod
   def log(self, message, type = "", parent = ""):
      
      current_time = datetime.now().time()
      formatted_time = current_time.strftime("%H:%M:%S")
      sign = None
      color = None
      attr = None

      if type == "":
         color = Fore.LIGHTWHITE_EX
      elif type == "warn":
         color = Fore.LIGHTYELLOW_EX
         sign = "-"
         attr = f"{parent}: Warning: "
      elif type == "error":
         color = Fore.LIGHTRED_EX
         sign = "!"
         attr = f"{parent}: Error: "
      elif type == "success":  
         color = Fore.LIGHTGREEN_EX
         sign = "+"
         attr = f"{parent}: "
      elif type == "info":
         color = Fore.LIGHTBLACK_EX
         sign = "i"
         attr = f"{parent}: "
   
      print(f"[{Fore.LIGHTCYAN_EX}{formatted_time}{Fore.RESET}]{Fore.LIGHTWHITE_EX}[{color}{sign}{Fore.LIGHTWHITE_EX}]{color}{attr}{message}")

   def loadLevel(self):
      fac = -3

      # water

      for y in range(28):
         for x in range(30):
            tile = WaterTile(x+fac, y+fac)
            p = game.toScreenCoords(tile.rect.x, tile.rect.y)
            tile.rect.x = p.x
            tile.rect.y = p.y
            game.AssetManager.water_tiles.add(tile)

      game.log(self, game.AssetManager.water_tiles, "info", "LevelLoader-WaterTiles")
      game.log(self, game.AssetManager.water_tiles.sprites()[0].rect, "info", "Debugger")

      # raft

      middle_x = game.SCREEN_SIZE.x // 2 
      middle_y = game.SCREEN_SIZE.y // 2

      for y in range(2):
         for x in range(2):
               tile = PlankTile(x + middle_x // game.TILE_SIZE, y + middle_y // game.TILE_SIZE)
               p = game.toScreenCoords(tile.rect.x, tile.rect.y)
               tile.rect.x = p.x - game.TILE_SIZE * 4
               tile.rect.y = p.y - game.TILE_SIZE * 2
               game.AssetManager.plank_tiles.add(tile)

      game.log(self, game.AssetManager.plank_tiles, "info", "LevelLoader-PlankTiles")
      game.log(self, game.AssetManager.plank_tiles.sprites()[0].rect, "info", "Debugger")
      

   def toScreenCoords(self, x, y):
      return pygame.Vector2((x-y + game.SCREEN_SIZE.x // 2 - game.TILE_SIZE, (x+y)//2))

   def render(self, image, position=(0, 0)):
      if isinstance(position, tuple):
         self.screen.blit(image, position)
      elif isinstance(position, pygame.Vector2):
         self.screen.blit(image, (position.x, position.y))


   def get_images_from_folder(self, path, flip):
      folder = Path(path)
      l = []
      for file in folder.iterdir():
         if file.is_file():
            image = pygame.image.load(f"{path}/{file.name}").convert_alpha()

            if flip:
                  image = pygame.transform.flip(image, True, False)

            l.append(pygame.transform.scale(image, (64, 64)))
      return l
   
   def processKey(self, input):
      if len(hud.hotbar.items) <= 0:
         self.log(self, f"Unable to access index {input}; hotbar is empty", "warn", "InputHandler")
         return
      try:
         key = input - 1
         item = hud.hotbar.items[key]
         self.log(self, f"Equipped item {hud.hotbar.items[key][0].type} at index {input}", "info", "InputHandler")
         # Integrate sound system when that is made here
         player.pickUp(item)

         # if item is a placable, show it with transparency
         tm = item[0]
         if tm.type in placableTypes:
            newPlacable = Placable(tm.rect.x, tm.rect.y, tm.type)
            if not newPlacable in game.AssetManager.placableTiles:
               game.AssetManager.placableTiles.add(newPlacable)
               game.log(self, f"Placed {tm.type}", "info", "InputHandler")

      except IndexError:
         self.log(self, f"Index {input} is out of range", "warn", "InputHandler")

   def handleKeyDown(self, event):

      key = event.key - pygame.K_0
      if 1 <= key <= 9:
         self.processKey(key)
         return
      # some other binds
      
   def handleKeyUp(self, event):
      pass

   def find_closest_tile(self, selected, mousePosition):
      if not selected:
         return None  # No tiles to check

      closest_tile = selected[0]
      closest_distance = math.hypot(
         mousePosition[0] - closest_tile.rect.centerx,
         mousePosition[1] - closest_tile.rect.centery
      )

      for tile in selected[1:]:
         distance = math.hypot(
               mousePosition[0] - tile.rect.centerx,
               mousePosition[1] - tile.rect.centery
         )

         if distance < closest_distance:
               closest_tile = tile
               closest_distance = distance

      return closest_tile

   def rotate_image(self, image, angle, center):
      rotated_image = pygame.transform.rotate(image, angle)
      new_rect = rotated_image.get_rect(center=center)
      return rotated_image, new_rect

class HUD:

   class Hotbar:

      def __init__(self, x, y):
         self.position = pygame.Vector2(x, y)
         self.image = game.AssetManager.HUDObjects["hotbar2"]
         self.items = []
         self.rect = self.image.get_rect()
         self.rect.topleft = self.position
         self.slots = 10
         self.slot_height = 32
         self.slot_width = (game.SCREEN_SIZE.x // self.slots) / 2
      
      def add_item(self, item):
         if len(self.items) >= self.slots:
            game.log(self, f"Couldn't pick up {item.type}: Inventory full!", "warn", "Hotbar")
            return
         for index, (image, _) in enumerate(self.items):
            if image is None:
               self.items[index] = (item, index)
               return
         self.items.append((item, len(self.items)))
         item.toggleInventoryMode() # btw dette gjør det for alle aktive instances, finn ut hvorfor senere. ikke pri 1. 

         if item in game.activeObjects:
            game.activeObjects.remove(item)

         game.log(self, f"Added {item.type} to inventory", "success", "Hotbar")

      
      def render(self):
         game.render(self.image, self.position)

         for item in self.items:
            obj, index = item
            xPos = index * self.slot_width + 258
            game.render(obj.image, (xPos, self.position.y + 7))
   
   class Stats:

      def __init__(self, x, y):
         self.position = pygame.Vector2(x, y)
         self.barHeight = 8
         # Images
         self.image = game.AssetManager.HUDObjects["hud"]
         self.healthBar = game.AssetManager.HUDObjects["health_bar"]
         self.hungerBar = game.AssetManager.HUDObjects["hunger_bar"]
         self.thirstBar = game.AssetManager.HUDObjects["thirst_bar"]
         # initial values
         self.health = 100
         self.hunger = 100
         self.thirst = 100
      
      def update(self):
         self.hunger -= 0.005
         self.thirst -= 0.002

         game.render(self.image, self.position)

         healthBar = pygame.transform.scale(self.healthBar, (self.health, self.barHeight))
         hungerBar = pygame.transform.scale(self.hungerBar, (int(self.hunger), self.barHeight))
         thirstBar = pygame.transform.scale(self.thirstBar, (int(self.thirst), self.barHeight))

         game.render(healthBar, (94, 29))
         game.render(hungerBar, (94, 49))
         game.render(thirstBar, (94, 69))
   
   class CraftingMenu:

      class Item(pygame.sprite.Sprite):

         recipes = {
            "hammer": {
               "wood": 1,
               "rope": 1,
            },
            "campfire": {
               "wood": 3,
            },
            "meat": {
               "leaf": 1,
            },
            "sail": {
               "wood": 2,
               "rope": 2,
               "cloth": 3,
            },
         }

         def __init__(self, name, image):
            super().__init__() 
            self.name = name
            self.image = image
            self.rect = self.image.get_rect() # on hovering rect, show a text label displaying the name above it
            self.rect.x = self.rect.y = 0
            try:
               self.recipe = self.recipes[self.name]
               game.log(self, f"Set recipe {self.recipe} for {self.name}", "info", "CraftingMenu")
            except KeyError:
               game.log(self, f"No recipe found for {self.name}", "warn", "CraftingMenu")
         
         def recipeCompleted(self, recipe):
            items = recipe.items()
            found_items = {}
            remove = []

            for itemName, count in items:
               found_count = 0
               for obj in hud.hotbar.items:
                     if obj[0].type == itemName:
                        found_count += 1
                        remove.append(obj[0])
                        if found_count == count:
                           break

               found_items[itemName] = found_count

            # Check if the count of each item matches the count specified in the recipe
            missing_items = [(itemName, count - found_items.get(itemName, 0)) for itemName, count in items if found_items.get(itemName, 0) != count]

            if not missing_items:
               return (True, remove)
            else:
               return (False, missing_items)
         
         def craft(self, item, image, remove):
            # når obj blir funnet i inventory, gjørat du returner en tuple med True eller False, (for greia jeg allerede gjør), og return en list med objects sånn at jeg kan poppe dem fra hud.hotbar.items
            #remove items from hotbar

            for obj, index in hud.hotbar.items:
               if obj in remove:
                  hud.hotbar.items.pop(index)
                  game.log(self, f"removed {obj.type} from hotbar")

            # add new item to hotbar
            newObj = game.AssetManager.Object(0, 0, image, item, 1)
            hud.hotbar.add_item(newObj)

         def update(self, x, y):
            self.rect.x, self.rect.y = x, y

            # If click on self rect and there is a recipe for the item
            if game.click(self.rect):
               if not hasattr(self, "recipe"):
                     return

               try:
                     result = self.recipeCompleted(self.recipe)

                     if result[0] == True:
                        self.craft(self.name, self.image, result[1])
                        game.log(self, f"Crafted {self.name}", "info", "CraftingMenu")
                     elif result[0] == False:
                        game.log(self, f"Cant craft {self.name}, missing {result[1]}", "warn", "CraftingMenu")

               except IndexError:
                     game.log(self, f"No items in hotbar", "warn", "")
      
      class Menu:

         def __init__(self, x, y, items):
            self.position = pygame.Vector2(x, y)
            self.items = items # get lenght of items * padding / grid size or something to determine height of menu
            self.image = game.AssetManager.HUDObjects["craftingMenuImage"]
            self.GRIDWIDTH = 4
            self.GRIDHEIGHT = 6
            self.CELLSIZE = 25
            self.MARGIN = 5
            self.CONTAINERWIDTH = self.GRIDWIDTH * (self.CELLSIZE + self.MARGIN) - self.MARGIN
            self.CONTAINERHEIGHT = self.GRIDHEIGHT * (self.CELLSIZE + self.MARGIN) - self.MARGIN
            self.CONTAINERRECT = pygame.Rect(x, y, self.CONTAINERWIDTH, self.CONTAINERHEIGHT)
            self.open = False
         
         def draw_grid(self):
            game.render(pygame.transform.scale(self.image, (self.CONTAINERWIDTH, self.CONTAINERHEIGHT)), (self.CONTAINERRECT.x, self.CONTAINERRECT.y))
            for i in range(self.GRIDWIDTH):
               for j in range(self.GRIDHEIGHT):
                     index = i + j * self.GRIDWIDTH
                     if index < len(self.items):
                        x = self.CONTAINERRECT.x + i * (self.CELLSIZE + self.MARGIN)
                        y = self.CONTAINERRECT.y + j * (self.CELLSIZE + self.MARGIN)
                        item = self.items[index]
                        game.render(pygame.transform.scale(item.image, (self.CELLSIZE, self.CELLSIZE)), (x, y))
                        item.update(x, y)
         
         def updateAttributes(self, x, y, items):
            self.CONTAINERRECT.x, self.CONTAINERRECT.y = x, y
            self.items = items

      class food(pygame.sprite.Sprite):
         
         def __init__(self):
            super().__init__() 
            self.image = game.AssetManager.HUDObjects["food"]
            self.rect = self.image.get_rect()
            self.rect.x = self.rect.y = 0
            self.items = pygame.sprite.Group()
            for name, image in game.AssetManager.getImages("./HUD/foodCategory", True).items():
               item = HUD.CraftingMenu.Item(name, image)
               self.items.add(item)
               game.log(self, f"created item {name}", "info", "CraftingMenu-FoodCategory")
      
      class utilities(pygame.sprite.Sprite):
         
         def __init__(self):
            super().__init__() 
            self.image = game.AssetManager.HUDObjects["utilities"]
            self.rect = self.image.get_rect()
            self.rect.x = self.rect.y = 0
            self.items = pygame.sprite.Group()
            for name, image in game.AssetManager.getImages("./HUD/utilitiesCategory", True).items():
               item = HUD.CraftingMenu.Item(name, image)
               self.items.add(item)
               game.log(self, f"created item {name}", "info", "CraftingMenu-UtilitiesCategory")

      class building(pygame.sprite.Sprite):
         
         def __init__(self):
            super().__init__() 
            self.image = game.AssetManager.HUDObjects["hammer"]
            self.rect = self.image.get_rect()
            self.rect.x = self.rect.y = 0
            self.items = pygame.sprite.Group()
            for name, image in game.AssetManager.getImages("./HUD/buildingCategory", True).items():
               item = HUD.CraftingMenu.Item(name, image)
               self.items.add(item)
               game.log(self, f"created item {name}", "info", "CraftingMenu-BuildingCategory")

      def __init__(self, x, y):
         self.position = pygame.Vector2(x, y)
         self.image = game.AssetManager.HUDObjects["craftingMenu"]
         self.slots = 3
         self.slot_width = 32
         self.slot_height = (game.SCREEN_SIZE.y // self.slots) / 2
         self.item = self.Item
         self.padding = self.slot_width - 13
         self.categories = []
         self.categories.append(self.food())
         self.categories.append(self.utilities())
         self.categories.append(self.building())
         self.menu = self.Menu(0, 0, [])
      
      def update(self):
         game.render(self.image, self.position)

         for index, obj in enumerate(self.categories):
            yPos = index * (self.slot_width + self.padding) + 125
            xPos = self.position.x + 10
            game.render(obj.image, (xPos, yPos))
            obj.rect.x, obj.rect.y = xPos, yPos

            if game.click(obj.rect):
               if self.menu.open == False:
                  self.menu.updateAttributes(xPos + 45, yPos - 10, obj.items.sprites())
                  self.menu.open = True
               else:
                  self.menu.open = False
            
            if self.menu and not len(self.menu.items) == 0 and self.menu.open == True:
               #pygame.draw.rect(game.screen, (0, 0, 0), self.menu.CONTAINERRECT)
               self.menu.draw_grid()
         

   # HUD

   def __init__(self):
      self.hotbar = self.Hotbar(235, 25)
      self.stats = self.Stats(20, 20)
      self.craftingmenu = self.CraftingMenu(20, 100)

   def handleUI(self):
      self.hotbar.render()
      self.stats.update()
      self.craftingmenu.update()
   

class Player:
   
   class Hand:

      def __init__(self, player, radius, color, thickness):
         self.player = player 
         self.radius = radius
         self.color = color
         self.thickness = thickness
         self.angle = 0
         self.position = None
         self.item = None

      def update(self, item):
         adjusted_radius = self.radius / 2 * 1.8

         center_x = self.player.position.x + self.player.size.x / 2
         center_y = self.player.position.y + self.player.size.y / 2

         hand_x = center_x + adjusted_radius * math.cos(math.radians(self.angle))
         hand_y = center_y + adjusted_radius * math.sin(math.radians(self.angle))

         self.position = (int(hand_x), int(hand_y))
         pygame.draw.circle(game.screen, (0, 0, 0), self.position, self.thickness + 2)
         pygame.draw.circle(game.screen, self.color, self.position, self.thickness)

         if item:
            self.item = item

            # draw the item (item is an Object)
            handXCenter = hand_x - (item.image.get_width() / 2)
            handYCenter = hand_y - (item.image.get_height() / 2)

            image = None

            if -90 < self.angle < 90:
               image = pygame.transform.scale(item.regularImage, (48, 48))
            else:
               image = image = pygame.transform.scale(item.flippedImage, (48, 48))

            game.render(image, (handXCenter, handYCenter))

   # -- player class --

   def __init__(self, x, y):
      self.position = pygame.Vector2(x, y)
      self.velocity = 2
      super().__init__()
      self.isAnimating = False
      self.angle = 0
      self.up_sprites = game.get_images_from_folder("./Sprites/up", False)
      self.down_sprites = game.get_images_from_folder("./Sprites/down", False)
      self.right_sprites = game.get_images_from_folder("./Sprites/side", False)
      self.left_sprites = game.get_images_from_folder("./Sprites/side", True)
      self.current_sprite = 0
      self.image = self.up_sprites[self.current_sprite]
      self.rect = self.image.get_rect()
      self.rect.x, self.rect.y = x, y
      self.center = pygame.Vector2(0, 0)
      self.center_color = None
      self.size = pygame.Vector2(self.image.get_width(), self.image.get_height())
      self.holding_item = False
      self.holding_item_img = None
      self.inWater = False
      self.hand = self.Hand(self, radius=32, color=(255, 0, 0), thickness=5)
      self.hoveringTilePosition = 0

   def pickUp(self, item):
      self.holding_item = not self.holding_item
      self.holding_item_img = item[0]

   def calculate_velocity(self, cursor_position):
      max_velocity = 1.5
      min_velocity = 0.5

      distance = self.position.distance_to(cursor_position)
      max_distance = 200.0 
      normalized_distance = min(distance / max_distance, 1.0)

      self.velocity = min_velocity + normalized_distance * (max_velocity - min_velocity)
   
   def animate(self, direction):
      self.direction = direction
      self.isAnimating = True
      
   def keyup(self):
      self.isAnimating = False
      self.current_sprite = 0

   def biomeHandler(self):
      color = game.screen.get_at((self.rect.centerx, self.rect.centery))
      '''r, g, b = color[0], color[1], color[2]
      ansi_color = f"\x1b[38;2;{r};{g};{b}m"
      print(f"{ansi_color}{color}{colorama.Style.RESET_ALL}")'''
      if color[:3] == (77, 166, 255):
         if not self.inWater:
               self.inWater = True

               # spawn shark
               shark = Shark()
               game.sharkInstance = shark

         # update the shark if it still is in the water
         if game.sharkInstance:
               game.sharkInstance.update()

      elif color[:3] == (215, 145, 92):
         if self.inWater:
               self.inWater = False

               # if shark exists, remove it before it hurts the player
               if game.sharkInstance:
                  del game.sharkInstance
                  game.log(self, "Shark removed", "info", "SharkManager")

   def update(self, cursor_position):
      player.hand.angle = player.angle
      player.hand.update(self.holding_item_img)

      if self.isAnimating:
         self.current_sprite += 0.17

         if self.current_sprite >= 4:  # 4 frames in all animations
               self.current_sprite = 0

         move_distance = self.velocity
         move_angle = math.radians(self.direction)

         delta_x = move_distance * math.cos(move_angle)
         delta_y = move_distance * math.sin(move_angle)

         self.position.x += delta_x
         self.position.y += delta_y

      self.rect.x, self.rect.y = self.position

      self.biomeHandler()

      self.calculate_velocity(cursor_position)

      if self.angle < -135 or self.angle >= 135:
         self.image = self.left_sprites[int(self.current_sprite)]
      elif -135 <= self.angle < -45:
         self.image = self.up_sprites[int(self.current_sprite)]
      elif -45 <= self.angle < 45:
         self.image = self.right_sprites[int(self.current_sprite)]
      else:
         self.image = self.down_sprites[int(self.current_sprite)]
      

print("--------------------------------------------------------------------------------------")
print("--------------------------------------------------------------------------------------")
print("--------------------------------------------------------------------------------------")
print("--------------------------------------------------------------------------------------")
print("--------------------------------------------------------------------------------------")

game = Game()
player = Player(game.SCREEN_SIZE.x // 2, game.SCREEN_SIZE.y // 2)
hud = HUD()
game.loadLevel()

selectivePlankTile = PlankTile(0, 0)
selectivePlankTile.image = game.AssetManager.plankSprites["selectivePlank"]
selectivePlankTile.image.set_alpha(99)
selected = []

placableTypes = game.AssetManager.getImages("./Tiles/Placables")
game.log(None, f"{placableTypes}", "info", "Debugger~Placable")

class Placable(pygame.sprite.Sprite):

   def __init__(self, x, y, type):
      super().__init__()
      self.image = placableTypes[type]
      self.placingImage = self.image.set_alpha(99) # known issue, will set main images alpha too
      self.callback = placableCallbacks[type]
      self.rect = self.image.get_rect()
      self.rect.x, self.rect.y = x, y
      self.type = type
      self.placed = False
      self.selecting = False
   
   def place(self):
      self.placed = True

   def update(self):
      closestTile = game.find_closest_tile(selected=selected, mousePosition=mousePosition)
      if not self.placed and closestTile and self.selecting: # hovering
         self.rect.topleft = closestTile.rect.topleft
      else:
         pass

      if self.selecting and not self.placed:
         game.render(self.placingImage, (self.rect.topleft)) # idk bro
      elif not self.selecting and self.placed:
         game.render(self.image, (self.rect.topleft))


running = True
while running:
    
   for event in pygame.event.get():
      if event.type == pygame.QUIT:
         sys.exit()
   
      if event.type == pygame.KEYDOWN:
         if event.key == pygame.K_ESCAPE:
            running = False
         if event.key == pygame.K_y:
            game.spawnObject(0, 0)
            obj = random.choice(game.activeObjects)
            hud.hotbar.add_item(obj)
         if event.key == pygame.K_o:
            mousePosition = pygame.Vector2(pygame.mouse.get_pos())
            player.position = mousePosition 

         # some hotbar stuff idk

         game.handleKeyDown(event)

      keys = pygame.key.get_pressed()
      
      if keys[K_w]:
            player.animate(angle_degrees)
      
      if keys[K_c]:
         print(pygame.mouse.get_pos())
      
      if event.type == pygame.KEYUP:
         if event.key == pygame.K_w:
            player.keyup()
         
         # some hotbar stuff idk

         game.handleKeyUp(event)
   
   # code

   mousePosition = pygame.Vector2(pygame.mouse.get_pos())

   game.AssetManager.water_tiles.update(mousePosition, selectivePlankTile)
   game.AssetManager.underTiles.update(mousePosition, selectivePlankTile)
   game.screen.fill("sky blue")
   game.AssetManager.underTiles.draw(game.screen)
   game.AssetManager.water_tiles.draw(game.screen)

   game.updateObjects()

   game.AssetManager.plank_tiles.draw(game.screen)
   game.AssetManager.placableTiles.draw(game.screen)

   mouseButtons = pygame.mouse.get_pressed()

   if player.hand.item and player.hand.item.type == "hammer":
      closestTile = game.find_closest_tile(selected=selected, mousePosition=mousePosition)
      if closestTile:
         selectivePlankTile.rect.topleft = closestTile.rect.topleft
         if mouseButtons[0]:
            closestTile.spawnPlank()

      game.render(selectivePlankTile.image, (selectivePlankTile.rect.topleft))
      

   dx = mousePosition.x - player.position.x
   dy = mousePosition.y - player.position.y
   angle = math.atan2(dy, dx)
   angle_degrees = math.degrees(angle)
   player.angle = angle_degrees

   player.update(mousePosition)
   game.render(player.image, player.position)

   hud.handleUI()

   pygame.display.update()

   game.clock.tick(60)
   fps = int(game.clock.get_fps())
   pygame.display.set_caption(f"Raft 2 - FPS: {fps}")
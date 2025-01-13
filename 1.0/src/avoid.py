import random
import math
import os
import sys
import pygame as pg
from pygame import Vector2, mixer, font

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

class Game:
    pg.init()
    mixer.init()
    font.init()

    program_icon = pg.image.load('assets\\img\\dodgeball_img.png')
    pg.display.set_icon(program_icon)
    pg.display.set_caption("Avoid") 

    def __init__(self):
        self.SCREEN_DIM = Vector2(600, 600)
        self.screen = pg.display.set_mode((self.SCREEN_DIM.x, self.SCREEN_DIM.y))
        
        self.clock = pg.time.Clock()
        self.running = False
        self.delta_time = 0
        self.player = Player(self)
        self.balls = [Ball(self)]
        self.delta_time = 0
        self.time_elapsed = 0
        self.level = 0
        self.highscore = 0
        self.std_font = font.Font("assets\\fonts\\minecraft_font.ttf", 18) 
        font

    def getPointToScreen(self, point: Vector2):
        return Vector2(((point.x / 1000) * self.SCREEN_DIM.x + self.SCREEN_DIM.x) / 2,
                    (-(point.y / 1000) * self.SCREEN_DIM.y + self.SCREEN_DIM.y) / 2)
    
    def renderScore(self):
        if self.highscore != 0:
            highscore = "HI  " + "{:05d}".format(self.highscore)
            highscore_surface = self.std_font.render(highscore, False, 'white')
            self.screen.blit(highscore_surface, (410, 10))
        score = "{:05d}".format(math.floor(self.time_elapsed / 0.1))
        score_surface = self.std_font.render(score, False, 'white')
        self.screen.blit(score_surface, (520, 10))

    def printEntities(self): 
        for ball in self.balls:
            ball.print()
        self.player.print()

    def updateEntities(self,delta_time):
        for ball in self.balls:
            ball.update(delta_time)
        self.player.update(delta_time)

    def GameOver(self):
        mixer.Sound("assets\\sfx\\game_over.mp3").play()
        self.player = Player(game)
        self.balls = [Ball(game)]
        score = math.floor(self.time_elapsed / 0.1)
        if score > self.highscore:
            self.highscore = score
        self.time_elapsed = 0
        self.running = False
        

    def checkGameOver(self):
        for ball in self.balls:
            if Vector2.distance_to(self.player.pos, ball.pos) < 60:
                self.GameOver()
        
        if self.player.pos.x > 980 or self.player.pos.x < -980:
            self.GameOver()
        if self.player.pos.y > 980 or self.player.pos.y < -980:
            self.GameOver()

    def updateLevel(self):
        old_level = self.level
        self.level = self.time_elapsed // 10
        if old_level != self.level and self.level != 0:
            mixer.Sound("assets\\sfx\\next_level.mp3").play()
            self.balls.append(Ball(game))

class Entity():
    def __init__(self, game, pos, vel):
        self.game = game
        self.pos = pos
        self.vel = vel

    def update(self, delta_time):
        self.pos += self.vel * delta_time

class Player(Entity):
    def __init__(self, game):
        super().__init__(game, 
                         Vector2(0, 0),
                         Vector2(300, 0))
        self.base_velocity = 1000
        
    def print(self):
        left_top = game.getPointToScreen(Vector2(self.pos.x - 20, self.pos.y + 20))
        width_height = Vector2(20, 20)
        pg.draw.rect(game.screen, 'white', pg.Rect(left_top, width_height))

    def handlePlayerInput(self):
        keyboard = pg.key.get_pressed()
        direction = Vector2(0, 0)
        if keyboard[pg.K_w]:
            direction.y += 1
        if keyboard[pg.K_a]:
            direction.x += -1
        if keyboard[pg.K_s]:
            direction.y += -1
        if keyboard[pg.K_d]:
            direction.x += 1
        if direction == Vector2(0, 0):
            self.vel = Vector2(0, 0)
            return
        Vector2.normalize_ip(direction)
        self.vel = direction * self.base_velocity     

    def update(self, delta_time):
        self.handlePlayerInput()
        super().update(delta_time)


class Ball(Entity):
    def __init__(self, game):
        angle = random.uniform(-math.pi, math.pi)
        vel = Vector2(math.cos(angle) * 1000, math.sin(angle) * 1000)
        pos = Vector2(random.randint(-1000, 1000), random.randint(-1000, 1000))
        while Vector2.distance_to(pos, game.player.pos) < 500:
            pos = Vector2(random.randint(-1000, 1000), random.randint(-1000, 1000))

        super().__init__(game,
                         pos,
                         vel)
        
    def print(self):
        center = game.getPointToScreen(self.pos)
        pg.draw.circle(game.screen, pg.Color(127, 0, 0), center, 10)
        pg.draw.circle(game.screen, 'red', center, 10, 1)

    def handleBouncing(self):
        if self.pos.x > 980 or self.pos.x < -980:
            if self.pos.x > 980:
                self.pos.x = 980
            else:
                self.pos.x = -980
            self.vel.x = -self.vel.x
            mixer.Sound("assets\\sfx\\bounce.mp3").play()
        if self.pos.y > 980 or self.pos.y < -980:
            if self.pos.y > 980:
                self.pos.y = 980
            else:
                self.pos.y = -980
            self.vel.y = -self.vel.y
            mixer.Sound("assets\\sfx\\bounce.mp3").play()

    def update(self, delta_time):
        self.handleBouncing()
        super().update(delta_time)

game = Game()


while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
    
    game.screen.fill(pg.Color(15, 15, 15))
    if game.running:
        game.checkGameOver()
        game.updateLevel()
        game.updateEntities(game.delta_time)
        game.printEntities()
        game.renderScore()
        game.time_elapsed += game.delta_time
    else:
        label = game.std_font.render("Press WASD to start", False, 'white')
        game.screen.blit(label, (190, 280))

        keyboard = pg.key.get_pressed()
        if keyboard[pg.K_w] or keyboard[pg.K_a] or keyboard[pg.K_s] or keyboard[pg.K_d]:
            game.running = True
    pg.display.flip()
    game.delta_time = game.clock.tick() / 1000
    
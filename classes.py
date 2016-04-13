# классы и функции

import pygame, sys, random, os
from consts import *

class Doodle(pygame.sprite.Sprite):
  ''' класс для главного персонажа '''
  def __init__(self, x, y):
    ''' конструктор класса '''
    self.image = pygame.image.load(os.path.join("pics", "doodle.png"))
    self.rect = self.image.get_rect()
    self.mask = pygame.mask.from_surface(self.image)
    self.rect.midbottom = x, y   # координаты середины нижнего основания doodle
    self.startpos       = [x, y] # позиция главного персонажа на сцене в момент отталкивания от платформы
    self.startspeedY    = 60     # начальная скорость по оси ординат
    self.repstarttime   = 0      # начальное время отталкивания
    self.speedX         = 3      # скорость перемещения вдоль оси абсцисс
    self.pastpos        = self.rect.y
    self.belowmarkline  = False  # по умолчанию предположим, что башка doodle не ниже демаркационной линии (середины экрана)
    self.transition     = False  # по умолчанию предположим, что doodle не перешел через демаркационную линию
    self.apexjump       = abs(int(self.startspeedY * self.startspeedY/GRAVITY - GRAVITY * (self.startspeedY/GRAVITY)**2/2)) # высота прыжка doodle
    self.freeze         = False  # флаг заморозки движения doodle по оси Y
    self.deltafreeze    = 0      # расстояние от замороженного doodle до платформы отталкивания
    self.heightmarkline = 500    # высота условной демаркационной линии, выше которой doodle не может подняться
  
  def getDirection(self):
    ''' вычислить направление движения вдоль оси Y (True - вниз) '''
    presentpos = self.rect.y
    delta = presentpos - self.pastpos
    self.pastpos = presentpos
    if delta < 0: return False
    else: return True
    
  def moveX(self, flagleft, flagright):
    ''' движение вдоль оси X '''
    if flagleft:  self.rect = self.rect.move([-self.speedX, 0])
    if flagright: self.rect = self.rect.move([self.speedX, 0])
    
  def initjump(self, abstime, sled):
    ''' подготовка к прыжку '''
    self.repstarttime = abstime
    self.startpos[1]  = sled.rect.y
    ''' костыль '''
    if self.rect.y >= 500: self.heightmarkline = 450
    else: self.heightmarkline = self.rect.y - 50
    
  def logicjump(self, abstime):
    ''' логика прыжка '''
    self.rect.bottom = int(self.startpos[1] - self.startspeedY * (abstime - self.repstarttime) + GRAVITY * (abstime - self.repstarttime)**2/2)
  
  def checkTransition(self):
    ''' отслеживание перехода через демаркационную линию '''
    if self.rect.y >= self.heightmarkline: self.belowmarkline = True
    if self.belowmarkline and self.rect.y < self.heightmarkline:
      self.belowmarkline = False
      return True
    return False
      

class Sled(pygame.sprite.Sprite):
  ''' класс для платформы '''
  def __init__(self, x, y):
    pygame.sprite.Sprite.__init__(self)
    self.image = pygame.image.load(os.path.join("pics", "sled.png"))
    self.rect = self.image.get_rect()
    self.rect.midbottom = x, y
    self.startpos       = [x, y] # позиция платформы на сцене перед началом опускания

class Scene(pygame.Surface):
  ''' класс для сцены '''
  def __init__(self, size):
    pygame.Surface.__init__(self, size)
    self.rect           = self.get_rect()
    self.numsleds       = 200   # количество платформ на сцене
    self.group_sleds    = []    # список, содержащий все платформы сцены
    self.pulldown       = False # флаг движения платформ вниз
    
    ''' генерация начальной группы платформ '''
    self.group_sleds.append(Sled(512, 580)) # первая платформа всегда на фиксированной позиции под doodle
    for i in range(0, self.numsleds-1): self.group_sleds.append(self.createSled())
    
  def createSled(self):
    ''' генерация ровно одной платформы '''
    return Sled(random.randint(0, WIDTH_SCREEN), self.group_sleds[-1].rect.y - random.randint(0, MAXGAPSLEDS))
  
  def Draw(self):
    ''' отрисовка объектов на сцене '''
    self.fill(WHITE)
    #pygame.draw.line(self, (0, 0, 0), (0, 400), (WIDTH_SCREEN, 400), 1)
    for sled in self.group_sleds: self.blit(sled.image, sled.rect)
  
  def initpullDown(self, doodle):
    ''' подготовка к опусканию платформ '''
    self.pulldown = True                                              # активируем флаг движения платформ вниз
    doodle.freeze = True                                              # замораживаем doodle
    for sled in self.group_sleds: sled.startpos[1] = sled.rect.bottom # находим стартовые местоположения платформ
    doodle.deltafreeze = doodle.startpos[1] - doodle.rect.bottom      # находим расстояние от платформы отталкивания
    return doodle.apexjump - doodle.deltafreeze                       # расстояние, на которое нужно опустить все платформы

  def pullDown(self, doodle, abstime):
    ''' спустить вниз платформы '''
    for sled in self.group_sleds:
      sled.rect.bottom = int(sled.startpos[1] - doodle.deltafreeze + doodle.startspeedY * (abstime - doodle.repstarttime) - GRAVITY * (abstime - doodle.repstarttime)**2/2)

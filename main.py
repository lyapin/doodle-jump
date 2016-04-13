#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Authors: Lyapin Evgeniy, Milke Alena
# Consultant: grishnan
# E-mails: grishnan@gmail.com
# License: CC BY-SA 3.0
# Description: Клон игры «Doodle Jump»

from classes import *

''' ИГРОВАЯ ИНИЦИАЛИЗАЦИЯ '''
pygame.init()
clock = pygame.time.Clock()
SCREEN = pygame.display.set_mode(SIZE_SCREEN)
pygame.display.set_caption("Doodle Jump")

scene = Scene((WIDTH_SCREEN, HEIGHT_SCREEN)) # создаём сцену
                           
doodle = Doodle(512, 580)                    # создаём главного персонажа

while True:
  
  ''' абсолютное время игровой вселенной '''
  abstime = pygame.time.get_ticks()/TIMESCALE
  
  ''' обработчик событий '''
  for event in pygame.event.get():
    if event.type == pygame.QUIT: pygame.quit(); sys.exit()
  keys = pygame.key.get_pressed()
  
  ''' логика движения вдоль оси X '''
  doodle.moveX(keys[pygame.K_LEFT], keys[pygame.K_RIGHT])
  
  ''' отслеживание столкновения персонажа с платформами '''
  if not doodle.freeze :
    for sled in scene.group_sleds:
      if pygame.sprite.collide_mask(doodle, sled) != None:
        if doodle.getDirection() and doodle.rect.centery < sled.rect.y:
          doodle.initjump(abstime, sled)
      doodle.logicjump(abstime)
  
  ''' перемещение платформ вниз по оси Y '''
  if not scene.pulldown:
    doodle.transition = doodle.checkTransition()                 # проверяем факт перехода doodle через демаркационную линию
    if doodle.transition: deltamove = scene.initpullDown(doodle) # как только факт перехода установлен, подготавливаем опускание платформ
    
  if scene.pulldown:                             # если платформы должны перемещаться вниз, то
    if scene.group_sleds[-1].rect.bottom - scene.group_sleds[-1].startpos[1] != deltamove:
      scene.pullDown(doodle, abstime)
    else:                                        # это потенциально багнутое место, т. к. выполнение этой ветки возможно при достижении только точного равенства значений, указанных в условии
      scene.pulldown = False                     # останавливаем платформы
      doodle.freeze  = False                     # размораживаем doodle
      doodle.startpos[1] += deltamove            # перевычисляем местоположение doodle так, чтобы он сразу начинал падать
    
  ''' отрисовка объектов '''
  scene.Draw()                                   # рисуем объекты на сцене
  scene.blit(doodle.image, doodle.rect)          # рисуем главного героя на сцене
  SCREEN.blit(scene, scene.rect)                 # рисуем сцену поверх экрана
  
  pygame.display.update()
  clock.tick(FPS)

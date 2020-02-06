import pygame  # подключение библиотек
import random
import os
import copy


def spawn_ship(row):  # функция для спавна новых кораблей на поле
    if SHIPS:  # проверка наличия оставшихся кораблей
        index = random.randrange(len(SHIPS))  # определение нового корабля
        n = SHIPS.pop(index)  # определение его уровня
        EnemyShip(n, row, game_all_sprites, ship_sprites)  # создание вражеского корабля


def terminate():  # функция завершения работы программы
    global running  # остановка цикла программы
    running = False
    with open(os.path.join('data', 'save.txt'), 'w') as f:
        # сохранение необходимых переменных в файл
        f.write(str(MY_HP) + '\n')
        f.write(str(MY_DAMAGE) + '\n')
        f.write(str(SHIP_VELOCITY) + '\n')
        f.write('\n'.join([str(e) for e in LEVEL_STARS]))


class LevelButton(pygame.sprite.Sprite):  # класс кнопки в меню уровней
    def __init__(self, n, *groups):
        super().__init__(*groups)
        self.n = n
        self.image = pygame.transform.scale(pygame.image.load(os.path.join('data', 'gui',
                                                                           'Ship_Parts',
                                                                           'Table_03.png')),
                                            (96, 96))  # загрузка изображения кнопки
        self.rect = self.image.get_rect()
        if (n - 1) // 5 == 0:  # задание координат кнопки
            self.rect.y = (SIZE[1] - 200) / 2
        else:
            self.rect.y = (SIZE[1] - 200) / 2 + 104
        self.rect.x = (SIZE[0] - 512) / 2 + 104 * ((n - 1) % 5)
        rendered_number = FONT.render(str(n), 1, pygame.color.Color('white'))
        # создание надписи с номером уровня
        self.image.blit(rendered_number, ((96 - rendered_number.get_rect().w) // 2,
                                          # добавление надписи на изображение
                                          (96 - rendered_number.get_rect().h) // 2))

    def update(self, *args):
        if args and self.rect.collidepoint(args[0].pos):  # проверка на нажатие на кнопку
            button_sound.play()  # проигрывание звука нажатия
            global current_location  # изменение текущих локации и уровня
            global current_level
            current_location = 'start_menu'
            current_level = self.n


class MyShip(pygame.sprite.Sprite):  # класс моего корабля
    def __init__(self, hp, damage, *groups):
        super().__init__(*groups)
        self.explosing = False  # определение нужных переменных
        self.power = 3
        self.c1 = 0
        self.c2 = 0
        self.image = pygame.image.load(os.path.join('data', 'ships', 'Ship1', 'Ship1.png'))
        # загрузка изображения корабля
        self.rect = self.image.get_rect()
        self.images = [pygame.image.load(os.path.join('data', 'anim', 'Explosions',
                                                      # загрузка изображений взрыва корабля
                                                      'Ship1_Explosion', str(i + 1).rjust(3, '0')
                                                      + '.png'))
                       for i in range(10)]
        self.hp = hp
        self.damage = damage
        self.exhaust = Exhaust(1, game_all_sprites, other_sprites)  # создание выхлопов корабля
        self.exhaust.rect.x, self.exhaust.rect.y = 74, (SIZE[1] - 160) / 2 + 116
        # задание координат выхлопов

    def get_shot(self, damage):  # функция принятия выстрела
        self.hp -= damage  # уменьшение hp
        if self.hp <= 0:  # проверка на смерть
            self.explosing = True  # взрыв корабля
            explosion_sound.play()  # звук взрыва
            self.exhaust.kill()  # удаление выхлопов корабля
            self.image = self.images[0]  # установка изображения взрыва
            self.rect.x -= 32  # корректировка координат нового изображения
            self.rect.y -= 33

    def update(self):
        if self.power < 3:  # добавление энергии для стрельбы
            self.power += 0.01
        if self.explosing:
            self.c2 = (self.c2 + 1) % 5  # изменение изображений взрыва
            if not self.c2:
                self.c1 += 1
                if self.c1 < 10:
                    self.image = self.images[self.c1]
                else:
                    self.kill()  # уничтожение корабля
                    global you_lose
                    you_lose = True  # установка поражения


class EnemyShip(pygame.sprite.Sprite):  # класс корабля противника
    def __init__(self, n, row, *groups):
        super().__init__(*groups)
        self.row = row  # сохранение необходимых переменных
        self.explosing = False
        self.flying = True
        self.n = n
        self.c1 = 0
        self.c2 = 0
        self.hp = (self.n - 1) * 25
        self.d = {1: 10, 2: 12, 3: 11, 4: 11, 5: 11, 6: 11}
        # количество изображений взрыва для разных кораблей
        self.a = self.d[n]
        self.images = [pygame.transform.flip(pygame.image.load(os.path.join('data', 'anim',
                                                                            'Explosions', 'Ship' +
                                                                            str(n) + '_Explosion',
                                                                            str(k + 1).rjust(3, '0')
                                                                            + '.png')), True, False)
                       # загрузка изображений взрыва
                       for k in range(self.a)]
        self.image = pygame.transform.flip(pygame.image.load(os.path.join('data', 'ships',
                                                                          'Ship' + str(n), 'Ship' +
                                                                          str(n) + '.png')), True,
                                           # загрузка изображения корабля
                                           False)
        self.rect = self.image.get_rect()
        if n == 2:  # установка конечных координат корабля
            self.finish = SIZE[0] - self.rect.w - 96
        elif n == 3:
            self.finish = SIZE[0] - self.rect.w - 88
        elif n == 4:
            self.finish = SIZE[0] - self.rect.w - 84
        elif n == 5:
            self.finish = SIZE[0] - self.rect.w - 80
        elif n == 6:
            self.finish = SIZE[0] - self.rect.w - 68
        self.rect.y = 128 + 96 * (row - 1) + (96 - self.rect.h) / 2
        # установка начальных координат корабля
        self.rect.x = SIZE[0]
        self.mask = pygame.mask.from_surface(self.image)  # установка маски корабля
        self.exhaust = Exhaust(self.n, game_all_sprites, other_sprites)
        # создание выхлопов корабля
        if n == 2:  # задание координат выхлопов
            self.exhaust.rect.x, self.exhaust.rect.y = \
                self.rect.x + self.rect.w - 30, self.rect.y + \
                (self.rect.h - self.exhaust.rect.h) / 2
        elif n == 3:
            self.exhaust.rect.x, self.exhaust.rect.y = \
                self.rect.x + self.rect.w - 24, self.rect.y + \
                (self.rect.h - self.exhaust.rect.h) / 2
        elif n == 4:
            self.exhaust.rect.x, self.exhaust.rect.y = \
                self.rect.x + self.rect.w - 16, self.rect.y + \
                (self.rect.h - self.exhaust.rect.h) / 2 + 2
        elif n == 5:
            self.exhaust.rect.x, self.exhaust.rect.y = \
                self.rect.x + self.rect.w - 10, self.rect.y + \
                (self.rect.h - self.exhaust.rect.h) / 2 + 9
        elif n == 6:
            self.exhaust.rect.x, self.exhaust.rect.y = \
                self.rect.x + self.rect.w - 24, self.rect.y + \
                (self.rect.h - self.exhaust.rect.h) / 2

    def get_shot(self, damage):  # функция принятия выстрела
        self.hp -= damage  # уменьшение hp
        if self.hp <= 0:  # проверка на смерть
            self.explosing = True  # взрыв корабля
            explosion_sound.play()  # звук взрыва
            self.exhaust.kill()  # удаление выхлопов корабля
            self.c1 = 0
            self.c2 = 0
            self.image = self.images[0]  # установка изображения взрыва
            if self.n == 2:  # корректировка координат нового изображения
                self.rect.x += 6
                self.rect.y -= 1
            elif self.n == 3:
                self.rect.x -= 63
                self.rect.y -= 64
            elif self.n == 4:
                self.rect.x -= 64
                self.rect.y -= 64
            elif self.n == 5:
                self.rect.x -= 60
                self.rect.y -= 57
            elif self.n == 6:
                self.rect.x -= 63
                self.rect.y -= 62

    def update(self):
        if self.flying:
            self.rect.x -= SHIP_VELOCITY  # подход корабля к стартовой позиции
            if self.rect.x <= self.finish:
                self.rect.x = self.finish
                self.flying = False
            if self.n == 2:  # задание координат выхлопов
                self.exhaust.rect.x, self.exhaust.rect.y = \
                    self.rect.x + self.rect.w - 30, self.rect.y + \
                    (self.rect.h - self.exhaust.rect.h) / 2
            elif self.n == 3:
                self.exhaust.rect.x, self.exhaust.rect.y = \
                    self.rect.x + self.rect.w - 24, self.rect.y + \
                    (self.rect.h - self.exhaust.rect.h) / 2
            elif self.n == 4:
                self.exhaust.rect.x, self.exhaust.rect.y = \
                    self.rect.x + self.rect.w - 16, self.rect.y + \
                    (self.rect.h - self.exhaust.rect.h) / 2 + 2
            elif self.n == 5:
                self.exhaust.rect.x, self.exhaust.rect.y = \
                    self.rect.x + self.rect.w - 10, self.rect.y + \
                    (self.rect.h - self.exhaust.rect.h) / 2 + 9
            elif self.n == 6:
                self.exhaust.rect.x, self.exhaust.rect.y = \
                    self.rect.x + self.rect.w - 24, self.rect.y + \
                    (self.rect.h - self.exhaust.rect.h) / 2
        elif self.explosing:
            self.c2 = (self.c2 + 1) % 5
            if not self.c2:
                self.c1 += 1
                if self.c1 < self.a:
                    self.image = self.images[self.c1]  # изменение изображения взрыва
                else:
                    self.kill()  # уничтожение корабля
                    spawn_ship(self.row)  # спавн нового корабля на его место
        else:
            self.c1 = (self.c1 + 1) % 50
            if not self.c1:
                shot = Shot(self.n, (self.n - 1) * 25, game_all_sprites, other_sprites)
                # выстрел корабля
                if self.n == 2:  # установка координат выстрела
                    shot.rect.x = self.rect.x - 24
                    shot.rect.y = self.rect.y + 32
                elif self.n == 3:
                    shot.rect.x = self.rect.x - 40
                    shot.rect.y = self.rect.y + 35
                elif self.n == 4:
                    shot.rect.x = self.rect.x - 40
                    shot.rect.y = self.rect.y + 35
                elif self.n == 5:
                    shot.rect.x = self.rect.x - 96
                    shot.rect.y = self.rect.y + 6
                elif self.n == 6:
                    shot.rect.x = self.rect.x - 96
                    shot.rect.y = self.rect.y + 2


class Exhaust(pygame.sprite.Sprite):  # класс выхлопов
    def __init__(self, n, *groups):
        super().__init__(*groups)
        self.images = [pygame.image.load(os.path.join('data', 'anim', 'Exhaust', 'Ship' + str(n),
                                                      'Normal_flight', '00' + str(i) + '.png'))
                       for i in range(1, 5)]  # загрузка изображений выхлопов
        if n != 1:  # поворот изображений
            self.images = [pygame.transform.flip(image, True, False) for image in self.images]
        self.image = self.images[0]
        self.c1 = 0
        self.c2 = 0
        self.rect = self.image.get_rect()

    def update(self):
        self.c2 = (self.c2 + 1) % 3  # смена изображения
        if not self.c2:
            self.c1 = (self.c1 + 1) % 4
            self.image = self.images[self.c1]


class Shot(pygame.sprite.Sprite):  # класс выстрела
    def __init__(self, n, damage, *groups):
        super().__init__(*groups)
        self.explosing = False  # установка необходимых переменных
        self.n = n
        self.damage = damage
        self.d = {1: (4, 5), 2: (6, 5), 3: (3, 4), 4: (5, 8), 5: (5, 8), 6: (4, 10)}
        # количество изображений разных фаз полета снаряда в зависимости от уровня корабля
        self.a, self.b = self.d[n]
        self.images1 = [pygame.image.load(os.path.join('data', 'anim', 'Shots', 'Shot' + str(n),
                                                       'shot' + str(n) + '_' + str(j) + '.png'))
                        for j in range(1, self.a + 1)]
        self.images3 = [pygame.image.load(os.path.join('data', 'anim', 'Shots', 'Shot' + str(n),
                                                       'shot' + str(n) + '_exp' + str(j) + '.png'))
                        for j in range(1, self.b + 1)]
        self.image2 = pygame.image.load(os.path.join('data', 'anim', 'Shots', 'Shot' + str(n),
                                                     'shot' + str(n) + '_asset.png'))
        # загрузка изображений трех фаз снаряда
        if n != 1:  # переворот изображений
            self.images1 = [pygame.transform.flip(image, True, False) for image in self.images1]
            self.images3 = [pygame.transform.flip(image, True, False) for image in self.images3]
            self.image2 = pygame.transform.flip(self.image2, True, False)
        self.mask = pygame.mask.from_surface(self.image2)  # создание маски выстрела
        self.image = self.images1[0]  # установка изображения
        self.rect = self.image.get_rect()
        self.c1 = 0
        self.c2 = 0
        shot_sound.play()  # звук снаряда

    def update(self):
        if not self.explosing:
            self.c2 = (self.c2 + 1) % 2
        else:
            self.c2 = (self.c2 + 1) % 4
        if not self.c2 and not self.explosing:
            self.c1 = self.c1 + 1
            if self.c1 < self.a:
                self.image = self.images1[self.c1]  # смена изображения первой фазы
            else:
                self.image = self.image2  # установка изображения второй фазы
                if self.n == 1:  # перемещение выстрела
                    self.rect.x += SHOT_VELOCITY
                else:
                    self.rect.x -= SHOT_VELOCITY
        if self.rect.x > SIZE[0] or self.rect.x < 0 - self.rect.w:
            self.kill()  # уничтожение выстрела при выходе за экран
        if self.explosing:
            if not self.c2:
                self.c1 = self.c1 + 1
                if self.c1 < self.b:
                    self.image = self.images3[self.c1]  # смена изображения третьей фазы
                else:
                    self.kill()  # уничтожение выстрела при взрыве
        else:
            for ship in ship_sprites.sprites():
                if pygame.sprite.collide_mask(self, ship) and not (self.n == 1 and
                                                                   type(ship) == MyShip):
                    # проверка на попадание в корабль
                    self.explosing = True  # взрыв снаряда
                    self.c1 = -1
                    self.c2 = 0
                    ship.get_shot(self.damage)  # принятие снаряда кораблем


pygame.init()  # инициализация pygame
SIZE = 1024, 512  # установка необходимых констант
FPS = 50
SHOT_VELOCITY = 40
SHIPS_DICT = {1: [2, 2, 2, 2, 3, 3],
              2: [2, 2, 3, 3, 4, 4],
              3: [3, 3, 3, 4, 4, 4],
              4: [3, 3, 4, 4, 5, 5],
              5: [4, 4, 4, 5, 5, 5],
              6: [4, 4, 5, 5, 6, 6],
              7: [5, 5, 5, 6, 6, 6],
              8: [5, 5, 6, 6, 6, 6],
              9: [5, 6, 6, 6, 6, 6],
              10: [6, 6, 6, 6, 6, 6]}
FONT = pygame.font.Font(None, 50)
with open(os.path.join('data', 'save.txt'), 'a') as f1:  # загрузка сохранения из файла
    pass
with open(os.path.join('data', 'save.txt'), 'r') as f2:
    arr = f2.readlines()
if not arr:
    SHIP_VELOCITY = 10
    MY_DAMAGE = 25
    MY_HP = 75
    with open(os.path.join('data', 'save.txt'), 'w') as f3:
        f3.write(str(MY_HP) + '\n')
        f3.write(str(MY_DAMAGE) + '\n')
        f3.write(str(SHIP_VELOCITY))
        for _ in range(10):
            f3.write('\n0')
else:
    MY_HP, MY_DAMAGE, SHIP_VELOCITY = [int(e.strip()) for e in arr[:3]]
HP_LEVEL = (MY_HP - 75) // 25  # определение уровней характеристик
DAMAGE_LEVEL = (MY_DAMAGE - 25) // 25
SPEED_LEVEL = (SHIP_VELOCITY - 10) // 2
if arr:  # определение количества звезд, полученных за уровни
    LEVEL_STARS = [int(e) for e in arr[3:]]
else:
    LEVEL_STARS = [0] * 10
MY_STARS = sum(LEVEL_STARS) - HP_LEVEL * (HP_LEVEL + 1) // 2 - DAMAGE_LEVEL * (DAMAGE_LEVEL + 1) //\
           2 - SPEED_LEVEL * (SPEED_LEVEL + 1) // 2  # определение количества оставшихся звезд
screen = pygame.display.set_mode(SIZE)
game_all_sprites = pygame.sprite.Group()  # создание спрайтов и их групп
ship_sprites = pygame.sprite.Group()
other_sprites = pygame.sprite.Group()
main_menu_all_sprites = pygame.sprite.Group()
main_menu_back_sprite = pygame.sprite.Group()
main_menu_button_sprites = pygame.sprite.Group()
main_menu_background = pygame.sprite.Sprite(main_menu_all_sprites, main_menu_back_sprite)
main_menu_background.image = pygame.transform.rotate(pygame.image.load(os.path.join('data', 'gui',
                                                                                    'Main_Menu',
                                                                                    'BG.png')), 90)
start_button = pygame.sprite.Sprite(main_menu_all_sprites, main_menu_button_sprites)
start_button.image = pygame.transform.scale(pygame.image.load(os.path.join('data', 'gui',
                                                                           'Main_Menu',
                                                                           'Start_BTN.png')),
                                            (328, 96))
start_button.rect = start_button.image.get_rect()
start_button.rect.x = (SIZE[0] - 328) // 2
start_button.rect.y = (SIZE[1] - 96) // 2 - 80
exit_button = pygame.sprite.Sprite(main_menu_all_sprites, main_menu_button_sprites)
exit_button.image = pygame.transform.scale(pygame.image.load(os.path.join('data', 'gui',
                                                                          'Main_Menu',
                                                                          'Exit_BTN.png')),
                                           (328, 96))
exit_button.rect = exit_button.image.get_rect()
exit_button.rect.x = (SIZE[0] - 328) // 2
exit_button.rect.y = (SIZE[1] + 96) // 2 + 50
hangar_button = pygame.sprite.Sprite(main_menu_all_sprites, main_menu_button_sprites)
hangar_button.image = pygame.transform.scale(pygame.image.load(os.path.join('data', 'gui',
                                                                            'Level_Menu',
                                                                            'Hangar_BTN.png')),
                                             (96, 96))
hangar_button.rect = hangar_button.image.get_rect()
hangar_button.rect.x = SIZE[0] - 116
hangar_button.rect.y = (SIZE[1] + 96) // 2 + 100
main_menu_background.image = pygame.transform.scale(main_menu_background.image, SIZE)
main_menu_background.rect = main_menu_background.image.get_rect()
hangar_all_sprites = pygame.sprite.Group()
hangar_window_sprite = pygame.sprite.Group()
hangar_icon_sprites = pygame.sprite.Group()
hangar_button_sprites = pygame.sprite.Group()
hangar_window = pygame.sprite.Sprite(hangar_all_sprites, hangar_window_sprite)
hangar_window.image = pygame.transform.scale(pygame.image.load(os.path.join('data', 'gui',
                                                                            'Hangar',
                                                                            'Window.png')),
                                             (329, 490))
hangar_window.rect = hangar_window.image.get_rect()
hangar_window.rect.x = (SIZE[0] - 329) / 2
hangar_window.rect.y = (SIZE[1] - 490) / 2
hangar_header = pygame.sprite.Sprite(hangar_all_sprites, hangar_icon_sprites)
hangar_header.image = pygame.transform.scale(pygame.image.load(os.path.join('data', 'gui',
                                                                            'Hangar',
                                                                            'Header.png')),
                                             (261, 40))
hangar_header.rect = hangar_header.image.get_rect()
hangar_header.rect.x = (SIZE[0] - 261) / 2
hangar_header.rect.y = (SIZE[1] - 490) / 2 + 7
hangar_hp_icon = pygame.sprite.Sprite(hangar_all_sprites, hangar_icon_sprites)
hangar_hp_icon.image = pygame.image.load(os.path.join('data', 'gui', 'Hangar', 'HP_Icon.png'))
hangar_hp_icon.rect = hangar_hp_icon.image.get_rect()
hangar_hp_icon.rect.x = (SIZE[0] - 65) / 2 - 100
hangar_hp_icon.rect.y = 100
hangar_damage_icon = pygame.sprite.Sprite(hangar_all_sprites, hangar_icon_sprites)
hangar_damage_icon.image = pygame.image.load(os.path.join('data', 'gui', 'Hangar',
                                                          'Damage_Icon.png'))
hangar_damage_icon.rect = hangar_damage_icon.image.get_rect()
hangar_damage_icon.rect.x = (SIZE[0] - 65) / 2 - 100
hangar_damage_icon.rect.y = 200
hangar_speed_icon = pygame.sprite.Sprite(hangar_all_sprites, hangar_icon_sprites)
hangar_speed_icon.image = pygame.image.load(os.path.join('data', 'gui', 'Hangar',
                                                         'Speed_Icon.png'))
hangar_speed_icon.rect = hangar_speed_icon.image.get_rect()
hangar_speed_icon.rect.x = (SIZE[0] - 65) / 2 - 100
hangar_speed_icon.rect.y = 300
hangar_hp_button = pygame.sprite.Sprite(hangar_all_sprites, hangar_button_sprites)
hangar_hp_button.image = pygame.transform.scale(pygame.image.load(os.path.join('data', 'gui',
                                                                               'Hangar',
                                                                               'Upgrade_BTN.png')),
                                                (60, 60))
hangar_hp_button.rect = hangar_hp_button.image.get_rect()
hangar_hp_button.rect.x = (SIZE[0] - 65) / 2 + 100
hangar_hp_button.rect.y = 100
hangar_damage_button = pygame.sprite.Sprite(hangar_all_sprites, hangar_button_sprites)
hangar_damage_button.image = pygame.transform.scale(pygame.image.load(
    os.path.join('data', 'gui', 'Hangar', 'Upgrade_BTN.png')), (60, 60))
hangar_damage_button.rect = hangar_damage_button.image.get_rect()
hangar_damage_button.rect.x = (SIZE[0] - 65) / 2 + 100
hangar_damage_button.rect.y = 200
hangar_speed_button = pygame.sprite.Sprite(hangar_all_sprites, hangar_button_sprites)
hangar_speed_button.image = pygame.transform.scale(pygame.image.load(
    os.path.join('data', 'gui', 'Hangar', 'Upgrade_BTN.png')), (60, 60))
hangar_speed_button.rect = hangar_speed_button.image.get_rect()
hangar_speed_button.rect.x = (SIZE[0] - 65) / 2 + 100
hangar_speed_button.rect.y = 300
hangar_hp_star = pygame.sprite.Sprite(hangar_all_sprites, hangar_icon_sprites)
hangar_hp_star.image = pygame.transform.scale(pygame.image.load(os.path.join('data', 'gui',
                                                                             'Level_Menu',
                                                                             'Star_03.png')),
                                              (73, 70))
hangar_hp_star.rect = hangar_hp_star.image.get_rect()
hangar_hp_star.rect.x = (SIZE[0] - 65) / 2 + 10
hangar_hp_star.rect.y = 90
hangar_damage_star = pygame.sprite.Sprite(hangar_all_sprites, hangar_icon_sprites)
hangar_damage_star.image = pygame.transform.scale(pygame.image.load(os.path.join('data', 'gui',
                                                                                 'Level_Menu',
                                                                                 'Star_03.png')),
                                                  (73, 70))
hangar_damage_star.rect = hangar_damage_star.image.get_rect()
hangar_damage_star.rect.x = (SIZE[0] - 65) / 2 + 10
hangar_damage_star.rect.y = 190
hangar_speed_star = pygame.sprite.Sprite(hangar_all_sprites, hangar_icon_sprites)
hangar_speed_star.image = pygame.transform.scale(pygame.image.load(os.path.join('data', 'gui',
                                                                                'Level_Menu',
                                                                                'Star_03.png')),
                                                 (73, 70))
hangar_speed_star.rect = hangar_speed_star.image.get_rect()
hangar_speed_star.rect.x = (SIZE[0] - 65) / 2 + 10
hangar_speed_star.rect.y = 290
hangar_my_star = pygame.sprite.Sprite(hangar_all_sprites, hangar_icon_sprites)
hangar_my_star.image = pygame.transform.scale(pygame.image.load(os.path.join('data', 'gui',
                                                                             'Level_Menu',
                                                                             'Star_03.png')),
                                              (73, 70))
hangar_my_star.rect = hangar_my_star.image.get_rect()
hangar_my_star.rect.x = (SIZE[0] - 65) / 2 + 10
hangar_my_star.rect.y = 390
if HP_LEVEL == 4:  # удаление кнопок улучшения при достижении максимального уровня характеристик
    hangar_hp_button.kill()
    hangar_hp_star.kill()
if DAMAGE_LEVEL == 4:
    hangar_damage_button.kill()
    hangar_damage_star.kill()
if SPEED_LEVEL == 4:
    hangar_speed_button.kill()
    hangar_speed_star.kill()
level_menu_all_sprites = pygame.sprite.Group()
level_menu_button_sprites = pygame.sprite.Group()
level_menu_back_button = pygame.sprite.Sprite(level_menu_all_sprites, level_menu_button_sprites)
level_menu_back_button.image = pygame.transform.scale(pygame.image.load(
    os.path.join('data', 'gui', 'Hangar', 'Backward_BTN.png')), (96, 96))
level_menu_back_button.rect = level_menu_back_button.image.get_rect()
level_menu_back_button.rect.x = 10
level_menu_back_button.rect.y = 10
for i in range(1, 11):
    LevelButton(i, level_menu_all_sprites, level_menu_button_sprites)
start_menu_all_sprites = pygame.sprite.Group()
start_menu_button_sprites = pygame.sprite.Group()
start_menu_icon_sprites = pygame.sprite.Group()
start_menu_star1_sprite = pygame.sprite.Group()
start_menu_star2_sprite = pygame.sprite.Group()
start_menu_star3_sprite = pygame.sprite.Group()
start_menu_star1 = pygame.sprite.Sprite(start_menu_all_sprites, start_menu_icon_sprites,
                                        start_menu_star1_sprite)
start_menu_star1.image = pygame.transform.scale(pygame.image.load(os.path.join('data', 'gui',
                                                                               'Level_Menu',
                                                                               'Star_03.png')),
                                                (73, 70))
start_menu_star1.rect = start_menu_star1.image.get_rect()
start_menu_star1.rect.x = (SIZE[0] - 73) / 2 - 100
start_menu_star1.rect.y = 100
start_menu_star2 = pygame.sprite.Sprite(start_menu_all_sprites, start_menu_icon_sprites,
                                        start_menu_star2_sprite)
start_menu_star2.image = pygame.transform.scale(pygame.image.load(os.path.join('data', 'gui',
                                                                               'Level_Menu',
                                                                               'Star_03.png')),
                                                (73, 70))
start_menu_star2.rect = start_menu_star2.image.get_rect()
start_menu_star2.rect.x = (SIZE[0] - 73) / 2
start_menu_star2.rect.y = 100
start_menu_star3 = pygame.sprite.Sprite(start_menu_all_sprites, start_menu_icon_sprites,
                                        start_menu_star3_sprite)
start_menu_star3.image = pygame.transform.scale(pygame.image.load(os.path.join('data', 'gui',
                                                                               'Level_Menu',
                                                                               'Star_03.png')),
                                                (73, 70))
start_menu_star3.rect = start_menu_star3.image.get_rect()
start_menu_star3.rect.x = (SIZE[0] - 73) / 2 + 100
start_menu_star3.rect.y = 100
start_menu_play_button = pygame.sprite.Sprite(start_menu_all_sprites, start_menu_button_sprites)
start_menu_play_button.image = pygame.image.load(os.path.join('data', 'gui', 'Level_Menu',
                                                              'Play_BTN.png'))
start_menu_play_button.rect = start_menu_play_button.image.get_rect()
start_menu_play_button.rect.x = (SIZE[0] - start_menu_play_button.rect.w) / 2
start_menu_play_button.rect.y = 250
you_win_header_sprite = pygame.sprite.Group()
you_win_record_sprite = pygame.sprite.Group()
you_win_button_sprites = pygame.sprite.Group()
you_win_header = pygame.sprite.Sprite(you_win_header_sprite)
you_win_header.image = pygame.transform.scale(pygame.image.load(os.path.join('data', 'gui',
                                                                             'You_Win',
                                                                             'Header.png')),
                                              (271, 40))
you_win_header.rect = you_win_header.image.get_rect()
you_win_header.rect.x = (SIZE[0] - 271) / 2
you_win_header.rect.y = 20
you_win_record = pygame.sprite.Sprite(you_win_record_sprite)
you_win_record.image = pygame.transform.scale(pygame.image.load(os.path.join('data', 'gui',
                                                                             'You_Win',
                                                                             'Record.png')),
                                              (249, 40))
you_win_record.rect = you_win_record.image.get_rect()
you_win_record.rect.x = (SIZE[0] - 249) / 2
you_win_record.rect.y = 200
you_win_replay_button = pygame.sprite.Sprite(you_win_button_sprites)
you_win_replay_button.image = pygame.image.load(os.path.join('data', 'gui', 'You_Win',
                                                             'Replay_BTN.png'))
you_win_replay_button.rect = you_win_replay_button.image.get_rect()
you_win_replay_button.rect.x = (SIZE[0] - you_win_replay_button.rect.w) / 2
you_win_replay_button.rect.y = 280
you_lose_all_sprites = pygame.sprite.Group()
you_lose_header = pygame.sprite.Sprite(you_lose_all_sprites)
you_lose_header.image = pygame.transform.scale(pygame.image.load(os.path.join('data', 'gui',
                                                                              'You_Lose',
                                                                              'Header.png')),
                                               (302, 40))
you_lose_header.rect = you_lose_header.image.get_rect()
you_lose_header.rect.x = (SIZE[0] - 302) / 2
you_lose_header.rect.y = 20
pause_all_sprites = pygame.sprite.Group()
pause_header = pygame.sprite.Sprite(pause_all_sprites)
pause_header.image = pygame.transform.scale(pygame.image.load(os.path.join('data', 'gui', 'Pause',
                                                                           'Header.png')),
                                            (203, 40))
pause_header.rect = pause_header.image.get_rect()
pause_header.rect.x = (SIZE[0] - 203) / 2
pause_header.rect.y = 20
pause_menu_button = pygame.sprite.Sprite(pause_all_sprites)
pause_menu_button.image = pygame.image.load(os.path.join('data', 'gui', 'Pause', 'Menu_BTN.png'))
pause_menu_button.rect = pause_menu_button.image.get_rect()
pause_menu_button.rect.x = (SIZE[0] - pause_menu_button.rect.w) / 2
pause_menu_button.rect.y = 70
health_bar_sprite = pygame.sprite.Group()
health_dot1_sprite = pygame.sprite.Group()
health_dot2_sprite = pygame.sprite.Group()
health_dot3_sprite = pygame.sprite.Group()
health_dot4_sprite = pygame.sprite.Group()
health_dot5_sprite = pygame.sprite.Group()
health_dot6_sprite = pygame.sprite.Group()
health_dot7_sprite = pygame.sprite.Group()
health_bar = pygame.sprite.Sprite(health_bar_sprite)
health_bar.image = pygame.image.load(os.path.join('data', 'gui', 'Main_UI', 'Health_Bar.png'))
health_bar.rect = health_bar.image.get_rect()
health_bar.rect.x = 10
health_bar.rect.y = 10
health_dot1 = pygame.sprite.Sprite(health_dot1_sprite)
health_dot1.image = pygame.image.load(os.path.join('data', 'gui', 'Main_UI', 'Health_Dot.png'))
health_dot1.rect = health_dot1.image.get_rect()
health_dot1.rect.x = 16
health_dot1.rect.y = 16
health_dot2 = pygame.sprite.Sprite(health_dot2_sprite)
health_dot2.image = pygame.image.load(os.path.join('data', 'gui', 'Main_UI', 'Health_Dot.png'))
health_dot2.rect = health_dot2.image.get_rect()
health_dot2.rect.x = 46
health_dot2.rect.y = 16
health_dot3 = pygame.sprite.Sprite(health_dot3_sprite)
health_dot3.image = pygame.image.load(os.path.join('data', 'gui', 'Main_UI', 'Health_Dot.png'))
health_dot3.rect = health_dot3.image.get_rect()
health_dot3.rect.x = 76
health_dot3.rect.y = 16
health_dot4 = pygame.sprite.Sprite(health_dot4_sprite)
health_dot4.image = pygame.image.load(os.path.join('data', 'gui', 'Main_UI', 'Health_Dot.png'))
health_dot4.rect = health_dot4.image.get_rect()
health_dot4.rect.x = 106
health_dot4.rect.y = 16
health_dot5 = pygame.sprite.Sprite(health_dot5_sprite)
health_dot5.image = pygame.image.load(os.path.join('data', 'gui', 'Main_UI', 'Health_Dot.png'))
health_dot5.rect = health_dot5.image.get_rect()
health_dot5.rect.x = 136
health_dot5.rect.y = 16
health_dot6 = pygame.sprite.Sprite(health_dot6_sprite)
health_dot6.image = pygame.image.load(os.path.join('data', 'gui', 'Main_UI', 'Health_Dot.png'))
health_dot6.rect = health_dot6.image.get_rect()
health_dot6.rect.x = 166
health_dot6.rect.y = 16
health_dot7 = pygame.sprite.Sprite(health_dot7_sprite)
health_dot7.image = pygame.image.load(os.path.join('data', 'gui', 'Main_UI', 'Health_Dot.png'))
health_dot7.rect = health_dot7.image.get_rect()
health_dot7.rect.x = 196
health_dot7.rect.y = 16
shot_sound = pygame.mixer.Sound(os.path.join('data', 'Shot.wav'))  # создание необходимых звуков
button_sound = pygame.mixer.Sound(os.path.join('data', 'Button.wav'))
explosion_sound = pygame.mixer.Sound(os.path.join('data', 'Explosion.wav'))
lose_sound = pygame.mixer.Sound(os.path.join('data', 'Lose.wav'))
win_sound = pygame.mixer.Sound(os.path.join('data', 'Win.wav'))
current_location = 'main_menu'  # определение текущей локации и текущего уровня (пока его нет)
current_level = 0
running = True
you_lose = False  # создание переменных победы, поражения и часов
you_win = False
clock = pygame.time.Clock()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()  # завершение программы
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if current_location == 'main_menu':
                if exit_button.rect.collidepoint(event.pos):
                    button_sound.play()  # звук нажатия на кнопку
                    terminate()  # завершение программы
                elif start_button.rect.collidepoint(event.pos):
                    button_sound.play()  # звук нажатия на кнопку
                    current_location = 'level_menu'  # изменение текущей локации
                elif hangar_button.rect.collidepoint(event.pos):
                    button_sound.play()  # звук нажатия на кнопку
                    current_location = 'hangar'  # изменение текущей локации
            elif current_location == 'hangar':
                if hangar_button.rect.collidepoint(event.pos):
                    button_sound.play()  # звук нажатия на кнопку
                    current_location = 'main_menu'  # изменение текущей локации
                elif hangar_hp_button.rect.collidepoint(event.pos):
                    if HP_LEVEL + 1 <= MY_STARS and HP_LEVEL <= 3:
                        # проверка на возможность улучшения
                        button_sound.play()  # звук нажатия на кнопку
                        MY_STARS -= HP_LEVEL + 1  # обновление характеристик
                        HP_LEVEL += 1
                        MY_HP += 25
                        if HP_LEVEL == 4:
                            hangar_hp_button.kill()  # уничтожение кнопки
                            hangar_hp_star.kill()
                elif hangar_damage_button.rect.collidepoint(event.pos):
                    if DAMAGE_LEVEL + 1 <= MY_STARS and DAMAGE_LEVEL <= 3:
                        # проверка на возможность улучшения
                        button_sound.play()  # звук нажатия на кнопку
                        MY_STARS -= DAMAGE_LEVEL + 1  # обновление характеристик
                        DAMAGE_LEVEL += 1
                        MY_DAMAGE += 25
                        if DAMAGE_LEVEL == 4:
                            hangar_damage_button.kill()  # уничтожение кнопки
                            hangar_damage_star.kill()
                elif hangar_speed_button.rect.collidepoint(event.pos):
                    if SPEED_LEVEL + 1 <= MY_STARS and SPEED_LEVEL <= 3:
                        # проверка на возможность улучшения
                        button_sound.play()  # звук нажатия на кнопку
                        MY_STARS -= SPEED_LEVEL + 1  # обновление характеристик
                        SPEED_LEVEL += 1
                        SHIP_VELOCITY += 2
                        if SPEED_LEVEL == 4:
                            hangar_speed_button.kill()  # уничтожение кнопки
                            hangar_speed_star.kill()
            elif current_location == 'level_menu':
                if level_menu_back_button.rect.collidepoint(event.pos):
                    button_sound.play()  # звук нажатия на кнопку
                    current_location = 'main_menu'  # изменение текущей локации
                else:
                    level_menu_all_sprites.update(event)  # проверка нажатия но кнопки уровней
            elif current_location == 'start_menu':
                if level_menu_back_button.rect.collidepoint(event.pos):
                    button_sound.play()  # звук нажатия на кнопку
                    current_location = 'level_menu'  # изменение текущей локации
                elif start_menu_play_button.rect.collidepoint(event.pos):
                    button_sound.play()  # звук нажатия на кнопку
                    current_location = 'game'  # изменение текущей локации
                    my_ship = MyShip(MY_HP, MY_DAMAGE, game_all_sprites, ship_sprites)
                    # создание своего корабля
                    my_ship.rect.x = 100
                    my_ship.rect.y = (SIZE[1] - 160) / 2 + 96
                    SHIPS = copy.deepcopy(SHIPS_DICT[current_level])
                    # создания списка кораблей противника
                    for row in range(1, 5):  # спавн первых 4 кораблей
                        spawn_ship(row)
            elif current_location == 'win_menu' or current_location == 'lose_menu':
                if you_win_replay_button.rect.collidepoint(event.pos):
                    button_sound.play()  # звук нажатия на кнопку
                    current_location = 'game'  # изменение текущей локации
                    my_ship = MyShip(MY_HP, MY_DAMAGE, game_all_sprites, ship_sprites)
                    # создание своего корабля
                    my_ship.rect.x = 100
                    my_ship.rect.y = (SIZE[1] - 160) / 2 + 96
                    SHIPS = copy.deepcopy(SHIPS_DICT[current_level])
                    # создания списка кораблей противника
                    for row in range(1, 5):  # спавн первых 4 кораблей
                        spawn_ship(row)
                elif level_menu_back_button.rect.collidepoint(event.pos):
                    button_sound.play()  # звук нажатия на кнопку
                    current_location = 'level_menu'  # изменение текущей локации
            elif current_location == 'pause':
                if pause_menu_button.rect.collidepoint(event.pos):
                    button_sound.play()  # звук нажатия на кнопку
                    current_location = 'level_menu'  # изменение текущей локации
                    for ship in ship_sprites.sprites():
                        ship.kill()  # уничтожение кораблей и их выхлопов
                        ship.exhaust.kill()
                    for sprite in other_sprites.sprites():
                        sprite.kill()  # уничтожение выстрелов
                    my_ship.kill()  # уничтожение моего корабля и его выхлопа
                    my_ship.exhaust.kill()
                elif you_win_replay_button.rect.collidepoint(event.pos):
                    current_location = 'game'  # изменение текущей локации
                    button_sound.play()  # звук нажатия на кнопку
                    for ship in ship_sprites.sprites():
                        ship.kill()  # уничтожение кораблей и их выхлопов
                        ship.exhaust.kill()
                    for sprite in other_sprites.sprites():
                        sprite.kill()  # уничтожение выстрелов
                    my_ship.kill()  # уничтожение моего корабля и его выхлопа
                    my_ship.exhaust.kill()
                    my_ship = MyShip(MY_HP, MY_DAMAGE, game_all_sprites, ship_sprites)
                    # создание моего корабля
                    my_ship.rect.x = 100  # задание его координат
                    my_ship.rect.y = (SIZE[1] - 160) / 2 + 96
                    SHIPS = copy.deepcopy(SHIPS_DICT[current_level])
                    # создаие списка кораблей противника на уровне
                    for row in range(1, 5):  # спавн первых четырех кораблей
                        spawn_ship(row)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if current_location == 'game' and not my_ship.explosing and my_ship.power >= 1:
                    shot = Shot(1, MY_DAMAGE, game_all_sprites, other_sprites)
                    # создание выстрела моего корабля
                    shot.rect.x = my_ship.rect.x + 64  # задание координат выстрела
                    shot.rect.y = my_ship.rect.y + 16
                    my_ship.power -= 1  # уменьшение энергии моего корабля
            elif event.key == pygame.K_ESCAPE:
                if current_location == 'game':
                    current_location = 'pause'  # изменение текущей локации
                elif current_location == 'pause':
                    current_location = 'game'  # изменение текущей локации
    if current_location == 'main_menu':
        main_menu_back_sprite.draw(screen)  # отображение необходимых спрайтов
        main_menu_button_sprites.draw(screen)
    elif current_location == 'hangar':
        hangar_window_sprite.draw(screen)  # отображение необходимых спрайтов
        hangar_icon_sprites.draw(screen)
        hangar_button_sprites.draw(screen)
        if HP_LEVEL != 4:
            hp_level_rendered = FONT.render(str(HP_LEVEL + 1), 1, pygame.color.Color('white'))
            hp_level_rect = hp_level_rendered.get_rect()
            hp_level_rect.x = (SIZE[0] - 65) / 2 - 20
            hp_level_rect.y = 110
            screen.blit(hp_level_rendered, hp_level_rect)
        if DAMAGE_LEVEL != 4:
            damage_level_rendered = FONT.render(str(DAMAGE_LEVEL + 1), 1,
                                                pygame.color.Color('white'))
            damage_level_rect = damage_level_rendered.get_rect()
            damage_level_rect.x = (SIZE[0] - 65) / 2 - 20
            damage_level_rect.y = 210
            screen.blit(damage_level_rendered, damage_level_rect)
        if SPEED_LEVEL != 4:
            speed_level_rendered = FONT.render(str(SPEED_LEVEL + 1), 1,
                                               pygame.color.Color('white'))
            speed_level_rect = speed_level_rendered.get_rect()
            speed_level_rect.x = (SIZE[0] - 65) / 2 - 20
            speed_level_rect.y = 310
            screen.blit(speed_level_rendered, speed_level_rect)
        star_count_rendered = FONT.render(str(MY_STARS), 1, pygame.color.Color('white'))
        star_count_rect = star_count_rendered.get_rect()
        star_count_rect.x = (SIZE[0] - 65) / 2 - 30
        star_count_rect.y = 410
        screen.blit(star_count_rendered, star_count_rect)
    elif current_location == 'level_menu':
        main_menu_back_sprite.draw(screen)  # отображение необходимых спрайтов
        level_menu_button_sprites.draw(screen)
    elif current_location == 'start_menu':
        hangar_window_sprite.draw(screen)  # отображение необходимых спрайтов
        if LEVEL_STARS[current_level - 1] >= 1:
            start_menu_star1_sprite.draw(screen)
        if LEVEL_STARS[current_level - 1] >= 2:
            start_menu_star2_sprite.draw(screen)
        if LEVEL_STARS[current_level - 1] >= 3:
            start_menu_star3_sprite.draw(screen)
        start_menu_button_sprites.draw(screen)
        rendered_number = FONT.render(str(current_level), 1, pygame.color.Color('white'))
        rendered_number_rect = rendered_number.get_rect()
        rendered_number_rect.x = (SIZE[0] - rendered_number_rect.w) / 2
        rendered_number_rect.y = 23
        screen.blit(rendered_number, rendered_number_rect)
    elif current_location == 'game':
        pressed = pygame.key.get_pressed()  # получение нажатых клавиш
        if pressed[276] and not my_ship.explosing:  # перемещение корабля и его выхлопов
            my_ship.rect.x -= SHIP_VELOCITY
            if my_ship.rect.x < 24:
                my_ship.rect.x = 24
            my_ship.exhaust.rect.x = my_ship.rect.x - 26
        if pressed[275] and not my_ship.explosing:
            my_ship.rect.x += SHIP_VELOCITY
            if my_ship.rect.x > SIZE[0] - 300:
                my_ship.rect.x = SIZE[0] - 300
            my_ship.exhaust.rect.x = my_ship.rect.x - 26
        if pressed[273] and not my_ship.explosing:
            my_ship.rect.y -= SHIP_VELOCITY
            if my_ship.rect.y < 96:
                my_ship.rect.y = 96
            my_ship.exhaust.rect.y = my_ship.rect.y + 18
        if pressed[274] and not my_ship.explosing:
            my_ship.rect.y += SHIP_VELOCITY
            if my_ship.rect.y > SIZE[1] - 64:
                my_ship.rect.y = SIZE[1] - 64
            my_ship.exhaust.rect.y = my_ship.rect.y + 18
        game_all_sprites.update()  # обновление спрайтов
        main_menu_back_sprite.draw(screen)  # отображение необходимых спрайтов
        ship_sprites.draw(screen)
        other_sprites.draw(screen)
        health_bar_sprite.draw(screen)
        if my_ship.hp >= 25:
            health_dot1_sprite.draw(screen)
        if my_ship.hp >= 50:
            health_dot2_sprite.draw(screen)
        if my_ship.hp >= 75:
            health_dot3_sprite.draw(screen)
        if my_ship.hp >= 100:
            health_dot4_sprite.draw(screen)
        if my_ship.hp >= 125:
            health_dot5_sprite.draw(screen)
        if my_ship.hp >= 150:
            health_dot6_sprite.draw(screen)
        if my_ship.hp >= 175:
            health_dot7_sprite.draw(screen)
        if len(ship_sprites.sprites()) == 1 and not you_lose:
            you_win = True  # установка победы
        if you_win:
            win_sound.play()  # звук победы
            current_location = 'win_menu'  # изменение текущей локации
            my_ship.kill()  # уничтожение моего корабля и его выхлопов
            my_ship.exhaust.kill()
            for sprite in other_sprites.sprites():
                sprite.kill()  # уничтожение выстрелов
            if my_ship.hp == MY_HP:
                current_stars = 3  # определение полученных звезд
            elif my_ship.hp >= MY_HP / 2:
                current_stars = 2
            else:
                current_stars = 1
            record = current_stars > LEVEL_STARS[current_level - 1]  # проверка рекорда
            LEVEL_STARS[current_level - 1] = max(LEVEL_STARS[current_level - 1], current_stars)
            # обновление переменых
            MY_STARS = sum(LEVEL_STARS) - HP_LEVEL * (HP_LEVEL + 1) // 2 - DAMAGE_LEVEL *\
                       (DAMAGE_LEVEL + 1) // 2 - SPEED_LEVEL * (SPEED_LEVEL + 1) // 2
        elif you_lose:
            lose_sound.play()  # звук поражения
            current_location = 'lose_menu'  # изменение текущей локации
            for ship in ship_sprites.sprites():
                ship.kill()  # уничтожение кораблей противника
                ship.exhaust.kill()
            for sprite in other_sprites.sprites():
                sprite.kill()  # уничтожение выстрелов
        you_win = False  # сброс переменных победы и поражения
        you_lose = False
    elif current_location == 'win_menu':
        main_menu_back_sprite.draw(screen)  # отображение необходимых спрайтов
        level_menu_button_sprites.draw(screen)
        hangar_window_sprite.draw(screen)
        if current_stars >= 1:
            start_menu_star1_sprite.draw(screen)
        if current_stars >= 2:
            start_menu_star2_sprite.draw(screen)
        if current_stars >= 3:
            start_menu_star3_sprite.draw(screen)
        you_win_button_sprites.draw(screen)
        you_win_header_sprite.draw(screen)
        if record:
            you_win_record_sprite.draw(screen)
    elif current_location == 'lose_menu':
        main_menu_back_sprite.draw(screen)  # отображение необходимых спрайтов
        level_menu_button_sprites.draw(screen)
        hangar_window_sprite.draw(screen)
        you_win_button_sprites.draw(screen)
        you_lose_all_sprites.draw(screen)
    elif current_location == 'pause':
        hangar_window_sprite.draw(screen)  # отображение необходимых спрайтов
        pause_all_sprites.draw(screen)
        you_win_button_sprites.draw(screen)
    pygame.display.flip()  # обновление холста
    clock.tick(FPS)
pygame.quit()  # выход

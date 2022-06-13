"""Asteroids

Реализация геймплея игры 'Астероиды'.
Поиск столкновений на основе квадродеревьев.
"""

import random
from math import pi
import pygame
import pygame_menu
from space_objects import Asteroid, SpaceShip, SpaceObject
from quadtree import Quadnode

FPS = 30
DARK_BLUE = (0, 0, 20)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
ROTATION_ANGLE = 0.1


class Settings:
    """Настройки"""
    params = {
        "size": 800,
        "number": 40,
        "min_radius": 5,
        "max_radius": 15,
        "min_speed": 1,
        "max_speed": 5
    }

    @staticmethod
    def screen_size() -> tuple:
        """Размер окна"""
        return Settings.params["size"], Settings.params["size"]

    @staticmethod
    def menu_size() -> tuple:
        """Размер окна главного меню"""
        return 800, 800

    @staticmethod
    def set_param(param: str, value: str):
        """Установка параметров

        :param param: тип параметра
        :param value: значение
        """
        if value.isdigit():
            Settings.params[param] = int(value)


pygame.init()
pygame.mixer.init()
pygame.display.set_caption("Asteroids")
pygame.display.set_icon(pygame.image.load("resources/icon.ico"))
clock = pygame.time.Clock()
base_surface = pygame.display.set_mode(Settings.screen_size())

heart_i = pygame.image.load("resources/heart.png")
heart_size = heart_i.get_width()
damage_s = pygame.mixer.Sound("resources/damage.mp3")
destroyed_s = pygame.mixer.Sound("resources/destroyed.mp3")
summon_s = pygame.mixer.Sound("resources/summon.mp3")
game_over_s = pygame.mixer.Sound("resources/game_over.mp3")
win_s = pygame.mixer.Sound("resources/win.mp3")


def menu():
    """Запуск главного меню"""
    pygame.display.set_mode(Settings.menu_size())

    menu_ = pygame_menu.Menu("Asteroids", *Settings.menu_size(),
                             theme=pygame_menu.themes.THEME_DARK)
    menu_.add.text_input(
        "Размер стороны окна: ",
        default=Settings.params["size"],
        onchange=lambda value: Settings.set_param("size", value))
    menu_.add.text_input(
        "Количество астероидов: ",
        default=Settings.params["number"],
        onchange=lambda value: Settings.set_param("number", value))
    menu_.add.text_input(
        "Минимальная скорость: ",
        default=Settings.params["min_speed"],
        onchange=lambda value: Settings.set_param("min_speed", value))
    menu_.add.text_input(
        "Максимальная скорость: ",
        default=Settings.params["max_speed"],
        onchange=lambda value: Settings.set_param("max_speed", value))
    menu_.add.text_input(
        "Минимальный радиус: ",
        default=Settings.params["min_radius"],
        onchange=lambda value: Settings.set_param("min_radius", value))
    menu_.add.text_input(
        "Максимальный радиус: ",
        default=Settings.params["max_radius"],
        onchange=lambda value: Settings.set_param("max_radius", value))

    menu_.add.button("Старт", game, font_color=GREEN)
    menu_.add.button("Выход", pygame_menu.events.EXIT, font_color=RED)
    menu_.mainloop(base_surface)


def draw(space_obj: SpaceObject):
    """Отрисовка объекта

    :param space_obj: объект для отрисовки
    """
    if isinstance(space_obj, SpaceShip):
        draw_func = pygame.draw.polygon
        params = ((space_obj.get_corner(SpaceShip.front_corner),
                   space_obj.get_corner(SpaceShip.right_corner),
                   space_obj.get_corner(SpaceShip.left_corner)),)
    else:
        draw_func = pygame.draw.circle
        params = ((space_obj.x, space_obj.y), space_obj.radius)
    draw_func(base_surface, space_obj.color, *params)


def add_asteroid(asteroids: list):
    """Добавление астероидов

    :param asteroids: список астероидов
    """
    for _ in range(Settings.params["number"]):
        speed = random.randint(Settings.params["min_speed"],
                               Settings.params["max_speed"])
        radius = random.randint(Settings.params["min_radius"],
                                Settings.params["max_radius"])
        rotate = random.random() * 2 * pi
        x = random.randint(0, Settings.params["size"])
        y = random.randint(0, Settings.params["size"])
        asteroids.append(Asteroid(pygame.math.Vector2(x, y),
                                  speed, rotate, radius))


def draw_hearts(hearts_number: int):
    """Отображение жизней

    :param hearts_number: число жизней
    """
    for i in range(hearts_number):
        base_surface.blit(heart_i, (1 + (heart_size + 1) * i, 1))


def spaceship_move(spaceship: SpaceShip):
    """Управление кораблем

    :param spaceship: корабль для управления
    """
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        spaceship.give_speed(True)
        spaceship.move()
    else:
        spaceship.give_speed(False)
    if keys[pygame.K_d]:
        spaceship.rotate += ROTATION_ANGLE
    elif keys[pygame.K_a]:
        spaceship.rotate -= ROTATION_ANGLE


def object_interaction(asteroids: list, bullets: list,
                       base_quadrant: Quadnode):
    """Симуляция взаимодействия объектов

    :param asteroids: список астероидов
    :param bullets: список снарядов
    :param base_quadrant: корень квадродерева
    """
    for i in asteroids:
        i.time_dec()
        base_quadrant.insert_object(i)

    for i in bullets:
        if i.time_inc():
            bullets.remove(i)
        base_quadrant.insert_object(i)

    for i in asteroids + bullets:
        if i.destroyed:
            if i in asteroids:
                asteroids.remove(i)
            if i in bullets:
                destroyed_s.play()
                bullets.remove(i)
        i.move()
        draw(i)


def game():
    """Запуск игрового процесса"""
    SpaceObject.max_size = Settings.params["size"]
    pygame.display.set_mode(Settings.screen_size())

    show_quadrants = False
    base_quadrant = Quadnode(pygame.math.Vector2(0, 0),
                             Settings.params["size"])

    asteroids = []
    add_asteroid(asteroids)
    spaceship = SpaceShip()
    bullets = []

    hearts = 5

    running = True
    while running:
        base_surface.fill(DARK_BLUE)

        object_interaction(asteroids, bullets, base_quadrant)

        base_quadrant.insert_object(spaceship)
        spaceship.time_dec()
        draw(spaceship)

        if spaceship.destroyed:
            damage_s.play()
            spaceship.destroyed = False
            if hearts:
                hearts -= 1
            else:
                running = False
                game_over_s.play()
        elif not asteroids:
            win_s.play()
            running = False

        draw_hearts(hearts)

        if show_quadrants:
            base_quadrant.draw_borders(base_surface, pygame.draw.rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bullets.append(spaceship.summon_bullet())
                    summon_s.play()
                if event.key == pygame.K_f:
                    show_quadrants = not show_quadrants

        spaceship_move(spaceship)

        pygame.display.update()

        base_quadrant.leaves.clear()
        base_quadrant.values.clear()
        clock.tick(FPS)

    pygame.display.set_mode(Settings.menu_size())


if __name__ == '__main__':
    menu()

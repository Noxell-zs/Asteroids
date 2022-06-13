"""Реализация космических объектов"""

from math import cos, sin, pi
from pygame.math import Vector2
from numbers import Real

SHIP_SPEED = 5
SHIP_RADIUS = 15
BULLET_SPEED = 8
BULLET_RADIUS = 3
THIRD_OF_CIRCLE = 2 * pi / 3
BULLET_DIST = 1.3

WHITE = (255, 255, 255)
YELLOW = (240, 240, 210)
RED = (240, 80, 80)
VIOLET = (170, 55, 170)


class SpaceObject:
    """Класс космического объекта"""
    max_size = 512
    color = WHITE

    def __init__(self, center: Vector2, speed: Vector2, radius: Real):
        """Инициализация

        :param center: центр объекта
        :param radius: радиус объекта
        :param speed: скорость объекта
        """
        self.radius = radius
        self.center = center
        self.speed = speed
        self.time = 0
        self.destroyed = False

    def move(self):
        """Перемещение за один такт"""
        if self.center.x > self.max_size:
            self.center.x = 0
        elif self.center.x < 0:
            self.center.x = self.max_size

        if self.center.y > self.max_size:
            self.center.y = 0
        elif self.center.y < 0:
            self.center.y = self.max_size

        self.center += self.speed

    @property
    def x(self) -> Real:
        """Координата x центра"""
        return self.center.x

    @property
    def y(self) -> Real:
        """Координата y центра"""
        return self.center.y

    @property
    def mass(self) -> Real:
        """Масса объекта"""
        return pi * (self.radius ** 2)

    def time_dec(self) -> bool:
        """Декремент времени

        :return: проверка на время жизни
        """
        if self.time > 0:
            self.time -= 1
            return True
        return False


class Asteroid(SpaceObject):
    """Класс астероида"""
    color = YELLOW

    def __init__(self, center: Vector2, speed: Real,
                 rotate: Real, radius: Real = 10):
        """Инициализация

        :param center: центр объекта
        :param radius: радиус объекта
        :param speed: линейная скорость объекта
        :param rotate: угол поворота в радианах
        """
        super().__init__(center, Vector2(speed * cos(rotate),
                                         speed * sin(rotate)), radius)


class Bullet(SpaceObject):
    """Класс снаряда"""
    death_time = 40
    color = RED

    def __init__(self, center: Vector2, rotate: Real):
        """Инициализация

        :param center: центр объекта
        :param rotate: угол поворота в радианах
        """
        super().__init__(center, Vector2(BULLET_SPEED * cos(rotate),
                         BULLET_SPEED * sin(rotate)), BULLET_RADIUS)

    def time_inc(self) -> bool:
        """Инкремент времени

        :return: проверка на уничтожение объекта
        """
        self.time += 1
        return self.time >= self.death_time


class SpaceShip(SpaceObject):
    """Класс космического корабля"""
    color = VIOLET
    front_corner = 0
    right_corner = 1
    left_corner = -1

    def __init__(self):
        """Инициализация"""
        half = self.max_size / 2
        super().__init__(Vector2(half, half),
                         Vector2(0, 0), SHIP_RADIUS)
        self.rotate = 0

    def give_speed(self, give: bool = True):
        """Установка скорости

        :param give: False для нулевой скорости,
                     True для ненулевой
        """
        norm_speed = give * SHIP_SPEED
        self.speed = Vector2(norm_speed * cos(self.rotate),
                             norm_speed * sin(self.rotate))

    def get_corner(self, position: int) -> tuple:
        """Получение координат угла

        :param position: положение угла
        """
        rotate = self.rotate + THIRD_OF_CIRCLE * position
        x = self.center.x + self.radius * cos(rotate)
        y = self.center.y + self.radius * sin(rotate)
        return x, y

    def summon_bullet(self) -> Bullet:
        """Создание снаряда перед кораблём"""
        changed_radius = self.radius * BULLET_DIST
        x = self.center.x + cos(self.rotate) * changed_radius
        y = self.center.y + sin(self.rotate) * changed_radius
        return Bullet(Vector2(x, y), self.rotate)


def speed_calculation(first: SpaceObject, second: SpaceObject) -> Real:
    """Расчёт скоростей при столкновении

    :param first: первый объект
    :param second: второй объект
    :return: скорость первого объекта
    """
    v_1 = first.speed
    v_2 = second.speed
    m_1 = second.mass
    m_2 = second.mass
    c_1 = first.center
    c_2 = second.center

    return (v_1 - (c_1 - c_2) * (2 * m_2 * ((v_1 - v_2) * (c_1 - c_2)) /
            (m_1 + m_2) / (c_1 - c_2).length_squared()))


def elastic_collision(first: SpaceObject, second: SpaceObject) -> tuple:
    """Расчёт скоростей при столкновении

    :param first: первый объект
    :param second: второй объект
    :return: скорости объектов после столкновения
    """
    return speed_calculation(first, second), speed_calculation(second, first)


def collision_analyze(first: SpaceObject, second: SpaceObject):
    """Анализ сталкивающихся объектов

    :param first: первый объект
    :param second: второй объект
    """
    if ((isinstance(first, Bullet) and isinstance(second, SpaceShip)) or
            (isinstance(second, Bullet) and isinstance(first, SpaceShip))):
        return

    if (isinstance(first, SpaceShip) or isinstance(first, Bullet) or
            isinstance(second, SpaceShip) or isinstance(second, Bullet)):
        first.destroyed = second.destroyed = True
        return

    if first.center == second.center:
        return

    first.speed, second.speed = elastic_collision(first, second)

    second.time = first.time = 5

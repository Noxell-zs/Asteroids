"""Реализация квадродерева"""

from pygame.math import Vector2
from pygame import Surface
from space_objects import collision_analyze, Bullet, SpaceObject
from numbers import Real

# Индексы квандрантов
TOP_LEFT = 0
TOP_RIGHT = 1
DOWN_LEFT = 2
DOWN_RIGHT = 3

MIN_DISTANCE = 1
GREEN = (0, 255, 0)


class Quadnode:
    """Узел квадродерева"""

    def __init__(self, corner: Vector2, distance: Real):
        """Инициализация угла

        :param corner: вершина верхнего правого угла
        :param distance: размер стороны
        """
        self.corner = corner
        self.distance = distance

        self.values = []
        self.leaves = {}

    def create_leaf(self, position: int):
        """Добавление нового узла

        :param position: идентификатор узла
        """
        half = self.distance / 2

        x_center = self.corner.x + half
        y_center = self.corner.y + half
        get_corner = {
            TOP_LEFT: self.corner,
            TOP_RIGHT: Vector2(x_center, self.corner.y),
            DOWN_LEFT: Vector2(self.corner.x, y_center),
            DOWN_RIGHT: Vector2(x_center, y_center),
        }

        if position not in get_corner:
            return

        self.leaves[position] = Quadnode(get_corner[position], half)

    def area_checking(self, space_obj: SpaceObject):
        """Проверка вхождения объекта в область.
        Добавление объекта.

        :param space_obj: объект для проверки
        """
        positions = []
        half = self.distance / 2

        distance_top = space_obj.center.y - space_obj.radius
        distance_down = space_obj.center.y + space_obj.radius
        distance_left = space_obj.center.x - space_obj.radius
        distance_right = space_obj.center.x + space_obj.radius
        y_center = self.corner.y + half
        x_center = self.corner.x + half

        if distance_top < y_center and distance_left < x_center:
            positions.append(TOP_LEFT)
        if distance_top < y_center and distance_right > x_center:
            positions.append(TOP_RIGHT)
        if distance_down > y_center and distance_left < x_center:
            positions.append(DOWN_LEFT)
        if distance_down > y_center and distance_right > x_center:
            positions.append(DOWN_RIGHT)

        for i in positions:
            if i not in self.leaves:
                self.create_leaf(i)
            self.leaves[i].insert_object(space_obj)

    def insert_object(self, space_obj: SpaceObject):
        """Вставка

        :param space_obj: объект для вставки
        """
        if (space_obj.time > 0 and not isinstance(space_obj, Bullet) or
                space_obj.destroyed):
            return

        if space_obj not in self.values:
            self.values.append(space_obj)

        if len(self.values) <= 1:
            return

        if (self.distance <= MIN_DISTANCE and
                (space_obj.center - self.values[0].center).length() <=
                space_obj.radius + self.values[0].radius):
            for i in self.values:
                if i is not space_obj:
                    collision_analyze(i, space_obj)
            return

        self.area_checking(space_obj)

        for val in self.values:
            if (val is not space_obj and val not in
                    [j for i in self.leaves.values() for j in i.values]):
                self.insert_object(val)

    def delete_object(self, space_obj: SpaceObject):
        """Удаление

        :param space_obj: объект для удаления
        """
        if space_obj not in self.values:
            return

        self.values.remove(space_obj)
        for i in self.leaves.values():
            i.delete_object(space_obj)

    def draw_borders(self, screen: Surface, func: callable):
        """Отрисовка границ квадранта

        :param screen: окно для отображения
        :param func: функция отрисовки
        """
        func(screen, GREEN, (self.corner.x, self.corner.y,
                             self.distance, self.distance), 1)
        for i in self.leaves.values():
            if i:
                i.draw_borders(screen, func)

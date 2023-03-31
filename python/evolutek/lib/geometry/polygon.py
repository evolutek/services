from math import cos, sin, radians, pi
from shapely.geometry import LineString
from shapely.geometry import Polygon as PolygonShape
from shapely.geometry import MultiPolygon as MultiPolygonShape

from evolutek.lib.geometry.point import Point

class Polygon(PolygonShape):

    def __init__(self, points):
        super().__init__(self, points)

    @staticmethod
    def create_empty():
        return Polygon([])

    @staticmethod
    def create_rectangle(p1, p2, offset):
        x1 = min(p1.x, p2.x)
        x2 = max(p1.x, p2.x)
        y1 = min(p1.y, p2.y)
        y2 = max(p1.y, p2.y)

        l = [
            (x1 - offset, y1 - offset),
            (x1 - offset, y2 + offset),
            (x2 + offset, y2 + offset),
            (x2 + offset, y1 - offset)
        ]

        return Polygon(l)

    @staticmethod
    def create_regular_polygon(vertex_count, radius, center, angle=0):
        angle_step = 2 * pi / vertex_count
        vertices = []
        angle = radians(angle)
        
        for i in range(vertex_count):
            cos_x = cos(angle)
            sin_y = sin(angle)
            vertices.append(Point(
                radius * cos_x + center.x,
                radius * sin_y + center.y
            ))
            angle += angle_step

        return Polygon(vertices)

    @staticmethod
    def create_octogon(center, radius):
        return Polygon.regular(
            8,
            radius=radius,
            center=center,
            angle=22.5,
        )

    @staticmethod
    def merge_polygons(polygons):
        merged_polygons = MultiPolygonShape()
        
        for polygon in polygons:
            merged_polygons = merged_polygons.union(polygon)
        
        return merged_polygons

    @staticmethod
    def remove_polygon(poly1, poly2):
        # poly1 is a Polygon
        if isinstance(poly1, Polygon):
            return poly1.difference(poly2)

        # poly1 is a MultiPolygon
        l = []
        for poly in poly1:
            result = poly.difference(poly2)

            if isinstance(result, Polygon):
                # the result is just a Polygon, add it to the list
                l.append(result)
            else:
                # the result is a MultiPolygon, add each Polygon
                for r in result:
                    l.append(r)

        # return a MultiPolygon
        return MultiPolygonShape(l)

    @staticmethod
    def remove_polygons(polygon, polygons):
        for _polygon in polygons:
            polygon = Polygon.remove_polygon(_polygon)
        return polygon


    def is_colliding_with(self, p1, p2):
        line = LineString([p1, p2])
        return line.crosses(self)

    @staticmethod
    def is_collinding_with_polygons(polygons, p1, p2):
        line = LineString([p1, p2])
        for polygon in polygons:
            if line.crosses(polygon):
                return True
        return False
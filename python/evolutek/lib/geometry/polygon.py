
from planar import Polygon as PolygonPlanar
from shapely.geometry import LineString, MultiPolygon, Polygon as PolygonShape

class Polygon(PolygonShape):

    def __init__(self, points):
        super().__init__([p.to_tuple() for p in points])

    @staticmethod
    def create_octogon(center, radius):
        l = PolygonPlanar.regular(8, radius=radius, angle=22.5, center=center.to_tuple())
        return Polygon(l)

    @staticmethod
    def create_rectanle(p1, p2):
        return Polygon(
            [
                p1,
                Point(p2.x, p1.y),
                p2,
                Point(p1.x, p2.y)
            ]
        )

    def is_collinding_with_line(self, p1, p2):
        line = LineString([p1, p2])
        return line.crosses(self)

    @staticmethod
    def is_collinding_with_line(self, p1, p2, polygons):
        line = LineString([p1, p2])

        for poly in polys:
            if line.crosses(self):
                return True

        return False

    def compute_collision_with_line(self, p1, p2):
        line = LineString([p1, p2])
        sides = []

        for i in range(len(self.exterior.coords) - 1):

            side = LineString([self.exterior.coords[i], self..exterior.coords[i + 1]])
            if line.crosses(side):
                sides.append(side)

        return sides

    @staticmethod
    def compute_nearest_collision_with_line(self, p1, p2, polygons):

        line = LineString([p1, p2])
        colliding_polygon = None
        colliding_side = None
        colliding_point = None
        # sqrt dist used to reduce computation time
        collinding_dist = 0

        for polygon in polygons:

            for side in poly.compute_collision_with_line(p1, p2):

                collision = Point.from_tuple(line.intersection(side))
                dist = p1.sqrdist(collision)

                if collision is None or dist < collinding_dist:
                    colliding_polygon = polygon
                    colliding_side = side
                    colliding_point = collision
                    collinding_dist = dist

        return colliding_point, colliding_side, colliding_polygon

    @staticmethod
    def merge(polygon1, polygon2):

        # polygon1 is a Polygon
        if isinstance(polygon1, Polygon):
            return polygon1.difference(polygon2)

        # polygon1 is a MultiPolygon
        l = []
        for polygon in polygon1:
            result = polygon.difference(polygon2)

            if isinstance(result, Polygon):
                # the result is just a Polygon, add it to the list
                l.append(result)
            else:
                # the result is a MultiPolygon, add each Polygon
                for r in result:
                    l.append(r)

        # return a MultiPolygon
        return MultiPolygon(l)

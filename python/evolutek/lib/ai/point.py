from math import pow, sqrt, cos, sin, atan, pi

def collide_orectangle_circle(circle, radius, rect_p1, rect_p2, width):
  """
    Returns true if the circle collides with the rectange determined by two
    points which are the intersection between the rectangle and a meadian.
    This function unrotate the rectangle and then detect a potential collision.
    circle, rect_p1 and rect_p2 are Point objects.
  """
  rect_center = Point(abs(rect_p2.x - rect_p1.x), abs(rect_p2.y - rect_p1.y))

  # compute the rotation angle of the circle
  coeff_x = (rect_p2.y - rect_p1.y) \
            / (1 if rect_p1.x == rect_p2.x else rect_p2.x - rect_p1.x)

  rotation = atan(coeff_x) - pi / 2


  # unrotated circle
  unrotated_c = Point(cos(rotation) * (circle.x - rect_center.x)   \
                      - sin(rotation) * (circle.y - rect_center.y) \
                      + rect_center.x,                             \
                      sin(rotation) * (circle.x - rect_center.x)   \
                      + cos(rotation) * (circle.y - rect_center.y) \
                      + rect_center.y)

  # closest unrotated point drom center od unrotated circle
  closest = Point(unrotated_c.x, unrotated_c.y)

  if unrotated_c.x < rect_center.x:
    closest.x = rect_center.x

  elif unrotated_c.x > rect_center.x + width:
    closest.x = rect_center.x + width

  height = rect_p1.distance(rect_p2)
  if unrotated_c.y < rect_center.y:
    closest.y = rect_center.y

  elif unrotated_c.y > rect_center.y + height:
    closest.y = rect_center.y + height

  # determine collision
  return unrotated_c.distance(closest) < radius

class Point:
  """
    A pair of cartesian coordinates (x, y)
  """

  def __init__(self, _x, _y):
    self.x = _x
    self.y = _y

  def __str__(self):
    return str(self.x) + ', ' + str(self.y)

  def distance(self, point):
    """
      Returns the disnace to the point passed in argument
    """
    return sqrt(pow(self.x - point.x, 2) + pow(self.y - point.y, 2))

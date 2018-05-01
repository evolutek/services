from math import pow, sqrt, cos, sin, atan, pi

def collide_orectangle_circle(circle, radius, rect_p1, rect_p2, width):
  """
    Returns true if the circle collides with the rectange determined by two
    points which are the intersection between the rectangle and a meadian.
    This function unrotate the rectangle and then detect a potential collision.
    circle, rect_p1 and rect_p2 are Point objects.
  """
  width *= 2
  height = rect_p1.distance(rect_p2)
  rect_center = Point((rect_p2.x + rect_p1.x) / 2, (rect_p2.y + rect_p1.y) / 2)

  # compute the rotation angle of the circle
  coeff_x = (rect_p2.y - rect_p1.y) / (1 if rect_p1.x == rect_p2.x else rect_p2.x - rect_p1.x)
  rotation = atan(-coeff_x) - pi/2

  """
  if rect_p1.x == rect_p2.x:
    coeff_x = 0
    angle = 0
  """

  # unrotated
  refx = rect_center.x - width / 2
  refy = rect_center.y - height / 2

  # unrotated circle
  unrotated_c = Point(cos(rotation) * (circle.x - rect_center.x)   \
                      - sin(rotation) * (circle.y - rect_center.y) \
                      + rect_center.x,                             \
                      sin(rotation) * (circle.x - rect_center.x)   \
                      + cos(rotation) * (circle.y - rect_center.y) \
                      + rect_center.y)

  # closest unrotated point from center of unrotated circle
  closest = Point(unrotated_c.x, unrotated_c.y)

  if unrotated_c.x < refx:
    closest.x = refx

  elif unrotated_c.x > refx + width:
    closest.x = refx + width

  if unrotated_c.y < refy:
    closest.y = refy

  elif unrotated_c.y > refy + height:
    closest.y = refy + height


  # determine collision
  return unrotated_c.distance(closest) < radius


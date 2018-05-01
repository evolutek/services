from time import time

def main():
  pt_start = Point(350, 700)

  pts = [ Point(520, 200), \
          Point(100, 520), \
          Point(620, 520), \
          Point(190, 200), \
          pt_start ]


def go(p):
  pass

  start_t = time()

  go(pt_start)  # take position
  while time() < time() + 100:   # run for 100 secs
    for p in pts:
      go(p)

  #maybe rotate the robot for better derive measuring


if __name__ == '__main__':
  main()

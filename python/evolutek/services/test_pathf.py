import pathfinding

def main():
	pathf = pathfinding.Pathfinding(3000, 2000, 100, 100, 100)
	pathf.AddRectangleObstacle(200, 200, 100, 100)
	pathf.map.ExportMap()

if __name__ == '__main__':
	main()

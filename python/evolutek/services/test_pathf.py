import pathfinding

def main():
	pathf = pathfinding.Pathfinding(300, 200, 10, 10, 10)
	pathf.AddRectangleObstacle(20, 20, 10, 10)
	pathf.map.ExportMap()

if __name__ == '__main__':
	main()

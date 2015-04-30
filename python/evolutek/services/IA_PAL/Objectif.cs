class Objectif
{
	public string name;
	public int x;
	public int y;
	public int teta;
	public bool possible;
	public bool finished;

	public void Objectif(sting _name, int _x, int _y, int _teta, bool _possible, bool _finished)
	{
		name = _name;
		x = _x;
		y = _y;
		teta = _teta;
		possible = _possible;
	}
}
class Objectifs_Green
{
	public List<Objectif> objectifs = new List<Objectif>;
	public int plots = 1;

	public void Objectifs()
	{
		Objectif plot_haut_gauche = new Objectif("plot_haut_gauche", 150, 2350, (3*pi)/2, true, false);
		objectifs.add(plot_haut_gauche);
		Objectif plot_haut_droite = new Objectif("plot_haut_droite", 100, 2900, pi/2, true, false);
		objectifs.add(plot_haut_droite);
		Objectif plot_bas_gauche = new Objectif("plot_bas_gauche", 1700, 1650, (5*pi)/3, true, false);
		objectifs.add(plot_bas_gauche);
		Objectif plot_bas_droite = new Objectif("plot_bas_droite", 1800, 2900, pi/2, false, false);
		objectifs.add(plot_bas_doite);
		Objectif clap_gauche = new Objectif("clap_gauche", 1900, 100, pi/2, true, false);
		objectifs.add(clap_gauche);
		Objectif clap_droit = new Objectif("clap_droit", 1900, 2900, (3*pi)/2, false, false);
		objectifs.add(clap_droit);
		Objectif recup_balle = new objectif("recup_balle", 1900, 1650, pi/2, true, false);
		objectifs.ad(recup_balle);
		Objectif pose_pile_gauche = new Objectif("pose_pile_gauche",  1900, 1500, 0, false, false);
		objectifs.add(pose_pile_gauche);
		Objectif pose_pile_droite = new Objectif("pose_pile_droite", 1900, 1650, 0, false, false);
		objectifs.add(pose_pile_droite);
		Objectif ramasse_gobelet_bas_droite = new Objectif("ramasse_gobelet_bas_droite", 1900, 2700, (3*pi)/2, false, false);
		objectifs.add(ramasse_gobelet_bas_droite);
		Objectif pose_gobelet_haut = new Objectif("pose_gobelet_haut", 800, 2900, (3*pi)/2, false, false);
		objectifs.add(pose_gobelet_haut);
		Objectif pose_gobelet_bas = new Objectif("pose_gobelet_bas", , 290, (3*pi)/2, true, false);
		objectifs.add(pose_gobelet_bas);

	}

	public int get_cost(Objectif objectif, int _x, int _y)
	{
		if(objectif.x < _x)
		{
			int z = _x - objectif.x;
		}else{
			int z = objectif.x - _x
		}
		if(objectif.y < _y)
		{
			int w = _y - objectif.y;
		}else{
			int w = objectif.y - _y
		}
		return (z*w);
	}

	public void do_objectif(Objectif objectif)
	{
		switch(objectif.name)
		{
			case "plot_haut_gauche":
				goto-xy(objectif.x, objectif.y);
				goto-teta(objectif.teta);
				goto-xy(objectif.x, objectif.y);
				goto-teta(objectif.teta);
				if(plot_attrape <=4 )
				{
					attape_plot_ascenceur_gauche();
					plot_attrape++;
				}else{
					goto-teta(current_teta + pi/3);
					goto-xy(objectif.x-50, objectif.y+50);
					attape_plot_ascenceur_droite();
					plot_attrape++;
				}
				goto-teta(current_teta + pi/3);
				goto-xy(objectif.x-50, objectif.y+50);
				if(plot_attrape <=4 )
				{
					attape_plot_ascenceur_gauche();
					plot_attrape++;
				}else{
					goto-teta(current_teta + pi/3));
					goto-xy(objectif.x-5, objectif.y+5);
					attape_plot_ascenceur_droite();
					plot_attrape++;
				}
				objectif.finished = true;
				break;

			case "plot_haut_droite":
				goto-xy(objectif.x, objectif.y);
				goto-teta(objectif.teta);
				if(plot_attrape <=4 )
				{
					attape_plot_ascenceur_gauche();
					plot_attrape++;
				}else{
					goto-teta(current_teta + pi/3);
					goto-xy(objectif.x-50, objectif.y-50);
					attape_plot_ascenceur_droite();
					plot_attrape++;
				}
				objectif.finished = true;
				break;

			case "plot_bas_gauche":
				goto-xy(objectif.x, objectif.y);
				goto-teta(objectif.teta);
				if(plot_attrape <=4 )
				{
					attape_plot_ascenceur_gauche();
					plot_attrape++;
				}else{
					goto-teta(current_teta + pi/3);
					goto-xy(objectif.x+50, objectif.y+50);
					attape_plot_ascenceur_droite();
					plot_attrape++;
				}
				goto-teta(pi/6);
				goto-xy(objectif.x-100, objectif.y+100);
				if(plot_attrape <=4 )
				{
					attape_plot_ascenceur_gauche();
					plot_attrape++;
				}else{
					goto-teta(current_teta + pi/3);
					goto-xy(objectif.x-50, objectif.y-50);
					attape_plot_ascenceur_droite();
					plot_attrape++;
				}
				objectif.finished = true;
				break;

			case "plot_bas_droite":
				goto-xy(objectif.x, objectif.y);
				goto-teta(objectif.teta);
				if(plot_attrape <=4 )
				{
					attape_plot_ascenceur_gauche();
					plot_attrape++;
				}else{
					goto-teta(current_teta - pi/3);
					goto-xy(objectif.x+50, objectif.y+50);
					attape_plot_ascenceur_droite();
					plot_attrape++;
				}
				goto-teta(current - pi/3);
				goto-xy(objectif.x+50, objectif.y+50);
				if(plot_attrape <=4 )
				{
					attape_plot_ascenceur_gauche();
					plot_attrape++;
				}else{
					goto-teta(current_teta - pi/3);
					goto-xy(objectif.x+50, objectif.y+50);
					attape_plot_ascenceur_droite();
					plot_attrape++;
				}
				objectifs.find(clap_droit).possible = true;
				objectif.finished = true;
				break;

			case "clap_gauche":
				goto-xy(objectif.x, objectif.y);
				goto-teta(objectif.teta);
				bras_open();
				goto-xy(1900, 1400);
				bras_close();
				objectif.finished = true;
				break;

			case "clap_droit":
				goto-xy(objectif.x, objectif.y);
				goto-teta(objectif.teta);
				bras_open();
				goto-xy(1900, 1600);
				bras_close();
				objectif.finished = true;
				break;

			case "recup_balle":
				goto-xy(objectif.x, objectif.y);
				goto-teta(objectif.teta);
				attape_plot_ascenceur_droite();
				objectif.finished = true;
				break;

			case "pose_pile_gauche":
				goto-xy(objectif.x, objectif.y);
				goto-teta(objectif.teta);
				depose_pile_gauche();
				goto-xy(objectif.x - 100, objectif.y);
				objectif.finished = true;
				break;

			case "pose_pile_droite":
				goto-xy(objectif.x, objectif.y);
				goto-teta(objectif.teta);
				depose_pile_droite();
				goto-xy(objectif.x-100, objectif.y);
				objectif.finished = true;
				break;

			case "ramasse_gobelet_bas_droite":
				goto-xy(objectif.x, objectif.y);
				goto-teta(objectif.teta);
				ramasse_gobelet();
				objectif.finished = true;
				objectifs.find(pose_gobelet_haut).possible = true;
				objectifs.find(plot_bas_droite).possible = true;
				break;

			case "pose_gobelet_haut":
				goto-xy(objectif.x, objectif.y);
				goto-teta(objectif.teta);
				depose_gobelet();
				goto-xy(objectif.x, objectif.y-100)
				objectif.finished = true;
				break;

			case "pose_gobelet_bas":
				goto-xy(objectif.x, objectif.y);
				goto-teta(objectif.teta);
				depose_gobelet();
				goto-xy(objectif.x, objectif.y-100)
				objectif.finished = true;
				objectifs.find(ramasse_gobelet_bas_gauche).possible = true;
				break;

			case defautl(string):
				print("bad objectif!");
				break;
		}
	}

	public bool is_finish_objetifs()
	{
		bool finish = true;
		foreach(Objectif objectif in objectifs)
			if(objectif.finish == false)
				finish = false;
	}
}

/* objectif class*/
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
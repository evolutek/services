#include <ascenceur_gauche.py>
#include <ascenceur_droite.py>
#include <tirette.py>
#include <Objectifs_Yellow.py>
#include <Objectifs_Green.py>

const float pi = 3,141 592 653 589 793;
string color = "yellow"; // call cellaserv
/* think to create a time */

/* main */
void main()
{
	/* wait for the tirette */
	while(tirette)
	{
		wait(1);	
	}
	/* à faire obligatoirement au début du match */
	/* depend of the color */
	if(color == "yellow")
	{	
		goto-xy(1000, 1000);
		goto-teta(0);
		goto-xy(1100,1000);
		if(plot_attrape <=4 )
		{
			attape_plot_ascenceur_gauche();
			plot_attrape++;
		}else{
			attape_plot_ascenceur_droite();
			plot_attrape++;
		}
		goto-xy (900,1000);
		attrape_gobelet();
		Objectifs_Yellow _objectifs = new Objectifs();
		while(!(_objectifs.is_finish_objectifs())
		{
			int cost = 6000000;
			Objectif _objectif;
			foreach(Objectif objectif in _objectifs.objectifs)
			{
				if(_objectifs.plots >= 4)
				{
					_objectifs.objectifs.find(pose_pile_gauche).possible = true;
				}
				if(_objectifs.plots >= 8)
				{
					_objectifs.objectifs.find(pose_pile_droite).possible = true;
				}			
				if(_objectifs.plots % 2 != 0)
				{			
					_objectifs.objectifs.find(plot_haut_droite).possible = false;
					_objectifs.objectifs.find(plot_bas_gauche).possible = false;
					_objectifs.objectifs.find(plot_bas_droite).possible = false;
				}else{
					_objectifs.objectifs.find(plot_haut_droite).possible = true;
					_objectifs.objectifs.find(plot_bas_gauche).possible = true;
					_objectifs.objectifs.find(plot_bas_droite).possible = true;
				}
				if(_objectifs.objectifs.find(recup_balle).finished == false && _objectifs.plots == 4)
				{
					_objectifs.objectifs.find(plot_haut_gauche).possible = false;
					_objectifs.objectifs.find(plot_haut_droite).possible = false;
					_objectifs.objectifs.find(plot_bas_gauche).possible = false;
					_objectifs.objectifs.find(plot_bas_droite).possible = false;
				}else{
					_objectifs.objectifs.find(plot_haut_gauche).possible = true;
					_objectifs.objectifs.find(plot_haut_droite).possible = true;
					_objectifs.objectifs.find(plot_bas_gauche).possible = true;
					_objectifs.objectifs.find(plot_bas_droite).possible = true;
				}
			}
			if(cost == 6000000)
				print("not objectif possible!");
			else
				_objectifs.do_objectifs(_objectif);
		}
		print("finish!");
	}else{
		goto-xy(1000, 2000);
		goto-teta(0);
		goto-xy(1100,2000);
		if(plot_attrape <=4 )
		{
			attape_plot_ascenceur_gauche();
			plot_attrape++;
		}else{
			attape_plot_ascenceur_droite();
			plot_attrape++;
		}
		goto-xy (900,2000);
		attrape_gobelet();
		Objectifs_Yellow _objectifs = new Objectifs();
		while(!(_objectifs.is_finish_objectifs())
		{
			int cost = 6000000;
			Objectif _objectif;
			foreach(Objectif objectif in _objectifs.objectifs)
			{
				if(_objectifs.plots >= 4)
				{
					_objectifs.objectifs.find(pose_pile_gauche).possible = true;
				}
				if(_objectifs.plots >= 8)
				{
					_objectifs.objectifs.find(pose_pile_droite).possible = true;
				}			
				if(_objectifs.plots % 2 != 0)
				{			
					_objectifs.objectifs.find(plot_haut_gauche).possible = false;
					_objectifs.objectifs.find(plot_bas_gauche).possible = false;
					_objectifs.objectifs.find(plot_bas_droite).possible = false;
				}else{
					_objectifs.objectifs.find(plot_haut_gauche).possible = true;
					_objectifs.objectifs.find(plot_bas_gauche).possible = true;
					_objectifs.objectifs.find(plot_bas_droite).possible = true;
				}
				if(_objectifs.objectifs.find(recup_balle).finished == false && _objectifs.plots == 4)
				{
					_objectifs.objectifs.find(plot_haut_gauche).possible = false;
					_objectifs.objectifs.find(plot_haut_droite).possible = false;
					_objectifs.objectifs.find(plot_bas_gauche).possible = false;
					_objectifs.objectifs.find(plot_bas_droite).possible = false;
				}else{
					_objectifs.objectifs.find(plot_haut_gauche).possible = true;
					_objectifs.objectifs.find(plot_haut_droite).possible = true;
					_objectifs.objectifs.find(plot_bas_gauche).possible = true;
					_objectifs.objectifs.find(plot_bas_droite).possible = true;
				}
				if(_objectifs.get_cost(objectif, x, y) < cost && objectif.possible)
				{
					_objectif = objectif
					cost = _objectifs.get_cost(objectif);
				}
			}
			if(cost == 6000000)
				print("not objectif possible!");
			else
				_objectifs.do_objectifs(_objectif);
		}
		print("finish!");
	}
}
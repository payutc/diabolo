diabolo
=======

C'est le serveur de payutc !


Setup - dev
=========

1. Mettre en place la base de donnée sql
2. Changer les paramètres de connection dans local_settings.py
3. (optionel) créer un virtualenv
3. Lancer install.sh qui installera django et les modules necessaires
(utiliser sudo si on n'est pas dans un virtualenv)
4. Lancer './manage.py syncdb' qui va créer les tables et les pré remplir
avec les fixtures. Répondre non à la question 'Voulez vous créer un super
utilisateur maintenant'.


TODO-LIST
=========

* Modeles
	* Ajouter un attribut supprime (datetime) sur toutes les tables que l'on peut pas supprimer... 

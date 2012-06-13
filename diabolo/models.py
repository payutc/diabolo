from django.db import models
from django.contrib.auth.models import User

from django.db.models.signals import post_save


class UserProfile(models.Model):
	user = models.OneToOneField(User)
	badge_id = models.CharField(max_length=50)
	pass_seller = models.CharField(max_length=50) # A virer selon matthieu
	birthday = models.DateField(null=True)
	bloque = models.BooleanField(default=False)
	solde = models.IntegerField(default=0)
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return "Profile : "+self.user.username


def create_user_profile(sender, instance, created, **kwargs):
	if created:
		UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)

class Groupe(models.Model):
	name = models.CharField(max_length=50)
	
	def __unicode__(self):
		return self.name

class Famille(models.Model):
	name = models.CharField(max_length=50)
	alcool = models.BooleanField()
	groupe = models.ForeignKey(Groupe, related_name="Groupe")
	
	def __unicode__(self):
		return self.name

class Asso(models.Model):
	name = models.CharField(max_length=50)
	sellers = models.ManyToManyField(User, verbose_name="list of sellers")

	def __unicode__(self):
		return self.name

class Article(models.Model):
	name = models.CharField(max_length=50)
	famille = models.ForeignKey(Famille, related_name="Famille")
	asso = models.ForeignKey(Asso, related_name="Association")
	stockinitial = models.IntegerField(null=True)
	stock = models.IntegerField(null=True)
	enVente = models.BooleanField()
	tva = models.DecimalField(default=0.0, max_digits=3, decimal_places=2)
	priceTTC = models.IntegerField()

	def __unicode__(self):
		return self.name
		
class PointOfSale(models.Model):
	name = models.CharField(max_length=50)
	key = models.CharField(max_length=50,null=True)
	check_seller_pass = models.BooleanField()

	def __unicode__(self):
		return self.name
		
class ArticlePos(models.Model):
	article = models.ForeignKey(Article, related_name="article")
	position = models.IntegerField()
	pos = models.ForeignKey(PointOfSale, related_name="pointdevente")
	debut = models.TimeField()
	fin = models.TimeField()

class Reversement(models.Model):
	date = models.DateTimeField()
	montant = models.IntegerField()
	ref = models.CharField(max_length=255)
	
	def __unicode__(self):
		return self.name
	
class Transaction(models.Model):
	article = models.ForeignKey(Article, null=True)
	user = models.ForeignKey(User, related_name="user")
	seller = models.ForeignKey(User, null=True, related_name="seller")
	asso = models.ForeignKey(Asso, null=True, related_name="asso")
	pos = models.ForeignKey(PointOfSale, related_name="pos")
	date = models.DateTimeField(auto_now_add=True)
	nb = models.IntegerField(default=1)
	prix_ttc = models.IntegerField()
	tva = models.DecimalField(max_digits=3, decimal_places=2)
	reverse = models.ForeignKey(Reversement, null=True, related_name="Transactionreverse")

	def __unicode__(self):
		return "Transaction(article=%s,seller=%s,buyer=%s,pos=%s,date=%s,tarifs=%s)" % (
			self.article,
			self.seller,
			self.buyer,
			self.pos,
			self.date,
			self.tarifs
		)


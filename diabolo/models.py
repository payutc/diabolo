from django.db import models
from django.contrib.auth.models import User

class Famille(models.Model):
	name = models.CharField(max_length=50)
	alcool = models.BooleanField()
	
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

	def __unicode__(self):
		return self.name
		
class PointOfSale(models.Model):
	name = models.CharField(max_length=50)
	auth_assos = models.ManyToManyField(Asso, verbose_name="list of authorized assos")

	def __unicode__(self):
		return self.name
		
class ArticlePos(models.Model):
	article = models.ForeignKey(Article, related_name="Article")
	position = models.IntegerField()
	pos = models.ForeignKey(PointOfSale, related_name="Point de vente")
	debut = models.TimeField()
	fin = models.TimeField()

class Groupe(models.Model):
	name = models.CharField(max_length=50)
	
	def __unicode__(self):
		return self.name

class Reversement(models.Model):
	date = models.DateTimeField()
	montant = models.IntegerField()
	ref = models.CharField(max_length=255)
	
	def __unicode__(self):
		return self.name
	
class Transaction(models.Model):
	article = models.ForeignKey(Article)
	seller = models.ForeignKey(User, related_name="seller")
	buyer = models.ForeignKey(User, related_name="buyer")
	pos = models.ForeignKey(PointOfSale, related_name="pos")
	date = models.DateTimeField()

	def __unicode__(self):
		return "Transaction(article=%s,seller=%s,buyer=%s,pos=%s,date=%s)" % (
			self.article,
			self.seller,
			self.buyer,
			self.pos,
			self.date
		)


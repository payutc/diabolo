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
	MustCheckSeller = models.BooleanField()

	def __unicode__(self):
		return self.name
		
class ArticlePos(models.Model):
	article = models.ForeignKey(Article, related_name="article")
	position = models.IntegerField()
	pos = models.ForeignKey(PointOfSale, related_name="pointdevente")
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
	article = models.ForeignKey(Article, null=True)
	userFrom = models.ForeignKey(User, related_name="userFrom")
	seller = models.ForeignKey(User, null=True, related_name="seller")
	assoTo = models.ForeignKey(Asso, null=True, related_name="assoTo")
	userTo = models.ForeignKey(User, null=True, related_name="userTo")
	pos = models.ForeignKey(PointOfSale, related_name="pos")
	date = models.DateTimeField()
	nb = models.IntegerField(default=1)
	tarifsTTC = models.IntegerField()
	TVA = models.DecimalField(max_digits=3, decimal_places=2)
	MODE_CHOICES = (
		('DEB', 'Debit'),
		('CRE', 'Credit')
	)
	reverse = models.ForeignKey(Reversement, null=True, related_name="Transactionreverse")
	mode = models.CharField(max_length=3, choices=MODE_CHOICES)

	def __unicode__(self):
		return "Transaction(article=%s,seller=%s,buyer=%s,pos=%s,date=%s,tarifs=%s)" % (
			self.article,
			self.seller,
			self.buyer,
			self.pos,
			self.date,
			self.tarifs
		)


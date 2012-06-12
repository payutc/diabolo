from django.db import models
from django.contrib.auth.models import User

class Produit(models.Model):
	name = models.CharField(max_length=50)
	price = models.IntegerField()

	def __unicode__(self):
		return self.name

class Fundation(models.Model):
	name = models.CharField(max_length=50)
	sellers = models.ManyToManyField(User, verbose_name="list of sellers")

	def __unicode__(self):
		return self.name

class PointOfSale(models.Model):
	name = models.CharField(max_length=50)
	auth_fundations = models.ManyToManyField(Fundation, verbose_name="list of authorized fundations")

	def __unicode__(self):
		return self.name

class Transaction(models.Model):
	produit = models.ForeignKey(Produit)
	seller = models.ForeignKey(User, related_name="seller")
	buyer = models.ForeignKey(User, related_name="buyer")
	pos = models.ForeignKey(PointOfSale, related_name="pos")
	date = models.DateTimeField()

	def __unicode__(self):
		return "Transaction(produit=%s,seller=%s,buyer=%s,pos=%s,date=%s)" % (
			self.produit,
			self.seller,
			self.buyer,
			self.pos,
			self.date
		)


from django.db import models
from django.contrib.auth.models import User, Group

from django.db.models.signals import post_save,post_syncdb
from django.core.exceptions import ValidationError
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from guardian.shortcuts import *


def add_can_view_permission(sender, **kwargs):
	for content_type in ContentType.objects.all():
		Permission.objects.get_or_create(content_type=content_type, codename='view_%s' % content_type.model, name='Can view %s' % content_type.name)

def create_user_profile(sender, instance, created, **kwargs):
	if created:
		UserProfile.objects.get_or_create(user=instance)

# signals
post_save.connect(create_user_profile, sender=User)
post_syncdb.connect(add_can_view_permission)

class Asso(Group):
	class Meta:
		proxy = True

	def user_is_seller(self, user):
		pk_groups = map(lambda g: g.id, user.groups.all())
		return self.id in pk_groups

class UserProfile(models.Model):
	user = models.OneToOneField(User)
	badge_id = models.CharField(max_length=50)
	birthday = models.DateField(null=True)
	bloque = models.BooleanField(default=False)
	solde = models.IntegerField(default=0)
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return "Profile : "+self.user.username


class Groupe(models.Model):
	name = models.CharField(max_length=50)
	
	def __unicode__(self):
		return self.name

class Famille(models.Model):
	name = models.CharField(max_length=50)
	alcool = models.BooleanField()
	
	def __unicode__(self):
		return self.name


class Article(models.Model):
	name = models.CharField(max_length=50)
	famille = models.ForeignKey(Famille)
	stockinitial = models.IntegerField(null=True)
	stock = models.IntegerField(null=True)
	enVente = models.BooleanField()
	tva = models.DecimalField(default=0.0, max_digits=3, decimal_places=2)
	prix_ttc = models.IntegerField()

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
	asso = models.ForeignKey(Asso)
	ref = models.CharField(max_length=255)
	
	def __unicode__(self):
		return self.name


class Transaction(models.Model):
	user = models.ForeignKey(User)
	amount = models.IntegerField()
	date = models.DateTimeField(auto_now_add=True)
	description = models.CharField(max_length=255)

	def __unicode__(self):
		return "Transaction(type=%s,montant=%s,date=%s,user=%s)" % (
			self.t,
			self.amount,
			self.date,
			self.user
		)

class Achat(Transaction):
	article = models.ForeignKey(Article)
	seller = models.ForeignKey(User, related_name="seller")
	asso = models.ForeignKey(Asso, related_name="asso")
	pos = models.ForeignKey(PointOfSale, related_name="pos")
	tva = models.DecimalField(max_digits=3, decimal_places=2)

	def is_authorized(self):
		# TODO checker
		# seller dans asso
		# article dans asso
		# sans alcool ou buyer majeur
		return True
	
	@property
	def buyer(self):
		return self.user
	@buyer.setter
	def buyer(self, value):
		self.user = value

	def save(self, *args, **kwargs):
		if not self.is_authorized():
			raise Exception("Achat non permis")
		super(Achat, self).save(*args, **kwargs)
		assign('view_achat', self.asso, self)
		assign('delete_achat', self.asso, self)
	
	def __unicode__(self):
		return "Achat(article=%s,seller=%s,buyer=%s,pos=%s,asso=%s,date=%s)" % (
			self.article,
			self.seller,
			self.buyer,
			self.pos,
			self.asso,
			self.date,
		)

		
class Paybox(Transaction):
	STATECHOICE = (
		('W', 'Wait paybox'),
		('A', 'Aborted'),
		('S', 'Success')
	)
	state = models.CharField(max_length=1, choices=STATECHOICE)
		
class Virement(Transaction):
	userfrom = models.OneToOneField(User, related_name="donneur")

	@property
	def userto(self):
		return self.user
	@userto.setter
	def userto(self, value):
		self.user = value
	
	def __unicode__(self):
		return "Virement(donneur=%s,receveur=%s,date=%s,amount=%s)" % (
			self.userfrom,
			self.userto,
			self.date,
			self.amount
		)

from django.db import models
from django.contrib.auth.models import User, Group

from django.db.models.signals import post_save,post_syncdb
from django.core.exceptions import ValidationError
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

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

class MyModel(models.Model):
	removed = models.DateTimeField(null=True, default=None)

	def delete(self, *args, **kwargs):
		self.removed = timezone.now()
		self.save()
	
	class Meta:
		abstract = True

class UserProfile(MyModel):
	user = models.OneToOneField(User)
	badge_id = models.CharField(max_length=50)
	birthday = models.DateField(null=True)
	bloque = models.BooleanField(default=False)
	solde = models.IntegerField(default=0)
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return "Profile : "+self.user.username


class Groupe(MyModel):
	name = models.CharField(max_length=50)
	
	def __unicode__(self):
		return self.name

class Famille(MyModel):
	name = models.CharField(max_length=50)
	alcool = models.BooleanField()
	
	def __unicode__(self):
		return self.name


class Article(MyModel):
	name = models.CharField(max_length=50)
	famille = models.ForeignKey(Famille)
	stockinitial = models.IntegerField(null=True)
	stock = models.IntegerField(null=True)
	enVente = models.BooleanField()
	tva = models.DecimalField(default=0.0, max_digits=3, decimal_places=2)
	prix_ttc = models.IntegerField()
	assos = models.ManyToManyField(Asso)
	
	@staticmethod
	def apply_asso_view_limits(asso, queryset):
		return queryset.filter(assos__pk=asso.pk)

	
	def __unicode__(self):
		return self.name
		
class PointOfSale(MyModel):
	name = models.CharField(max_length=50)
	key = models.CharField(max_length=50,null=True)
	check_seller_pass = models.BooleanField()

	def __unicode__(self):
		return self.name
		
class ArticlePos(MyModel):
	article = models.ForeignKey(Article, related_name="article")
	position = models.IntegerField()
	pos = models.ForeignKey(PointOfSale, related_name="pointdevente")
	debut = models.TimeField()
	fin = models.TimeField()

class Reversement(MyModel):
	date = models.DateTimeField()
	montant = models.IntegerField()
	asso = models.ForeignKey(Asso)
	ref = models.CharField(max_length=255)
	
	def __unicode__(self):
		return self.name


class Transaction(MyModel):
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
	
	@staticmethod
	def apply_asso_view_limits(asso, queryset):
		return queryset.filter(asso__pk=asso.pk)
	
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
	userfrom = models.OneToOneField(User, related_name="userfrom")

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


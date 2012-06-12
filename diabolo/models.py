from django.db import models
from django.contrib.auth.models import User

from django.db.models.signals import post_save


class UserProfile(models.Model):
	user = models.OneToOneField(User)
	badge_id = models.CharField(max_length=50)



def create_user_profile(sender, instance, created, **kwargs):
	if created:
		m = hashlib.sha1()
		m.update(str(random.random()))
		m.update(instance.username)
		activation_key = m.hexdigest()
		key_expires = timezone.now() + timezone.timedelta(2)
		UserProfile.objects.create(user=instance,
							key_expires=key_expires,
							activation_key=activation_key,
		)

post_save.connect(create_user_profile, sender=User)


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

	def __unicode__(self):
		return self.name
		
class PointOfSale(models.Model):
	name = models.CharField(max_length=50)
	key = models.CharField(max_length=50,null=True)
	MustCheckSeller = models.BooleanField()

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


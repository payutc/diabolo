from django.db import models
from django.contrib.auth.models import User

from django.db.models.signals import post_save

from django.core.exceptions import ValidationError

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


def create_user_profile(sender, instance, created, **kwargs):
	if created:
		UserProfile.objects.get_or_create(user=instance)

post_save.connect(create_user_profile, sender=User)

class Groupe(models.Model):
	name = models.CharField(max_length=50)
	
	def __unicode__(self):
		return self.name

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
	TCHOICE = (
		('P', 'Paybox'),
		('A', 'Achat'),
		('V', 'Virement')
	)
	t = models.CharField(max_length=1, choices=TCHOICE)
	description = models.CharField(max_length=255)

	def __unicode__(self):
		return "Transaction(type=%s,montant=%s,date=%s,user=%s)" % (
			self.t,
			self.amount,
			self.date,
			self.user
		)

class Achat(models.Model):
	article = models.ForeignKey(Article)
	buyer = models.ForeignKey(User, related_name="buyer")
	seller = models.ForeignKey(User, related_name="seller")
	asso = models.ForeignKey(Asso, related_name="asso")
	pos = models.ForeignKey(PointOfSale, related_name="pos")
	date = models.DateTimeField(auto_now_add=True)
	tva = models.DecimalField(max_digits=3, decimal_places=2)
	transaction = models.ForeignKey(Transaction, null=True)
	
	amount = None
	description = None
	
	def save(self, *args, **kwargs):
		amount = kwargs.get('amount', None) or self.amount
		description = kwargs.get('description', None) or self.description
	
		if not amount or not description:
			raise Exception("need amount and description")
			
		if 'amount' in kwargs: del kwargs['amount']
		if 'description' in kwargs: del kwargs['description']
		
		try:
			self.full_clean(exclude=['transaction','date'])
		except ValidationError as e:
			print e
			raise e
		transaction = Transaction.objects.create(t='A', user=self.buyer, amount=amount, description=description)
		self.transaction = transaction
		super(Achat, self).save(*args, **kwargs)
	
	def __unicode__(self):
		return "Achat(article=%s,seller=%s,buyer=%s,pos=%s,asso=%s,date=%s)" % (
			self.article,
			self.seller,
			self.buyer,
			self.pos,
			self.asso,
			self.date,
		)

		
class Paybox(models.Model):
	loader = models.ForeignKey(User, related_name="loader")
	date = models.DateTimeField(auto_now_add=True)
	amount = models.IntegerField()
	STATECHOICE = (
		('W', 'Wait paybox'),
		('A', 'Aborted'),
		('S', 'Success')
	)
	state = models.CharField(max_length=1, choices=STATECHOICE)
	transaction = models.ForeignKey(Transaction, null=True)

	def __unicode__(self):
		return "Paybox(buyer=%s,date=%s,amount=%s,state=%s)" % (
			self.buyer,
			self.date,
			self.amount,
			self.state
		)
		
class Virement(models.Model):
	userfrom = models.ForeignKey(User, related_name="donneur")
	userto = models.ForeignKey(User, related_name="receveur")
	date = models.DateTimeField(auto_now_add=True)
	amount = models.IntegerField()
	transaction = models.ForeignKey(Transaction, null=True)

	def __unicode__(self):
		return "Virement(donneur=%s,receveur=%s,date=%s,amount=%s)" % (
			self.userfrom,
			self.userto,
			self.date,
			self.amount
		)

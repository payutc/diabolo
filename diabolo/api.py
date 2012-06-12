from tastypie.resources import ModelResource
from tastypie import fields
from tastypie.authentication import Authentication
from tastypie.authorization import Authorization

from django.contrib.auth.models import User
from diabolo.models import *



class SillyAuthentication(Authentication):
	def is_authenticated(self, request, **kwargs):
		if request.user:
			print kwargs
			return True
		return False

	# Optional but recommended
	def get_identifier(self, request):
		return request.user.username

class SillyAuthorization(Authorization):
	def is_authorized(self, request, object=None):
		return True

	# Optional but useful for advanced limiting, such as per user.
	def apply_limits(self, request, object_list):
		if request and hasattr(request, 'user'):
			return object_list.filter(author__username=request.user.username)

		return object_list.none()


class UserResource(ModelResource):
	class Meta:
		queryset = User.objects.all()
		resource_name = 'user'
		#excludes = ['email', 'password', 'is_active', 'is_staff', 'is_superuser']
		fields = ['username', 'first_name', 'last_name']
		allowed_methods = ['get']
		#authentication = BasicAuthentication()
		#authorization = DjangoAuthorization()

class ArticleResource(ModelResource):
	class Meta:
		queryset = Article.objects.all()
		resource_name = 'article'

class POSResource(ModelResource):
	class Meta:
		queryset = PointOfSale.objects.all()
		resource_name = 'pos'
	
class TransactionResource(ModelResource):
	buyer = fields.ForeignKey(UserResource, 'buyer')
	seller = fields.ForeignKey(UserResource, 'seller')
	article = fields.ForeignKey(ArticleResource, 'article')
	pos = fields.ForeignKey(POSResource, 'pos')
	
	class Meta:
		queryset = Transaction.objects.select_related(depth=1).all()
		resource_name = 'transaction'
		authorization = Authorization()

class ReversementResource(ModelResource):
	class Meta:
		queryset = Reversement.objects.all()
		
class FamilleResource(ModelResource):
	class Meta:
		queryset = Famille.objects.all()
		
class AssoResource(ModelResource):
	class Meta:
		queryset = Asso.objects.all()

class GroupeResource(ModelResource):
	class Meta:
		queryset = Groupe.objects.all()
		

from tastypie.resources import ModelResource
from tastypie import fields
from tastypie.authorization import Authorization

from django.contrib.auth.models import User
from diabolo.models import *


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


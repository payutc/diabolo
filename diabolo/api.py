from tastypie.resources import ModelResource
from tastypie import fields
from tastypie.authentication import Authentication
from tastypie.authorization import Authorization
from tastypie.http import HttpUnauthorized

from django.contrib.auth.models import User
from diabolo.models import *

class SillyAuthentication(Authentication):
	def _unauthorized(self):
		return HttpUnauthorized()

	def extract_credentials(self, request):
		if request.META.get('HTTP_AUTHORIZATION'):
			(auth_type, data) = request.META['HTTP_AUTHORIZATION'].split()

			if auth_type.lower() != 'pos':
				raise ValueError("Incorrect authorization header.")

			badge_id, pos_id, pos_key = data.split(':', 1)
		else:
			badge_id = request.GET.get('badge_id') or request.POST.get('badge_id')
			password = request.GET.get('pass') or request.POST.get('pass')
			pos_id = request.GET.get('pos_id') or request.POST.get('pos_id')
			pos_key = request.GET.get('pos_key') or request.POST.get('pos_key')

		return badge_id, password, pos_id, pos_key

	def is_authenticated(self, request, **kwargs):
		"""
		Finds the user and checks their API key.

		Should return either ``True`` if allowed, ``False`` if not or an
		``HttpResponse`` if you need something custom.
		"""

		try:
			badge_id, password, pos_id, pos_key = self.extract_credentials(request)
		except ValueError:
			return self._unauthorized()

		if not badge_id or not pos_id or not pos_key:
			return self._unauthorized()

		try:
			user = User.objects.get(userprofile__badge_id__exact=badge_id)
			pos = PointOfSale.objects.get(pk=pos_id)
		except Exception as ex:
			print ex
			return self._unauthorized()
		if pos.key != pos_key:
			return self._unauthorized()
		if pos.check_seller_pass and password != user.userprofile.pass_seller:
			return self._unauthorized()
		
		request.user = user
		request.session['pos'] = pos
		
		return True

	def get_identifier(self, request):
		"""
		Provides a unique string identifier for the requestor.

		This implementation returns the user's username.
		"""
		badge_id, password, pos_id, pos_key = self.extract_credentials(request)
		return badge_id or 'nouser'


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
		authentication = SillyAuthentication() #BasicAuthentication()
		#authorization = DjangoAuthorization()

class ArticleResource(ModelResource):
	class Meta:
		queryset = Article.objects.all()
		resource_name = 'article'
		authentication = SillyAuthentication()

class POSResource(ModelResource):
	class Meta:
		queryset = PointOfSale.objects.all()
		resource_name = 'pos'
		authentication = SillyAuthentication()
	
class TransactionResource(ModelResource):
	buyer = fields.ForeignKey(UserResource, 'buyer')
	seller = fields.ForeignKey(UserResource, 'seller')
	article = fields.ForeignKey(ArticleResource, 'article')
	pos = fields.ForeignKey(POSResource, 'pos')
	
	class Meta:
		queryset = Transaction.objects.select_related(depth=1).all()
		resource_name = 'transaction'
		authorization = Authorization()
		authentication = SillyAuthentication()

class ReversementResource(ModelResource):
	class Meta:
		queryset = Reversement.objects.all()
		authentication = SillyAuthentication()
		
class FamilleResource(ModelResource):
	class Meta:
		queryset = Famille.objects.all()
		authentication = SillyAuthentication()
		
class AssoResource(ModelResource):
	class Meta:
		queryset = Asso.objects.all()
		authentication = SillyAuthentication()

class GroupeResource(ModelResource):
	class Meta:
		queryset = Groupe.objects.all()
		authentication = SillyAuthentication()
		

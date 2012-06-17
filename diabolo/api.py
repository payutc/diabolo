from tastypie.resources import ModelResource
from tastypie import fields
from tastypie.authentication import Authentication
from tastypie.authorization import Authorization
from tastypie.http import HttpUnauthorized
from tastypie.utils import is_valid_jsonp_callback_value, dict_strip_unicode_keys, trailing_slash

from django.conf.urls.defaults import url
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate,login,logout
from diabolo.models import *
from django.conf import settings


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
		if hasattr(request, 'user') and request.user.is_authenticated():
			return True

		try:
			badge_id, password, pos_id, pos_key = self.extract_credentials(request)
		except ValueError:
			return self._unauthorized()

		if not badge_id or not pos_id or not pos_key:
			return self._unauthorized()

		
		# recuperation pos
		try:
			pos = PointOfSale.objects.get(pk=pos_id)
		except Exception as ex:
			print ex
			return self._unauthorized()
		if pos.key != pos_key:
			return self._unauthorized()

		# recuperation seller
		if not pos.check_seller_pass:
			password = None
		user = authenticate(badge_id=badge_id, password=password)
		if not user or not user.is_active:
			return self._unauthorized

		# enregistrement dans la session
		login(request, user)
		request.session['pos'] = pos
		return True

	def get_identifier(self, request):
		"""
		Provides a unique string identifier for the requestor.

		This implementation returns the user's username.
		"""
		return request.user.username


class SillyAuthorization(Authorization):
	def is_authorized(self, request, object=None):
		return True

	# Optional but useful for advanced limiting, such as per user.
	def apply_limits(self, request, object_list):
		# GET-style methods are always allowed.
		if request.method in ('GET', 'OPTIONS', 'HEAD'):
			return True

		klass = self.resource_meta.object_class

		# If it doesn't look like a model, we can't check permissions.
		if not klass or not getattr(klass, '_meta', None):
			print 'Does not look like a model, we can not check permissions'
			return False

		permission_map = {
			'POST': ['%s.add_%s'],
			'PUT': ['%s.change_%s'],
			'DELETE': ['%s.delete_%s'],
			'PATCH': ['%s.add_%s', '%s.change_%s', '%s.delete_%s'],
		}
		permission_codes = []

		# If we don't recognize the HTTP method, we don't know what
		# permissions to check. Deny.
		if request.method not in permission_map:
			return False

		for perm in permission_map[request.method]:
			permission_codes.append(perm % (klass._meta.app_label, klass._meta.module_name))

		# User must be logged in to check permissions.
		if not hasattr(request, 'user'):
			return False

		return request.user.has_perms(permission_codes, object_list)

class UserResource(ModelResource):
	class Meta:
		queryset = User.objects.all()
		resource_name = 'user'
		#excludes = ['email', 'password', 'is_active', 'is_staff', 'is_superuser']
		fields = ['username', 'first_name', 'last_name']
		allowed_methods = ['get']
		authentication = SillyAuthentication() #BasicAuthentication()
		#authorization = DjangoAuthorization()
	
	def override_urls(self):
		return [
			url(r"^(?P<resource_name>%s)/login%s$" %
				(self._meta.resource_name, trailing_slash()),
				self.wrap_view('login'), name="api_login"),
			url(r"^(?P<resource_name>%s)/logout%s$" %
				(self._meta.resource_name, trailing_slash()),
				self.wrap_view('logout'), name="api_logout"),
			url(r"^(?P<resource_name>%s)/me%s$" %
				(self._meta.resource_name, trailing_slash()),
				self.wrap_view('me'), name="api_me"),
		] + self.base_urls()

	def me(self, request, **kwargs):
		kwargs['pk'] = request.user.id
		return self.dispatch_detail(request, **kwargs)
	
	def login(self, request, **kwargs):
		self.is_authenticated(request)
		return self.create_response(request, {'success': True})
		
	def logout(self, request, **kwargs):
		logout(request)
		return self.create_response(request, {'success': True}) 
	
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
		#authentication = SillyAuthentication()

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

class GroupResource(ModelResource):
	class Meta:
		queryset = Group.objects.all()
		authentication = SillyAuthentication()
		

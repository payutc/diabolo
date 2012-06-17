from tastypie.resources import ModelResource
from tastypie import fields
from tastypie.authentication import MultiAuthentication,BasicAuthentication,Authentication
from tastypie.authorization import Authorization
from tastypie.http import HttpUnauthorized
from tastypie.utils import is_valid_jsonp_callback_value, dict_strip_unicode_keys, trailing_slash

from django.conf.urls.defaults import url
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate,login,logout
from diabolo.models import *
from django.conf import settings

class UserAuthentication(Authentication):
	def _unauthorized(self):
		return HttpUnauthorized()

	def extract_credentials(self, request):
		if request.META.get('HTTP_AUTHORIZATION'):
			(auth_type, data) = request.META['HTTP_AUTHORIZATION'].split()

			if auth_type.lower() != 'pos':
				raise ValueError("Incorrect authorization header.")

			username, password = data.split(':', 1)
		else:
			username = request.GET.get('username') or request.POST.get('username')
			password = request.GET.get('password') or request.POST.get('password')

		return username, password
	
	def is_authenticated(self, request, **kwargs):
		"""
		Finds the user and checks their API key.

		Should return either ``True`` if allowed, ``False`` if not or an
		``HttpResponse`` if you need something custom.
		"""
		if hasattr(request, 'user') and request.user.is_authenticated():
			return True

		try:
			username, password = self.extract_credentials(request)
		except ValueError:
			return self._unauthorized()

		if not username or not password:
			return self._unauthorized()
		
		user = authenticate(username=username, password=password)
		if not user or not user.is_active:
			return self._unauthorized

		# enregistrement dans la session
		login(request, user)
		
		return True

	def get_identifier(self, request):
		"""
		Provides a unique string identifier for the requestor.

		This implementation returns the user's username.
		"""
		return request.user.username
	
class PosAuthentication(Authentication):
	def _unauthorized(self):
		return HttpUnauthorized()

	def extract_credentials(self, request):
		if request.META.get('HTTP_AUTHORIZATION'):
			(auth_type, data) = request.META['HTTP_AUTHORIZATION'].split()

			if auth_type.lower() != 'pos':
				raise ValueError("Incorrect authorization header.")

			badge_id, password, pos_id, pos_key = data.split(':', 3)
		else:
			badge_id = request.GET.get('badge_id') or request.POST.get('badge_id')
			password = request.GET.get('password') or request.POST.get('password')
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


class TransactionAuthorization(Authorization):
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
		authentication = MultiAuthentication(PosAuthentication(),UserAuthentication())
		#authorization = DjangoAuthorization()
	
	def prepend_urls(self):
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
		]

	def me(self, request, **kwargs):
		kwargs['pk'] = request.user.id
		return self.dispatch_detail(request, **kwargs)
	
	def login(self, request, **kwargs):
		print request.GET
		self.throttle_check(request)
		self.is_authenticated(request)
		self.log_throttled_access(request)
		return self.create_response(request, {'success': True})
		
	def logout(self, request, **kwargs):
		self.throttle_check(request)
		logout(request)
		self.log_throttled_access(request)
		return self.create_response(request, {'success': True}) 
	
class ArticleResource(ModelResource):
	class Meta:
		queryset = Article.objects.all()
		resource_name = 'article'
		authentication = PosAuthentication()

class POSResource(ModelResource):
	class Meta:
		queryset = PointOfSale.objects.all()
		resource_name = 'pos'
		authentication = PosAuthentication()

class AchatResource(ModelResource):
	def hydrate(self, bundle):
		print "COUCOU",bundle
		return bundle
	
	class Meta:
		queryset = Achat.objects.select_related(depth=1).all()
		authorization = Authorization()
		authentication = MultiAuthentication(PosAuthentication(),UserAuthentication())

		
class TransactionResource(ModelResource):
	buyer = fields.ForeignKey(UserResource, 'buyer')
	seller = fields.ForeignKey(UserResource, 'seller')
	article = fields.ForeignKey(ArticleResource, 'article')
	pos = fields.ForeignKey(POSResource, 'pos')
	
	class Meta:
		queryset = Transaction.objects.select_related(depth=1).all()
		resource_name = 'transaction'
		authorization = Authorization()
		#authentication = PosAuthentication()

class ReversementResource(ModelResource):
	class Meta:
		queryset = Reversement.objects.all()
		authentication = PosAuthentication()
		
class FamilleResource(ModelResource):
	class Meta:
		queryset = Famille.objects.all()
		authentication = PosAuthentication()
		
class AssoResource(ModelResource):
	class Meta:
		queryset = Asso.objects.all()
		authentication = PosAuthentication()

class GroupResource(ModelResource):
	class Meta:
		queryset = Group.objects.all()
		authentication = PosAuthentication()
		

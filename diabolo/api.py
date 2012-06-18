# -*- coding: utf-8 -*-
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

from collections import OrderedDict

class MyAuthentication(Authentication):
	def __init__(self, auth_type, credentials):
		# identification par header
		self.auth_type = auth_type
		# stores credentials extracted
		self.credentials = dict()
		self.required = dict()
		for name,required in credentials:
			self.credentials[name] = None
			self.required[name] = required
			

	def _unauthorized(self):
		return HttpUnauthorized()
	
	def pre_authenticate(self, request):
		pass

	def authenticate(self, request):
		user = authenticate(**self.credentials)
		return user
	
	def post_login(self, request, user):
		pass

	def extract_credentials(self, request):
		if request.META.get('HTTP_AUTHORIZATION'):
			(auth_type, data) = request.META['HTTP_AUTHORIZATION'].split()

			if auth_type.lower() != 'pos':
				raise ValueError("Incorrect authorization header.")

			values = data.split(':', len(d)-1)
			for x,v in zip(self.credentials,values):
				self.credentials[x] = v
		else:
			for x in self.credentials:
				self.credentials[x] = request.GET.get(x) or request.POST.get(x)
	
	def is_authenticated(self, request):

		# check si l'user est déjà autentifié
		if hasattr(request, 'user') and request.user.is_authenticated():
			return True
		
		# récupération des crédentials
		try:
			self.extract_credentials(request)
		except ValueError:
			return self._unauthorized()

		# check que ceux requies sont bien présents
		for x in self.credentials:
			required = self.required.get(x, False)
			if required and not self.credentials[x]:
				return self._unauthorized()

		# pre authenticate
		try:
			self.pre_authenticate(request)
		except Exception as ex:
			print ex
			return self._unauthorized()

		# authenticate
		user = self.authenticate(request)
		if not user or not user.is_active:
			return self._unauthorized

		# login
		login(request, user)
		# post login
		self.post_login(request, user)
		
		return True

	def get_identifier(self, request):
		"""
		Provides a unique string identifier for the requestor.

		This implementation returns the user's username.
		"""
		return request.user.username
	
class UserAuthentication(MyAuthentication):
	def __init__(self):
		super(UserAuthentication, self).__init__('user', (('username',True),('password',True)))
	
	
class PosAuthentication(MyAuthentication):
	def __init__(self):
		super(PosAuthentication, self).__init__('user', (('badge_id',True),('password',False),('pos_id',True),('pos_key',True)))

	def pre_authenticate(self, request):
		self.pos = PointOfSale.objects.get(pk=self.credentials['pos_id'])
		
		if self.pos.key != pos_key:
			raise Exception('pos_key is invalid')

		if not self.pos.check_seller_pass:
			self.credentials['password'] = False

	def post_login(self, request):
		request.session['pos'] = self.pos


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
		

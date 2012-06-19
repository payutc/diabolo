# -*- coding: utf-8 -*-
"""
from tastypie.resources import ModelResource
from tastypie import fields
from tastypie.authentication import MultiAuthentication,BasicAuthentication,Authentication
from tastypie.authorization import Authorization
from tastypie.http import HttpUnauthorized
from tastypie.utils import is_valid_jsonp_callback_value, dict_strip_unicode_keys, trailing_slash
from tastypie.validation import Validation

from guardian.shortcuts import *

from django.conf.urls.defaults import url
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate,login,logout
from diabolo.models import *
from django.conf import settings
"""
from tastypie.resources import ModelResource
from tastypie import fields
from tastypie.utils import is_valid_jsonp_callback_value, dict_strip_unicode_keys, trailing_slash
from tastypie.authentication import MultiAuthentication,BasicAuthentication,Authentication
from tastypie.authorization import Authorization

from django.conf.urls.defaults import url
from diabolo.models import *
from django.contrib.auth import authenticate,login,logout

from authorization import *
from authentication import *

class UserResource(ModelResource):
	class Meta:
		queryset = User.objects.all()
		resource_name = 'user'
		#excludes = ['email', 'password', 'is_active', 'is_staff', 'is_superuser']
		fields = ['username', 'first_name', 'last_name']
		allowed_methods = ['get']
		authentication = MultiAuthentication(PosAuthentication(),UserAuthentication())
	
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
		allowed_methods = ['get']
		authentication = PosAuthentication()
		authorization = ArticleAuthorization()

class AchatResource(ModelResource):
	def hydrate(self, bundle):
		print "HYDRATE"
		# get article
		article = Article.objects.get(pk=bundle.data['article'])
		# get buyer
		buyer = User.objects.get(userprofile__badge_id=bundle.data['badge_id'])
		# get seller
		seller = bundle.request.user
		# get pos
		pos = bundle.request.session['pos']
		# get asso
		asso = bundle.request.session['asso']

		# store in data
		bundle.data['tva'] = article.tva

		# store directly relation in object
		bundle.obj.article = article
		bundle.obj.seller = seller
		bundle.obj.buyer = buyer
		bundle.obj.pos = pos
		bundle.obj.asso = asso

		# store directly amount and description needed for save function
		bundle.obj.amount = article.prix_ttc
		bundle.obj.description = bundle.data['description']
		
		return bundle
	
	def obj_update(self, bundle, request=None, skip_errors=False, **kwargs):
		"""
		Permet d'éviter l'édition d'un objet.
		"""
		raise Exception("interdit d'éditer un achat")
	
	def obj_delete(self, request=None, **kwargs):
		"""
		Surcharge de la méthode obj_delete à cause du patch, qui ne donne
		aucun moyen de vérifier lors du premier is_authorized.
		A voir pour le futur du côté de
		request = convert_post_to_patch(request)
		deserialized = self.deserialize(request, ...)
		pour faire le test dans la classe AchatAuthorization
		"""
		obj = kwargs.pop('_obj', None)

		if not hasattr(obj, 'delete'):
			try:
				obj = self.obj_get(request, **kwargs)
			except ObjectDoesNotExist:
				raise NotFound("A model instance matching the provided arguments could not be found.")

		self.is_authorized(request, obj)
		obj.delete()
		
	class Meta:
		queryset = Achat.objects.select_related(depth=1).all()
		authorization = AchatAuthorization()
		authentication = PosAuthentication()

class AssoResource(ModelResource):
	class Meta:
		queryset = Asso.objects.all()
		authentication = PosAuthentication()

class PayboxResource(ModelResource):
	def hydrate(self, bundle):
		# TODO call paybox
		# TODO remplir les champs
		return bundle
		
	class Meta:
		queryset = Paybox.objects.all()
		allowed_methods = ['get', 'post']
		authentication = UserAuthentication()

class TransactionResource(ModelResource):
	class Meta:
		queryset = Transaction.objects.all()
		allowed_methods = ['get']
		authentication = UserAuthentication()

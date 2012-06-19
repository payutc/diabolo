# -*- coding: utf-8 -*-
from tastypie.authentication import Authentication
from tastypie.http import HttpUnauthorized

from django.contrib.auth import authenticate,login,logout

from collections import OrderedDict

from diabolo.models import *

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

	def post_authenticate(self, request, user):
		pass
	
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
			print "no user"
			return self._unauthorized
		
		# post authenticate
		try:
			self.post_authenticate(request,user)
		except Exception as ex:
			print ex
			return self._unauthorized()
		
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
		
class CasAuthentication(MyAuthentication):
	def __init__(self):
		super(CasAuthentication, self).__init__('cas', (('ticket',True),('service',True)))
	
	
class PosAuthentication(MyAuthentication):
	def __init__(self):
		super(PosAuthentication, self).__init__('pos', (('badge_id',True),('password',False),('pos_id',True),('pos_key',True),('asso_id',True)))

	def pre_authenticate(self, request):
		# TODO check seller in asso
		self.pos = PointOfSale.objects.get(pk=self.credentials['pos_id'])
		self.asso = Asso.objects.get(pk=self.credentials['asso_id'])
		
		if self.pos.key != self.credentials['pos_key']:
			raise Exception('pos_key is invalid')

		if not self.pos.check_seller_pass:
			self.credentials['password'] = False
	
	def post_authenticate(self, request, user):
		if not self.asso.user_is_seller(user):
			raise Exception('user is not a seller of this association')
		
	def post_login(self, request, user):
		request.session['pos'] = self.pos
		request.session['asso'] = self.asso


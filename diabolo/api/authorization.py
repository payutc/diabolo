# -*- coding: utf-8 -*-
from tastypie.authorization import Authorization

from guardian.shortcuts import *

from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate,login,logout
from diabolo.models import *



class AchatAuthorization(Authorization):
	def extract_permission_codes(self, request):
		klass = self.resource_meta.object_class
		
		permission_map = {
			'GET': ['%s.view_%s'],
			'POST': ['%s.add_%s'],
			'DELETE': ['%s.delete_%s'],
			'PATCH': ['%s.add_%s'],
		}
		
		if request.method not in permission_map:
			return []
		
		permission_codes = []
		for perm in permission_map[request.method]:
			permission_codes.append(perm % (klass._meta.app_label, klass._meta.module_name))

		return permission_codes

	def is_authorized(self, request, object=None):
		# vérification qu'on a bien un user, un pos et une asso
		if not (hasattr(request, 'user') and 'pos' in request.session and 'asso' in request.session):
			return False

		# GET-style methods are always allowed.
		if request.method in ('GET', 'OPTIONS', 'HEAD'):
			print "GET", object
			return True
		
		klass = self.resource_meta.object_class

		# If it doesn't look like a model, we can't check permissions.
		if not klass or not getattr(klass, '_meta', None):
			return True


		permission_codes = self.extract_permission_codes(request)
		# If we don't recognize the HTTP method, we don't know what
		# permissions to check. Deny.
		if not permission_codes:
			return False

		if not request.user.has_perms(permission_codes, object):
			print "Pas le droit", permission_codes, object
			return False

		print "ok", permission_codes, object
		return True
	
	def apply_limits(self, request, object_list):
		permission_codes = self.extract_permission_codes(request)
		return get_objects_for_group(request.session['asso'], permission_codes, object_list)


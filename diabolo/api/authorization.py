# -*- coding: utf-8 -*-
from tastypie.authorization import Authorization,ReadOnlyAuthorization

from guardian.shortcuts import *
from guardian.core import ObjectPermissionChecker

from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate,login,logout
from diabolo.models import *


class ArticleAuthorization(ReadOnlyAuthorization):
	def is_authorized(self, request, object=None):
		# vérification qu'on a bien un user, un pos et une asso
		if not (hasattr(request, 'user') and 'pos' in request.session and 'asso' in request.session):
			return False
		return super(ArticleAuthorization, self).is_authorized(request, object)
	
	def apply_limits(self, request, object_list):
		queryset = Article.apply_asso_view_limits(request.session['asso'], object_list)
		# TODO filtrer par période d'ouverture
		#queryset.filter(...)
		return queryset

class AchatAuthorization(Authorization):
	def is_authorized(self, request, object=None):
		# vérification qu'on a bien un user, un pos et une asso
		if not (hasattr(request, 'user') and 'pos' in request.session and 'asso' in request.session):
			return False

		# GET-style methods are always allowed.
		# Note un filtre est appliqué ensuite dans apply_limits
		if request.method == 'GET':
			print "GET", object
			return True

		# toujours autoriser, le clean sera fait dans lors de l'hydratation
		elif request.method == 'POST':
			return True

		# autoriser les patch pour les bulks insert, de même que post
		# le clean se fera côté AchatResource
		elif request.method == 'PATCH':
			return True

		return False
	
	def apply_limits(self, request, object_list):
		print "apply_limits", object_list
		queryset = Achat.apply_asso_view_limits(request.session['asso'], object_list)
		return queryset


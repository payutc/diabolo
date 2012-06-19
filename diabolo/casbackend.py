from django.conf import settings
from django.contrib.auth.models import User, check_password
import urllib2, re

class CasBackend(object):
	def authenticate(self, ticket, service, **kwargs):
		val_url = "https://cas.utc.fr/cas/validate" + \
		 '?service=' + service + \
		 '&ticket=' + ticket
		print "cas_debug", val_url
		r = urllib2.urlopen(val_url).readlines()   # returns 2 lines
		print "cas_debug", r
		if len(r) == 2 and re.match("yes", r[0]) != None:
			login = r[1].strip()
		else:
			print "cas_debug no user"
			return None
		try:
			user = User.objects.get(username=login)
			return user
		except User.DoesNotExist:
			print "cas_debug user unfound", login
			return None

	def get_user(self, user_id):
		try:
			user = User.objects.get(pk=user_id)
			return user
		except User.DoesNotExist:
			return None

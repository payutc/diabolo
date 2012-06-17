from django.conf import settings
from django.contrib.auth.models import User, check_password

class BadgeBackend(object):
	def authenticate(self, badge_id=None, password=None):
		try:
			user = User.objects.get(userprofile__badge_id__exact=badge_id)
			if not password or user.check_password(password):
				return user
			return None
		except User.DoesNotExist:
			return None

	def get_user(self, user_id):
		try:
			user = User.objects.get(pk=user_id)
			return user
		except User.DoesNotExist:
			return None

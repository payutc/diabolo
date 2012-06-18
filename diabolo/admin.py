import diabolo.models as diabolo_models
from django.db.models import Model
from django.contrib import admin
from guardian.admin import GuardedModelAdmin
import inspect


for name,obj in inspect.getmembers(diabolo_models):
	try:
		if name and inspect.isclass(obj) and isinstance(obj(), Model):
			try:
				admin.site.register(obj, GuardedModelAdmin)
			except admin.sites.AlreadyRegistered:
				pass
	except Exception:
		pass

"""
admin.site.register(UserProfile)
admin.site.register(Article)
admin.site.register(Asso)
admin.site.register(PointOfSale)
admin.site.register(Transaction)
admin.site.register(Reversement)
"""

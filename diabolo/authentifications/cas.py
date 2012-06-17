import urllib2, re
from xml.dom.minidom import parse, parseString

class CasClient:
	@staticmethod
	def Validate(ticket, service):
		val_url = "https://cas.utc.fr/cas/validate" + \
		 '?service=' + service + \
		 '&ticket=' + ticket
		print val_url
		r = urllib2.urlopen(val_url).readlines()   # returns 2 lines
		print r
		if len(r) == 2 and re.match("yes", r[0]) != None:
			return r[1].strip()
		return None


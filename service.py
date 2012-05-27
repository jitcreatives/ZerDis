#!/usr/bin/python

import os
import cherrypy
from cherrypy.lib.static import serve_file

from logic.find_prefix import find_prefixes
from logic.ClientContext import ClientContext
from logic.KnfAuthorize import KnfAuthorize
from logic.KnfRule import KnfRule
from logic.LiteralMatches import LiteralMatches

HTTPS = False
SERVER = "http://192.168.12.112"
PORT = ":8080"
PATH = ""

class CertDistribution(object):
    
    knf = KnfAuthorize()


    def __init__(self):
    	lit = LiteralMatches(negated = False, key = 'domain', pattern = '[mail]+')
    	rule = KnfRule()
    	rule.add_literal(lit)
    	self.knf.add_rule(rule)

    @cherrypy.expose
    def default(self, *args, **kwargs):
    	'''
    	if root ('/') return prefixes 
    	if not root: 
    		search for a matching prefix
    		success: return found buckets for prefix
    		else: return random text phrase :)
		if it is a bucket:
			return object
    	'''
    	
    	headers = cherrypy.request.headers
    	
        url = cherrypy.url().replace("%s%s" % (SERVER, PORT),"")
        if url == '/':
        	prefix_dict = find_prefixes()
        	return str(prefix_dict.keys())
        elif not os.path.exists(url[1:]): 
        	prefix_dict = find_prefixes()
        	try:
        		buckets = prefix_dict[url[1:]]
        		return str(prefix_dict[url[1:]])
        	except:
        		return "nothing found for this prefix, sorry dude!"
        else:
        	# create client context
        	cc = ClientContext()
        	cc.context_map = headers
        	#cc.add_domain(headers["domain"]) 

    		authorized = self.knf.authorize(cc)
    		if authorized:
    			return serve_file(os.getcwd() + url, "application/x-download", "attachment")
    		else:
    			cherrypy.response.status = 401
    			return "UNAUTHORIZED"
        return("Hallo Joerg -> CertDistribution powered by J.I.T.")

if __name__ == '__main__':
	cherrypy.server.socket_host = '192.168.12.112'
	#cherrypy.root = CertDistribution()
	#cherrypy.server.start()
	cherrypy.quickstart(CertDistribution())

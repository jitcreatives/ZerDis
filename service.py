#!/usr/bin/python

import os
import cherrypy
from cherrypy.lib.static import serve_file

from logic.find_prefix import find_prefixes
from logic.ClientContext import ClientContext
from logic.KnfAuthorize import KnfAuthorize
from logic.KnfRule import KnfRule
from logic.LiteralMatches import LiteralMatches
from logic.LiteralDNSCheck import LiteralDNSCheck
from logic.LiteralSystemCall import LiteralSystemCall

HTTPS = False
SERVER = "https://mgmt01.jit-creatives.de"
PORT = ":4661"
PATH = "/var/ssl"

class CertDistribution(object):
    
    knf = KnfAuthorize()


    def __init__(self):
    	lit_1 = LiteralMatches(negated = False, key = 'domain', pattern = '(.*\.jit-creatives.de)|(.*\.jitmail.de)')
    	lit_2 = LiteralDNSCheck(negated = False)
        lit_3 = LiteralSystemCall(negated = False, pattern = "ssh root@$ip exit 0")
    	rule = KnfRule()
        rule.add_literal(lit_3)
        rule.add_literal(lit_1)
    	rule.add_literal(lit_2)

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

    	print headers
        url = cherrypy.url().replace("%s%s" % (SERVER, PORT),"")
        if url == '/':
        	prefix_dict = find_prefixes()
        	return str(prefix_dict.keys())
        elif not os.path.exists(PATH + url): 
        	prefix_dict = find_prefixes()
        	try:
        		buckets = prefix_dict[url[1:]]
        		return str(prefix_dict[url[1:]])
        	except:
        		return "nothing found for this prefix, sorry dude!"
        else:
        	# create client context
        	cc = ClientContext()
        	cc.add_path(url[1:])
        	if headers.has_key("domain"):
        		cc.add_domain(headers["domain"])
        	if headers.has_key("Remote-Addr"):
        		cc.add_ip(headers["Remote-Addr"])
			if headers.has_key("Token"):
				cc.add_ip(headers["Token"])

    		authorized = self.knf.authorize(cc)
    		if authorized:
    			return serve_file(PATH + url, "application/x-download", "attachment")
    		else:
    			cherrypy.response.status = 401
    			return "UNAUTHORIZED"
        return "CertDistribution powered by J.I.T.<br />If you see this message something went wrong."

if __name__ == '__main__':
	server_config = {
        'server.socket_host': 'mgmt01.jit-creatives.de',
        'server.socket_port':4661,

        'server.ssl_module':'pyopenssl',
        'server.ssl_certificate':'/var/ssl/mgmt01.jit-creatives.de/req.pem.crt',
        'server.ssl_private_key':'/var/ssl/mgmt01.jit-creatives.de/req.pem.key',
        'server.ssl_certificate_chain':'/var/ssl/startssl_caincrt'
    	}
	cherrypy.config.update(server_config)
	cherrypy.quickstart(CertDistribution())

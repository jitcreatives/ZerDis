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
SERVER = "https://csr-pc45.zib.de"
LISTEN = "0.0.0.0"
PORT = ":4661"
PATH = "/var/ssl"

CERT = '/home/explicit/data/pim/certs/DFN-Verein_PCA_Grid_G01/cert-host_csr-pc45.pem'
KEY = '/home/explicit/data/pim/certs/DFN-Verein_PCA_Grid_G01/keys/cert-host_csr-pc45.key'
CA = '/home/explicit/data/pim/certs/DFN-Verein_PCA_Grid_G01.pem'
#CERT = '/var/ssl/mgmt01.jit-creatives.de/req.pem.crt',
#KEY = '/var/ssl/mgmt01.jit-creatives.de/req.pem.key',
#CA = '/var/ssl/startssl_caincrt'

class CertDistribution(object):
    
    knf = KnfAuthorize()


    def __init__(self):
        if not os.path.exists( PATH ):
            raise ValueError( PATH + " does not exist" )

    	rule = KnfRule()

    	lit_1 = LiteralMatches(negated = False, key = 'domain', pattern = '.*')
        rule.add_literal(lit_1)

    	lit_2 = LiteralDNSCheck(negated = False)
    	#rule.add_literal(lit_2)

        lit_3 = LiteralSystemCall(negated = False, pattern = "ssh root@$ip exit 0")
        #rule.add_literal(lit_3)

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

        url_no_protocol = cherrypy.url().partition( "://" )[2]
        url_splited = url_no_protocol.partition( "/" )
        url = url_splited[1] + url_splited[2]

        if url == '/':
            prefix_dict = find_prefixes( PATH )
            # define output
            return_str = ""
            for k in prefix_dict.keys():
                return_str += "%s\n" % (k)
        
            #return str(prefix_dict.keys())
            return return_str

        elif not os.path.exists(PATH + url): 
        	prefix_dict = find_prefixes( PATH )
        	try:
        		bucket = prefix_dict[url]
			cherrypy.response.status = 202
        		return str( bucket )
        	except:
			cherrypy.response.status = 404
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
        'server.socket_host': LISTEN,
        'server.socket_port':4661,

        'server.ssl_module':'pyopenssl',
        'server.ssl_certificate':CERT,
        'server.ssl_private_key':KEY,
        'server.ssl_certificate_chain':CA
    	}
	cherrypy.config.update(server_config)
	cherrypy.quickstart(CertDistribution())

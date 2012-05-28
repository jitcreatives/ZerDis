
import socket

from KnfLiteral import KnfLiteral

class LiteralDNSCheck( KnfLiteral ):

        def __init__( self, negated ):
                KnfLiteral.__init__( self, negated )

        def check( self, context ):
                #ip = socket.gethostbyname( context.context_map[ 'domain' ] )
		hostname = socket.gethostbyaddr( context.context_map[ 'ip' ] )[0]

		#print hostname
		#print ip

		#for hostname in hostnames:
		if hostname == context.context_map[ 'domain' ]:
		#if ip == context.context_map[ 'ip' ]:
			return True

		return False

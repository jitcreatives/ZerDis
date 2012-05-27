
import socket

from KnfLiteral import KnfLiteral

class LiteralDNSCheck( KnfLiteral ):

        def __init__( self, negated ):
                KnfLiteral.__init__( self, negated )

        def check( self, context ):
                ip = socket.gethostbyname( context.context_map[ 'domain' ] )
                if ip == context.context_map[ 'domain' ]:
                        return True
                else:
                        return False


class ClientContext( object ):
        context_map = {}

        def add_domain( self, domain ):
                self.context_map[ 'domain' ] = domain

        def add_ip( self, ip ):
                self.context_map[ 'ip' ] = ip

        def add_token( self, token ):
                self.context_map[ 'token' ] = token

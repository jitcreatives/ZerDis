
import KnfRule
import ClientContext

class KnfAuthorize( object ):
        rules = []

        def add_rule( self, rule ):
                if not isinstance( rule, KnfRule ):
                        raise ValueError( "Parameter rule should be of type KnfRule!" );

                self.rules.append( rule );
                return

        def authorize( self, context ):
                if not isinstance( context, ClientContext ):
                        raise ValueError( "Parameter context should be of type ClientContext!" )

                for r in self.rules:
                        try:
                                if r.check( context ):
                                        return True
                        except:
                                pass

                return False

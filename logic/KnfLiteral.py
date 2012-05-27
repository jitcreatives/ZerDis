
class KnfLiteral( object ):
        negated = False

        def __init__( self, negated ):
                super( object, self ).__init__()
                self.negated = negated

        def check( self, context ):
                raise "Method not implemented"

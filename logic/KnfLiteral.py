
class KnfLiteral:
        negated = False

        def __init__( self, negated ):
                self.negated = negated

        def check( self, context ):
                raise "Method not implemented"

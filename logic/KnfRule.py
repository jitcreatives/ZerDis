
from KnfLiteral import KnfLiteral

class KnfRule( object ):
        literals = []

        def add_literal( self, literal, negated = False ):
                if not isinstance( literal, KnfLiteral ):
                        raise ValueError( 'Parameter literal must be of type KnfLiteral' )

                self.literals.append( literal )
                return;

        def check( self, context ):
                for l in self.literals:
                        if not l.negated ^ l.check( context ):
                                return False

                return True


from KnfLiteral import KnfLiteral

class LiteralAllow( KnfLiteral ):


    def __init__( self, negated ):
        KnfLiteral.__init__( self, negated )


    def check( self, context ):
        return True


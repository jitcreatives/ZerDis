
import re

from KnfLiteral import KnfLiteral

class LiteralMatches( KnfLiteral ):
        key = ""

        def __init__( self, negated, key, pattern ):
                super( KnfLiteral, self ).__init__( negated )
                self.key = key
                self.regex = re.compile( pattern )

        def check( self, context ):
                value = context.context_map[ self.key ]
                result = self.regex.match( value )

                if result:
                        return True
                else:
                        return False

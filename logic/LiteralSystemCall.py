
import subprocess
from String import Template

from KnfLiteral import KnfLiteral

class LiteralSystemCall( KnfLiteral ):

    def __init__( self, negated, pattern ):
        KnfLiteral.__init__( self, negated )
        self.pattern = pattern

    def check( self, context ):
        syscall = Template( self.pattern ).substitude( context.context_map )

        if 0 == subprocess.call( syscall, shell = True ):
            return True
        else:
            return False

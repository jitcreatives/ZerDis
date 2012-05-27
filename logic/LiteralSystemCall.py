
import subprocess
from string import Template

from KnfLiteral import KnfLiteral

class LiteralSystemCall( KnfLiteral ):

    def __init__( self, negated, pattern ):
        KnfLiteral.__init__( self, negated )
        self.pattern = pattern

    def check( self, context ):
        syscall = Template( self.pattern ).substitute( context.context_map )

        if 0 == subprocess.call( syscall, shell = True ):
            return True
        else:
            return False

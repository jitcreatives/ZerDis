
LISTEN = "0.0.0.0"
PORT = 4661
PATH = "/var/ssl"

CERT = '/home/explicit/data/pim/certs/DFN-Verein_PCA_Grid_G01/cert-host_csr-pc45.pem'
KEY = '/home/explicit/data/pim/certs/DFN-Verein_PCA_Grid_G01/keys/cert-host_csr-pc45.key'
CA = '/home/explicit/data/pim/certs/DFN-Verein_PCA_Grid_G01.pem'
#CERT = '/var/ssl/mgmt01.jit-creatives.de/req.pem.crt',
#KEY = '/var/ssl/mgmt01.jit-creatives.de/req.pem.key',
#CA = '/var/ssl/startssl_caincrt'

from logic.KnfAuthorize import KnfAuthorize
from logic.KnfRule import KnfRule
from logic.LiteralAllow import LiteralAllow
from logic.LiteralMatches import LiteralMatches
from logic.LiteralDNSCheck import LiteralDNSCheck
from logic.LiteralSystemCall import LiteralSystemCall

knf = KnfAuthorize()

rule = KnfRule()

lit_0 = LiteralAllow( negated = False )
rule.add_literal(lit_0)

lit_1 = LiteralMatches(negated = False, key = 'domain', pattern = '.*')
#rule.add_literal(lit_1)

lit_2 = LiteralDNSCheck(negated = False)
#rule.add_literal(lit_2)

lit_3 = LiteralSystemCall(negated = False, pattern = "ssh root@$ip exit 0")
#rule.add_literal(lit_3)

knf.add_rule(rule)


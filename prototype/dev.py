'''import-just-about-everything file for hacking on this project'''

# Even though it's not a good general programming practice, wildcard imports
# make iterating and hacking on the source code easier.  From "element/", start
# python, type "from prototype.dev import *"
# Now you have access to all the names.

from .Ast import Ast
from .Builtin import *
from .Scanner import Scan
from .Parser import Parse
from .Semantic import *
from .Eval import Eval

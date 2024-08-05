# tuple[str]
# except BS (str) and LF (str)
ADVERB = "'","/","\\"
ASSIGN = ":","::"
BS = "\\"
CPAREN = ')','}',']'
ENDEXP = '',';','\n'
KEYWORD = "and","or","in","export","import"
LF = "\n"
OPAREN = '(','{','['
VERB = tuple("~!@#$%^&*-_=+|,.<>?")
VERBM = tuple(x+':' for x in VERB)
WHITESPACE = " ","\t"


from lark import Lark

p = Lark.open("grascii.lark", 
        parser="earley", 
        ambiguity="explicit")

print(p.parse("NG").pretty())

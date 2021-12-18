import ast

class Module:
    def __init__(self, pytext, filename, node):
        self.filename = filename
        self.lineno = 1
        self.col_offset = 0
        self.end_lineno = len(pytext.split('\n'))
        self.end_col_offset = len(pytext.split('\n')[-1].encode('utf-8'))
        self.docstring = Docstring.get_docstring(filename, node)
        self.classes = [ClassDef(filename, n) for n in node.body if ClassDef.wants(n)]
        self.functions = [FunctionDef(filename, n) for n in node.body if FunctionDef.wants(n)]

    def print(self):
        print(f'MODULE {self.filename}: ({self.lineno}, {self.col_offset}) - ({self.end_lineno}, {self.end_col_offset})')
        self.docstring.print()
        print('Classes:')
        for c in self.classes:
            c.print()
        print('Functions:')
        for f in self.functions:
            f.print()

class ClassDef:
    def __init__(self, filename, node):
        self.filename = filename
        self.lineno = node.lineno
        self.col_offset = node.col_offset
        self.end_lineno = node.end_lineno
        self.end_col_offset = node.end_col_offset
        self.name = node.name
        self.docstring = Docstring.get_docstring(filename, node)
        self.methods = [FunctionDef(filename, n) for n in node.body if FunctionDef.wants(n)]

    def wants(node):
        return isinstance(node, ast.ClassDef) and not node.name.startswith('_')

    def print(self):
        print(f'  CLASS `{self.name}` {self.filename}: ({self.lineno}, {self.col_offset}) - ({self.end_lineno}, {self.end_col_offset})')
        self.docstring.print()
        for m in self.methods:
            m.print()

class FunctionDef:
    def __init__(self, filename, node):
        self.filename = filename
        self.lineno = node.lineno
        self.col_offset = node.col_offset
        self.end_lineno = node.end_lineno
        self.end_col_offset = node.end_col_offset
        self.name = node.name
        self.docstring = Docstring.get_docstring(filename, node)
        self.args = Arg.args(filename, node.args)

    def wants(node):
        return isinstance(node, ast.FunctionDef) and not node.name.startswith('_')

    def print(self):
        print(f'    FUNCTION `{self.name}` {self.filename}: ({self.lineno}, {self.col_offset}) - ({self.end_lineno}, {self.end_col_offset})')
        self.docstring.print()
        for arg in self.args:
            arg.print()

class Arg:
    def __init__(self, filename, node, is_positional, is_keyword, is_vararg, default):
        self.filename = filename
        self.lineno = node.lineno
        self.col_offset = node.col_offset
        self.end_lineno = node.end_lineno
        self.end_col_offset = node.end_col_offset
        self.name = node.arg
        self.typ = Type(None) if node.annotation == None else Type(node.annotation)
        self.is_positional = is_positional
        self.is_keyword = is_keyword
        self.is_vararg = is_vararg
        self.default = default

    def args(filename, args):
        result = []

        posargs = [(arg,False) for arg in args.posonlyargs] + [(arg,True) for arg in args.args]
        posdefaults = [None] * (len(posargs) - len(args.defaults)) + args.defaults

        for (arg,kw),default in zip(posargs, posdefaults):
            result.append(Arg(filename, arg, True, kw, False, Default(default)))

        if args.vararg != None:
            result.append(Arg(filename, args.vararg, True, False, True, Default(None)))

        for arg,default in zip(args.kwonlyargs, args.kw_defaults):
            result.append(Arg(filename, arg, False, True, False, Default(default)))

        if args.kwarg != None:
            result.append(Arg(filename, args.kwarg, False, True, True, Default(None)))

        return result

    def print(self):
        print(f'        ARG `{self.name}` {self.filename}: ({self.lineno}, {self.col_offset}) - ({self.end_lineno}, {self.end_col_offset})')
        print(f'             {"pos " if self.is_positional else ""}{"kw " if self.is_keyword else ""}{"vararg " if self.is_vararg else ""}')
        self.default.print()
        self.typ.print()

class Docstring:
    def __init__(self, filename, string):
        self.filename = filename
        self.string = string

    def get_docstring(filename, node):
        if len(node.body) > 0 and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant) and isinstance(node.body[0].value.value, str):
            return Docstring(filename, node.body[0].value.value)
        else:
            return Docstring(filename, None)

    def print(self):
        if self.string == None:
            print(f'             NO DOCSTRING')
        else:
            print(f'             DOCSTRING')
            for line in self.string.split('\n')[:10]:
                print(f'                {line}')

class Default:
    def __init__(self, node):
        self.node = node

    def print(self):
        if self.node == None:
            print(f'             NO DEFAULT')
        else:
            print(f'             DEFAULT')

class Type:
    def __init__(self, node):
        self.node = node

    def print(self):
        if self.node == None:
            print(f'             NO TYPE')
        else:
            print(f'             TYPE')

def extract_interfaces(pytext, filename):
    module = ast.parse(pytext)
    return Module(pytext, filename, module)

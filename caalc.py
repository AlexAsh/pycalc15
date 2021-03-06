#!/usr/bin/python
# coding: utf

import readline
import sys
import tpg
import itertools
import re


def make_op(s):
    return {
        '+': lambda x,y: x+y,
        '-': lambda x,y: x-y,
        '*': lambda x,y: x*y,
        '/': lambda x,y: x/y,
        '&': lambda x,y: x&y,
        '|': lambda x,y: x|y,
    }[s]


def clear_quotes(string):
    return re.search('[^\'"]+', string).group(0)


class Vector(list):
    def __init__(self, *argp, **argn):
        list.__init__(self, *argp, **argn)

    def __str__(self):
        if not isinstance(self[0], Vector):
            return "[" + " ".join(str(c) for c in self) + "]"
        maxlens = [0 for i in range(len(self[0]))]
        for i in range(len(self[0])):
            maxlen = 0
            for j in range(len(self)):
                if len(str(self[j][i])) > maxlen:
                    maxlen = len(str(self[j][i]))
            maxlens[i] = maxlen
        strings = ''
        for i in range(len(self)):
            for j in range(len(self[0])):
                value = str(self[i][j])
                strings += ' ' * (maxlens[j] - len(value)) + value + ' '
            strings += "\n"
        return "[\n" + strings + "]"

    def __op(self, a, op):
        try:
            return self.__class__(op(s,e) for s,e in zip(self, a))
        except TypeError:
            return self.__class__(op(c,a) for c in self)

    def __add__(self, a): return self.__op(a, lambda c,d: c+d)
    def __sub__(self, a): return self.__op(a, lambda c,d: c-d)
    def __div__(self, a): return self.__op(a, lambda c,d: c/d)
    def __mul__(self, a):
        if not isinstance(self[0], Vector):
            return self.__op(a, lambda c, d: c * d)
        res = []
        for i in range(len(self)):
            row = []
            for j in range(len(a[0])):
                value = self[i][0] * a[0][j]
                for k in range(1, len(self)):
                    value += self[i][k] * a[k][j]
                row += [value]
            res += [Vector(row)]
        return Vector(res)

    def __and__(self, a):
        try:
            return reduce(lambda s, (c,d): s+c*d, zip(self, a), 0)
        except TypeError:
            return self.__class__(c and a for c in self)

    def __or__(self, a):
        try:
            return self.__class__(itertools.chain(self, a))
        except TypeError:
            return self.__class__(c or a for c in self)

class Calc(tpg.Parser):
    r"""

    separator spaces: '\s+' ;
    separator comment: '#.*' ;

    token fnumber: '\d+[.]\d*' float ;
    token number: '\d+' int ;
    token op1: '[|&+-]' make_op ;
    token op2: '[*/]' make_op ;
    token finish: '\s*exit\s*';
    token filepath: '[\'"](\w|\s|[./-])+[\'"]' clear_quotes;
    token id: '\w+' ;

    START/e -> Operator $e=None$ | Expr/e | $e=None$ ;
    Operator -> 'script\(' filepath/i '\)' $script(i)$ | finish $exit()$ |Assign ;
    Assign -> id/i '=' Expr/e $Vars[i]=e$ ;
    Expr/t -> Fact/t ( op1/op Fact/f $t=op(t,f)$ )* ;
    Fact/f -> Atom/f ( op2/op Atom/a $f=op(f,a)$ )* ;
    Atom/a ->   Vector/a
              | id/i ( check $i in Vars$ | error $"Undefined variable '{}'".format(i)$ ) $a=Vars[i]$
              | fnumber/a
              | number/a
              | '\(' Expr/a '\)' ;
    Vector/$Vector(a)$ -> '\[' '\]' $a=[]$ | '\[' Atoms/a '\]' ;
    Atoms/v -> Atom/a Atoms/t $v=[a]+t$ | Atom/a $v=[a]$ ;

    """

calc = Calc()
Vars = {}
PS1 = '--> '


def script(filepath):
    with open(filepath, 'r') as fp:
        for line in fp:
            do_calc(line)


def do_calc(line):
    try:
        res = calc(line)
    except tpg.Error as exc:
        print >> sys.stderr, exc
        res = None
    if res is not None:
        print res

while True:
    do_calc(raw_input(PS1))

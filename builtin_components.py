#!/usr/bin/env python3

class And:
    names = ["and", "&"]
    uid="and"
    display = "&"
    inputs = 2
    outputs = 1

    def prog(a,b):
        return a and b

class Or:
    names = ["or", "||"]
    uid="or"
    display = "||"
    inputs = 2
    outputs = 1

    def prog(a, b):
        return a or b


class Xor:
    names = ["xor", "^"]
    uid="xor"
    display = "^"
    inputs = 2
    outputs = 1

    def prog(a, b):
        return (a and not b) or (not a and b)


class Not:
    names = ["not", "~", "!"]
    uid="not"
    display = "¬"
    inputs = 1
    outputs = 1

    def prog(a):
        return not a

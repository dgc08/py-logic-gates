#!/usr/bin/env python3

class And:
    names = ["and", "&"]
    display = "&"
    inputs = 2
    outputs = 1

    def prog(a,b):
        return a and b

class Or:
    names = ["or", "||"]
    display = "||"
    inputs = 2
    outputs = 1

    def prog(a, b):
        return a or b


class Xor:
    names = ["xor", "^"]
    display = "^"
    inputs = 2
    outputs = 1

    def prog(a, b):
        return (a and not b) or (not a and b)


class Not:
    names = ["not", "~", "!"]
    display = "¬"
    inputs = 1
    outputs = 1

    def prog(a):
        return not a

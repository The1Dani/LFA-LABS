from __future__ import annotations
import json
import array
import random


class Grammar:
    def __init__(self, VN:list[str], VT: list[str], P: dict[str,list[str]]):
        self.VN = VN
        self.VT = VT
        self.P = P

    def _changeTo(self, index, s):
        c = s[index]
        start = s[:index]
        end= s[index+1:]
        return start + random.choice(self.P[c]) + end

    def _next(self, s: str) -> tuple[bool, str]:
        for i, c in enumerate(s):
            if c in self.VN:
                return (True, self._changeTo(i ,s))
        else:
            return (False, s)

    def generate(self):
        s="S"
        while True:
            _b, s = self._next(s)
            if not _b:
                return s

    def toFiniteAutomation(self) -> FiniteAutomata:
        Q = self.VN + ["Vf"]
        SIGMA = self.VT
        DELTA: dict[str, dict[str, list[str]]] = {}
        F = ["Vf"]
        Q0 = "S"

        isDFA = True

        for fr, rule in self.P.items():
            if fr not in DELTA:
                DELTA[fr] = {}
            for st in self.P[fr]:
                if st[0] in DELTA[fr]:
                    isDFA = False
                else:
                    DELTA[fr][st[0]] = []
                if len(st) == 2:
                    DELTA[fr][st[0]] += [st[1]]
                elif len(st) == 1:
                    DELTA[fr][st[0]] += ["Vf"]

        return FiniteAutomata(Q, SIGMA, DELTA, Q0, F, isDFA)

class FiniteAutomata:

    STATE_FAIL = "FAIL"

    def __init__(self, q:list[str],
                    sigma:list[str],
                    delta:dict[str,
                    dict[str, list[str]]],
                    q0:str,
                    f:list[str],
                    DFA:bool = True):
                        
        self.Q: list[str] = q
        self.SIGMA: list[str] = sigma
        self.DELTA: dict[str, dict[str, list[str]]] = delta
        self.Q0: str = q0
        self.F: list[str] = f
        self.STATES = [self.Q0]
        self.DFA = DFA

    def _next(self, c):
        newStates = self.STATES.copy()
        for ind, state in enumerate(self.STATES):
            if not (state in self.DELTA and c in self.DELTA[state]):
                del newStates[ind]
        self.STATES = newStates
        newStates = self.STATES.copy()
        for ind, state in enumerate(self.STATES):
            if state in self.DELTA and c in self.DELTA[state]:
                for i, path in enumerate(self.DELTA[state][c]):
                    if len(newStates) > i:
                        newStates[ind] = self.DELTA[state][c][i]
                    else:
                        newStates.append(self.DELTA[state][c][i])
            else:
                del newStates[ind]
        self.STATES = newStates

    def _isFinal(self):
        for state in self.STATES:
            if state in self.F:
                return True
        return False

    def _isFailed(self):
        return len(self.STATES) == 0

    def _reset(self):
        self.STATES = [self.Q0]

    def stringBelongToLanguage(self, s):

        for i, c in enumerate(s):
            self._next(c)
            if self._isFailed():
                break

        if self._isFinal():
            self._reset()
            return True

        self._reset()
        return False

def getGrammarsFromJson(grammar_json) -> list[Grammar]:

    res = []
    for grammar in grammars_json:
        VN = grammar["VN"]
        VT = grammar["VT"]
        P = {}
        for rl in grammar["P"]:
            for n, t in rl.items():
                if n not in P:
                    P[n] = []
                P[n].append(t)
        res.append(Grammar(VN, VT, P,))
    return res

if __name__ == "__main__":

    with open("variants.json") as f:
        grammars_json = json.load(f)

    grammars = getGrammarsFromJson(grammars_json)

    for ind, grammar in enumerate(grammars):
        automata = grammar.toFiniteAutomation()
        print(f"\n--------------NR{ind:02}|DFA={automata.DFA}----------------")
        words = []
        for _ in range(5):
            words.append(grammar.generate())
        for word in words:
            belongs = automata.stringBelongToLanguage(word)
            if not belongs:
                raise ValueError(f"Word '{word}' does not belong to the language.")
            print(f"{word} -> {belongs}")

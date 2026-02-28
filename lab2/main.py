from __future__ import annotations
import json
import random

GENERATE_GRAPHS = True
if GENERATE_GRAPHS:
  from graphviz import Digraph

  def visualize_dfa(dfa_obj, name):
      dot = Digraph(comment='DFA Visualization', name=name, directory="graphs")
      dot.attr(rankdir='LR') # Left to Right layout
  
      # Add states
      for q in dfa_obj.Q:
          if q in dfa_obj.F:
              dot.node(q, shape='doublecircle') # Final states
          else:
              dot.node(q, shape='circle')
  
      # Add invisible start node
      dot.node('start', label='', shape='none')
      dot.edge('start', dfa_obj.Q0)
  
      # Add transitions
      for state, transitions in dfa_obj.DELTA.items():
          for char, next_state in transitions.items():
              if next_state != "FAIL":
                  dot.edge(state, next_state, label=char)
    
      dot.render(format='png', cleanup=True)


class Grammar:
    def __init__(self,
      VN:list[str],
      VT:list[str],
      P: dict[str,list[str]],
      Start: str = "S",
    ):
        self.VN = VN
        self.VT = VT
        self.P = P
        self.Start = Start

    def _changeTo(self, index, s):
        c = s[index:len(s)]
        start = s[:index]
        end= s[index+ len(s):]
        return start + random.choice(self.P[c]) + end
    
    def _tokens(self, s: str) -> list[tuple[int, str]]:
      start = 0
      end = 1
      tokens = []
      while end <= len(s):
        if s[start:end] in self.VN or s[start:end] in self.VT:
          tokens.append((start, s[start:end]))
          start = end
        end += 1
        
      return tokens
     
    def _next(self, s: str) -> tuple[bool, str]:
        for i, c in self._tokens(s):
            if c in self.VN:
                return (True, self._changeTo(i ,s))
        else:
            return (False, s)

    def generate(self):
        s=self.Start
        while True:
            _b, s = self._next(s)
            if not _b:
                return s
    
    def type(self) -> str:
        is_type_3 = True
        is_type_2 = True
        is_type_1 = True
        
        # Track direction for Type 3 (Right-linear vs Left-linear)
        direction = None # Can be 'right' or 'left'

        for lhs, rhs_list in self.P.items():
            # Get tokens for LHS
            lhs_tokens = [t[1] for t in self._tokens(lhs)]
            lhs_non_terminals = [t for t in lhs_tokens if t in self.VN]
            
            # Type 0 Check: LHS must contain at least one non-terminal
            if not lhs_non_terminals:
                raise ValueError("Invalid Grammar: LHS must contain at least one non-terminal.")

            # Type 2 Check: LHS must be a single non-terminal
            if len(lhs_tokens) != 1 or lhs_tokens[0] not in self.VN:
                is_type_2 = False
                is_type_3 = False

            for rhs in rhs_list:
                rhs_tokens = [t[1] for t in self._tokens(rhs)]
                
                # Type 1 Check: |LHS| <= |RHS| (ignoring S -> epsilon exception for simplicity)
                if len(rhs_tokens) < len(lhs_tokens) and rhs != "":
                    is_type_1 = False

                # Type 3 Check: Only if it's still potentially Type 2
                if is_type_2:
                    non_terminals_in_rhs = [t for t in rhs_tokens if t in self.VN]
                    
                    if len(non_terminals_in_rhs) > 1:
                        is_type_3 = False
                    elif len(non_terminals_in_rhs) == 1:
                        # Check if it's Right-Linear (A -> aB) or Left-Linear (A -> Ba)
                        curr_dir = 'right' if rhs_tokens[-1] in self.VN else 'left'
                        
                        # If a terminal and non-terminal are mixed, it must be at the ends
                        if len(rhs_tokens) > 2:
                            is_type_3 = False # Simplification: Type 3 usually A -> a or A -> aB
                        
                        if direction is None:
                            direction = curr_dir
                        elif direction != curr_dir:
                            is_type_3 = False

        if is_type_3: return "Type 3: Regular Grammar"
        if is_type_2: return "Type 2: Context-Free Grammar"
        if is_type_1: return "Type 1: Context-Sensitive Grammar"
        return "Type 0: Unrestricted Grammar"
    
    def toNFA(self) -> NFA:
        Q = self.VN + ["Vf"]
        SIGMA = self.VT
        DELTA: dict[str, dict[str, list[str]]] = {}
        F = ["Vf"]
        Q0 = "S"

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

        return NFA(Q, SIGMA, DELTA, Q0, F)
    def equals(self, other):
      vneqals = self.VN == other.VN
      vteqals = self.VT == other.VT
      pequals = self.P == other.P
      return vneqals and vteqals and pequals

class NFA:

    STATE_FAIL = "FAIL"

    def __init__(self, q:list[str],
                    sigma:list[str],
                    delta:dict[str,dict[str, list[str]]],
                    q0:str,
                    f:list[str]):

        self.Q: list[str] = q
        self.SIGMA: list[str] = sigma
        self.DELTA: dict[str, dict[str, list[str]]] = delta
        self.Q0: str = q0
        self.F: list[str] = f
        self.STATES = [self.Q0]
        

    def _next(self, token):
      next_possible_states = set()
      for state in self.STATES:
          if state in self.DELTA and token in self.DELTA[state]:
              for target in self.DELTA[state][token]:
                  next_possible_states.add(target)
      
      self.STATES = list(next_possible_states)

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
        
    def isDFA(self) -> bool:
        for state, transitions in self.DELTA.items():
            if not all(len(v) == 1 for v in transitions.values()):
                return False
        return True
        
    def toDFA(self) -> DFA:
        # Use a sorted list to ensure the key is always identical for the same set
        start_set = frozenset([self.Q0])
        start_name = str(sorted(list(start_set)))
        
        dfa_delta = {}
        states_to_process = [start_set]
        dfa_states = {start_set}
        final_states = set()
        
        while states_to_process:
            current_set = states_to_process.pop()
            current_name = str(sorted(list(current_set)))
            
            # Check if this set contains any NFA final states
            if any(s in self.F for s in current_set):
                final_states.add(current_name)
                
            dfa_delta[current_name] = {}
            
            for char in self.SIGMA:
                next_set = set()
                for nfa_state in current_set:
                    if nfa_state in self.DELTA and char in self.DELTA[nfa_state]:
                        next_set.update(self.DELTA[nfa_state][char])
                
                if not next_set:
                    continue
                    
                next_frozenset = frozenset(next_set)
                next_name = str(sorted(list(next_frozenset)))
                dfa_delta[current_name][char] = next_name
                
                if next_frozenset not in dfa_states:
                    dfa_states.add(next_frozenset)
                    states_to_process.append(next_frozenset)
    
        all_dfa_state_names = [str(sorted(list(s))) for s in dfa_states]
        return DFA(all_dfa_state_names, self.SIGMA, dfa_delta, start_name, list(final_states))
              
    def toGrammar(self) -> Grammar:
        VT = self.SIGMA
        q = self.Q[:]
        VN = q
        P = {}
        for state, transitions in self.DELTA.items():
          for c, next_states in transitions.items():
            for next_state in next_states:
              next_state = next_state if next_state not in self.F else ""
              transition = f"{c}{next_state}"
              if state not in P:
                P[state] = []
              P[state].append(transition)
        return Grammar(VN, VT, P, Start=self.Q0)
    
      
    
class DFA:
  STATE_FAIL = "FAIL"

  def __init__(self, q:list[str],
              sigma:list[str],
              delta:dict[str, dict[str, str]],
              q0:str,
              f:list[str]):

    self.Q: list[str] = q
    self.SIGMA: list[str] = sigma
    self.DELTA: dict[str, dict[str, str]] = delta
    self.Q0: str = q0
    self.F: list[str] = f
    self.STATE = self.Q0
    
  def _next(self, c: str) -> None:
    state = self.STATE
    if state in self.DELTA and c in self.DELTA[state]:
      self.STATE = self.DELTA[state][c]
    else:
      self.STATE = self.STATE_FAIL

  def _isFinal(self):
    return self.STATE in self.F
    
  def _isFailed(self):
      return self.STATE == self.STATE_FAIL

  def _reset(self):
      self.STATE = self.Q0

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

def getAutomationsFromJson(automation_json) -> list[NFA]:
  res = []
  for aut in automation_json:
    delta :dict[str,dict[str, list[str]]] = {}
    for d in aut["Delta"]:
      for key, val in d.items():
        if key not in delta:
          delta[key] = {}
        if val[0] not in delta[key]:
          delta[key][val[0]] = []
        delta[key][val[0]] += [val[1]]
        
    res.append(
      NFA(
        aut["Q"],
        aut["Sigma"],
        delta,
        "q0",
        aut["F"]
      )
    )
  return res

if __name__ == "__main__":
  with open("/home/dani/faf/lfa/lab2/variants.json") as f:
    automation_json = json.load(f)
    
  # --- Type 3: Regular Grammar ---
  # Rules: A -> a, A -> aB (Right-Linear)
  g3 = Grammar(
      VN=["S", "A"],
      VT=["a", "b"],
      P={
          "S": ["a", "aA"],
          "A": ["bA", "b"]
      },
      Start="S"
  )

  # --- Type 2: Context-Free Grammar ---
  # Rules: LHS is always a single non-terminal, RHS can be anything
  g2 = Grammar(
      VN=["S"],
      VT=["a", "b"],
      P={
          "S": ["aSb", "ab"]  # Classic non-regular language {a^n b^n}
      },
      Start="S"
  )

  # --- Type 1: Context-Sensitive Grammar ---
  # Rules: |LHS| <= |RHS|
  g1 = Grammar(
      VN=["S", "A", "B", "C"],
      VT=["a", "b", "c"],
      P={
          "S": ["abc", "aAbc"],
          "Ab": ["bA"],      # Length 2 -> Length 2
          "Ac": ["Bbcc"],    # Length 2 -> Length 4
          "bB": ["Bb"],      # Length 2 -> Length 2
          "aB": ["aa", "aaA"] 
      },
      Start="S"
  )

  # --- Type 0: Unrestricted Grammar ---
  # Rules: No restrictions (e.g., LHS can be longer than RHS)
  g0 = Grammar(
      VN=["S", "A"],
      VT=["a"],
      P={
          "S": ["aA"],
          "aA": ["a"], # Length 2 -> Length 1 (Shrinking grammar)
      },
      Start="S"
  )
  gs = [g0, g1, g2, g3]
  
  for g in gs:
      print(g.type())
  
  automations = getAutomationsFromJson(automation_json)
  
  print()
  
  for i, aut in enumerate(automations):
    grammar = aut.toGrammar()
    print(grammar.type())
    print(f"{aut.isDFA()=}")
    for _ in range(1000):
      word = grammar.generate()
      dfa = aut.toDFA()
      word_belongs = dfa.stringBelongToLanguage(word) == aut.stringBelongToLanguage(word)
      
      if not word_belongs:
        raise ValueError(f"Word {word} does not belong to the language")
    print(f"{word_belongs=}")
    if GENERATE_GRAPHS:
      visualize_dfa(automations[i].toDFA(), f"{i:02}")
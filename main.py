import re
import sys
from collections import defaultdict
from anytree import Node, RenderTree
from anytree.exporter import DotExporter

class LL1Parser:
    def __init__(self, grammar_file):
        self.grammar = defaultdict(dict)
        self.first = defaultdict(set)
        self.follow = defaultdict(set)
        self.parse_table = defaultdict(dict)
        self.non_terminals = set()
        self.terminals = set()
        self.start_symbol = None
        self.load_grammar(grammar_file)
        self.compute_first_sets()
        self.compute_follow_sets()
        self.construct_parse_table()

    def load_grammar(self, grammar_file):
        with open(grammar_file, 'r') as file:
            for line in file:
                lhs, rhs = line.strip().split('->')
                lhs = lhs.strip()
                if not self.start_symbol:
                    self.start_symbol = lhs
                self.non_terminals.add(lhs)
                for prod in rhs.split('|'):
                    production = tuple(prod.strip().split())
                    self.grammar[lhs][production[0]] = list(production)
                    for symbol in production:
                        if not symbol.isupper() and symbol != 'ε':
                            self.terminals.add(symbol)

    def compute_first_sets(self):
        for terminal in self.terminals:
            self.first[terminal].add(terminal)
        for non_terminal in self.non_terminals:
            self.first[non_terminal] = self.compute_first(non_terminal)

    def compute_first(self, symbol):
        if symbol in self.terminals:
            return {symbol}
        first_set = set()
        for production in self.grammar[symbol].values():
            for sym in production:
                sym_first = self.compute_first(sym)
                first_set.update(sym_first - {'ε'})
                if 'ε' not in sym_first:
                    break
            else:
                first_set.add('ε')
        return first_set

    def compute_follow_sets(self):
        self.follow[self.start_symbol].add('$')
        for non_terminal in self.non_terminals:
            self.follow[non_terminal] = self.compute_follow(non_terminal)

    def compute_follow(self, symbol):
        follow_set = set()
        for lhs, productions in self.grammar.items():
            for production in productions.values():
                for i, sym in enumerate(production):
                    if sym == symbol:
                        if i + 1 < len(production):
                            follow_set.update(self.first[production[i + 1]] - {'ε'})
                        if i + 1 == len(production) or 'ε' in self.first[production[i + 1]]:
                            follow_set.update(self.follow[lhs])
        return follow_set

    def construct_parse_table(self):
        for non_terminal, productions in self.grammar.items():
            for lookahead, production in productions.items():
                first_set = set()
                for symbol in production:
                    first_set.update(self.first[symbol] - {'ε'})
                    if 'ε' not in self.first[symbol]:
                        break
                else:
                    first_set.add('ε')
                for terminal in first_set:
                    self.parse_table[non_terminal][terminal] = production
                if 'ε' in first_set:
                    for follow_symbol in self.follow[non_terminal]:
                        self.parse_table[non_terminal][follow_symbol] = production

    def parse(self, input_string):
        input_tokens = input_string.split() + ['$']
        stack = ['$', self.start_symbol]
        index = 0

        root = Node(self.start_symbol)
        current_node = root

        while stack:
            top = stack.pop()
            current_token = input_tokens[index]

            if top == current_token:
                Node(current_token, parent=current_node)
                index += 1
                if current_token == '$' and not stack:
                    print("Parse successful!")
                    self.display_parse_tree(root)
                    return
            elif top in self.grammar:
                rule = self.parse_table.get(top, {}).get(current_token)
                if rule is not None:
                    new_node = Node(f"{top} -> {' '.join(rule)}", parent=current_node)
                    stack.extend(reversed(rule))
                    current_node = new_node
                else:
                    print(f"Error: No matching rule found for ({top}, {current_token}).")
                    return
            else:
                print(f"Error: Unexpected symbol '{top}' in stack.")
                return

        if not stack and index == len(input_tokens) - 1:
            print("Parse successful!")
            self.display_parse_tree(root)
        else:
            print("Error: Parsing incomplete.")

    def display_parse_tree(self, root):
        for pre, _, node in RenderTree(root):
            print(f"{pre}{node.name}")


    

if __name__ == "__main__":
    grammar_file = input("Please, input the grammar file: ")
    input_string = input("Please, input the string: ")
    parser = LL1Parser(grammar_file)
    parser.parse(input_string)

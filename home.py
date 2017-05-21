from anytree.dotexport import RenderTreeGraph
from anytree import Node, RenderTree
import locale
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

class Home:
    def __init__(self):
        self.data = []
    def get_facts(self, tree):
        facts = []
        for pre, fill, node in RenderTree(tree):
            if node.name != "":
                for sibling in node.siblings:
                    if sibling.name != "":
                        facts.append(tuple(sorted((node.name, sibling.name), cmp=locale.strcoll, reverse=True)))
                facts = list(set(facts))
                self.facts = {cat: fact for cat, fact in facts}
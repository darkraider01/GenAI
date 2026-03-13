from semanticscholar import SemanticScholar
sch = SemanticScholar()
p = sch.get_paper('ARXIV:1706.03762')
print("Keys in p:", dir(p))
print("Has references:", hasattr(p, 'references'))
if hasattr(p, 'references'):
    print("Num references:", len(p.references) if p.references else 0)

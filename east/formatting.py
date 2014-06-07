# -*- coding: utf-8 -*

def table2xml(keyphrases_table):
    res = u"<table>\n"
    for keyphrase in sorted(keyphrases_table.keys()):
        res += u'  <keyphrase value="%s">\n' % keyphrase
        for text in sorted(keyphrases_table[keyphrase].keys()):
            res += u'    <text name="%s">' % text
            res += u'%.3f' % keyphrases_table[keyphrase][text]
            res += u'</text>\n'
        res += u'  </keyphrase>\n'
    res += u"</table>\n"
    return res


def table2csv(keyphrases_table):

    def quote(s):
        return '"' + s.replace('"', "'") + '"'

    keyphrases = sorted(keyphrases_table.keys())
    texts = sorted(keyphrases_table[keyphrases[0]].keys())
    res = u"," + ",".join(map(quote, keyphrases)) + "\n"  # Heading
    for text in texts:
        scores = map(lambda score: u"%.3f" % score,
                     [keyphrases_table[keyphrase][text] for keyphrase in keyphrases])
        res += (quote(text) + "," + ",".join(scores) + "\n")
    return res


def graph2edges(graph):
    res = u""
    for node in graph:
        if graph[node]:
            res += "%s -> %s\n" % (node, ", ".join(graph[node]))
    return res


def graph2gml(graph):
    res = u"graph\n[\n"
    i = 0
    node_ids = {}
    for node in graph:
        res += '  node\n  [\n    id %i\n    label "%s"\n  ]\n' % (i, node)
        node_ids[node] = i
        i += 1
    for node in graph:
        for adj_node in graph[node]:
            res += '  edge\n  [\n    source %i\n    target %i\n  ]\n' % (node_ids[node],
                                                                         node_ids[adj_node])
    res += "]\n"
    return res

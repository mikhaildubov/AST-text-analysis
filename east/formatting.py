# -*- coding: utf-8 -*


def format_table(table, format):
    if format == "xml":
        return table2xml(keyphrases_table)
    elif format == "csv":
        return table2csv(keyphrases_table)
    else:
        raise Exception("Unknown table format: '%s'. "
                        "Please use one of: 'xml', 'csv'." % format)


def table2xml(keyphrases_table):
    res = "<table>\n"
    for keyphrase in sorted(keyphrases_table.keys()):
        res += '  <keyphrase value="%s">\n' % keyphrase
        for text in sorted(keyphrases_table[keyphrase].keys()):
            res += '    <text name="%s">' % text
            res += '%.3f' % keyphrases_table[keyphrase][text]
            res += '</text>\n'
        res += '  </keyphrase>\n'
    res += "</table>\n"
    return res


def table2csv(keyphrases_table):

    def quote(s):
        return '"' + s.replace('"', "'") + '"'

    keyphrases = sorted(keyphrases_table.keys())
    texts = sorted(keyphrases_table[keyphrases[0]].keys())
    res = "," + ",".join(map(quote, keyphrases)) + "\n"  # Heading
    for text in texts:
        scores = map(lambda score: u"%.3f" % score,
                     [keyphrases_table[keyphrase][text] for keyphrase in keyphrases])
        res += (quote(text) + "," + ",".join(scores) + "\n")
    return res


def format_graph(graph, format):
    if format == "gml":
        return graph2gml(graph)
    elif format == "edges":
        return graph2edges(graph)
    else:
        raise Exception("Unknown graph format: '%s'. "
                        "Please use one of: 'gml', 'edges'." % format)


def graph2edges(graph):
    # TODO(mikhaildubov): Exception on the US constitution example!
    res = ""
    node_edges = {}
    for edge in graph["edges"]:
        source_label = graph["nodes"][edge["source"]]["label"]
        target_label = graph["nodes"][edge["target"]]["label"]
        if source_label not in node_edges:
            node_edges[source_label] = []
        node_edges[source_label].append(target_label)
    for node in node_edges:
        res += "%s -> %s\n" % (node, ", ".join(node_edges[node]))
    return res


def graph2gml(graph):
    res = "graph\n[\n"
    res += "  directed 1\n"
    res += "  referral_confidence %.2f\n" % graph["referral_confidence"]
    res += "  relevance_threshold %.2f\n" % graph["relevance_threshold"]
    res += "  support_threshold %i\n" % graph["support_threshold"]
    for node in graph["nodes"]:
        res += ('  node\n  [\n    id %i\n    label "%s"\n  ]\n' %
                (node["id"], node["label"]))
    for edge in graph["edges"]:
        res += ('  edge\n  [\n    source %i\n    target %i\n    confidence %.2f\n  ]\n' %
                (edge["source"], edge["target"], edge["confidence"]))
    res += "]\n"
    return res

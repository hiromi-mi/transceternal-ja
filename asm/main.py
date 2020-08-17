# Transceternal Assembeler
# SPDX-License-Identifier: CC0-1.0

from string import digits, ascii_uppercase, ascii_lowercase
import sys

text = """
label init
set 0111 0011
alloc 0110 010 1010
if 0100 0011 init
goto exit
"""

def new_node(graphs, left, right):
    _id = retain_node(graphs)
    graphs[_id][0] = left
    graphs[_id][1] = right
    return _id

def new_state_set(graphs, left_str, right_str, B0, B1):
    _id = retain_node(graphs)
    graphs[_id][0] = new_node(graphs, B0, new_node(graphs, 
        construct(graphs, left_str, B0, B1), construct(graphs, right_str, B0, B1)))
    return _id

def new_node_self(graphs):
    _id = retain_node(graphs)
    graphs[_id][0] = _id
    graphs[_id][1] = _id
    return _id

def new_state_if_nodes(graphs, left, right, then_node):
    _id = retain_node(graphs)
    top = retain_node(graphs)
    graphs[_id][0] = top
    graphs[top][0] = new_node_self(graphs)
    node = retain_node(graphs)
    graphs[top][1] = node
    graphs[node][0] = new_node(graphs, left, right)
    graphs[node][1] = then_node
    return _id

def new_state_if(graphs, left_str, right_str, then_node, B0, B1):
    return new_state_if_nodes(graphs, construct(graphs, left_str, B0, B1), construct(graphs, right_str, B0, B1), then_node)

def new_state_alloc_nodes(graphs, alloc_node, left, right, B0, B1):
    _id = retain_node(graphs)
    top = new_node(graphs, B1, "-1")
    graphs[_id][0] = top
    node = retain_node(graphs)
    graphs[top][1] = node
    graphs[node][0] = alloc_node
    graphs[node][1] = new_node(graphs, left, right)
    return _id

def new_state_alloc(graphs, alloc_str, left_str, right_str, B0, B1):
    return new_state_alloc_nodes(graphs, construct(graphs, alloc_str, B0, B1), construct(graphs, left_str, B0, B1), construct(graphs, right_str, B0, B1), B0, B1)

def retain_node(graphs):
    _id = tob62(len(graphs))
    graphs[_id] = ["-1", "-1"]
    return _id

def construct(graphs, node_str, B0, B1):
    node = ''
    top = ''
    for a in node_str:
        newnode = retain_node(graphs)
        if node:
            graphs[node][1] = newnode
        else:
            top = newnode
        node = newnode
        graphs[node][0] = B0 if a == '0' else B1

    graphs[node][1] = node
    return top

def main(text):
    graphs = {}
    root = retain_node(graphs)
    admin = retain_node(graphs)
    B0 = retain_node(graphs)
    graphs[B0][0] = B0
    graphs[B0][1] = B0

    B1 = retain_node(graphs)
    graphs[B1][0] = B0
    graphs[B1][1] = B0

    graphs[root][0] = admin
    graphs[admin][0] = B0
    graphs[admin][1] = B1

    # root[1] だけ埋まってない

    labels = {"exit" : B0}
    
    texts = text.split("\n")
    curplace = "01"
    prevgraph = root
    for aline in texts:
        if aline.strip() == "":
            continue
        aconst = aline.strip().split(" ")
        if len(aconst) == 0 or aconst[0] == "#":
            continue
        if aconst[0] == "label":
            labels[aconst[1]] = prevgraph
        if aconst[0] == "set":
            graphs[prevgraph][1] = new_state_set(graphs, aconst[1], aconst[2], B0, B1)
            prevgraph = graphs[prevgraph][1]
        if aconst[0] == "alloc":
            graphs[prevgraph][1] = new_state_alloc(graphs, aconst[1], aconst[2], aconst[3], B0, B1)
            prevgraph = graphs[prevgraph][1]
        if aconst[0] == "if":
            graphs[prevgraph][1] = new_state_if(graphs, aconst[1], aconst[2], "label:"+aconst[3], B0, B1)
            prevgraph = graphs[prevgraph][1]
        if aconst[0] == "goto":
            graphs[prevgraph][1] = "label:"+aconst[1]
            prevgraph = retain_node(graphs)
            # とりあえず, 使うようになれば何かしら使われるはず...
            graphs[prevgraph][0] = B0
            graphs[prevgraph][1] = B0
        if aconst[0] == ".const":
            node = root
            for item in aconst[1][:-2]:
                node = graphs[node][item]
            graphs[node][aconst[-1]] = construct(graphs, aconst[2], B0, B1)

    
    output(graphs, labels)

def tob62(val):
    _d36 = digits + ascii_uppercase + ascii_lowercase
    per = len(_d36)
    if (val < per):
        return _d36[val]
    else:
        return tob62(val // per) + _d36[val%per]

def solve_label(labels, item):
    if item[0:6] != "label:":
        return item
    else:
        return labels[item[6:]]

def output(graphs, labels):
    stack = [list(graphs.keys())[0]]
    stack2 = [[]]

    watched = set([])
    print(stack[0], end=' ')
    while len(stack) > 0:
        last_id = stack[-1]
        last_item = stack2[-1]
        if last_id in watched:
            stack.pop()
            stack2.pop()
            continue

        # isNew なら 0番目の内容を出力してそっちに飛んでいく
        # not isNew なら1番目の内容を出力してそっちに飛んでいく
        if len(last_item) == 0:
            node = solve_label(labels, graphs[last_id][0])
        else:
            node = solve_label(labels, graphs[last_id][1])

        last_item.append(node)
        print(node, end=' ')

        while len(stack2[-1]) == 2:
            watched.add(stack.pop())
            stack2.pop()
            if len(stack) == 0:
                break

        if node not in stack:
            stack.append(node)
            stack2.append([])

    print()
    if set(graphs.keys()) != watched:
        print("Warning: there are unused item", file=sys.stderr)

main(text)

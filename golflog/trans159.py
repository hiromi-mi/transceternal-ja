# Transceternal Esolang Codegolf Contest #6 生成Script by @_hiromi_mi
# SPDX-License-Identifier: CC0-1.0

from string import ascii_letters, digits, punctuation
import sys

from typing import Dict

def tob36(val):
    _d36 = digits + ascii_letters + punctuation + "".join([chr(x) for x in range(0x3a3, 0x052f)]) + "".join([chr(x) for x in range(0x61e, 0x70d)])
    _ld = len(_d36)
    if (val < _ld):
        return _d36[val]
    else:
        return tob36(val // _ld) + _d36[val%_ld]

def retain_node(graphs):
    _id = tob36(len(graphs))
    graphs[_id] = ["-1", "-1"]
    return _id

def new_node(graphs, left, right):
    _id = retain_node(graphs)
    graphs[_id][0] = left
    graphs[_id][1] = right
    return _id

def construct(graphs, node_str, B0, B1, const=True):
    if "0" not in node_str:
        return construct_ones(graphs, len(node_str), B0, B1)
    
    # just other than last:
    if "1" not in node_str[:-1] and node_str[-1] == "1":
        return construct_oneszero(graphs, len(node_str), B0, B1)

    node = ''
    top = ''
    if const:
        if node_str in construct.table:
            return construct.table[node_str]

    lastnode = ''
    for index, a in enumerate(node_str):
        if len(node_str[index:]) > 0 and "0" not in node_str[index:]:
            lastnode = construct_ones(graphs, len(node_str[index:]), B0, B1)
            break
        newnode = retain_node(graphs)
        if node:
            graphs[node][1] = newnode
        else:
            top = newnode
        node = newnode
        lastnode = newnode
        graphs[node][0] = B0 if a == '0' else B1
        # 残りが1だけのとき

    graphs[node][1] = lastnode
    if const:
        construct.table[node_str] = top
    return top

construct.table = {}

def construct_ones(graphs, num, B0, B1):
    if construct_ones.num > num:
        result = traverse(graphs, construct_ones.longest, "1" * (construct_ones.num - num), B0, B1)
        #print(graphs[result], result, construct_ones.num, num)
        return result

    if construct_ones.num == num:
        result = construct_ones.longest
        return result

    # construct_ones.num < num
    node = ''
    top = ''

    for a in "1" * (num - construct_ones.num):
        newnode = retain_node(graphs)
        if node:
            graphs[node][1] = newnode
        else:
            top = newnode
        node = newnode
        graphs[node][0] = B1 #B0 if a == '0' else B1

    # ここが 0 のとき"" 空白文字がはいるからおかしくなった
    #graphs[node][1] = node if construct_ones.num == 0 else construct_ones.longest
    graphs[node][1] = B0 if construct_ones.num == 0 else construct_ones.longest

    construct_ones.num = num
    construct_ones.longest = top
    return top

construct_ones.longest = ""
construct_ones.num = 0

def construct_oneszero(graphs, num, B0, B1):
    # just create zero
    if construct_oneszero.longest == "":
        # share with construct_ones
        construct_oneszero.longest = construct_ones(graphs, 1, B0, B1)
        construct_oneszero.num = 1
        #construct_oneszero.longest = retain_node(graphs)
        #graphs[construct_oneszero.longest][0] = B1
        #graphs[construct_oneszero.longest][1] = construct_oneszero.longest
        #construct_oneszero.num = 1

    if construct_oneszero.num > num:
        result = traverse(graphs, construct_oneszero.longest, "0" * (construct_oneszero.num - num), B0, B1)
        #print(graphs[result], result, construct_oneszero.num, num)
        return result

    if construct_oneszero.num == num:
        result = construct_oneszero.longest
        return result

    # construct_oneszero.num < num
    node = ''
    top = ''

    for a in "0" * (num - construct_oneszero.num):
        newnode = retain_node(graphs)
        if node:
            graphs[node][1] = newnode
        else:
            top = newnode
        node = newnode
        graphs[node][0] = B0 #B0 if a == '0' else B1

    # ここが 0 のとき"" 空白文字がはいるからおかしくなった
    graphs[node][1] = construct_oneszero.longest

    construct_oneszero.num = num
    construct_oneszero.longest = top
    return top

construct_oneszero.num = 0
construct_oneszero.longest = ""

def new_state_set(graphs, left_str, right_str, B0, B1):
    _id = retain_node(graphs)
    graphs[_id][0] = new_node(graphs, B0, new_node(graphs, 
        construct(graphs, left_str, B0, B1), construct(graphs, right_str, B0, B1)))
    return _id

# instead of root
#def new_node_self(graphs):
#    _id = retain_node(graphs)
#    graphs[_id][0] = _id
#    graphs[_id][1] = _id
#    return _id

def new_state_if_nodes_base(graphs, base_node, then_node):
    _id = retain_node(graphs)
    top = retain_node(graphs)
    graphs[_id][0] = top
    graphs[top][0] = "0" # TODO: root
    node = retain_node(graphs)
    graphs[top][1] = node
    graphs[node][0] = base_node
    graphs[node][1] = then_node
    return _id

def new_state_if_nodes(graphs, left, right, then_node):
    _id = retain_node(graphs)
    top = retain_node(graphs)
    graphs[_id][0] = top
    #graphs[top][0] = new_node_self(graphs)
    graphs[top][0] = "0" # TODO: root
    node = retain_node(graphs)
    graphs[top][1] = node
    graphs[node][0] = new_node(graphs, left, right)
    graphs[node][1] = then_node
    return _id

def new_state_if(graphs, left_str, right_str, then_node, B0, B1):
    return new_state_if_nodes(graphs, construct(graphs, left_str, B0, B1), construct(graphs, right_str, B0, B1), then_node)

def next_state(graphs, prev_state, n):
    graphs[prev_state][1] = n

def traverse(graphs: str, from_node: str, traverse_str: str, B0: str, B1: str) -> str:
    node = from_node
    for a in traverse_str:
        if a == 1 and graphs[node][0] == B0:
            print("Error", file=sys.stderr)
        if a == 0 and graphs[node][0] != B0:
            print("Error", file=sys.stderr)
        node = graphs[node][1]
    return node


def generate_if(graphs, then_state, else_state, B0, B1):
    #vals = construct(graphs, '1' * 16 + '1' * 8 + '0', B0, B1)
    #vals = construct(graphs, '1' * 16 + '0', B0, B1)
    vals = construct(graphs, '1' * (16-4) + '0', B0, B1)
    # 状態にかかわる場所

    # TODO ここは construct/traverse いちどで済む
    #for i in [1,2,3,4,5,6,7]:
    #for i in [2,3,4,5,6,7]:
    #for i in [4,5,6,7]:
    for i in [4-4,5-4,6-4,7-4]:
        # if の直前のbase node を共有させる
        base = traverse(graphs, vals, '1'*(i+8-1), B0, B1)
        graphs[base][0] = traverse(graphs, vals, '1'*(i), B0, B1)
        #then_state = new_state_if_nodes(graphs, 
        #        traverse(graphs, vals, '1'*(i), B0, B1),
        #        traverse(graphs, vals, '1'*(i+8), B0, B1),
        #        then_state)
        then_state = new_state_if_nodes_base(graphs, base, then_state)
        graphs[then_state][1] = else_state
    cur_state = then_state

    graphs[cur_state][1] = else_state
    return cur_state

def main():
    graphs = {} # type: Dict[str, list]
    root = retain_node(graphs)
    admin = retain_node(graphs)
    B0 = retain_node(graphs)
    graphs[B0][0] = B0
    #graphs[B0][1] = B0
    B1 = retain_node(graphs)
    # 001 - 0 - 1 が本体
    # 001 - 0 - 0 が not 本体
    #vartop_graph = retain_node(graphs)
    #graphs[B1][0] = vartop_graph

    #count_graph = construct(graphs, "1" *(34-1) +"0", B0, B1, False)
    #count_graph = construct(graphs, "1" *(34-1) +"0", B0, B1)
    #count_graph = construct(graphs, "1" *(33-1), B0, B1)
    #graphs[B0][1] = count_graph
    #count_graph = B0
    #graphs[vartop_graph][0] = count_graph

    #rslttop_graph = retain_node(graphs)
    #graphs[B0][0] = rslttop_graph
    graphs[B0][0] = B1
    #graphs[B0][0] = admin
    #graphs[rslttop_graph][0] = B1
    #graphs[rslttop_graph][1] = B0
    #construct(graphs, "11", B0, B1)
    # ここは変数置場
    graphs[B1][0] = B1 #TODO
    #graphs[B1][1] = B0
    graphs[B1][1] = B1
    #graphs[B1][1] = rslttop_graph
    graphs[root][0] = admin
    graphs[admin][0] = B0
    graphs[admin][1] = B1

    # 001 を仮出力置場に
    #part2_state = new_state_set(graphs, '0011', '1'*(8*1+1), B0, B1)
    #part5_state = new_state_set(graphs, '0011', '1'*(8*4+1), B0, B1)

    # 文字を複製

    #FIXME
    # basenode を中心に見ていく
    part2_state = retain_node(graphs)
    addr0011 = construct(graphs, '0011', B0, B1)
    #  11 の [0] を addr0011 にして if を共有
    # もっといける; 0011 のところの右辺が 1 なので 0011 の 0 を set の B0 扱いにする
    addr011 = graphs[addr0011][1]
    base = graphs[addr011][1]
    graphs[base][0] = addr0011
    #graphs[part2_state][0] = new_node(graphs, B0, base)
    graphs[part2_state][0] = addr011
    #part2_state = new_state_set(graphs, '0011', '1'*(1), B0, B1)

    #FIXME

    part5_state = retain_node(graphs)
    #base = construct_ones(graphs, 1+(8*3+1), B0, B1)
    base = construct_ones(graphs, 1+(11), B0, B1)
    graphs[base][0] = addr0011
    graphs[part5_state][0] = new_node(graphs, B0, base)
    #part5_state = new_state_set(graphs, '0011', '1'*(8*3+1), B0, B1)

    # 最初の最初、2文字目から見にいくように9bit分複製
    # entrypoint
    #FIXME

    entry_state = retain_node(graphs)
    base = construct_ones(graphs, 1+(8+1), B0, B1)
    addr1 = construct(graphs, '1', B0, B1)
    graphs[base][0] = addr1
    graphs[entry_state][0] = new_node(graphs, B0, base)
    graphs[root][1] = entry_state

    # 複製した文字の「次」の文字をポインタが指すように変更
    # そのとき 00111...1 ではなく 複製前の文字列で見たほうが 0010..0 というノードを作らずに済む
    #FIXME
    addr001 = construct(graphs, '001', B0, B1)

    copy2_state = retain_node(graphs)
    base = construct_ones(graphs, (8+1), B0, B1)
    graphs[base][0] = addr001
    graphs[copy2_state][0] = new_node(graphs, B0, base)
    #copy2_state = new_state_set(graphs, '001', '1'*8, B0, B1)
    next_state(graphs, part2_state, copy2_state)

    # 29 個進めたので
    #FIXME
    copy5_state = retain_node(graphs)
    base = construct_ones(graphs, (4+1), B0, B1)
    graphs[base][0] = addr001
    graphs[copy5_state][0] = new_node(graphs, B0, base)
    #copy5_state = new_state_set(graphs, '001', '1'*(4), B0, B1)

    #cur_state = new_state_set(graphs, '1', '1'*65, B0, B1)
    #graphs[part2_state][1] = cur_state
    #graphs[part5_state][1] = cur_state

    # '1' を64バイト分ずらす
    # '1' * 64 の生成を防ぐために2つ文分離
    # -> 最初に8bits ずらしているのなら 64 ではなく 56 でよくないか？
    #cur_state = new_state_set(graphs, '1', '1'*33, B0, B1)
    #cur_state = new_state_set(graphs, '1', '1'*29, B0, B1)
    cur_state = new_state_set(graphs, '1', '1'*15, B0, B1)
    # 29 さえあれば 1 をたどれば 31 を表せる! 1 でも0 でも関係ない ! cnt_graph 不要
    #graphs[B0][1] = graphs[cur_state][0]
    graphs[B0][1] = B0

    copy_5_cur_state = new_node(graphs, graphs[cur_state][0], copy5_state)
    copy_5_cur_state_2 = new_node(graphs, graphs[cur_state][0], copy5_state)
    next_state(graphs, copy_5_cur_state, part5_state)
    next_state(graphs, part5_state, copy_5_cur_state_2)
    next_state(graphs, copy_5_cur_state_2, copy5_state)
    #cur_state3 = new_state_set(graphs, '1', '1'*29, B0, B1)
# cur_state と cur_state3 の内容は同じ -> なので引数部分のノード共通化できる
    cur_state2 = new_node(graphs, graphs[cur_state][0], '')
    cur_state3 = new_node(graphs, graphs[cur_state][0], '')
    cur_state4 = new_node(graphs, graphs[cur_state][0], '')

    next_state(graphs, copy2_state, cur_state)
    next_state(graphs, cur_state, cur_state2)
    next_state(graphs, cur_state2, cur_state3)
    next_state(graphs, copy5_state, cur_state3)
    next_state(graphs, cur_state3, cur_state4)

    genif_state = generate_if(graphs, part2_state, copy_5_cur_state, B0, B1)
    next_state(graphs, graphs[root][1], genif_state)


    #copy_state = new_state_set(graphs, '0011', '0011' + '1'*8, B0, B1)
    #next_state(graphs, cur_state, copy_state)
    # 空白文字で埋める. そうしないと最終行に既存部分のゴミが混入
    #copy_state2 = new_state_set(graphs, '00111', '000', B0, B1)
    #copy_state2 = new_state_set(graphs, '0011', '000', B0, B1)
    copy_state2 = new_state_set(graphs, '0011', '000', B0, B1)
    next_state(graphs, cur_state4, copy_state2)

    #ending_state = new_state_set(graphs, '1', '001011', B0, B1)
    #ending_state = new_state_set(graphs, '1', '00101', B0, B1)
    # 仮置場のものを出力に設定
    ending_state = new_state_set(graphs, '1', '00001', B0, B1)
    next_state(graphs, ending_state, B0)

    # End of Text かどうか？
    #isendable_state = new_state_if(graphs, '00100', '000', ending_state, B0, B1)
    # そのノードのみ比較するには0 つける必要あり
    #isendable_state = new_state_if(graphs, '000', '11', ending_state, B0, B1)
    # 11 は既に使っているので、B0[1] -> B0 なことを使って、if の右辺を11 にする
    # そうすると空いている 111[0] に 000 を入れられる
    base = construct_ones(graphs, 3, B0, B1)
    graphs[base][0] = construct(graphs, '000', B0, B1)
    isendable_state = new_state_if_nodes_base(graphs, base, ending_state)
    #isendable_state = new_state_if_nodes(graphs, B0, B0, ending_state)
    next_state(graphs, copy_state2, isendable_state)

    # countup
    # 使い回し前提
    # TODO 手抜き. construct が一般に処理できるべき
    #addr00011 = new_node(graphs, B0, construct(graphs, '0011', B0, B1))
    #countup_state = new_state_set(graphs, '001001', '0010011', B0, B1)
    #countup_state = new_state_set(graphs, '0001', '00011', B0, B1)
    #countup_state = retain_node(graphs)
    #graphs[countup_state][0] = new_node(graphs, B0, new_node(graphs, 
    #    construct(graphs, '0001', B0, B1), addr00011))
    #next_state(graphs, isendable_state, graphs[root][1])
    #next_state(graphs, isendable_state, countup_state)
    #next_state(graphs, countup_state, graphs[root][1])
    next_state(graphs, isendable_state, graphs[root][1])

    output(graphs)

def output(graphs):
    stack = [list(graphs.keys())[0]]
    stack2 = [[]]

    watched = set([])
    #print(stack[0], end=' ')
    print(stack[0], end='')
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
            node = graphs[last_id][0]
        else:
            node = graphs[last_id][1]

        last_item.append(node)
        #print(node, end=' ')
        print(node, end='')
        #print(stack)
        #print(stack2)

        while len(stack2[-1]) == 2:
            watched.add(stack.pop())
            stack2.pop()
            if len(stack) == 0:
                break

        if node not in stack:
            stack.append(node)
            stack2.append([])

    #print()
    if set(graphs.keys()) != watched:
        print("Errors: not watched yet", file=sys.stderr)

main()

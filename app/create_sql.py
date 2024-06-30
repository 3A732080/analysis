from helper.base_define import data_get, dd, dump, similarity
from service.er_graph_service import create_lf_graph_by_only_text
from service.er_sql_service import get_logical_form, transfer_sql, combine_sql
from graph.base_define import Shape, NodeAttr, Node, Graph
from tqdm import tqdm
from collections import OrderedDict

def create_sql(data, text, pbar, action) -> str:
    graph_lists, type = create_lf_graph_by_only_text(data, text, pbar)

    if action == '詞性分析':
        text = text.replace('?', "")
        text = text.replace('.', "")
        split_text = text.split(' ')

        res = OrderedDict()

        for split_text_temp in split_text:
            if split_text_temp == '?':
                continue

            if split_text_temp == '.':
                continue

            split_text_temp = split_text_temp.replace('?', "")
            split_text_temp = split_text_temp.replace('.', "")

            if split_text_temp == '':
                    continue

            res[split_text_temp] = {
                'modifier' : [],
                'subject' : [],
                'object' : [],
            }

        for graph in graph_lists:
            for node_temp in graph.nodes:
                score = 0
                get_text = None

                if node_temp.shape == Shape.predicate.value:
                    continue

                for split_text_temp in split_text:
                    score_temp = similarity(split_text_temp, node_temp.name)

                    if score_temp > score:
                        score = score_temp
                        get_text = split_text_temp

                for connection_temp in node_temp.connections:
                    if connection_temp.attr == 'modifier':
                        res[connection_temp.node.name.split('=')[1].strip().replace("'", '')][connection_temp.attr].append(get_text)
                    else:
                        score = 0
                        get_node_text = None

                        for split_text_temp in split_text:
                            score_temp = similarity(split_text_temp, connection_temp.node.name)

                            if score_temp > score:
                                score = score_temp
                                get_node_text = split_text_temp

                        res[get_node_text][connection_temp.attr].append(get_text)
        return res

    pbar.update(1)
    dump(f"處理進度: 產生邏輯形式 (LF)...")

    sql_lists = []

    for graph in graph_lists:
        tqdm.write(" ")
        dump("-------------------------------------------------------------------------")
        dump('|                                                                       |')
        dump('|                              邏輯形式 (LF)                            |')
        dump('|                                                                       |')
        dump("-------------------------------------------------------------------------")


        for node_temp in graph.nodes:
            dump('-------node-------')
            dump('node:')
            dump(node_temp, node_temp.ref)
            dump('connections:')

            if len(node_temp.connections) == 0:
                dump('empty')

            for connection_temp in node_temp.connections:
                dump(connection_temp)

        tqdm.write(" ")
        dump("-------------------------------------------------------------------------")
        dump('|                                                                       |')
        dump('|                           處理邏輯形式 (LF)                           |')
        dump('|                                                                       |')
        dump("-------------------------------------------------------------------------")

        pbar.update(20)
        dump(f"處理進度: 對 lf 圖 (list) 進行拆解並逐層匹配到對應要處理的 SQL 階段...")

        logical_form = get_logical_form(graph, pbar)

        pbar.update(20)
        dump(f"處理進度: 將各階段的 SQL 轉換成對應的查詢語言...")
        sql_lists.append(transfer_sql(logical_form))

    sql = combine_sql(sql_lists, type)

    return sql
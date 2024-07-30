from helper.base_define import data_get, dd, dump, similarity
from graph.base_define import Shape, NodeAttr, Node, Graph
from service.sentence_analysis_service import SentenceAnalysis
from enum import Enum

class SimilarScore(Enum):
    Table = 0.65
    Column = 0.4
    TEXT = 0.7
    RANGE_TEXT = 0.6
    ADJ_TEXT = 0.6

    def __float__(self):
        return float(self.value)

    def __eq__(self, other):
        if isinstance(other, float):
            return float(self) == other
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, float):
            return float(self) != other
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, float):
            return float(self) < other
        return NotImplemented

    def __le__(self, other):
        if isinstance(other, float):
            return float(self) <= other
        return NotImplemented

    def __gt__(self, other):
        if isinstance(other, float):
            return float(self) > other
        return NotImplemented

    def __ge__(self, other):
        if isinstance(other, float):
            return float(self) >= other
        return NotImplemented


def create_lf_graph(data:dict, res: dict) -> Graph:
    graph = Graph()

    for table in res[Shape.entity.value]:
        graph.insert(
            Shape.entity.value,
            table,
            'id_not_used',
            {}
        )

    for relation_table in res[Shape.diamond.value]:
        relation_table_node_temp = graph.insert(
            Shape.diamond.value,
            relation_table,
            'id_not_used',
            {}
        )

        subject_node_temp = graph.search_by_shape_and_name(data[Shape.diamond.value][relation_table]['subject']['shape'],  data[Shape.diamond.value][relation_table]['subject']['name'])
        object_node_temp = graph.search_by_shape_and_name(data[Shape.diamond.value][relation_table]['object']['shape'],  data[Shape.diamond.value][relation_table]['object']['name'])

        if subject_node_temp != None:
            relation_table_node_temp.connect(subject_node_temp, data[Shape.diamond.value][relation_table]['subject']['key'], 'subject')

        if object_node_temp != None:
            relation_table_node_temp.connect(object_node_temp, data[Shape.diamond.value][relation_table]['object']['key'], 'object')

    return graph

def create_lf_graph_by_only_text(data: dict, text: str, pbar):
    graph_lists = []
    sentence_analysis = SentenceAnalysis()

    pbar.update(10)
    dump(f"處理進度: 識別問題中每個詞彙的詞性與關係...")

    analyze_sentence_lists, type = prepare_create_lf_graph_by_analyze_sentence(
        data,
        sentence_analysis,
        text,
        pbar
    )

    if compare_structures_union(analyze_sentence_lists):
        type = 'union'

    analyze_sentence_lists_temp = merge_if_conditions_met(analyze_sentence_lists)

    if len(analyze_sentence_lists_temp) != 0:
        analyze_sentence_lists = analyze_sentence_lists_temp

        if type == 'union':
            type = 'merge_or'

    for analyze_sentence_list in analyze_sentence_lists:
        res, attr = analyze_sentence_list['structure_temp'], analyze_sentence_list['structure_attr_temp']

        pbar.update(1)
        dump(f"處理進度: 為關鍵字建立對應節點（矩形、菱形），以及建立動詞對應的連線...")
        graph = create_lf_graph(data, res)

        for row in res[Shape.predicate.value]:
            pbar.update(1)
            dump(f"處理進度: 橢圓形節點 找到對應的矩形節點並連線...")
            node_temp = graph.search_by_shape_and_name(
                Shape.entity.value,
                row['table'],
            )

            if node_temp == None:
                node_temp = graph.search_by_shape_and_name(
                    Shape.diamond.value,
                    row['table'],
                )

                if node_temp == None:
                    continue

            column_temp = row['column']
            operation_temp = '='
            value_temp = row['value']

            node_name_temp = f"{column_temp}{operation_temp}'{value_temp}'"

            value_node_temp = graph.insert(Shape.predicate.value, node_name_temp, 'id_not_used', {})

            if value_node_temp != None:
                node_temp.connect(value_node_temp, 'modifier', 'modifier')

        
        head_noun_status = False

        for table_temp, table_attr_temp in attr[Shape.diamond.value].items():
            for attr_temp in table_attr_temp:
                if NodeAttr.headnoun.value in attr_temp:
                    node_temp = graph.search_by_shape_and_name(
                        Shape.diamond.value,
                        table_temp,
                    )

                    if node_temp == None:
                        raise Exception("找不到節點")

                    node_name_temp = attr_temp[NodeAttr.headnoun.value][0] + ' = ?' 

                    search_default_node = graph.insert(Shape.predicate.value, node_name_temp, 'id_not_used', {})
                    search_default_node.connect(node_temp, 'headnoun', 'headnoun')
                    head_noun_status = True

        if not head_noun_status:
            for table_temp in res[Shape.entity.value]:
                pbar.update(1)
                dump(f"處理進度: 找出目標提取欄位設置之處...")
                node_temp = graph.search_by_shape_and_name(
                    Shape.entity.value,
                    table_temp,
                )

                if node_temp == None:
                    continue

                node_double_check_temp = graph.search_by_shape_to_another_shape_and_name_lists(
                    Shape.diamond.value,
                    Shape.entity.value,
                    node_temp
                )

                if (len(node_temp.connections) == 0 or len(res[Shape.entity.value]) == 1) and len(node_double_check_temp) != 2:
                    column_temp = data[Shape.entity.value][table_temp]['headnoun']

                    for attr_table_temp, table_attr_temp in attr[Shape.entity.value].items():
                        for attr_temp in table_attr_temp:
                            if NodeAttr.headnoun.value in attr_temp and attr_table_temp == table_temp:
                                column_temp = attr_temp[NodeAttr.headnoun.value][0]

                    node_name_temp = column_temp + ' = ?' 

                    search_default_node = graph.insert(Shape.predicate.value, node_name_temp, 'id_not_used', {})
                    search_default_node.connect(node_temp, 'headnoun', 'headnoun')

                    head_noun_status = True

                    break

        pbar.update(1)
        dump(f"處理進度: 找出總體限量對應的節點...")
        for table_temp, table_attr_temp in attr[Shape.entity.value].items():
            for attr_temp in table_attr_temp:
                if NodeAttr.range.value in attr_temp:
                    node_temp = graph.search_by_shape_and_name(
                        Shape.entity.value,
                        table_temp,
                    )

                    if node_temp == None:
                        raise Exception("找不到節點")

                    node_temp.ref[NodeAttr.range.value] = attr_temp[NodeAttr.range.value]

        pbar.update(1)
        dump(f"處理進度: 找出否定詞彙對應的節點（橢圓）...")
        for table_temp, table_attr_temp in attr[Shape.predicate.value].items():
            for column_temp, column_attr_temp in table_attr_temp.items():
                for value_temp, value_attr_temp in column_attr_temp.items():
                    for attr_temp_list in value_attr_temp:
                        for attr_temp in attr_temp_list:
                            if NodeAttr.negative.value in attr_temp:
                                node_temp = graph.search_by_shape_and_like_name(
                                    Shape.predicate.value,
                                    value_temp,
                                )

                                if node_temp == None:
                                    raise Exception("找不到節點")

                                node_temp.name =  node_temp.name.replace("=", ' != ')
                            if NodeAttr.compare_node.value in attr_temp:
                                node_temp = graph.search_by_shape_and_like_name(
                                    Shape.predicate.value,
                                    value_temp,
                                )

                                if node_temp == None:
                                    raise Exception("找不到節點")

                                compare_value = attr_temp_list[NodeAttr.compare_node.value]

                                node_temp.name =  node_temp.name.replace("=", f" {compare_value} ")

        pbar.update(1)
        dump(f"處理進度: 找出否定詞彙對應的節點（菱形）...")
        for table_temp, table_attr_temp in attr[Shape.diamond.value].items():
            for attr_temp in table_attr_temp:
                if NodeAttr.negative.value in attr_temp and NodeAttr.negative_node.value in attr_temp :
                    node_temp = graph.search_by_shape_and_name(
                        Shape.diamond.value,
                        table_temp,
                    )

                    if node_temp == None:
                        raise Exception("找不到節點")

                    node_temp.ref[NodeAttr.negative.value] = attr_temp[NodeAttr.negative.value]
                    node_temp.ref[NodeAttr.negative_node.value] = attr_temp[NodeAttr.negative_node.value]
                elif NodeAttr.negative.value in attr_temp:
                    node_temp = graph.search_by_shape_and_name(
                        Shape.diamond.value,
                        table_temp,
                    )

                    if node_temp == None:
                        raise Exception("找不到節點")

                    node_temp.ref[NodeAttr.negative.value] = attr_temp[NodeAttr.negative.value]

        graph_lists.append(graph)

    return graph_lists, type

def generate_by_relation(data: dict, res_temp: list) -> list:
    structure_temp = {
        Shape.entity.value: [],
        Shape.predicate.value: [],
        Shape.diamond.value: [],
    }

    status = False

    for row in res_temp:
        if row['part_of_speech'] == 'VERB' and row['dependency'] != 'ROOT':
            relation_table_temp = search_similarity_relation_table_by_data(data, Shape.diamond.value, row['text'])

            if relation_table_temp == None:
                continue

            table_temp = search_similarity_table_by_data(data, Shape.entity.value, [row['head_text']])

            if table_temp == None:
                similarity_table_temp_lists = []

                for res_temp_row in res_temp:
                    if row['head_text'] == res_temp_row['text']:
                            for res_temp_children_text_row in res_temp_row['children']:
                                for res_temp_row2 in res_temp:
                                    if res_temp_children_text_row == res_temp_row2['head_text']:
                                        similarity_table_temp_lists.append(res_temp_row2['text'])

                table_temp = search_similarity_table_by_data(data, Shape.entity.value, similarity_table_temp_lists)

            if table_temp == None:
                similarity_table_temp_lists = []

                for res_temp_row in res_temp:
                    if row['head_text'] == res_temp_row['head_text']:
                        similarity_table_temp_lists.append(res_temp_row['text'])

                table_temp = search_similarity_relation_table_by_data(data, Shape.entity.value, None, similarity_table_temp_lists)

            if table_temp == None:
                raise Exception("[generate_by_relation] 找不到 Table")

            structure_temp[Shape.entity.value].append(table_temp)

            another_table = table_temp

            table_temp = search_similarity_table_by_data(data, Shape.entity.value, row['children'])

            if table_temp == None:
                for children_text in row['children']:
                    for res_temp_row in res_temp:
                        if children_text == res_temp_row['text'] and res_temp_row['dependency'] == 'agent':
                            table_temp = search_similarity_relation_table_by_data(data, Shape.entity.value, res_temp_row['head_text'])

                            if table_temp == None:
                                table_temp = search_similarity_table_by_data_with_dependency_agent(data, Shape.entity.value, res_temp_row['children'])

            if table_temp == None or table_temp in structure_temp[Shape.entity.value]:
                table_temp= get_table_by_relation_table(data, relation_table_temp, another_table)

            if table_temp == None:
                raise Exception("[generate_by_relation] 找不到 Table")

            structure_temp[Shape.entity.value].append(table_temp)

            if len(structure_temp[Shape.entity.value]) != 0 or len(structure_temp[Shape.entity.value]) % 2 == 0:
                table_temp = search_relation_table_by_data(data, structure_temp[Shape.entity.value][len(structure_temp[Shape.entity.value]) - 2] , structure_temp[Shape.entity.value][len(structure_temp[Shape.entity.value]) - 1])

                if table_temp != relation_table_temp:
                    continue

                structure_temp[Shape.diamond.value].append(table_temp)

                status = True

    if status == False:
        return None

    return structure_temp

def generate_by_main_table(data: dict, res_temp: list) -> list:
    structure_temp = {
        Shape.entity.value: [],
        Shape.predicate.value: [],
        Shape.diamond.value: [],
    }

    part_of_speech_num = 0

    for row in res_temp:
        if row['part_of_speech'] == 'PROPN':
            part_of_speech_num += 1

    if part_of_speech_num == 2:
        for row in res_temp:
            if row['part_of_speech'] == 'PROPN':
                table_temp, column_temp, _ = search_similarity_column_by_data(data, Shape.diamond.value, None, row['text'], None, True)

                if table_temp == None:
                    raise Exception("[generate_by_main_table] 找不到 Table")

                structure_temp[Shape.diamond.value].append(table_temp)

                if column_temp == None:
                    raise Exception("[generate_by_main_table] 找不到 Column")

                structure_temp[Shape.predicate.value].append({'table': table_temp, 'column': column_temp, 'value': row['text']})

        if len(structure_temp[Shape.predicate.value]) == 2:
            structure_temp[Shape.diamond.value] = list(set(structure_temp[Shape.diamond.value]))

            return structure_temp


    for row in res_temp:
        if row['part_of_speech'] == 'PROPN' and row['dependency'] == 'nsubjpass' and row['head_pos'] == 'VERB':
            table_temp = search_similarity_table_by_data(data, Shape.entity.value, row['children'])

            if table_temp == None:
                raise Exception("[generate_by_main_table] 找不到 Table")

            structure_temp[Shape.entity.value].append(table_temp)

            return structure_temp

    for row in res_temp:
        if row['part_of_speech'] == 'VERB' and row['dependency'] != 'ROOT':
            table_temp = search_similarity_table_by_data(data, Shape.entity.value, [row['head_text']])

            if table_temp == None:
                for res_temp_row in res_temp:
                    if row['head_text'] == res_temp_row['head_text']:
                        table_temp_check = search_similarity_relation_table_by_data(data, Shape.entity.value, res_temp_row['text'])

                        if table_temp == None and table_temp_check != None:
                            table_temp = table_temp_check

                        if table_temp != table_temp_check and table_temp_check != None:
                            raise Exception("[generate_by_main_table] 找不到相似 Table")

                if row['dependency'] == 'pcomp' and row['head_pos'] == 'ADP':
                    table_temp, column_temp, _ = search_similarity_column_by_data(data, Shape.entity.value, None, row['text'], None, True)
                    check_table_temp, check_column_temp, _ = search_similarity_column_by_data(data, Shape.entity.value, None, None, row['children'], True)

                    if (table_temp != None and column_temp != None
                        and table_temp == check_table_temp and column_temp == check_column_temp):
                        structure_temp[Shape.entity.value].append(table_temp)

                        return structure_temp
                    else:
                        raise Exception("[generate_by_main_table] 找不到相似 Table")

            if table_temp == None:
                continue

            column_temp = search_similarity_column_by_data(data, Shape.entity.value, table_temp, row['text'])

            if column_temp == None:
                raise Exception("[generate_by_main_table] 找不到 Column")

            structure_temp[Shape.entity.value].append(table_temp)

            return structure_temp

    for row in res_temp:
        if row['part_of_speech'] == 'AUX':
            table_temp = search_similarity_table_by_data(data, Shape.entity.value, [row['head_text']])

            if table_temp == None:
                for res_temp_row in res_temp:
                    if row['head_text'] == res_temp_row['head_text'] and res_temp_row['part_of_speech'] == 'NOUN':
                        table_temp = search_similarity_relation_table_by_data(data, Shape.entity.value, res_temp_row['text'])

                        if table_temp != None:
                            break

                    if row['head_text'] == res_temp_row['head_text'] and res_temp_row['part_of_speech'] == 'ADP':
                        table_temp = search_similarity_relation_table_by_data(data, Shape.entity.value, None, res_temp_row['children'])

                        if table_temp != None:
                            break

            if table_temp == None:
                
                continue

            column_temp = search_similarity_column_by_data(data, Shape.entity.value, table_temp, None, row['children'])

            if column_temp == None:
                raise Exception("[generate_by_main_table] 找不到 Column")

            structure_temp[Shape.entity.value].append(table_temp)

            for res_temp_row in res_temp:
                found = False

                if row['text'] == res_temp_row['head_text'] and res_temp_row['dependency'] == 'attr':
                    for table_temp in structure_temp[Shape.entity.value]:
                        relation_table_temp, column_temp, _ = search_similarity_column_by_data(data, Shape.diamond.value, None, res_temp_row['text'], None, True)

                        if column_temp != None:
                            table_temp, column_temp = search_relation_column_by_value(data, relation_table_temp, res_temp_row['text'])
                            structure_temp[Shape.predicate.value].append({'table': table_temp, 'column': column_temp, 'value': res_temp_row['text']})
                            found = True

                            break
                if found:
                    break

            return structure_temp

    for row in res_temp:
        if row['part_of_speech'] == 'ADJ':
            table_temp = search_similarity_table_by_data(data, Shape.entity.value, [row['head_text']])

            if table_temp == None:
                raise Exception("[generate_by_main_table] 找不到 Table")

            column_temp = search_similarity_column_by_data(data, Shape.entity.value, table_temp, row['text'])

            if column_temp == None:
                continue

            structure_temp[Shape.entity.value].append(table_temp)

            structure_temp[Shape.predicate.value].append({'table': table_temp, 'column': column_temp, 'value': row['text']})

            return structure_temp

    for row in res_temp:
        if row['part_of_speech'] == 'NOUN' and row['dependency'] == 'compound':
            for res_temp_row in res_temp:
                if row['head_text'] == res_temp_row['text'] and res_temp_row['dependency'] == 'pobj' and res_temp_row['head_pos'] == 'ADP':
                    table_temp, column_temp, _ = search_similarity_column_by_data(data, Shape.entity.value, None, row['text'], None, True)
                    check_table_temp, check_column_temp, _ = search_similarity_column_by_data(data, Shape.entity.value, None, res_temp_row['text'], None, True)

                    if (table_temp != None and column_temp != None
                        and table_temp == check_table_temp and column_temp == check_column_temp):
                        structure_temp[Shape.entity.value].append(table_temp)
                        structure_temp[Shape.predicate.value].append({'table': table_temp, 'column': column_temp, 'value': res_temp_row['text']})

                        return structure_temp
                    else:
                        raise Exception("[generate_by_main_table] 找不到相似 Table")

    for row in res_temp:
        if row['dependency'] == 'ROOT':
            table_temp = search_similarity_table_by_data(data, Shape.entity.value, row['children'])

            if table_temp == None:
                for res_temp_row in res_temp:
                    if res_temp_row['head_text'] in row['children']:
                        table_temp = search_similarity_relation_table_by_data(data, Shape.entity.value, res_temp_row['text'])

                        if table_temp != None:
                            break

            if table_temp == None:
                
                continue

            for res_temp_row in res_temp:
                found = False

                if res_temp_row['part_of_speech'] == 'NOUN' and res_temp_row['dependency'] == 'compound':
                    column_temp = search_similarity_column_by_data(data, Shape.entity.value, table_temp, res_temp_row['text'])

                    if column_temp == None:
                        continue

                    structure_temp[Shape.entity.value].append(table_temp)
                    structure_temp[Shape.predicate.value].append({'table': table_temp, 'column': column_temp, 'value': res_temp_row['head_text']})

                    return structure_temp

    for row in res_temp:
        if row['part_of_speech'] == 'NOUN':
            for res_temp_row in res_temp:
                if res_temp_row['text'] == 'of' and row['text'] in res_temp_row['children']:
                    table_temp = search_similarity_table_by_data(data, Shape.entity.value, res_temp_row['children'])

                    if table_temp == None:
                        raise Exception("[generate_by_main_table] 找不到 Table")

                    structure_temp[Shape.entity.value].append(table_temp)

                    return structure_temp


    return None

def prepare_create_lf_graph_by_analyze_sentence(data: dict,sentence_analysis: SentenceAnalysis, text: str, pbar):
    text = text.replace('.', '')
    text = text.replace('?', '')
    res = []
    explode, type = sentence_analysis.analyze_explode(text)
    
    for explode_res_temp in explode:
        structure_attr_temp = {
            Shape.entity.value: {},
            Shape.predicate.value: {},
            Shape.diamond.value: {},
        }

        res_temp = sentence_analysis.analyze_sentence(explode_res_temp)
        
        pbar.update(10)
        dump(f"處理進度: 尋找動詞，它是主要結構...")
        generate_temp = generate_by_relation(data, res_temp)

        if generate_temp != None:
            structure_temp = generate_temp

        if generate_temp == None:
            generate_temp = generate_by_main_table(data, res_temp)

        if generate_temp != None:
            structure_temp = generate_temp

        if generate_temp == None:
            raise Exception("找不到主要結構")

        pbar.update(1)
        dump(f"處理進度: 尋找限定詞範圍...")
        for row in res_temp:
            if row['part_of_speech'] == 'DET' and row['text'] not in ['the']:
                for row_temp in structure_temp[Shape.entity.value]:
                    if similarity(row['head_text'], row_temp) > SimilarScore.RANGE_TEXT:
                        table_temp = row_temp
                        if table_temp not in structure_attr_temp[Shape.entity.value]:
                            structure_attr_temp[Shape.entity.value][table_temp] = []

                        structure_attr_temp[Shape.entity.value][table_temp].append({ NodeAttr.range.value : row['text']})

        pbar.update(1)
        dump(f"處理進度: 尋找形容詞...")
        for row in res_temp:
            if row['part_of_speech'] == 'ADJ':
                for row_temp in structure_temp[Shape.entity.value]:
                    if similarity(row_temp, row['head_text']) > SimilarScore.ADJ_TEXT or row['dependency'] == 'acomp':
                        column_temp = search_similarity_column_by_data(data, Shape.entity.value, row_temp, row['text'])

                        if column_temp != None:
                            structure_temp[Shape.predicate.value].append({'table': row_temp, 'column': column_temp, 'value': row['text']})

        pbar.update(1)
        dump(f"處理進度: 尋找數值...")
        for row in res_temp:
            if row['part_of_speech'] == 'NUM':
                for res_temp_row in res_temp:
                    if row['head_text'] == res_temp_row['text']:
                        for row_temp in structure_temp[Shape.entity.value]:
                            if similarity(row_temp, res_temp_row['head_text']) > SimilarScore.ADJ_TEXT:
                                column_temp = search_similarity_column_by_data(data, Shape.entity.value, row_temp, row['text'])

                                if column_temp != None:
                                    structure_temp[Shape.predicate.value].append({'table': row_temp, 'column': column_temp, 'value': row['text']})

                                if 'than' not in row['children']:
                                    break

                                compare_temp = '>'

                                if set(['less', 'fewer', 'under', 'below', 'lower', 'inferior', 'deficient']) & set(row['children']):
                                    compare_temp = '<'

                                if row_temp not in structure_attr_temp[Shape.predicate.value]:
                                    structure_attr_temp[Shape.predicate.value][row_temp] = {}

                                if column_temp not in structure_attr_temp[Shape.predicate.value][row_temp]:
                                    structure_attr_temp[Shape.predicate.value][row_temp][column_temp] = {}

                                if row['text'] not in structure_attr_temp[Shape.predicate.value][row_temp][column_temp]:
                                    structure_attr_temp[Shape.predicate.value][row_temp][column_temp][row['text']] = []

                                structure_attr_temp[Shape.predicate.value][row_temp][column_temp][row['text']].append({ NodeAttr.compare_node.value : compare_temp})

                                break

        pbar.update(1)
        dump(f"處理進度: 尋找專有代名詞...")
        for row in res_temp:
            found = False

            if row['part_of_speech'] == 'PROPN':
                for table_temp in structure_temp[Shape.entity.value]:
                    column_temp = search_similarity_column_by_data(data, Shape.entity.value, table_temp, row['text'])

                    if column_temp != None:
                        structure_temp[Shape.predicate.value].append({'table': table_temp, 'column': column_temp, 'value': row['text']})
                        found = True

                        break

                if found:
                    break

                for table_temp in structure_temp[Shape.entity.value]:
                    relation_table_temp, column_temp, _ = search_similarity_column_by_data(data, Shape.diamond.value, None, row['text'], None, True)

                    if column_temp != None:
                        table_temp, _ = search_relation_column_by_value(data, relation_table_temp, row['text'])
                        structure_temp[Shape.predicate.value].append({'table': table_temp, 'column': column_temp, 'value': row['text']})
                        found = True
                        break

                if found:
                    break

                for table_temp in structure_temp[Shape.entity.value]:
                    column_temp = search_similarity_column_by_data(data, Shape.entity.value, table_temp, row['head_text'])
                    if column_temp != None:
                        structure_temp[Shape.predicate.value].append({'table': table_temp, 'column': column_temp, 'value': row['text']})
                        found = True
                        break

                if found:
                    break

                for res_temp_row in res_temp:
                    if row['head_text'] == res_temp_row['text']:
                        for table_temp in structure_temp[Shape.entity.value]:
                            if similarity(res_temp_row['head_text'], table_temp) > SimilarScore.Table:
                                column_temp = search_similarity_column_by_data(data, Shape.entity.value, table_temp, row['text'])

                                if column_temp != None:
                                    structure_temp[Shape.predicate.value].append({'table': table_temp, 'column': column_temp, 'value': row['text']})

                                if column_temp != None:
                                    found = True
                                    break

                        if found:
                            break
        
        pbar.update(1)
        dump(f"處理進度: 尋找名詞...")
        for row in res_temp:
            if row['part_of_speech'] == 'VERB' and row['dependency'] != 'ROOT':
                
                entity_table_temp , column_temp, column_value_temp = search_similarity_column_by_data(data, Shape.entity.value, None, None, row['children'], True)
                relation_table_temp = search_similarity_relation_table_by_data(data, Shape.diamond.value, row['text'])

                if entity_table_temp == column_value_temp:
                    continue

                if column_value_temp in ['who', 'whose', 'where', 'where', 'which', 'that', 'part', 'supplier']:
                    continue

                if relation_table_temp not in generate_temp[Shape.diamond.value]:
                    continue

                if entity_table_temp not in generate_temp[Shape.entity.value]:
                    continue

                if len(generate_temp[Shape.predicate.value]) != 0:
                    continue

                structure_temp[Shape.predicate.value].append({'table': entity_table_temp, 'column': column_temp, 'value': column_value_temp})
                break

        
        pbar.update(1)
        dump(f"處理進度: 尋找否定詞...")
        for row in res_temp:
            if row['dependency'] == 'neg':
                relation_table_temp = search_similarity_relation_table_by_data(data, Shape.diamond.value, row['head_text'])
                negative_node_temp = None

                for res_temp_row in res_temp:
                    if row['head_text'] == res_temp_row['text']:
                        for res_temp_children_text_row in res_temp_row['children']:
                            for res_temp_row2 in res_temp:
                                if res_temp_children_text_row == res_temp_row2['text'] and  res_temp_row2['dependency'] == 'nsubjpass':
                                    negative_node_temp = search_similarity_relation_table_by_data(data, Shape.entity.value, res_temp_row2['head_text'])

                        if negative_node_temp == None:
                            negative_node_temp = search_similarity_table_by_data(data, Shape.entity.value, [res_temp_row['head_text']])

                        if negative_node_temp == None:
                            negative_node_temp, _, _ = search_similarity_column_by_data(data, Shape.entity.value, None, res_temp_row['head_text'])

                if relation_table_temp in structure_temp[Shape.diamond.value]:
                    if relation_table_temp != None:
                        if relation_table_temp not in structure_attr_temp[Shape.diamond.value]:
                            structure_attr_temp[Shape.diamond.value][relation_table_temp] = []

                        structure_attr_temp[Shape.diamond.value][relation_table_temp].append(
                            {
                                NodeAttr.negative.value : row['text'],
                                NodeAttr.negative_node.value : negative_node_temp,
                            }
                        )

                        continue

                for table_temp in structure_temp[Shape.entity.value]:
                    for res_temp_row in res_temp:
                        if row['head_text'] == res_temp_row['text']:
                            column_temp = search_similarity_column_by_data(data, Shape.entity.value, table_temp, None, res_temp_row['children'])

                    if column_temp == None:
                        column_temp = search_similarity_column_by_data(data, Shape.entity.value, table_temp, row['head_text'])

                    for again_row in res_temp:
                        if row['head_text'] == again_row['text']:
                            table_temp = again_row['head_text']

                    if table_temp not in structure_temp[Shape.entity.value]:
                        
                        table_temp = structure_temp[Shape.entity.value][0]

                    for predicate_temp in structure_temp[Shape.predicate.value]:
                        if column_temp != predicate_temp['column']:
                            continue

                        if table_temp not in structure_attr_temp[Shape.predicate.value]:
                            structure_attr_temp[Shape.predicate.value][table_temp] = {}

                        if column_temp not in structure_attr_temp[Shape.predicate.value][table_temp]:
                            structure_attr_temp[Shape.predicate.value][table_temp][column_temp] = {}

                        if predicate_temp['value'] not in structure_attr_temp[Shape.predicate.value][table_temp][column_temp]:
                            structure_attr_temp[Shape.predicate.value][table_temp][column_temp][predicate_temp['value']] = []

                        structure_attr_temp[Shape.predicate.value][table_temp][column_temp][predicate_temp['value']].append({ NodeAttr.negative.value : row['text']})

        pbar.update(1)
        for row in res_temp:
            for releation_table in structure_temp[Shape.diamond.value]:
                entity_table_temp, column_temp  = search_relation_column_by_value(data, releation_table, row['text'])

                if entity_table_temp != None and entity_table_temp in structure_temp[Shape.entity.value]:
                    if releation_table in structure_attr_temp[Shape.diamond.value]:
                        for i in range(len(structure_attr_temp[Shape.diamond.value][releation_table])):
                            if (
                                NodeAttr.negative.value in structure_attr_temp[Shape.diamond.value][releation_table][i]
                                and structure_attr_temp[Shape.diamond.value][releation_table][i][NodeAttr.negative_node.value] == entity_table_temp
                            ):
                                structure_attr_temp[Shape.diamond.value][releation_table][i][NodeAttr.negative_node.value] = column_temp
                                break

                    structure_temp[Shape.entity.value].remove(entity_table_temp)
                    structure_temp[Shape.predicate.value].append({'table': releation_table, 'column': column_temp, 'value': row['text']})
        
        pbar.update(1)
        dump(f"處理進度: 提取目標欄位...")
        for index, row in enumerate(res_temp):
            table_temp = None

            if row['dependency'] == 'dobj':
                for res_temp_row in res_temp:
                    if res_temp_row['text'] in row['children'] and res_temp_row['head_text'] == row['text']:
                        for row_temp in structure_temp[Shape.entity.value]:
                            table_temp = search_similarity_relation_table_by_data(data, Shape.entity.value, res_temp_row['text'])

                            if table_temp == row_temp:
                                column_temp = search_similarity_column_by_data(data, Shape.entity.value, table_temp, row['text'])

                                if column_temp != None:
                                    if table_temp not in structure_attr_temp[Shape.entity.value]:
                                        structure_attr_temp[Shape.entity.value][table_temp] = []

                                    haved_status = False
                                    for structure_entity_attr_temp in structure_attr_temp[Shape.entity.value][table_temp]:
                                        if NodeAttr.headnoun.value in structure_entity_attr_temp:
                                            haved_status = True
                                            break

                                    if not haved_status:
                                        structure_attr_temp[Shape.entity.value][table_temp].append({ NodeAttr.headnoun.value : [column_temp]})

            if row['dependency'] == 'ROOT' and index != len(res_temp) -1 and index != len(res_temp) - 2:
                for index_res_temp_row, res_temp_row in enumerate(res_temp):
                    haved_status = False
                    row_temp_children = []

                    table_list = list(data[Shape.diamond.value].keys()) + list(data[Shape.entity.value].keys())

                    for children_temp in row['children']:
                        if children_temp not in table_list:
                            row_temp_children.append(children_temp)

                    row['children'] = row_temp_children

                    if res_temp_row['head_text'] == row['head_text'] and res_temp_row['part_of_speech'] == 'NOUN' and res_temp_row['text'] in row['children'] and index_res_temp_row != 0:
                        if len(structure_temp[Shape.entity.value]) == 0:
                            table_temp, column_temp, _ = search_similarity_column_by_data(data, Shape.diamond.value, None, None, row['children'])

                            if table_temp != None and column_temp != None:
                                if table_temp not in structure_attr_temp[Shape.diamond.value]:
                                    structure_attr_temp[Shape.diamond.value][table_temp] = []

                                if table_temp in structure_attr_temp[Shape.diamond.value]:
                                    for structure_entity_attr_temp in structure_attr_temp[Shape.diamond.value][table_temp]:
                                        if NodeAttr.headnoun.value in structure_entity_attr_temp:
                                            haved_status = True
                                            break

                                if not haved_status:
                                    structure_attr_temp[Shape.diamond.value][table_temp].append({ NodeAttr.headnoun.value : [column_temp]})
                                    break
                        else:
                            table_temp = None
                            for res_temp_row2 in res_temp:
                                if res_temp_row2['head_text'] == 'of':
                                    check_table_temp = search_similarity_table_by_data(data, Shape.entity.value, [res_temp_row2['text']])

                                    if check_table_temp != None:
                                        table_temp = check_table_temp

                                if set(['part', 'parts']) & set(res_temp_row['children']):
                                    table_temp = 'parts'

                            if table_temp == None:
                                table_temp, column_temp, _ = search_similarity_column_by_data(data, Shape.entity.value, None, None, row['children'])

                            column_temp = search_similarity_column_by_data(data, Shape.entity.value, table_temp, None, row['children'])

                            haved_status = False

                            if table_temp not in structure_temp[Shape.entity.value]:
                                table_temp = structure_temp[Shape.entity.value][0]

                            if table_temp != None and column_temp != None:
                                if table_temp not in structure_attr_temp[Shape.entity.value]:
                                    structure_attr_temp[Shape.entity.value][table_temp] = []

                                if table_temp in structure_attr_temp[Shape.entity.value]:
                                    for structure_entity_attr_temp in structure_attr_temp[Shape.entity.value][table_temp]:
                                        if NodeAttr.headnoun.value in structure_entity_attr_temp:
                                            haved_status = True
                                            break

                                if not haved_status:
                                    structure_attr_temp[Shape.entity.value][table_temp].append({ NodeAttr.headnoun.value : [column_temp]})
                                    break

                    haved_status = False

                    if res_temp_row['head_text'] in row['children']:
                        for res_temp_row2 in res_temp:
                            if res_temp_row2['head_text'] == res_temp_row['text']:

                                for row_temp in structure_temp[Shape.entity.value]:
                                    if similarity(res_temp_row2['text'], row_temp) > SimilarScore.TEXT:
                                        table_temp = search_similarity_table_by_data(data, Shape.entity.value, [res_temp_row2['text']])

                                if table_temp != None:
                                    column_temp = search_similarity_column_by_data(data, Shape.entity.value, table_temp, None, row['children'])

                                    if column_temp != None:
                                        if table_temp not in structure_attr_temp[Shape.entity.value]:
                                            structure_attr_temp[Shape.entity.value][table_temp] = []


                                        haved_status = False
                                        if table_temp in structure_attr_temp[Shape.entity.value]:
                                            for structure_entity_attr_temp in structure_attr_temp[Shape.entity.value][table_temp]:
                                                if NodeAttr.headnoun.value in structure_entity_attr_temp:
                                                    haved_status = True
                                                    break

                                        if not haved_status:
                                                structure_attr_temp[Shape.entity.value][table_temp].append({ NodeAttr.headnoun.value : [column_temp]})

            
            if row['dependency'] == 'nsubj':
                for res_temp_row in res_temp:
                    if res_temp_row['text'] in row['children'] and res_temp_row['head_text'] in row['text']:
                        for res_temp_row_children in res_temp_row['children']:
                            for row_temp in structure_temp[Shape.entity.value]:
                                table_temp = None

                                if similarity(res_temp_row_children, row_temp) > SimilarScore.TEXT:
                                    table_temp = search_similarity_table_by_data(data, Shape.entity.value, [res_temp_row_children])

                                if table_temp != None:
                                    column_temp = search_similarity_column_by_data(data, Shape.entity.value, table_temp, row['text'], None)

                                    if column_temp != None:
                                        if table_temp not in structure_attr_temp[Shape.entity.value]:
                                            structure_attr_temp[Shape.entity.value][table_temp] = []


                                    haved_status = False
                                    for structure_entity_attr_temp in structure_attr_temp[Shape.entity.value][table_temp]:
                                        if NodeAttr.headnoun.value in structure_entity_attr_temp:
                                            haved_status = True
                                            break

                                    if not haved_status:
                                            structure_attr_temp[Shape.entity.value][table_temp].append({ NodeAttr.headnoun.value : [column_temp]})

        pbar.update(1)
        for entity_temp in structure_temp[Shape.entity.value]:
            range_status = False
            negative_status = False

            if entity_temp in structure_attr_temp[Shape.entity.value]:
                for i in range(len(structure_attr_temp[Shape.entity.value][entity_temp])):
                    if NodeAttr.range.value in structure_attr_temp[Shape.entity.value][entity_temp][i]:
                        range_status = True

                        break

            simplify_headnoun_column = None
            if entity_temp in structure_attr_temp[Shape.entity.value]:
                for entity_attr_temp in structure_attr_temp[Shape.entity.value][entity_temp]:
                    if NodeAttr.headnoun.value in entity_attr_temp:
                        simplify_headnoun_column = entity_attr_temp[NodeAttr.headnoun.value][0]

                        break

            if simplify_headnoun_column == None:
                continue

            for diamond_temp in structure_temp[Shape.diamond.value]:
                column_temp_temp  = search_relation_column_by_table(data, diamond_temp, entity_temp)

                if simplify_headnoun_column == column_temp_temp:
                    
                    if diamond_temp in structure_attr_temp[Shape.diamond.value]:
                        for i in range(len(structure_attr_temp[Shape.diamond.value][diamond_temp])):
                            if NodeAttr.negative.value in structure_attr_temp[Shape.diamond.value][diamond_temp][i]:
                                negative_status = True

                                break

                    if (range_status and negative_status) or negative_status:
                        continue

                    structure_temp[Shape.entity.value].remove(entity_temp)
                    del structure_attr_temp[Shape.entity.value][entity_temp]

                    if diamond_temp not in structure_attr_temp[Shape.diamond.value]:
                        structure_attr_temp[Shape.diamond.value][diamond_temp] = []

                    if releation_table in structure_attr_temp[Shape.diamond.value]:
                        for i in range(len(structure_attr_temp[Shape.diamond.value][releation_table])):
                            if (
                                NodeAttr.negative.value in structure_attr_temp[Shape.diamond.value][releation_table][i]
                                and structure_attr_temp[Shape.diamond.value][releation_table][i][NodeAttr.negative_node.value] == entity_temp
                            ):
                                structure_attr_temp[Shape.diamond.value][releation_table][i][NodeAttr.negative_node.value] = simplify_headnoun_column
                                break

                    structure_attr_temp[Shape.diamond.value][diamond_temp].append({ NodeAttr.headnoun.value : [simplify_headnoun_column]})

        res.append(
            {
                "structure_temp": structure_temp,
                "structure_attr_temp": structure_attr_temp
            }
        )
    
    return res, type

def search_similarity_column_by_data(data: dict, shape: str, table: str , text: str = None, text_lists = None, equal = False) -> str:
    score = 0
    column = None
    column_value = None

    if table == None:
        table_temp = None

        if text != None:
            for shape_table, shape_table_values in data[shape].items():
                for key, values in shape_table_values['similar_of_column'].items():
                    for similar_key in values:
                        if text in data[shape][shape_table]['n'][key]:
                            continue

                        score_temp = similarity(similar_key, text)

                        if equal and text.lower() == similar_key.lower():
                            score = score_temp
                            column = key
                            table_temp = shape_table
                            column_value = text

                        elif score_temp > score and score_temp > SimilarScore.Column:
                            score = score_temp
                            column = key
                            table_temp = shape_table
                            column_value = text

            return table_temp, column, column_value

        text_lists = [s for s in text_lists if '?' not in s]

        for text in text_lists:
            for shape_table, shape_table_values in data[shape].items():
                for key, values in shape_table_values['similar_of_column'].items():
                    for similar_key in values:
                        if text in data[shape][shape_table]['n'][key]:
                            continue

                        score_temp = similarity(similar_key, text)

                        if equal and text.lower() == similar_key.lower():
                            score = score_temp
                            column = key
                            table_temp = shape_table
                            column_value = text

                        if score_temp > score and score_temp > SimilarScore.Column:
                            score = score_temp
                            column = key
                            table_temp = shape_table
                            column_value = text

        return table_temp, column, column_value

    if text != None:
        for key, values in data[shape][table]['similar_of_column'].items():
            for similar_key in values:
                if text in data[shape][table]['n'][key]:
                    continue

                score_temp = similarity(similar_key, text)
                
                if score_temp > score and score_temp > SimilarScore.Column:
                    score = score_temp
                    column = key
        return column

    for text in text_lists:
        for key, values in data[shape][table]['similar_of_column'].items():
            for similar_key in values:
                if text in data[shape][table]['n'][key]:
                    continue

                score_temp = similarity(similar_key, text)

                if score_temp > score and score_temp > SimilarScore.Column:
                    score = score_temp
                    column = key

    return column

def search_similarity_table_by_data(data: dict, shape: str, text_list: list) -> str:
    score = 0
    table = None

    for text in text_list:
        for key, values in data[shape].items():
            score_temp = similarity(key, text)

            if score_temp > score and score_temp > SimilarScore.Table:
                score = score_temp
                table = key

    return table

def search_similarity_table_by_data_with_dependency_agent(data: dict, shape: str, text_list: list) -> str:
    score = 0

    table = None

    for text in text_list:
        for key, values in data[shape].items():
            score_temp = similarity(key, text)

            if score_temp > score:
                score = score_temp
                table = key

    return table

def search_similarity_relation_table_by_data(data: dict, shape: str, text: str = None, text_lists = None) -> str:
    score = 0

    table = None

    if text != None:
        for key, values in data[shape].items():
            for similar_key in values['similar_of_table']:
                score_temp = similarity(similar_key, text)
                
                if score_temp > score and score_temp > SimilarScore.Table:
                    score = score_temp
                    table = key
        return table

    for text in text_lists:
        for key, values in data[shape].items():
            for similar_key in values['similar_of_table']:
                score_temp = similarity(similar_key, text)
                if score_temp > score and score_temp > SimilarScore.Table:
                    score = score_temp
                    table = key
    return table

def search_relation_table_by_data(data: dict, table_one: str, table_two: str) -> str:
    for key, values in data[Shape.diamond.value].items():
        if values['subject']['name'] ==  table_one and values['object']['name'] ==  table_two:
            return key

        if values['object']['name'] ==  table_one and values['subject']['name'] ==  table_two:
            return key

    return None

def search_relation_column_by_value(data: dict, relation_table: str, value: str) -> str:
    for k, v in data[Shape.diamond.value][relation_table]['similar_of_column'].items():
        if value in v:
            if data[Shape.diamond.value][relation_table]['object']['key'] == k:
                return data[Shape.diamond.value][relation_table]['object']['name'], k

            if data[Shape.diamond.value][relation_table]['subject']['key'] == k:
                return data[Shape.diamond.value][relation_table]['subject']['name'], k

    return None, None

def search_relation_column_by_table(data: dict, relation_table: str, table_name: str) -> str:
    if data[Shape.diamond.value][relation_table]['object']['name'] == table_name:
        return data[Shape.diamond.value][relation_table]['object']['key']

    if data[Shape.diamond.value][relation_table]['subject']['name'] == table_name:
        return data[Shape.diamond.value][relation_table]['subject']['key']

    return None

def get_table_by_relation_table(data: dict, relation_table: str, another_table: str) -> str:
    if data[Shape.diamond.value][relation_table]['subject']['name'] == another_table:
        return data[Shape.diamond.value][relation_table]['object']['name']

    if data[Shape.diamond.value][relation_table]['object']['name'] == another_table:
        return data[Shape.diamond.value][relation_table]['subject']['name']

    return None

def compare_structures_union(data):
    def normalize_structure(structure):
        
        normalized_structure = structure.copy()
        normalized_structure['predicate'] = [
            {k: v for k, v in predicate.items() if k != 'value'}
            for predicate in structure['predicate']
        ]
        return normalized_structure

    
    reference_structure = normalize_structure(data[0]['structure_temp'])

    
    for item in data[1:]:
        current_structure = normalize_structure(item['structure_temp'])
        if reference_structure != current_structure:
            return False

    return True

def merge_if_conditions_met(data):
    if not data or len(data) < 2:
        return []

    
    reference_attr_temp = data[0]['structure_attr_temp']
    reference_diamond = data[0]['structure_temp']['diamond']
    reference_entity = data[0]['structure_temp']['entity']
    merged_predicates = []
    predicate_set = set()

    for item in data:
        
        if item['structure_attr_temp'] != reference_attr_temp:
            return []  

        structure = item['structure_temp']

        if len(structure['diamond']) != 0 or len(structure['entity']) != 1:
            return []  

        if structure['diamond'] != reference_diamond or structure['entity'] != reference_entity:
            return []  

        
        for predicate in structure['predicate']:
            predicate_key = (predicate['column'], predicate['table'])
            if predicate_key in predicate_set:
                return []  
            predicate_set.add(predicate_key)
            merged_predicates.append(predicate)
    
    merged_structure = {
        'structure_attr_temp': reference_attr_temp,
        'structure_temp': {
            'diamond': reference_diamond,
            'entity': reference_entity,
            'predicate': merged_predicates
        }
    }
    return [merged_structure]
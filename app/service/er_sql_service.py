from helper.base_define import data_get, dd, dump, similarity
from graph.base_define import Shape, NodeAttr, Node, Graph
from service.sentence_analysis_service import SentenceAnalysis

def get_logical_form(graph: Graph, pbar) -> list:
    table_name = {
        "index": 0,
        "mapping": {},
    }

    logical_form = []

    pbar.update(5)
    dump(f"處理進度: 找出目標提取欄位 ...")
    connects_temp = graph.search_connections(Shape.predicate.value, Shape.entity.value, False)

    if len(connects_temp) == 0:
        connects_temp = graph.search_connections(Shape.predicate.value, Shape.diamond.value, False)

        if len(connects_temp) != 1:
            return []

        (node1_temp, node2_temp) = connects_temp[0]

        if node2_temp.connections[0].node.shape == Shape.entity.value:
            entity_connects = graph.search_connections(Shape.entity.value, Shape.predicate.value, False)

            if NodeAttr.range.value in node2_temp.connections[0].node.ref and (NodeAttr.negative.value in node2_temp.ref) == False:
                table_name, logical_form_temp = simplify_primary_key_scenario_range(table_name, node1_temp, node2_temp, entity_connects)
            
            elif NodeAttr.range.value in node2_temp.connections[0].node.ref and (NodeAttr.negative.value in node2_temp.ref) == True:
                table_name, logical_form_temp = scenario_five(table_name, node1_temp, relation_diamond_node_temp)

            else:
                (node3_temp, node4_temp) = entity_connects[0]
                table_name, logical_form_temp = simplify_primary_key_scenario_basic(table_name, node1_temp, node2_temp, node3_temp)

        else:
            table_name, logical_form_temp = simplify_primary_key_scenario_one(table_name, node1_temp, node2_temp)

        logical_form.append(logical_form_temp)

        return logical_form

    for connect_temp in connects_temp:
        (node1_temp, node2_temp) = connect_temp

        pbar.update(5)
        dump(f"處理進度: 找出目標提取欄位對應矩形節點所連線的「菱形節點」 ...")

        muti_relation_diamond_node_temp_lists = get_muti_relation_diamond_node(graph, node2_temp)

        pbar.update(5)
        dump(f"處理進度: 分辨 LF 情境圖 ...")

        if len(muti_relation_diamond_node_temp_lists) == 2:
            all_table_name_temp = []
            all_node = []
            entity_node_temp_lists = []

            for relation_diamond_node_temp in muti_relation_diamond_node_temp_lists:
                if relation_diamond_node_temp.name not in all_table_name_temp:
                    all_table_name_temp.append(relation_diamond_node_temp.name)
                    all_node.append(relation_diamond_node_temp)

                for connection_temp in relation_diamond_node_temp.connections:
                    if connection_temp.node.name not in all_table_name_temp:
                        all_table_name_temp.append(connection_temp.node.name)
                        all_node.append(connection_temp.node)

                        if connection_temp.node.shape == Shape.entity.value:
                            entity_node_temp_lists.append(connection_temp.node)
            
            relation_diamond_node_temp = switch_connections(relation_diamond_node_temp)

            table_name, logical_form_temp = prepare_table(table_name, node1_temp, all_node)

            table_name, logical_form_temp = multi_scenario_one(table_name, logical_form_temp, entity_node_temp_lists)

            logical_form.append(logical_form_temp)

            continue

        if len(muti_relation_diamond_node_temp_lists) == 1:
            relation_diamond_node_temp = muti_relation_diamond_node_temp_lists[0]

            relation_have_predicate_node = False

            for node_temp in relation_diamond_node_temp.connections:
                if node_temp.node.shape == Shape.predicate.value:
                    relation_have_predicate_node = True

            if relation_have_predicate_node and NodeAttr.negative.value in relation_diamond_node_temp.ref:
                if (relation_diamond_node_temp.ref[NodeAttr.negative_node.value] != relation_diamond_node_temp.connections[1].node.name
                    and node1_temp.connections[0].node.name == relation_diamond_node_temp.connections[1].node.name):
                    relation_diamond_node_temp = switch_connections(relation_diamond_node_temp)

                table_name, logical_form_temp = simplify_scenario_not(table_name, node1_temp, relation_diamond_node_temp)

                logical_form.append(logical_form_temp)

                continue

            if relation_have_predicate_node:
                table_name, logical_form_temp = simplify_scenario_one(table_name, node1_temp, relation_diamond_node_temp)

                logical_form.append(logical_form_temp)

                continue

            if relation_diamond_node_temp == None or len(relation_diamond_node_temp.connections) != 2:
                continue

            if NodeAttr.negative.value in relation_diamond_node_temp.ref and NodeAttr.negative_node.value in relation_diamond_node_temp.ref and (NodeAttr.range.value in relation_diamond_node_temp.connections[0].node.ref or NodeAttr.range.value in relation_diamond_node_temp.connections[1].node.ref):
                if (relation_diamond_node_temp.ref[NodeAttr.negative_node.value] != relation_diamond_node_temp.connections[1].node.name
                    and node1_temp.connections[0].node.name != relation_diamond_node_temp.connections[1].node.name):
                    relation_diamond_node_temp = switch_connections(relation_diamond_node_temp)

                table_name, logical_form_temp = scenario_five(table_name, node1_temp, relation_diamond_node_temp)
            elif NodeAttr.range.value in relation_diamond_node_temp.connections[1].node.ref:
                table_name, logical_form_temp = scenario_range(table_name, node1_temp, relation_diamond_node_temp)
            elif NodeAttr.range.value in relation_diamond_node_temp.connections[0].node.ref:
                relation_diamond_node_temp = switch_connections(relation_diamond_node_temp)
                table_name, logical_form_temp = scenario_range(table_name, node1_temp, relation_diamond_node_temp)
            elif NodeAttr.negative.value in relation_diamond_node_temp.ref and NodeAttr.negative_node.value not in relation_diamond_node_temp.ref:
                table_name, logical_form_temp = scenario_three(table_name, node1_temp, relation_diamond_node_temp)
            elif NodeAttr.negative.value in relation_diamond_node_temp.ref:
                if (relation_diamond_node_temp.ref[NodeAttr.negative_node.value] != relation_diamond_node_temp.connections[1].node.name
                    and node1_temp.connections[0].node.name == relation_diamond_node_temp.connections[1].node.name):
                    relation_diamond_node_temp = switch_connections(relation_diamond_node_temp)

                table_name, logical_form_temp = scenario_three(table_name, node1_temp, relation_diamond_node_temp)
            else:
                all_table_name_temp = []
                all_node = []
                entity_node_temp_lists = []

                for relation_diamond_node_temp in muti_relation_diamond_node_temp_lists:
                    if relation_diamond_node_temp.name not in all_table_name_temp:
                        all_table_name_temp.append(relation_diamond_node_temp.name)
                        all_node.append(relation_diamond_node_temp)

                    for connection_temp in relation_diamond_node_temp.connections:
                        if connection_temp.node.name not in all_table_name_temp:
                            all_table_name_temp.append(connection_temp.node.name)
                            all_node.append(connection_temp.node)

                            if connection_temp.node.shape == Shape.entity.value:
                                entity_node_temp_lists.append(connection_temp.node)

                table_name, logical_form_temp = prepare_table(table_name, node1_temp, all_node)

                table_name, logical_form_temp = multi_scenario_one(table_name, logical_form_temp, entity_node_temp_lists)

                # logical_form.append(logical_form_temp)

            logical_form.append(logical_form_temp)

            continue

        if len(muti_relation_diamond_node_temp_lists) != 0:
            continue

        node1_temp_entity_node = graph.search_by_shape_and_name_to_another_shape(Shape.entity.value, node2_temp.name, Shape.predicate.value)

        if node1_temp_entity_node != None:
            table_name, logical_form_temp = simplify_rec_scenario_one(table_name, node1_temp, node1_temp_entity_node)
            logical_form.append(logical_form_temp)

            continue

        raise Exception("沒有判斷式")

    return logical_form

def build_sub_query(table_name, table, condition = None) -> str:
    index = table_name['index']
    sub_query_table = f"T{index}"
    table_name['index'] += 1
    table_name["mapping"][f"{table}"] = sub_query_table

    return (table_name, f"{table} {sub_query_table}")

def base_select(select, tables, condition) -> str:
    joined_tables = ', '.join(tables)
    return f"SELECT DISTINCT {select} FROM {joined_tables} WHERE {condition}"

def simplify_base_select(select, tables, condition) -> str:
    joined_tables = ', '.join(tables)
    return f"SELECT {select} FROM {joined_tables} WHERE {condition}"

def simplify_base_select_no_tmp(select, tables, condition) -> str:
    joined_tables = ', '.join(tables)
    return f"SELECT DISTINCT {select} FROM {joined_tables} WHERE {condition}"

def base_where(search_muti_list) -> str:
    return ' AND '.join([f'{temp["table"]}.{temp["column"]} {temp["operation"]} {temp["value"]}' for temp in search_muti_list])

def where_not_exists(sub_query , table, search_list = None, search_muti_list = None, condition = None) -> str:
    search = None

    if search_list != None:
        search = ' AND '.join([f"{table}.{temp}" for temp in search_list])

    if search_muti_list != None:
        search = ' AND '.join([
            f'{temp["table1"]}.{temp["value1"]}' if 'value1' in temp else f'{temp["table1"]}.{temp["column1"]} = {temp["table2"]}.{temp["column2"]}'
            for temp in search_muti_list
        ])

    if search == None and condition != None:
        return f" NOT EXISTS ( SELECT 1 FROM {sub_query} WHERE {condition} )"

    if condition != None:
        return f" NOT EXISTS ( SELECT 1 FROM {sub_query} WHERE {search} AND {condition} )"

    return f" NOT EXISTS ( SELECT 1 FROM {sub_query} WHERE {search} )"

def simplify_where_not_exists(sub_query , table = None, search_list = None, search_muti_list = None, condition = None) -> str:
    search = None

    if search_list != None:
        search = ' AND '.join([f"{table}.{temp}" for temp in search_list])

    if search_muti_list != None:
        search = ' AND '.join([
            f'{temp["table1"]}.{temp["value1"]}' if 'value1' in temp else f'{temp["table1"]}.{temp["column1"]} = {temp["table2"]}.{temp["column2"]}'
            for temp in search_muti_list
        ])

    if search == None and condition != None:
        return f" NOT EXISTS ( SELECT 1 FROM {sub_query} WHERE {condition} )"

    if condition != None:
        return f" NOT EXISTS ( SELECT 1 FROM {sub_query} WHERE {search} AND {condition} )"

    return f" NOT EXISTS ( SELECT 1 FROM {sub_query} WHERE {search} )"

def where_exists(sub_query , table, search_list = None, search_muti_list = None, condition = None) -> str:
    search = None

    if search_list != None:
        search = ' AND '.join([f"{table}.{temp}" for temp in search_list])

    if search_muti_list != None:
        search = ' AND '.join([
            f'{temp["table1"]}.{temp["value1"]}' if 'value1' in temp else f'{temp["table1"]}.{temp["column1"]} = {temp["table2"]}.{temp["column2"]}'
            for temp in search_muti_list
        ])

    if search == None and condition != None:
        return f" EXISTS ( SELECT 1 FROM {sub_query} WHERE {condition} )"

    if condition != None:
        return f" EXISTS ( SELECT 1 FROM {sub_query} WHERE {search} AND {condition} )"

    return f" EXISTS ( SELECT 1 FROM {sub_query} WHERE {search} )"

def join_where(table, condition_table1, condition_column1, condition_table2, condition_column2, other) -> str:
    return f"{table}.{condition_column1} = {condition_table1}.{condition_column1} AND {table}.{condition_column2} = {condition_table2}.{condition_column2} {other}"

def simplify_join_where(table, condition_table1, condition_column1, other) -> str:
    return f"{table}.{condition_column1} = {condition_table1}.{condition_column1} {other}"

def entity_connect_to_predicate(table, search_list) -> str:
    return ' AND ' +  ' AND '.join([f"{table}.{search}" for search in search_list])

def simplify_connect_to_predicate(search_list) -> str:
    return ' AND ' +  ' AND '.join([f"{search}" for search in search_list]) # ' AND ' + 'pno = P2'

def prepare_table(table_name, node1_temp, all_node) -> list:
    logical_form_temp = []
    sub_query_list_temp = []

    for node_temp in all_node:
        (table_name, sub_query_temp) = build_sub_query(table_name, node_temp.name)
        sub_query_list_temp.append(sub_query_temp)

    logical_form_temp.append(
        {
            "sql": base_select(
                    table_name['mapping'][node1_temp.connections[0].node.name] + '.' + node1_temp.name.split('=')[0].strip(),
                    sub_query_list_temp,
                    '???'
                )
        }
    )

    for node_temp in all_node:
        if node_temp.shape == Shape.diamond.value:
            logical_form_temp.append(
                {
                    "sql": join_where(
                            table_name['mapping'][node_temp.name],
                            table_name['mapping'][node_temp.connections[0].node.name],
                            node_temp.connections[0].name,
                            table_name['mapping'][node_temp.connections[1].node.name],
                            node_temp.connections[1].name,
                            'AND ???'
                        )
                }
            )

    logical_form_temp[-1]['sql'] = logical_form_temp[-1]['sql'].replace("AND ???", '???')

    return table_name, logical_form_temp

def multi_scenario_one(table_name, logical_form_temp, entity_node_temp_lists) -> list:
    if len(entity_node_temp_lists) == 0:
        return table_name, logical_form_temp

    for entity_node_temp in entity_node_temp_lists:
        for predicate_node_connection_temp in entity_node_temp.connections:
            if predicate_node_connection_temp.node.shape == Shape.predicate.value:
                logical_form_temp.append(
                    {
                        "sql": entity_connect_to_predicate(
                                table_name['mapping'][entity_node_temp.name],
                                [predicate_node_connection_temp.node.name]
                            )
                    }
                )

    return table_name, logical_form_temp

def simplify_scenario_one(table_name, node1_temp, node2_temp_releation_node) -> list:
    logical_form_temp = []

    logical_form_temp.append(
        {
            "sql": simplify_base_select_no_tmp(
                    node1_temp.name.split('=')[0].strip(),
                    [
                        node1_temp.connections[0].node.name,
                        node2_temp_releation_node.name
                    ],
                    '???'
                )
        }
    )
    
    search_list_temp = []
    for node_temp in node2_temp_releation_node.connections:
        if (node_temp.node.shape == Shape.predicate.value) and (node1_temp.connections[0].node.name != node2_temp_releation_node.name) :
            search_list_temp.append(node2_temp_releation_node.connections[1].node.name)
            modifier_list_temp = node2_temp_releation_node.connections[1].name
            continue
        
        if (node_temp.node.shape == Shape.predicate.value) and (node1_temp.connections[0].node.name == node2_temp_releation_node.name):
            modifier_list_temp = ''
            dd("新的情境")

    logical_form_temp.append(
        {
            "sql": simplify_join_where(
                    node2_temp_releation_node.name,
                    node2_temp_releation_node.connections[0].node.name,
                    node2_temp_releation_node.connections[0].name,
                    'AND ???'
                )
        }
    )
    
    logical_form_temp[-1]['sql'] = logical_form_temp[-1]['sql'].replace("AND ???", '???')

    logical_form_temp.append(
        {
            "sql": simplify_connect_to_predicate(
                    search_list_temp
                )
        }
    )

    return table_name, logical_form_temp

def scenario_one(table_name, node1_temp, node2_temp_releation_node) -> list:
    logical_form_temp = []

    (table_name, sub_query_temp1) = build_sub_query(table_name, node2_temp_releation_node.connections[0].node.name)
    (table_name, sub_query_temp2) = build_sub_query(table_name, node2_temp_releation_node.name)
    (table_name, sub_query_temp3) = build_sub_query(table_name, node2_temp_releation_node.connections[1].node.name)

    logical_form_temp.append(
        {
            "sql": base_select(
                    table_name['mapping'][node1_temp.connections[0].node.name] + '.' + node1_temp.name.split('=')[0].strip(),   
                    [
                        sub_query_temp1,
                        sub_query_temp2,
                        sub_query_temp3
                    ],
                    '???'
                )
        }
    )

    logical_form_temp.append(
        {
            "sql": join_where(
                    table_name['mapping'][node2_temp_releation_node.name],
                    table_name['mapping'][node2_temp_releation_node.connections[0].node.name],
                    node2_temp_releation_node.connections[0].name,
                    table_name['mapping'][node2_temp_releation_node.connections[1].node.name],
                    node2_temp_releation_node.connections[1].name,
                    '???'
                )
        }
    )

    node2_temp_connect_predicate_node = []

    for node_temp in node2_temp_releation_node.connections[1].node.connections:
        if node_temp.node.shape == Shape.predicate.value:
            node2_temp_connect_predicate_node.append(node_temp.node)

    if len(node2_temp_connect_predicate_node) == 0:
        raise Exception("沒有連接到橢圓形")

    search_list_temp = []

    for node_temp in node2_temp_connect_predicate_node:
        search_list_temp.append(node_temp.name)

    logical_form_temp.append(
        {
            "sql": entity_connect_to_predicate(
                    table_name['mapping'][node2_temp_releation_node.connections[1].node.name],
                    search_list_temp
                )
        }
    )

    return table_name, logical_form_temp

def scenario_range(table_name, node1_temp, node2_temp_releation_node) -> list:
    logical_form_temp = []

    (table_name, sub_query_temp1) = build_sub_query(table_name, node2_temp_releation_node.connections[0].node.name)
    (table_name, sub_query_temp2) = build_sub_query(table_name, node2_temp_releation_node.name)
    (table_name, sub_query_temp3) = build_sub_query(table_name, node2_temp_releation_node.connections[1].node.name)

    logical_form_temp.append(
        {
            "sql": base_select(
                    table_name['mapping'][node1_temp.connections[0].node.name] + '.' + node1_temp.name.split('=')[0].strip(),   
                    [
                        sub_query_temp1
                    ],
                    '???'
                )
        }
    )

    search_list_temp = []

    for node_temp in node2_temp_releation_node.connections[1].node.connections:
        if node_temp.node.shape == Shape.predicate.value:
            search_list_temp.append(node_temp.node.name)

    if len(search_list_temp) == 0 :
        search_list_temp = None

    logical_form_temp.append(
        {
            "sql": where_not_exists(
                    sub_query_temp3,
                    table_name['mapping'][node2_temp_releation_node.connections[1].node.name],
                    search_list_temp,
                    None,
                    '???'
                )
        }
    )

    logical_form_temp.append(
        {
            "sql": where_not_exists(
                    sub_query_temp2,
                    table_name['mapping'][node2_temp_releation_node.name],
                    None,
                    [
                        {
                            'table1': table_name['mapping'][node2_temp_releation_node.name],
                            'column1': node2_temp_releation_node.connections[0].name,
                            'table2': table_name['mapping'][node2_temp_releation_node.connections[0].node.name],
                            'column2': node2_temp_releation_node.connections[0].name,
                        },
                        {
                            'table1':  table_name['mapping'][node2_temp_releation_node.name],
                            'column1': node2_temp_releation_node.connections[1].name,
                            'table2': table_name['mapping'][node2_temp_releation_node.connections[1].node.name],
                            'column2': node2_temp_releation_node.connections[1].name,
                        }
                    ],
                )
        }
    )

    return table_name, logical_form_temp

def scenario_three(table_name, node1_temp, node2_temp_releation_node) -> list:
    logical_form_temp = []

    (table_name, sub_query_temp1) = build_sub_query(table_name, node2_temp_releation_node.connections[0].node.name)
    (table_name, sub_query_temp2) = build_sub_query(table_name, node2_temp_releation_node.name)
    (table_name, sub_query_temp3) = build_sub_query(table_name, node2_temp_releation_node.connections[1].node.name)

    logical_form_temp.append(
        {
            "sql": base_select(
                    table_name['mapping'][node1_temp.connections[0].node.name] + '.' + node1_temp.name.split('=')[0].strip(),
                    [
                        sub_query_temp1
                    ],
                    '???'
                )
        }
    )

    search_list_temp = []

    for node_temp in node2_temp_releation_node.connections[1].node.connections:
        if node_temp.node.shape == Shape.predicate.value:
            search_list_temp.append(node_temp.node.name)

    logical_form_temp.append(
        {
            "sql": where_not_exists(
                    sub_query_temp3,
                    table_name['mapping'][node2_temp_releation_node.connections[1].node.name],
                    search_list_temp,
                    None,
                    '???'
                )
        }
    )

    logical_form_temp.append(
        {
            "sql": where_exists(
                    sub_query_temp2,
                    table_name['mapping'][node2_temp_releation_node.name],
                    None,
                    [
                        {
                            'table1': table_name['mapping'][node2_temp_releation_node.name],
                            'column1': node2_temp_releation_node.connections[0].name,
                            'table2': table_name['mapping'][node2_temp_releation_node.connections[0].node.name],
                            'column2': node2_temp_releation_node.connections[0].name,
                        },
                        {
                            'table1':  table_name['mapping'][node2_temp_releation_node.name],
                            'column1': node2_temp_releation_node.connections[1].name,
                            'table2': table_name['mapping'][node2_temp_releation_node.connections[1].node.name],
                            'column2': node2_temp_releation_node.connections[1].name,
                        }
                    ],
                )
        }
    )

    return table_name, logical_form_temp

def simplify_scenario_not(table_name, node1_temp, node2_temp_releation_node) -> list:
    logical_form_temp = []

    logical_form_temp.append(
        {
            "sql": simplify_base_select_no_tmp(
                    node1_temp.name.split('=')[0].strip(),
                    [
                        node1_temp.connections[0].node.name,
                    ],
                    '???'
                )
        }
    )
    
    search_list_temp = []
    for node_temp in node2_temp_releation_node.connections:
        if node_temp.node.shape == Shape.predicate.value:
            search_list_temp.append(node_temp.node.name)

    if len(search_list_temp) == 0 :
        search_list_temp = None

    logical_form_temp.append(
        {
            "sql": simplify_where_not_exists(
                    node2_temp_releation_node.name,
                    None,
                    None,
                    [
                        {
                            'table1': node2_temp_releation_node.name,
                            'column1': node2_temp_releation_node.connections[0].name,
                            'table2': node2_temp_releation_node.connections[0].node.name,
                            'column2': node2_temp_releation_node.connections[0].name,
                        }
                    ],
                    '???'
                )
        }
    )

    logical_form_temp[-1]['sql'] = logical_form_temp[-1]['sql'].replace("AND ???", '???')

    logical_form_temp.append(
        {
            "sql": simplify_connect_to_predicate(
                    search_list_temp
                )
        }
    )

    return table_name, logical_form_temp

def simplify_rec_scenario_one(table_name, node1_temp, node1_temp_entity_node) -> list:
    logical_form_temp = []

    logical_form_temp.append(
        {
            "sql": simplify_base_select(
                    node1_temp.name.split('=')[0].strip(),

                    [
                        node1_temp.connections[0].node.name,
                    ],
                    '???'
                )
        }
    )

    search_list_temp = []

    for node_temp in node1_temp_entity_node.connections:
        if node_temp.node.shape == Shape.predicate.value:
            search_list_temp.append(node_temp.node.name)

    if len(search_list_temp) == 0:
        raise Exception("沒有連接到橢圓形")

    logical_form_temp.append(
        {
            "sql": simplify_connect_to_predicate(
                    search_list_temp
                )
        }
    )
   
    logical_form_temp[-1]['sql'] = logical_form_temp[-1]['sql'].replace(" AND", '', 1)

    return table_name, logical_form_temp

def simplify_primary_key_scenario_one(table_name, node1_temp, node1_temp_diamond_node) -> list:
    logical_form_temp = []

    logical_form_temp.append(
        {
            "sql": simplify_base_select(
                    node1_temp.name.split('=')[0].strip(),

                    [
                        node1_temp.connections[0].node.name,
                    ],
                    '???'
                )
        }
    )

    search_list_temp = []

    for node_temp in node1_temp_diamond_node.connections:
        if node_temp.node.shape == Shape.predicate.value:
            search_list_temp.append(node_temp.node.name)

    if len(search_list_temp) == 0:
        raise Exception("沒有連接到橢圓形")

    logical_form_temp.append(
        {
            "sql": simplify_connect_to_predicate(
                    search_list_temp
                )
        }
    )

    logical_form_temp[-1]['sql'] = logical_form_temp[-1]['sql'].replace(" AND", '', 1)

    return table_name, logical_form_temp

def simplify_primary_key_scenario_basic(table_name, node1_temp, node2_temp, node3_temp) -> list: 
    logical_form_temp = []

    logical_form_temp.append(
        {
            "sql": simplify_base_select_no_tmp(
                    node1_temp.name.split('=')[0].strip(),

                    [
                        node1_temp.connections[0].node.name,
                        node2_temp.connections[0].node.name,
                    ],
                    '???'
                )
        }
    )

    search_list_temp = []
    for node_temp in node2_temp.connections:
        if node_temp.node.shape == Shape.entity.value and node2_temp.connections[0].node.name == node3_temp.name:
            search_list_temp.append(node3_temp.connections[0].node.name)

    logical_form_temp.append(
        {
            "sql": simplify_join_where(
                    node2_temp.name,
                    node2_temp.connections[0].node.name,
                    node2_temp.connections[0].name,
                    'AND ???'
                )
        }
    )

    logical_form_temp[-1]['sql'] = logical_form_temp[-1]['sql'].replace("AND ???", '???')

    if len(search_list_temp) == 0:
        raise Exception("沒有連接到橢圓形")

    logical_form_temp.append(
        {
            "sql": simplify_connect_to_predicate(
                    search_list_temp
                )
        }
    )
    
    return table_name, logical_form_temp

def simplify_primary_key_scenario_range(table_name, node1_temp, node2_temp, node3_temp) -> list: 
    logical_form_temp = []
    
    (table_name, sub_query_temp1) = build_sub_query(table_name, node2_temp.name)
    
    logical_form_temp.append(
        {
            "sql": base_select(
                    node1_temp.name.split('=')[0].strip(),
                    [
                        sub_query_temp1
                    ],
                    '???'
                )
        }
    )

    search_list_temp = []
    for node_temp in node2_temp.connections:
        if node_temp.node.shape == Shape.entity.value:
            if node3_temp:
                dump('總體限量＋特定條件')
                node3, predicate_node = node3_temp[0]

                if predicate_node.shape == Shape.predicate.value:
                    search_list_temp.append(predicate_node.name)


    if len(search_list_temp) == 0 :
        search_list_temp = None

    logical_form_temp.append(
        {
            "sql": simplify_where_not_exists(
                    node_temp.node.name,
                    node2_temp.connections[0].node.name,
                    search_list_temp,
                    None,
                    '???'
                )
        }
    )
    dump(logical_form_temp)

    logical_form_temp.append(
        {
            "sql": simplify_where_not_exists(
                    node2_temp.name,
                    None,
                    None,
                    [
                        {
                            'table1': node2_temp.name,
                            'column1': node2_temp.connections[0].name,
                            'table2': node2_temp.connections[0].node.name,
                            'column2': node2_temp.connections[0].name,
                        },
                        {
                            'table1': node2_temp.name,
                            'column1': node1_temp.name.split('=')[0].strip(),
                            'table2': table_name['mapping'][node2_temp.name],
                            'column2': node1_temp.name.split('=')[0].strip(),
                        }
                    ]
                )
        }
    )
    dump(logical_form_temp)

    logical_form_temp[-1]['sql'] = logical_form_temp[-1]['sql'].replace("AND ???", '???')
    
    return table_name, logical_form_temp


def scenario_five(table_name, node1_temp, node2_temp_releation_node) -> list:
    logical_form_temp = []

    (table_name, sub_query_temp1) = build_sub_query(table_name, node2_temp_releation_node.connections[0].node.name)
    (table_name, sub_query_temp2) = build_sub_query(table_name, node2_temp_releation_node.name)
    (table_name, sub_query_temp3) = build_sub_query(table_name, node2_temp_releation_node.connections[1].node.name)

    logical_form_temp.append(
        {
            "sql": base_select(
                    table_name['mapping'][node1_temp.connections[0].node.name] + '.' + node1_temp.name.split('=')[0].strip(),
                    [
                        sub_query_temp3
                    ],
                    '???'
                )
        }
    )

    search_list_temp = []

    for node_temp in node2_temp_releation_node.connections[0].node.connections:
        if node_temp.node.shape == Shape.predicate.value:
            search_list_temp.append(node_temp.node.name)

    for node_temp in node2_temp_releation_node.connections[1].node.connections:
        if node_temp.node.shape == Shape.predicate.value:
            search_list_temp.append(node_temp.node.name)

    if len(search_list_temp) == 0 :
        search_list_temp = None

    logical_form_temp.append(
        {
            "sql": where_exists(
                    sub_query_temp1,
                    table_name['mapping'][node2_temp_releation_node.connections[0].node.name],
                    search_list_temp,
                    None,
                    '???'
                )
        }
    )

    logical_form_temp.append(
        {
            "sql": where_not_exists(
                    sub_query_temp2,
                    table_name['mapping'][node2_temp_releation_node.name],
                    None,
                    [
                        {
                            'table1': table_name['mapping'][node2_temp_releation_node.name],
                            'column1': node2_temp_releation_node.connections[1].name,
                            'table2': table_name['mapping'][node2_temp_releation_node.connections[1].node.name],
                            'column2': node2_temp_releation_node.connections[1].name,
                        },
                        {
                            'table1':  table_name['mapping'][node2_temp_releation_node.name],
                            'column1': node2_temp_releation_node.connections[0].name,
                            'table2': table_name['mapping'][node2_temp_releation_node.connections[0].node.name],
                            'column2': node2_temp_releation_node.connections[0].name,
                        }
                    ],
                )
        }
    )

    return table_name, logical_form_temp

def get_muti_relation_diamond_node(graph: Graph, node_head: Node) -> list:
    diamond_node_lists = []
    diamond_node_name_temp_list = []

    while node_head != None:
        diamond_node_temp = graph.search_by_shape_to_another_shape_and_name(Shape.diamond.value, Shape.entity.value, node_head.name, diamond_node_name_temp_list)

        if diamond_node_temp == None or len(diamond_node_temp.connections) != 2:
            node_head = None

            continue

        diamond_node_lists.append(diamond_node_temp)
        diamond_node_name_temp_list.append(diamond_node_temp.name)

        node_head = diamond_node_temp.connections[1].node

    return diamond_node_lists

def switch_connections(node: Node) -> Node:
    connection_temp = node.connections[0]
    node.connections[0] = node.connections[1]
    node.connections[1] = connection_temp

    return node

def transfer_sql(logical_form: list) -> str:
    sql = ''
    replace = False

    for form in logical_form:
        for row in form:
            if replace:
                sql = sql.replace("???", row['sql'])
            else:
                sql = row['sql']
            replace = '???' in row['sql']

    return sql

    return [
        [
            {
                "index": '0',
                "sql": base_select('sname', ['suppliers', 'shipments', 'parts'], '???')
            },
            {
                "index": '1',
                "sql": join_where('shipments', 'suppliers', 'sno', 'parts', 'pno', '???')
            },
            {
                "index": '2',
                "sql": entity_connect_to_predicate("parts", "color='red'")
            }
        ]
    ]

import re

def intersect_to_and(sql_query):
    # 提取所有的子查詢
    subqueries = re.findall(r'SELECT .*? FROM .*? WHERE .*?(?= intersect |$)', sql_query, re.IGNORECASE)

    if len(subqueries) != 2:
        return sql_query

    # 提取條件部分
    conditions = []
    for subquery in subqueries:
        where_clause = re.search(r'WHERE (.*)', subquery, re.IGNORECASE)
        if where_clause:
            conditions.append(where_clause.group(1).strip())

    if len(conditions) != 2:
        return sql_query

    # 合併條件
    merged_conditions = f"{conditions[0]} AND {conditions[1]}"

    # 提取主查詢部分
    main_query = re.match(r'(SELECT .*? FROM .*?) WHERE', subqueries[0], re.IGNORECASE).group(1)

    # 生成最終查詢
    final_query = f"{main_query} WHERE {merged_conditions}"
    return final_query

import re

def union_to_or(sql_query):
    subqueries = re.findall(r'SELECT .*? FROM .*? WHERE .*?(?= union |$)', sql_query, re.IGNORECASE)

    if len(subqueries) < 2:
        return sql_query

    conditions = []
    for subquery in subqueries:
        where_clause = re.search(r'WHERE (.*)', subquery, re.IGNORECASE)
        if where_clause:
            conditions.append('(' + where_clause.group(1).strip() + ')')

    if len(conditions) < 2:
        return sql_query

    merged_conditions = ' OR '.join(conditions)

    main_query = re.match(r'(SELECT .*? FROM .*?) WHERE', subqueries[0], re.IGNORECASE).group(1)

    final_query = f"{main_query} WHERE {merged_conditions}"
    return final_query

def combine_sql(sql_lists: list, type: str) -> str:
    sql = f" {type} ".join(sql_lists)

    if type == 'merge_or':
        sql = sql.replace(' AND ', ' OR ')

    return sql
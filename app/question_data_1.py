from data_1 import data
from helper.base_define import data_get, dd, dump, print_table_leetcode_style, print_table_result, print_table_result_html
from create_sql import create_sql
from pymssql_fun import DatabaseConnection
from tqdm import tqdm

def exec(question: str = 'None', action: str = 'None'):
    db = DatabaseConnection('mssql:1433', 'sa', 'YourStrong!Passw0rd', 'master')

    print_table_leetcode_style(data)

    if question == 'None':
        dump("請輸入您想要查詢的資料: (例如:List suppliers who supply all red parts)")

        text = input(": ")
    else:
        text = question

    pbar = tqdm(total=100, desc="處理進度", dynamic_ncols=True)

    def exit():
        db.close()

        pbar.update(100 - pbar.n)
        pbar.close()

    # text = "List suppliers who supply red parts" # 1 (1 2) okkkkk
    # SELECT DISTINCT T1.sname FROM shipments T0, suppliers T1, parts T2 WHERE T0.sno = T1.sno AND T0.pno = T2.pno AND T2.color='red'

    # text = "List suppliers who supply green parts" # 1-1 okkkkk
    # SELECT DISTINCT T1.sname FROM shipments T0, suppliers T1, parts T2 WHERE T0.sno = T1.sno AND T0.pno = T2.pno AND T2.color='green'

    # text = "List the number of suppliers who supply green parts." # 1-2 okkkkk
    # (優化情境) SELECT DISTINCT sno FROM shipments, parts WHERE shipments.pno = parts.pno  AND color='green'
    # (優化情境更新) SELECT DISTINCT sno FROM shipments, parts WHERE shipments.pno = parts.pno  AND parts.color='green'

    # text = "List suppliers who do not supply red parts" # 2 (1 3) okkkkk
    # SELECT DISTINCT T0.sname FROM suppliers T0 WHERE NOT EXISTS ( SELECT 1 FROM parts T2 WHERE T2.color='red' AND EXISTS ( SELECT 1 FROM shipments T1 WHERE T1.sno = T0.sno AND T1.pno = T2.pno ) )

    # text = "List suppliers who do not supply part P2" # 2 okkkkk
    # SELECT DISTINCT T0.sname FROM suppliers T0 WHERE NOT EXISTS ( SELECT 1 FROM shipments T1 WHERE T1.sno = T0.sno AND T1.pno='P2' )

    # text = "List suppliers who supply all parts" # 3 okkkkk
    # SELECT DISTINCT T0.sname FROM suppliers T0 WHERE NOT EXISTS ( SELECT 1 FROM parts T2 WHERE NOT EXISTS ( SELECT 1 FROM shipments T1 WHERE T1.sno = T0.sno AND T1.pno = T2.pno ) )

    # text = "List suppliers who supply all red parts" # 3-1 (1 1) okkkkk
    # SELECT DISTINCT T0.sname FROM suppliers T0 WHERE NOT EXISTS ( SELECT 1 FROM parts T2 WHERE T2.color='red' AND NOT EXISTS ( SELECT 1 FROM shipments T1 WHERE T1.sno = T0.sno AND T1.pno = T2.pno ) )

    # text = "List the number of suppliers who supply all parts." # 3-2 okkkkk
    #  (優化情境) SELECT DISTINCT sno FROM shipments T0 WHERE  NOT EXISTS ( SELECT 1 FROM parts WHERE  NOT EXISTS ( SELECT 1 FROM shipments WHERE shipments.pno = parts.pno AND shipments.sno = T0.sno ) )

    # text = "List the number of suppliers who supply all green parts." # 3-2 okkkkk
    #  (優化情境) SELECT DISTINCT sno FROM shipments T0 WHERE  NOT EXISTS ( SELECT 1 FROM parts WHERE parts.color='green' AND  NOT EXISTS ( SELECT 1 FROM shipments WHERE shipments.pno = parts.pno AND shipments.sno = T0.sno ) )

    # text = "List suppliers who supply all red parts or are not located in Paris" # 3-2 (1 1-1) okkkkk
    # SELECT DISTINCT T0.sname FROM suppliers T0 WHERE NOT EXISTS ( SELECT 1 FROM parts T2 WHERE T2.color='red' AND NOT EXISTS ( SELECT 1 FROM shipments T1 WHERE T1.sno = T0.sno AND T1.pno = T2.pno ) ) union SELECT DISTINCT T0.sname FROM suppliers T0 WHERE  T0.city != 'Paris'

    #text = "List suppliers who supply all red parts and are not located in Paris." # 3-3 okkkkk
    #SELECT DISTINCT T0.sname FROM suppliers T0 WHERE NOT EXISTS ( SELECT 1 FROM parts T2 WHERE T2.color='red' AND NOT EXISTS ( SELECT 1 FROM shipments T1 WHERE T1.sno = T0.sno AND T1.pno = T2.pno ) ) INTERSECT SELECT DISTINCT T0.sname FROM suppliers T0 WHERE  T0.city != 'Paris'
    # SELECT DISTINCT T0.sname FROM suppliers T0 WHERE NOT EXISTS ( SELECT 1 FROM parts T2 WHERE T2.color='red' AND NOT EXISTS ( SELECT 1 FROM shipments T1 WHERE T1.sno = T0.sno AND T1.pno = T2.pno ) ) AND T0.city != 'Paris'


    # text = "List suppliers who do not supply all parts" # 4 okkkkk
    # SELECT DISTINCT T2.sname FROM suppliers T2 WHERE EXISTS ( SELECT 1 FROM parts T0 WHERE NOT EXISTS ( SELECT 1 FROM shipments T1 WHERE T1.sno = T2.sno AND T1.pno = T0.pno ) )

    # text = "List suppliers who do not supply all red parts" # 4-1 okkkkk
    # SELECT DISTINCT T2.sname FROM suppliers T2 WHERE EXISTS ( SELECT 1 FROM parts T0 WHERE T0.color='red' AND NOT EXISTS ( SELECT 1 FROM shipments T1 WHERE T1.sno = T2.sno AND T1.pno = T0.pno ) )

    # text = "List suppliers who do not supply all blue parts" # 4-1 okkkkk
    # SELECT DISTINCT T2.sname FROM suppliers T2 WHERE EXISTS ( SELECT 1 FROM parts T0 WHERE T0.color='blue' AND NOT EXISTS ( SELECT 1 FROM shipments T1 WHERE T1.sno = T2.sno AND T1.pno = T0.pno ) )

    # text = "List the number of suppliers who do not supply all parts." # 4-2   (待檢查)
    # SELECT DISTINCT T2.sno FROM suppliers T2 WHERE  EXISTS ( SELECT 1 FROM parts T0 WHERE  NOT EXISTS ( SELECT 1 FROM shipments T1 WHERE T1.sno = T2.sno AND T1.pno = T0.pno ) )

    # text = "List the number of suppliers who do not supply all green parts." # 4-2   (待檢查)
    # SELECT DISTINCT T2.sno FROM suppliers T2 WHERE  EXISTS ( SELECT 1 FROM parts T0 WHERE T0.color='green' AND  NOT EXISTS ( SELECT 1 FROM shipments T1 WHERE T1.sno = T2.sno AND T1.pno = T0.pno ) )

    # text = "List parts that are supplied by the suppliers." # 5
    #

    # text = "List the parts that are supplied by London supplier" # 5-1 (待修正: LF 錯誤)
    # SELECT DISTINCT T2.pname FROM shipments T0, suppliers T1, parts T2 WHERE T0.sno = T1.sno AND T0.pno = T2.pno AND T1.city='London'

    # text = "List parts that are supplied by the supplier named Clark" # 5-1  (待修正: LF 錯誤)
    # SELECT DISTINCT T2.pname FROM shipments T0, suppliers T1, parts T2 WHERE T0.sno = T1.sno AND T0.pno = T2.pno AND T1.sname='Clark'
    
    # text = "List parts which are supplied by Bolt." # 5-1
    # 

    # text = "List parts which are supplied by S1" # 5-2   （待修正：不需暫存表）
    # SELECT DISTINCT T0.pname FROM parts T0 WHERE EXISTS ( SELECT 1 FROM shipments T1 WHERE T1.pno = T0.pno AND T1.sno='S1' )
    # (優化情境)  SELECT DISTINCT pname FROM parts, shipments WHERE shipments.pno = parts.pno  AND sno='S1'
    # (優化情境更新)  SELECT DISTINCT pname FROM parts, shipments WHERE shipments.pno = parts.pno  AND shipments.sno='S1'

    # text = "List the number of parts which are supplied by S4." # 5-2   okkkkk
    # (優化情境) SELECT pno FROM shipments WHERE  sno='S4'

    # text = "List the number of parts which are supplied by Blake." # 5-2   okkkkk
    # (優化情境) SELECT DISTINCT pno FROM shipments, suppliers WHERE shipments.sno = suppliers.sno  AND sname='Blake'

    # text = "List the number of parts that are supplied by the supplier named Clark." # 5-2   okkkkk
    # (優化情境) SELECT DISTINCT pno FROM shipments, suppliers WHERE shipments.sno = suppliers.sno  AND sname='Clark'


    # text = "List parts that are not supplied by Smith" # 6  okkkkk
    # SELECT DISTINCT T0.pname FROM parts T0 WHERE  NOT EXISTS ( SELECT 1 FROM suppliers T2 WHERE T2.sname='Smith' AND EXISTS ( SELECT 1 FROM shipments T1 WHERE T1.pno = T0.pno AND T1.sno = T2.sno ) )

    # text = "List parts that are not supplied by Jones" # 6  okkkkk
    # SELECT DISTINCT T0.pname FROM parts T0 WHERE  NOT EXISTS ( SELECT 1 FROM suppliers T2 WHERE T2.sname='Jones' AND EXISTS ( SELECT 1 FROM shipments T1 WHERE T1.pno = T0.pno AND T1.sno = T2.sno ) )

    # text = "List the number of parts that are not supplied by Jones." # 6-2
    #   

    # text = "List parts that are supplied by all suppliers" # 7  (待修正: LF 錯誤)
    # SELECT DISTINCT T0.pname FROM parts T0 WHERE NOT EXISTS ( SELECT 1 FROM suppliers T2 WHERE NOT EXISTS ( SELECT 1 FROM shipments T1 WHERE T1.pno = T0.pno AND T1.sno = T2.sno ) )
    
    # text = "List the number of parts that are supplied by all suppliers." # 7-2  okkkkk
    # (優化情境) SELECT DISTINCT pno FROM shipments T0 WHERE  NOT EXISTS ( SELECT 1 FROM suppliers WHERE  NOT EXISTS ( SELECT 1 FROM shipments WHERE shipments.sno = suppliers.sno AND shipments.pno = T0.pno ) )

    # text = "List the parts that are not supplied by all suppliers" # 8  okkkkk
    # SELECT DISTINCT T2.pname FROM parts T2 WHERE EXISTS ( SELECT 1 FROM suppliers T0 WHERE NOT EXISTS ( SELECT 1 FROM shipments T1 WHERE T1.pno = T2.pno AND T1.sno = T0.sno ) )

    # text = "List the part numbers which are not supplied by all suppliers." # 8-2  (待檢查)
    # SELECT DISTINCT T2.pno FROM parts T2 WHERE  EXISTS ( SELECT 1 FROM suppliers T0 WHERE  NOT EXISTS ( SELECT 1 FROM shipments T1 WHERE T1.pno = T2.pno AND T1.sno = T0.sno ) )
    
    # text = "List the number of  parts which are not supplied by all London suppliers." # 8-2  (待檢查)
    # SELECT DISTINCT T2.pno FROM parts T2 WHERE  EXISTS ( SELECT 1 FROM suppliers T0 WHERE T0.city='London' AND  NOT EXISTS ( SELECT 1 FROM shipments T1 WHERE T1.pno = T2.pno AND T1.sno = T0.sno ) )





    ## 單表提取

    # text = "List the name of suppliers that are located in London" # 1 okkkkk
    # SELECT DISTINCT T0.sname FROM suppliers T0 WHERE  T0.city='London'

    # text = "List the suppliers who are located in London" # 1 okkkkk
    # SELECT DISTINCT T0.sname FROM suppliers T0 WHERE  T0.city='London'

    # text = "List the number of suppliers that are located in London." # 1 okkkkk
    # SELECT DISTINCT T0.sno FROM suppliers T0 WHERE  T0.city='London'

    # text = "List suppliers whose locations are not in Paris" # 4 okkkkk
    # text = "List suppliers who are not located in Paris" # 4 okkkkk
    # SELECT DISTINCT T0.sname FROM suppliers T0 WHERE T0.city != 'Paris'

    # text = "List parts that are stored in Rome." # 5 okkkkk
    # SELECT DISTINCT T0.pname FROM parts T0 WHERE  T0.city='Rome'

    # text = "List the number of parts that are stored in London." # 5-1 okkkkk
    # SELECT DISTINCT T0.pno FROM parts T0 WHERE  T0.city='London'

    # text = "List parts that are stored in Rome and are blue." # 5-2 okkkkk
    # SELECT DISTINCT T0.pname FROM parts T0 WHERE T0.city='Rome' AND T0.color='blue'

    # text = "List part numbers that are stored in Rome." # ok ， 單欄位 5，若改成 the number of parts 就可以執行
    # SELECT DISTINCT T0.pno FROM parts T0 WHERE  T0.city='Rome'

    # text = "List the number of parts whose stored in Paris"
    # SELECT DISTINCT T0.pno FROM parts T0 WHERE  T0.city='Paris'

    # text = "List the number of parts whose color are blue and are stored in Paris." # ok
    # SELECT DISTINCT T0.pno FROM parts T0 WHERE  T0.color='blue' intersect SELECT DISTINCT T0.pno FROM parts T0 WHERE  T0.city='Paris'

    # text = "list suppliers who supply part P2"
    # SELECT DISTINCT T0.sname FROM suppliers T0 WHERE  EXISTS ( SELECT 1 FROM shipments T1 WHERE T1.sno = T0.sno AND T1.pno='P2' )

    # text = "list the city of suppliers who supply part P5"
    # SELECT DISTINCT T0.city FROM suppliers T0 WHERE  EXISTS ( SELECT 1 FROM shipments T1 WHERE T1.sno = T0.sno AND T1.pno='P5' )

    # text = 'list the status of suppliers who supply part P5'
    # SELECT DISTINCT T0.status FROM suppliers T0 WHERE  EXISTS ( SELECT 1 FROM shipments T1 WHERE T1.sno = T0.sno AND T1.pno='P5' )

    # text = 'list the number of suppliers who supply part P2'
    # SELECT sno FROM shipments WHERE  pno='P2'

    # text = 'List the supplier numbers that supply part P2'
    # SELECT sno FROM shipments WHERE  pno='P2'

    pbar.update(10)
    dump(f"處理進度: 查詢（問題）...")

    if action == '詞性分析':
        exit

        return create_sql(data, text, pbar, action)

    if action == '轉換後的 SQL':
        exit

        return create_sql(data, text, pbar, action)

    if action == 'SQL 的執行結果':
        result = db.query(text)
        exit

        if result['success']:
            return print_table_result_html(result)

    sql = create_sql(data, text, pbar, action)

    dump("處理進度: 產生以下 sql")
    tqdm.write(" ")
    tqdm.write("'" + 'sql: ' + sql + "'")
    tqdm.write(" ")

    result = db.query(sql)

    dump("以下為SQL執行結果")
    print_table_result(result, pbar)
    tqdm.write(" ")

    exit

if __name__ == '__main__':
    exec()
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

    # text = "List suppliers who supply red parts" 
    # SELECT DISTINCT T1.sname FROM (SELECT * FROM shipments) T0, (SELECT * FROM suppliers) T1, (SELECT * FROM parts) T2 WHERE T0.sno = T1.sno AND T0.pno = T2.pno AND T2.color='red'

    # text = "List suppliers who supply green parts" 
    # SELECT DISTINCT T1.sname FROM (SELECT * FROM shipments) T0, (SELECT * FROM suppliers) T1, (SELECT * FROM parts) T2 WHERE T0.sno = T1.sno AND T0.pno = T2.pno AND T2.color='green'

    # text = "List the number of suppliers who supply green parts." 
    # SELECT DISTINCT T1.sno FROM (SELECT * FROM shipments) T0, (SELECT * FROM suppliers) T1, (SELECT * FROM parts) T2 WHERE T0.sno = T1.sno AND T0.pno = T2.pno AND T2.color='green'

    # text = "List suppliers who do not supply red parts" 
    # SELECT DISTINCT T0.sname FROM (SELECT * FROM suppliers) T0 WHERE NOT EXISTS ( SELECT 1 FROM (SELECT * FROM parts) T2 WHERE T2.color='red' AND EXISTS ( SELECT 1 FROM (SELECT * FROM shipments) T1 WHERE T1.sno = T0.sno AND T1.pno = T2.pno ) )

    # text = "List suppliers who do not supply part P2" 
    # SELECT DISTINCT T0.sname FROM (SELECT * FROM suppliers) T0 WHERE NOT EXISTS ( SELECT 1 FROM (SELECT * FROM shipments) T1 WHERE T1.sno = T0.sno AND T1.pno='P2' )


    # text = "List suppliers who supply all parts" 
    # SELECT DISTINCT T0.sname FROM (SELECT * FROM suppliers) T0 WHERE NOT EXISTS ( SELECT 1 FROM (SELECT * FROM parts) T2 WHERE NOT EXISTS ( SELECT 1 FROM (SELECT * FROM shipments) T1 WHERE T1.sno = T0.sno AND T1.pno = T2.pno ) )

    # text = "List suppliers who supply all red parts" 
    # SELECT DISTINCT T0.sname FROM (SELECT * FROM suppliers) T0 WHERE NOT EXISTS ( SELECT 1 FROM (SELECT * FROM parts) T2 WHERE T2.color='red' AND NOT EXISTS ( SELECT 1 FROM (SELECT * FROM shipments) T1 WHERE T1.sno = T0.sno AND T1.pno = T2.pno ) )

    # text = "List suppliers who supply all red parts or are not located in Paris" 
    # SELECT DISTINCT T0.sname FROM (SELECT * FROM suppliers) T0 WHERE NOT EXISTS ( SELECT 1 FROM (SELECT * FROM parts) T2 WHERE T2.color='red' AND NOT EXISTS ( SELECT 1 FROM (SELECT * FROM shipments) T1 WHERE T1.sno = T0.sno AND T1.pno = T2.pno ) ) union SELECT DISTINCT T0.sname FROM (SELECT * FROM suppliers) T0 WHERE  T0.city != 'Paris'

    #text = "List suppliers who supply all red parts and are not located in Paris." 
    #SELECT DISTINCT T0.sname FROM (SELECT * FROM suppliers) T0 WHERE NOT EXISTS ( SELECT 1 FROM (SELECT * FROM parts) T2 WHERE T2.color='red' AND NOT EXISTS ( SELECT 1 FROM (SELECT * FROM shipments) T1 WHERE T1.sno = T0.sno AND T1.pno = T2.pno ) ) INTERSECT SELECT DISTINCT T0.sname FROM (SELECT * FROM suppliers) T0 WHERE  T0.city != 'Paris'
    # SELECT DISTINCT T0.sname FROM (SELECT * FROM suppliers) T0 WHERE NOT EXISTS ( SELECT 1 FROM (SELECT * FROM parts) T2 WHERE T2.color='red' AND NOT EXISTS ( SELECT 1 FROM (SELECT * FROM shipments) T1 WHERE T1.sno = T0.sno AND T1.pno = T2.pno ) ) AND T0.city != 'Paris'


    # text = "List suppliers who do not supply all parts" 
    # SELECT DISTINCT T2.sname FROM (SELECT * FROM suppliers) T2 WHERE EXISTS ( SELECT 1 FROM (SELECT * FROM parts) T0 WHERE NOT EXISTS ( SELECT 1 FROM (SELECT * FROM shipments) T1 WHERE T1.sno = T2.sno AND T1.pno = T0.pno ) )

    # text = "List suppliers who do not supply all red parts" 
    # SELECT DISTINCT T2.sname FROM (SELECT * FROM suppliers) T2 WHERE EXISTS ( SELECT 1 FROM (SELECT * FROM parts) T0 WHERE T0.color='red' AND NOT EXISTS ( SELECT 1 FROM (SELECT * FROM shipments) T1 WHERE T1.sno = T2.sno AND T1.pno = T0.pno ) )

    # text = "List suppliers who do not supply all blue parts" 
    # SELECT DISTINCT T2.sname FROM (SELECT * FROM suppliers) T2 WHERE EXISTS ( SELECT 1 FROM (SELECT * FROM parts) T0 WHERE T0.color='blue' AND NOT EXISTS ( SELECT 1 FROM (SELECT * FROM shipments) T1 WHERE T1.sno = T2.sno AND T1.pno = T0.pno ) )


    # text = "List the parts that are supplied by London supplier" 
    # SELECT DISTINCT T2.pname FROM (SELECT * FROM shipments) T0, (SELECT * FROM suppliers) T1, (SELECT * FROM parts) T2 WHERE T0.sno = T1.sno AND T0.pno = T2.pno AND T1.city='London'

    # text = "List parts that are supplied by the supplier named Clark" 
    # SELECT DISTINCT T2.pname FROM (SELECT * FROM shipments) T0, (SELECT * FROM suppliers) T1, (SELECT * FROM parts) T2 WHERE T0.sno = T1.sno AND T0.pno = T2.pno AND T1.sname='Clark'

    # text = "List parts which are supplied by S1" 
    # SELECT DISTINCT T0.pname FROM (SELECT * FROM parts) T0 WHERE EXISTS ( SELECT 1 FROM (SELECT * FROM shipments) T1 WHERE T1.pno = T0.pno AND T1.sno='S1' )


    # text = "List parts that are not supplied by Smith" 
    # SELECT DISTINCT T0.pname FROM (SELECT * FROM parts) T0 WHERE  NOT EXISTS ( SELECT 1 FROM (SELECT * FROM suppliers) T2 WHERE T2.sname='Smith' AND EXISTS ( SELECT 1 FROM (SELECT * FROM shipments) T1 WHERE T1.pno = T0.pno AND T1.sno = T2.sno ) )

    # text = "List parts that are not supplied by Jones" 
    # SELECT DISTINCT T0.pname FROM (SELECT * FROM parts) T0 WHERE  NOT EXISTS ( SELECT 1 FROM (SELECT * FROM suppliers) T2 WHERE T2.sname='Jones' AND EXISTS ( SELECT 1 FROM (SELECT * FROM shipments) T1 WHERE T1.pno = T0.pno AND T1.sno = T2.sno ) )

    # text = "List parts that are supplied by all suppliers" 
    # SELECT DISTINCT T0.pname FROM (SELECT * FROM parts) T0 WHERE NOT EXISTS ( SELECT 1 FROM (SELECT * FROM suppliers) T2 WHERE NOT EXISTS ( SELECT 1 FROM (SELECT * FROM shipments) T1 WHERE T1.pno = T0.pno AND T1.sno = T2.sno ) )

    # text = "List the parts that are not supplied by all suppliers" 
    # SELECT DISTINCT T2.pname FROM (SELECT * FROM parts) T2 WHERE EXISTS ( SELECT 1 FROM (SELECT * FROM suppliers) T0 WHERE NOT EXISTS ( SELECT 1 FROM (SELECT * FROM shipments) T1 WHERE T1.pno = T2.pno AND T1.sno = T0.sno ) )





    ## 單表提取

    # text = "List the name of suppliers that are located in London" 
    # SELECT DISTINCT T0.sname FROM (SELECT * FROM suppliers) T0 WHERE  T0.city='London'

    # text = "List the suppliers who are located in London" 
    # SELECT DISTINCT T0.sname FROM (SELECT * FROM suppliers) T0 WHERE  T0.city='London'

    # text = "List the number of suppliers that are located in London." 
    # SELECT DISTINCT T0.sno FROM (SELECT * FROM suppliers) T0 WHERE  T0.city='London'

    # text = "List suppliers whose locations are not in Paris" 
    # text = "List suppliers who are not located in Paris" 
    # SELECT DISTINCT T0.sname FROM (SELECT * FROM suppliers) T0 WHERE T0.city != 'Paris'

    # text = "List parts that are stored in Rome." 
    # SELECT DISTINCT T0.pname FROM (SELECT * FROM parts) T0 WHERE  T0.city='Rome'

    # text = "List the number of parts that are stored in London." 
    # SELECT DISTINCT T0.pno FROM (SELECT * FROM parts) T0 WHERE  T0.city='London'

    # text = "List parts that are stored in Rome and are blue." 
    # SELECT DISTINCT T0.pname FROM (SELECT * FROM parts) T0 WHERE T0.city='Rome' AND T0.color='blue'

    # text = "List part numbers that are stored in Rome." 
    # SELECT DISTINCT T0.pno FROM parts T0 WHERE  T0.city='Rome'

    # text = "List the number of parts whose stored in Paris"
    # SELECT DISTINCT T0.pno FROM parts T0 WHERE  T0.city='Paris'

    # text = "List the number of parts whose color are blue and are stored in Paris." 
    # SELECT DISTINCT T0.pno FROM parts T0 WHERE  T0.color='blue' intersect SELECT DISTINCT T0.pno FROM parts T0 WHERE  T0.city='Paris'

    # text = "list suppliers who supply part P2"
    # SELECT DISTINCT T0.sname FROM suppliers T0 WHERE  EXISTS ( SELECT 1 FROM shipments T1 WHERE T1.sno = T0.sno AND T1.pno='P2' )

    # text = "list the city of suppliers who supply part P5"
    # SELECT DISTINCT T0.city FROM suppliers T0 WHERE  EXISTS ( SELECT 1 FROM shipments T1 WHERE T1.sno = T0.sno AND T1.pno='P5' )

    # text = 'list the status of suppliers who supply part P5'
    # SELECT DISTINCT T0.status FROM suppliers T0 WHERE  EXISTS ( SELECT 1 FROM shipments T1 WHERE T1.sno = T0.sno AND T1.pno='P5' )

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
            return print_table_result_html(result['data'])

    sql = create_sql(data, text, pbar, action)

    dump("處理進度: 產生以下 sql")
    tqdm.write(" ")
    tqdm.write("'" + sql + "'")
    tqdm.write(" ")

    result = db.query(sql)

    dump("處理進度: 以下為資料結果")
    print_table_result(result, pbar)

    exit

if __name__ == '__main__':
    exec()
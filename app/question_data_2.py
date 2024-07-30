from data_2 import data
from helper.base_define import data_get, dd, dump, print_table_leetcode_style, print_table_result, print_table_result_html
from create_sql import create_sql
from pymssql_fun import DatabaseConnection
from tqdm import tqdm

def exec(question: str = 'None', action: str = 'None'):
    db = DatabaseConnection('mssql:1433', 'sa', 'YourStrong!Passw0rd', 'master')

    print_table_leetcode_style(data)

    if question == 'None':
        dump("請輸入您想要查詢的資料: (例如:List the students who take the course taught by Frank?)")

        text = input(": ")
    else:
        text = question

    pbar = tqdm(total=100, desc="處理進度", dynamic_ncols=True)

    def exit():
        
        db.close()
        pbar.update(100 - pbar.n)  
        pbar.close()


    # text = "List the students who take the course taught by Frank?" # 1 (1 4)
    # SELECT DISTINCT T1.sname FROM (SELECT * FROM take) T0, (SELECT * FROM student) T1, (SELECT * FROM course) T2, (SELECT * FROM teach) T3, (SELECT * FROM teacher) T4 WHERE T0.sno = T1.sno AND T0.cno = T2.cno AND T3.tno = T4.tno AND T3.cno = T2.cno AND T4.tname='Frank'

    # text = "List the name of teachers who teach DBMS" # 1 okkkkk
    # SELECT DISTINCT T1.tname FROM (SELECT * FROM teach) T0, (SELECT * FROM teacher) T1, (SELECT * FROM course) T2 WHERE T0.tno = T1.tno AND T0.cno = T2.cno AND T2.cname='DBMS'


    #text = "List the name of teachers who do not teach Advanced_DBMS" # 2 okkkkk
    # SELECT DISTINCT T0.tname FROM (SELECT * FROM teacher) T0 WHERE  NOT EXISTS ( SELECT 1 FROM (SELECT * FROM course) T2 WHERE T2.cname='Advanced_DBMS' AND EXISTS ( SELECT 1 FROM (SELECT * FROM teach) T1 WHERE T1.tno = T0.tno AND T1.cno = T2.cno ) )

    # text = 'List the name of teachers who teach all courses.' # 3 okkkkk
    # SELECT DISTINCT T0.tname FROM (SELECT * FROM teacher) T0 WHERE  NOT EXISTS ( SELECT 1 FROM (SELECT * FROM course) T2 WHERE  NOT EXISTS ( SELECT 1 FROM (SELECT * FROM teach) T1 WHERE T1.tno = T0.tno AND T1.cno = T2.cno ) )


    # text = "List the name of teachers who do not teach all courses?" # 4 (2 4) okkkkk
    # SELECT DISTINCT T2.tname FROM (SELECT * FROM teacher) T2 WHERE  EXISTS ( SELECT 1 FROM (SELECT * FROM course) T0 WHERE  NOT EXISTS ( SELECT 1 FROM (SELECT * FROM teach) T1 WHERE T1.tno = T2.tno AND T1.cno = T0.cno ) )

    # text = "List the name of course that are taught by Frank?" # 5 (2 5) okkkkk
    # SELECT DISTINCT T2.cname FROM (SELECT * FROM teach) T0, (SELECT * FROM teacher) T1, (SELECT * FROM course) T2 WHERE T0.tno = T1.tno AND T0.cno = T2.cno  AND T1.tname='Frank'

    # text = "List the courses that are not taught by Annie?" # 6 (2 6) okkkkk
    # SELECT DISTINCT T0.cname FROM (SELECT * FROM course) T0 WHERE NOT EXISTS ( SELECT 1 FROM (SELECT * FROM teacher) T2 WHERE T2.tname='Annie' AND  EXISTS ( SELECT 1 FROM (SELECT * FROM teach) T1 WHERE T1.cno = T0.cno AND T1.tno = T2.tno ) )

    # text = "List the courses that are taught by all teachers?"# 7 (2 7) okkkkk
    # SELECT DISTINCT T0.cname FROM (SELECT * FROM course) T0 WHERE  NOT EXISTS ( SELECT 1 FROM (SELECT * FROM teacher) T2 WHERE  NOT EXISTS ( SELECT 1 FROM (SELECT * FROM teach) T1 WHERE T1.cno = T0.cno AND T1.tno = T2.tno ) )

    # text = "List the courses that are not taught by all teachers?" # 8 (2 8) okkkkk
    # SELECT DISTINCT T2.cname FROM (SELECT * FROM course) T2 WHERE  EXISTS ( SELECT 1 FROM (SELECT * FROM teacher) T0 WHERE NOT EXISTS ( SELECT 1 FROM (SELECT * FROM teach) T1 WHERE T1.cno = T2.cno AND T1.tno = T0.tno ) )

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
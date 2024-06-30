from flask import Flask, jsonify, request, send_from_directory
from helper.base_define import data_get, dd, dump, print_table_leetcode_style, generate_table_html, print_table_result, print_table_result_html
from service.sentence_analysis_service import SentenceAnalysis
import os
from chatbot.chat_gpt import ChatGpt
from chatbot.claude import Claude
from chatbot.google_gemini import GoogleGemini
from chatbot.helper_fun import load_file_content
from pymssql_fun import DatabaseConnection
import spacy
from spacy import displacy

app = Flask(__name__, static_folder='static', static_url_path='/static')

@app.route('/')
def home():
    return send_from_directory(os.getcwd(), 'index.html')

@app.route('/styles.css')
def styles():
    return send_from_directory(os.getcwd(), 'styles.css')

@app.route('/images/<dbname>')
def serve_database_image(dbname):
    filename = f"{dbname}.png"
    return send_from_directory(app.static_folder, filename)

@app.route('/generate_table', methods=['POST'])
def generate_table():
    database = request.json.get("database")
    if database == '資料庫-1':
        from data_1 import data
        from question_example_1 import question_example

    else:
        from data_2 import data
        from question_example_2 import question_example

    html_output = generate_table_html(data)
    return jsonify({"html": html_output, "question_example": question_example})

@app.route('/speech_analysis', methods=['POST'])
def speech_analysis():
    database = request.json.get("database")
    question = request.json.get("question")
    action = request.json.get("action")

    try:
        if database == '資料庫-1':
            from question_data_1 import exec
        else:
            from question_data_2 import exec

        return jsonify(
            {
                "success": True,
                "res": exec(question, action),
            }
        )
    except Exception as e:
        sentence_analysis = SentenceAnalysis()
        sentence_analysis.analyze_sentence(question)

        return jsonify(
            {
                "success": False,
                "res": sentence_analysis.analyze_sentence(question),
            }
        )

@app.route('/get_dependency', methods=['POST'])
def get_dependency_parse():
    question = request.json.get("question")

    if not question:
        return jsonify({"error": "No question provided"}), 400

    nlp = spacy.load("en_core_web_trf")
    doc = nlp(question)
    dep_html = displacy.render(doc, style="dep", page=True)
    
    return jsonify({'html': dep_html})


@app.route('/get_sql', methods=['POST'])
def get_sql():
    database = request.json.get("database")
    question = request.json.get("question")
    action = request.json.get("action")

    if database == '資料庫-1':
        from question_data_1 import exec
    else:
        from question_data_2 import exec

    return jsonify({"res": exec(question, action)})

@app.route('/query', methods=['POST'])
def query():
    database = request.json.get("database")
    question = request.json.get("question")
    action = request.json.get("action")

    if database == '資料庫-1':
        from question_data_1 import exec
    else:
        from question_data_2 import exec

    return jsonify({"res": exec(question, action)})



@app.route('/chatgpt_api', methods=['POST'])
def chat_chatGPT():
    database = request.json.get("database")
    question = request.json.get("question")
    

    if database == '資料庫-1':
        database = 'data_1'
    else:
        database = 'data_2'
    
    chat_gpt = ChatGpt()
    sql = chat_gpt.main(question, database)

    return jsonify({"success": True,"res": sql})

@app.route('/gemini_api', methods=['POST'])
def chat_gemini():
    database = request.json.get("database")
    question = request.json.get("question")
    

    if database == '資料庫-1':
        database = 'data_1'
    else:
        database = 'data_2'
    
    gemini = GoogleGemini()
    sql = gemini.main(question, database)
    
    dump(sql)
    return jsonify({"success": True,"res": sql})

@app.route('/claude_api', methods=['POST'])
def chat_claude():
    database = request.json.get("database")
    question = request.json.get("question")
    

    if database == '資料庫-1':
        database = 'data_1'
    else:
        database = 'data_2'

    claude = Claude()
    sql = claude.main(question, database)
    

    return jsonify({"success": True,"res": sql})

@app.route('/execute_sql', methods=['POST'])
def execute_query():
    database = request.json.get("database")
    sql = request.json.get("sql")
    

    if database == '資料庫-1':
        from question_data_1 import exec
    else:
        from question_data_2 import exec
    
    dump(sql)
    db = DatabaseConnection('mssql:1433', 'sa', 'YourStrong!Passw0rd', 'master')
    result = db.query(sql)
    dump(result)
    if result['success']:
        dump(print_table_result_html(result['data']))
        return jsonify({"res": (print_table_result_html(result['data']))})
    else:
        
        return jsonify({"res": "錯誤！無效 SQL"})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)

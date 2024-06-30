import re, json
import sys, pprint

def clean_json_string(s, add_exception = False):
    if add_exception == True:
        start_index = s.find('"reasoning_process" : "') + 23
        end_index = s.find('",')

        if start_index != -1 and end_index != -1:
            reasoning_process = s[start_index:end_index]
            reasoning_process = reasoning_process.replace('"', "'")
            s = s[:start_index] + reasoning_process + s[end_index:]

        start_index = s.find('"sql": "') + 8
        end_index = s.find('"}')

        if start_index != -1 and end_index != -1:
            reasoning_process = s[start_index:end_index]
            reasoning_process = reasoning_process.replace('"', "'")
            s = s[:start_index] + reasoning_process + s[end_index:]

    return re.sub(r'[\x00-\x1F]+', ' ', s)

def extra_clean_json_string(s, add_exception=False):
    if add_exception:
        patterns = [('"reasoning_process" : "', '",'), ('"sql": "', '"}')]
        for start_marker, end_marker in patterns:
            start_index = s.find(start_marker) + len(start_marker)
            end_index = s.find(end_marker, start_index)
            if start_index != -1 and end_index != -1:
                text_to_replace = s[start_index:end_index]
                s = s[:start_index] + text_to_replace.replace('"', "'") + s[end_index:]

    return re.sub(r'[\x00-\x1F]+', ' ', s)

def data_get(data, path, default = None):
    keys = path.split('.')
    try:
        for key in keys:
            if key.isdigit():
                data = data[int(key)]
            else:
                data = data[key]
        return data
    except (KeyError, TypeError, IndexError):
        return default

def dd(*args):
    for arg in args:
        pprint.pprint(arg, None, 1, 120)
    sys.exit()

def dump(*args):
    for arg in args:
        pprint.pprint(arg, None, 1, 120)

def load_file_content(filename):
    """讀取文件並返回內容"""
    with open(filename, 'r', encoding='utf-8') as file:
        return file.read()

def save_content(data, filepath):
    with open(filepath, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def format_text(data, text):
    return rf""" This is the database and question:
    {data}
    {text}
    ---
    Please reply in json format according to the above structure, without redundant output and escape characters, so that I can get the MS SQL syntax for testing:
    example(No escape characters):

    {{
    "sql": " "
    }}
    """

def is_string(variable):
    return isinstance(variable, str)
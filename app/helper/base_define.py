import sys, pprint
import spacy
import numpy as np
from tqdm import tqdm
import re, json


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
        tqdm.write(pprint.pformat(arg, indent=1, width=120))

nlp = spacy.load("en_core_web_trf")

def similarity(text1, text2):
    text1 = text1.replace("_", ' ')
    text2 = text2.replace("_", ' ')

    vec1 = nlp(text1).vector
    vec2 = nlp(text2).vector

    return vec1.dot(vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def print_table_leetcode_style(data):
    for entity, tables in data.items():
        for table_name, table_data in tables.items():
            print("\n" + f"Table: {table_name}")

            columns = table_data["columns"]
            values = table_data["values"]
            column_widths = [max(len(str(item)) for item in [col] + [row[i] for row in values]) for i, col in enumerate(columns)]

            separator = "+".join(['-' * (width + 2) for width in column_widths])
            print(f"+{separator}+")
            headers = " | ".join([f"{col:<{column_widths[i]}}" for i, col in enumerate(columns)])
            print(f"| {headers} |")
            print(f"+{separator}+")

            for row in values:
                row_str = " | ".join([f"{str(cell):<{column_widths[i]}}" for i, cell in enumerate(row)])
                print(f"| {row_str} |")
            print(f"+{separator}+")

def generate_table_html(data):
    html_output = "<div class='row justify-content-center' style='margin-top: 20px;'>"
    entity_html = "<div class='col-8'>"
    space_html = "<div class='col-md-auto'>"
    diamond_html = "<div class='col-3'>"
    
    for shape, tables in data.items():
        for table_name, table_data in tables.items():
            table_html = f"<h5>{table_name}</h5>"
            columns = table_data["columns"]
            values = table_data["values"]
            
            table_html += "<table class='table table-bordered custom-bordered table-margin'>"
            table_html += "<thead><tr>"
            for col in columns:
                table_html += f"<th class='column-background'>{col}</th>"
            table_html += "</tr></thead>"
            table_html += "<tbody>"
            for row in values:
                table_html += "<tr class='value-background'>"
                for cell in row:
                    table_html += f"<td>{cell}</td>"
                table_html += "</tr>"
            table_html += "</tbody></table>"
            
            if shape == "entity":
                entity_html += table_html
            elif shape == "diamond":
                diamond_html += table_html
    
    entity_html += "</div><br>"
    diamond_html += "</div>"
    space_html += "</div>"
    html_output += entity_html + space_html + diamond_html
    html_output += "</div>"
    return html_output


def print_table_result_html(data):
    columns = data['column']
    values = data['value']

    column_widths = []
    for i, col in enumerate(columns):
        if values:
            max_width = max(len(col), *(len(str(row[i])) for row in values))
        else:
            max_width = len(col)
        column_widths.append(max_width)

    html_output = "<table class='table table-bordered'>"

    html_output += "<thead><tr>"
    for col in columns:
        html_output += f"<th>{col}</th>"
    html_output += "</tr></thead>"

    html_output += "<tbody>"
    if values:
        for row in values:
            html_output += "<tr>"
            for cell in row:
                html_output += f"<td>{cell}</td>"
            html_output += "</tr>"
    else:
        html_output += "<tr>"
        for width in column_widths:
            html_output += f"<td>{' ' * width}</td>"
        html_output += "</tr>"
    html_output += "</tbody></table>"

    return html_output

def print_table_result(data, pbar):
    columns = data['column']
    values = data['value']

    column_widths = []
    for i, col in enumerate(columns):
        if values:
            max_width = max(len(col), *(len(str(row[i])) for row in values))
        else:
            max_width = len(col)
        column_widths.append(max_width)
    
    separator = "+-" + "-+-".join('-' * width for width in column_widths) + "-+"
    dump(separator)

    header = "| " + " | ".join(f"{col:<{column_widths[i]}}" for i, col in enumerate(columns)) + " |"
    dump(header)
    dump(separator)

    if values:
        for row in values:
            row_data = "| " + " | ".join(f"{str(item):<{column_widths[i]}}" for i, item in enumerate(row)) + " |"
            dump(row_data)
    else:
        empty_row = "| " + " | ".join(" " * width for width in column_widths) + " |"
        dump(empty_row)
    
    dump(separator)
    pbar.update(2)
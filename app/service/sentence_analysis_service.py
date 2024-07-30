import spacy
from helper.base_define import data_get, dd, dump
from helper.base_define import data_get
from graph.base_define import Shape
import re

class SentenceAnalysis:
    def analyze_sentence(self, text):
        pattern = r'\bwhose\s+\w+\s+is\b'
        match = re.search(pattern, text)

        if (
            "suppliers that supply" in text
            or "suppliers that do not supply" in text
            or "suppliers who supply" in text
            or "suppliers who do not supply" in text
            or match
        ):
            nlp = spacy.load("en_core_web_trf")
        else:
            nlp = spacy.load('en_core_web_md')

        doc = nlp(text)
        pos_relations = []
        for token in doc:
            pos_relations.append({
                "text": token.text,
                "part_of_speech": token.pos_,
                "dependency": token.dep_,
                "head_text": token.head.text,
                "head_pos": token.head.pos_,
                "children": [child.text for child in token.children]
            })

        return pos_relations

    def analyze_explode(self, text):
        nlp = spacy.load('en_core_web_md')
        doc = nlp(text)
        goal_temp = 3
        type = None

        if len(doc) == 6:
            goal_temp = 1

        if "List the part numbers with" in text:
            goal_temp = 5

        or_token_index = None
        for token in doc:
            if token.text.lower() == 'or':
                or_token_index = token.i
                type = 'union'
                break
        if or_token_index == None:
            or_token_index = None
            for token in doc:
                if token.text.lower() == 'and':
                    or_token_index = token.i
                    type = 'intersect'
                    break

        for token in doc:
            if token.text.lower() in ['who', 'whose', 'where', 'where', 'which']:
                goal_temp = token.i + 1

        if or_token_index:
            part1 = doc[:or_token_index]
            part2 = doc[or_token_index + 1:]

            sentence1 = ''.join([token.text_with_ws for token in part1]).strip() + '?'
            subject_phrase = ''.join([token.text_with_ws for token in doc[:goal_temp]]).strip()  
            sentence2 = subject_phrase + ' ' + ''.join([token.text_with_ws for token in part2]).strip()
        else:
            
            sentence1 = doc.text

        res = []

        res.append(sentence1)
        if or_token_index:
            res.append(sentence2)

        return res, type

import json
import requests
from datetime import datetime
from chatbot.helper_fun import clean_json_string, dd, dump, load_file_content, save_content, format_text
import os, time

class GoogleGemini:
    def add_question_to_data(self, data, question):
        data['contents'].append({
            "role": "user",
            "parts": [{"text":
                question
            }]
        })

    def send_request_and_process_response(self, session, url, headers, data):
        status = 0

        while (status != 200):
            response = session.post(url, headers=headers, json=data)
            status = response.status_code

            time.sleep(1)
    
        return response.json()['candidates'][0]['content']['parts'][0]['text']

    def get_answer_sql(self, answer_text):
        dump(answer_text)
        try:
            answer_text = json.loads(clean_json_string(answer_text, True))
            return answer_text["sql"].replace("\\n", " ")
        except Exception as e:
            try:
                answer_text = json.loads(clean_json_string(answer_text, True)[7:-3])

                return answer_text["sql"].replace("\\n", " ")
            except Exception as e:
                try:
                    answer_text = json.loads(clean_json_string(answer_text))

                    return answer_text["sql"].replace("\\n", " ")
                except Exception as e:
                    return str(e)

    def main(self, question, database, temperature = 1, top_p = 1):
        api_key = load_file_content('./chatbot/google_gemini.env')
        session = requests.Session()

        url = f'https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={api_key}'
        headers = {'Content-Type': 'application/json'}

        data = {
            "contents": [],
            "generationConfig": {
                "temperature": float(temperature),
                "topP": float(top_p),
                # "topK": "40",
                # "candidateCount": "<integer>",
                # "maxOutputTokens": "<integer>",
                # "stopSequences": ["<string>"]
            }
        }
 
        data['contents'] = []

        self.add_question_to_data(data, format_text(database, question))

        response_text = self.send_request_and_process_response(session, url, headers, data)

        save_content(response_text, f"./chatbot/output/gemini/{temperature}_{top_p}_response.json")

        return self.get_answer_sql(response_text)
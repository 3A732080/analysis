import requests
import json
from datetime import datetime
import time
from chatbot.helper_fun import clean_json_string, dd, dump, load_file_content, save_content, format_text

class ChatGpt:
    def call_chat_gpt_api(self, api_key, message, temperature = 1, top_p = 1):
        """使用 ChatGPT API 發送單個消息並獲得回應"""
        try:
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {api_key}'
                },
                json={
                    'model': 'gpt-3.5-turbo',
                    'messages': message,
                    'temperature': float(temperature),
                    'top_p': float(top_p),
                    # 'top_k': 40
                })
            response.raise_for_status()

            return response.json()
        except requests.RequestException as e:
            dd(f"[ChatGpt] API error: {e}")

    def get_answer_sql(self, answer_text):
        try:
            return json.loads(clean_json_string(answer_text))["sql"].replace("\\n", " ")
        except Exception as e:
            try:
                return json.loads(clean_json_string(answer_text))["sql"].replace("\\n", " ")
            except Exception as e:
                return str(e)

    def main(self, question, data, temperature = 1, top_p = 1):
        # 載入 api_key
        api_key = load_file_content('./chatbot/chat_gpt.env')

        messages = []

        data = load_file_content(f"./chatbot/{data}.txt")
        messages.append({"role": "user", "content": format_text(data, question)})

        content = self.call_chat_gpt_api(api_key, messages, temperature, top_p)

        if content and 'choices' in content and content['choices']:
            response_text = content['choices'][0].get('message', {}).get('content', '')

        return self.get_answer_sql(response_text)

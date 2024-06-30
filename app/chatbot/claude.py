import anthropic, json, time 
from datetime import datetime
from chatbot.helper_fun import clean_json_string, extra_clean_json_string, dd, dump, load_file_content, save_content, format_text

class Claude:
    def add_message(self, messages, role, text):
        """添加對話到messages列表"""
        messages.append({
            "role": role,
            "content": [{"type": "text", "text": text}]
        })

    def get_answer_sql(self, answer_text):
        dump(answer_text)
        try:
            json_start = answer_text.index('{')
            json_end = answer_text.rindex('}') + 1
            json_text = answer_text[json_start:json_end]
            sql_query = json.loads(json_text.replace("\\n", " ").replace("\\", " "))['sql '].strip()
            return sql_query
        except Exception as e:
            try:
                json_start = answer_text.index('{')
                json_end = answer_text.rindex('}') + 1
                json_text = answer_text[json_start:json_end]
                clean_json = extra_clean_json_string(json_text, add_exception=True)
                sql_query = json.loads(clean_json)["sql"].replace("\\n", " ")
                return sql_query
            except Exception as e:
                return str(e)

    def main(self, question, data, temperature = 1, top_p = 1):
        api_key = load_file_content('./chatbot/claude.env')

        client = anthropic.Anthropic(api_key=api_key)

        messages = []

        data = load_file_content(f"./chatbot/{data}.txt")
        self.add_message(messages, "user", format_text(data, question))

        # 創建對話消息
        message = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=3000,
            temperature=float(temperature),
            top_p=float(top_p),
            # top_k=40,
            messages=messages
        )

        response_text = message.content[0].text if message.content else ""

        save_content(response_text, f"./chatbot/output/claude/{temperature}_{top_p}_response.json")

        return self.get_answer_sql(response_text)

import spacy


nlp = spacy.load('en_core_web_md')
sentence = "List the names of courses that are taught by Frank?"
doc = nlp(sentence)

course_token = None
frank_token = None


for token in doc:
    if token.text.lower() == 'course':
        course_token = token
    elif token.text == 'Frank':
        frank_token = token


if course_token and frank_token:
    
    current_token = frank_token.head  
    while current_token != course_token and current_token.head != current_token:
        if current_token.text == 'taught' and current_token.head.text == 'course':
            print("Frank teaches the course.")
            break
        current_token = current_token.head
else:
    print("Cannot find either 'course' or 'Frank' in the sentence.")


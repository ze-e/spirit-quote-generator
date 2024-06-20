from flask import Flask, render_template, request, jsonify
import requests
import pyperclip
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)

def get_response(msg):
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    client = OpenAI(
        api_key=OPENAI_API_KEY,
    )    
    completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
            {"role": "system", "content": """
            You are a quote generator. 
            Generate a famous quote or quotes based on the query.
            """},
            {"role": "user", "content": msg}
        ]
    )
    print(completion.choices[0].message.content)
    try:
        return completion.choices[0].message.content
    except:
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_quotes', methods=['POST'])

def get_quotes():
    num_quotes = int(request.form.get('num_quotes'))
    month = request.form.get('month')
    msg = f"""Write {num_quotes} quotes that have to do with the month {month.lower()}. 
        These quotes can be about the month itself, holidays or events in that month,
        or the season that occurs in that month. All quotes must be from a famous person
        or work of art. No quotes can be anonymous. All quotes must have an attribution (attribution = the source of the quote)
        All quotes must be 12 words or less. All quotes must be real quotes.
        
        Use this format:
        <quote 1> -- <attribution> \n
        <quote 2> -- <attribution> \n
        ...
        <quote <final number>> -- <attribution>
        """
    response = get_response(msg)
    if response:
        return jsonify({'quotes': response}), 200
    else:
        return jsonify({'error': 'Failed to fetch quotes'}), 500

@app.route('/copy_quotes', methods=['POST'])
def copy_quotes():
    quotes = request.json.get('quotes')
    quotes_text = "\n".join(quotes)
    pyperclip.copy(quotes_text)
    return jsonify({'message': 'Quotes copied to clipboard!'})

if __name__ == '__main__':
    app.run(debug=True)

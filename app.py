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
            You are a quote generator assistant. 
            """},
            {"role": "user", "content": msg}
        ]
    )
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
    msg = f"""Print {num_quotes} famous quotes that have to do with the month {month.lower()}. 
        These quotes can be about the month itself, holidays or events in that month,
        or the season that occurs in that month. All quotes must be from a famous person
        or work of art. All quotes must have an attribution (attribution = the source of the quote)
        All quotes must be 12 words or less. All quotes must be real quotes.
        DO NOT include quotes from "anonymous" or "various"

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


@app.route('/validate_quotes', methods=['POST'])
def validate_quotes():
    # Extract quotes from the request body
    data = request.get_json()
    quotes = data.get('quotes', [])
    if not quotes:
        return jsonify({'error': 'No quotes provided'}), 500
    
    try:
        trueMsg = "All quotes are valid!"
        falseMsg = "Some quotes are invalid"
        msg = f""" 
            Check if any of the following quotes are fake quotes, then give one of two responses

            1. If there are one or more fake quotes, then print the following:

            "{falseMsg}:
            <insert list of the invalid quotes>
            "

            2. If there are no fake quotes, simply print the following verbatim with NO OTHER INFORMATION:
            
            "{trueMsg}"
            
            Here is the list of quotes:
            {quotes}
            """
        response = get_response(msg)

        if response and trueMsg in response:
            return jsonify({'message': response}), 200
        elif response and falseMsg in response:
            return jsonify({'message': response}), 500
        else:
            return jsonify({'error': 'Error validating quotes'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/copy_quotes', methods=['POST'])
def copy_quotes():
    quotes = request.json.get('quotes')
    quotes_text = "\n".join(quotes)
    pyperclip.copy(quotes_text)
    return jsonify({'message': 'Quotes copied to clipboard!'})

if __name__ == '__main__':
    app.run(debug=True)

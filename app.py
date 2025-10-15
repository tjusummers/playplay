from flask import Flask, render_template, send_file
from generator import generate_operations
import pdfkit
import os

pdfkit_config = pdfkit.configuration(wkhtmltopdf='/path/to/wkhtmltopdf')


app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/generate')
def generate():
    problems = generate_operations()
    return render_template('questions.html', problems=problems)

@app.route('/download')
def download():
    problems = generate_operations()
    html = render_template('questions.html', problems=problems)
    pdf_path = 'questions.pdf'
    pdfkit.from_string(html, pdf_path)
    return send_file(pdf_path, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)

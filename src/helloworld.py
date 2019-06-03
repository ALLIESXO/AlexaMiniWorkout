from flask import Flask, render_template
from flask_ask import Ask, statement

app = Flask(__name__)
ask = Ask(app, "/") 

@ask.launch
def hello():
    return statement("Hello World")

if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, render_template
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)


@app.route('/')
def screenbloom():
    return render_template('/welcome.html')

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
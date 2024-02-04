from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('panel.html')

@app.route('/load_time')
def load_time():
    from time import strftime
    return strftime("%Y-%m-%d %H:%M:%S")

@app.route('/settings')
def settings():
    return render_template('settings.html')


if __name__ == '__main__':
    app.run(debug=True)
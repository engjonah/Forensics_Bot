#Keep bot up 24/7
#Use https://uptimerobot.com/ to ping website every 15 mins to keep replit from shutting down
from flask import Flask, render_template
from threading import Thread

app = Flask(__name__, template_folder='templates')

@app.route('/')
def main():
    return render_template('index.html')

def run():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    server = Thread(target=run)
    server.start()
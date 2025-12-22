from flask import Flask, render_template
from data_sources import DataSourceA, DataSourceB

app = Flask(__name__)

data_sources = [DataSourceA(), DataSourceB()]

@app.route('/')
def home():
    signals = [source.read_signal() for source in data_sources]
    return render_template('index.html', signals=signals)

if __name__ == '__main__':
    app.run(debug=True)
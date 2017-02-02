from flask import Flask
from flask import jsonify

import io_utils

app = Flask(__name__)


@app.route('/')
def index():
    a = {1: ["movie1", "movie3"], 2: "movie2"}
    return jsonify(a)


if __name__ == '__main__':
    app.run(debug=True)

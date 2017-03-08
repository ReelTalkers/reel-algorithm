from flask import Flask, request, jsonify
import recommendations
import io_utils


app = Flask(__name__)


@app.route('/single_user_recommendations', methods=['POST'])
def single_user_recommendations():
    return jsonify(request.get_json())


@app.route('/group_recommendations', methods=['POST'])
def group_recommendations():
    return jsonify(request.get_json())


if __name__ == '__main__':
    app.run(debug=True)

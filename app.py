from flask import Flask, jsonify
import boto3

app = Flask(__name__)

dynamodb = boto3.resource('dynamodb', region_name='us-west-2')

@app.route('/')
def index():
    return jsonify({'message': 'Welcome to the Flask DynamoDB app!'})

if __name__ == '__main__':
    app.run(debug=True)
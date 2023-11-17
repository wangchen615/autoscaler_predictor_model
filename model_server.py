from flask import Flask, request, jsonify
import pandas as pd
from io import StringIO
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from datetime import timedelta
from statsmodels.tsa.statespace.sarimax import SARIMAX

app = Flask(__name__)

# Global variable to store the model
cpu_model = None
memory_model = None
requests_model = None

@app.route('/fit-model', methods=['POST'])
def fit_model():
    global cpu_model, memory_model, requests_model

    # Read CSV file from the request
    file = request.files['file']

    # Determine file type from filename extension
    file_type = file.filename.split('.')[-1].lower()

    # Convert file to DataFrame based on file type
    if file_type == 'csv':
        df = pd.read_csv(StringIO(file.read().decode('utf-8')))
    elif file_type == 'json':
        df = pd.read_json(StringIO(file.read().decode('utf-8')))
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    else:
        return jsonify({'error': 'Unsupported file type'}), 400

    # Validate DataFrame format
    if 'timestamp' not in df.columns:
        return jsonify({'error': 'CSV must contain timestamp column'}), 400

    response = {}

    # Convert timestamps to total minutes since midnight
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['minutes_since_midnight'] = df['timestamp'].dt.hour * 60 + df['timestamp'].dt.minute

    # Prepare model inputs
    X = df[['minutes_since_midnight']]

    # Define 4-degree polynomial regression model
    polynomial_regression = make_pipeline(PolynomialFeatures(4), LinearRegression())

    # Check for columns and fit models accordingly
    if 'cpu' in df.columns and 'memory' in df.columns:

        # Fit model for CPU
        cpu_model = polynomial_regression
        cpu_model.fit(X, df['cpu'])
        response['cpu_model'] = 'Model fitted for CPU'

        # Fit model for memory
        memory_model = polynomial_regression
        memory_model.fit(X, df['memory'])
        response['memory_model'] = 'Model fitted for memory'

    elif 'requests' in df.columns:
        # Fit a single model for requests
        requests_model = polynomial_regression
        requests_model.fit(X, df['requests'])
        response['requests_model'] = 'Model fitted for requests'

    else:
        response['error'] = 'Required columns not found'

    return jsonify(response)


@app.route('/predict', methods=['GET'])
def predict():
    global cpu_model, memory_model, requests_model

    # Use request.args to get query parameters for GET request
    predict_type = request.args.get('type')  # 'resources' or 'requests'
    timestamp = request.args.get('timestamp')

    if not timestamp:
        return jsonify({'error': 'No timestamp provided'}), 400

    # Convert timestamp to total minutes since midnight
    try:
        timestamp = pd.to_datetime(timestamp)
        minutes_since_midnight = timestamp.hour * 60 + timestamp.minute
    except ValueError:
        return jsonify({'error': 'Invalid timestamp format'}), 400

    if predict_type == 'resource':
        # Check if models are loaded
        if cpu_model is None or memory_model is None:
            return jsonify({'error': 'CPU or Memory model is not loaded'}), 500

        # Predict CPU and Memory
        cpu_prediction = int(cpu_model.predict([[minutes_since_midnight]])[0])
        memory_prediction = int(memory_model.predict([[minutes_since_midnight]])[0])
        return jsonify({'cpu': cpu_prediction, 'memory': memory_prediction})

    elif predict_type == 'requests':
        # Check if model is loaded
        if requests_model is None:
            return jsonify({'error': 'Requests model is not loaded'}), 500

        # Predict Requests
        requests_prediction = int(requests_model.predict([[minutes_since_midnight]])[0])
        return jsonify({'requests': requests_prediction})

    else:
        return jsonify({'error': 'Invalid prediction type'}), 400

@app.route('/forecast', methods=['POST'])
def forecast():
    # Check if the request contains JSON data
    if request.is_json:
        data = request.get_json()
        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    else:
        # Read CSV file from the request
        file = request.files.get('file')
        if not file:
            return jsonify({'error': 'No file provided'}), 400
        # Convert file to DataFrame
        df = pd.read_csv(StringIO(file.read().decode('utf-8')))

    # Validate DataFrame format and presence of timestamp
    if 'timestamp' not in df.columns:
        return jsonify({'error': 'CSV/JSON must contain timestamp column'}), 400

    # Convert timestamps to DateTime and sort
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)
    df.sort_index(inplace=True)

    # Predict for the next 15 minutes
    last_timestamp = df.index[-1]
    next_timestamp = last_timestamp + timedelta(minutes=15)

    prediction = {}

    # SARIMA models for each type of data
    if 'cpu' in df.columns and 'memory' in df.columns:
        cpu_model = SARIMAX(df['cpu'], order=(1, 1, 1), seasonal_order=(1, 1, 1, 4))
        cpu_results = cpu_model.fit()
        prediction['cpu'] = cpu_results.forecast(steps=1)[0]

        memory_model = SARIMAX(df['memory'], order=(1, 1, 1), seasonal_order=(1, 1, 1, 4))
        memory_results = memory_model.fit()
        prediction['memory'] = memory_results.forecast(steps=1)[0]

    if 'requests' in df.columns:
        requests_model = SARIMAX(df['requests'], order=(1, 1, 1), seasonal_order=(1, 1, 1, 4))
        requests_results = requests_model.fit()
        prediction['requests'] = requests_results.forecast(steps=1)[0]

    prediction['timestamp'] = next_timestamp.strftime('%Y-%m-%d %H:%M:%S')
    return jsonify(prediction)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
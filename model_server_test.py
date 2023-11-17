import requests
import pytest

# URL of the Flask server (assuming it's running locally)
base_url = 'http://127.0.0.1:5001'

# Sample data for testing
sample_csv_data = './data/testing.csv'

# Test for fitting the model
def test_fit_model():
    with open(sample_csv_data, 'rb') as file:
        response = requests.post(f'{base_url}/fit-model', files={'file': file})
    assert response.status_code == 200
    # You can add more assertions here based on the expected response

# Test for prediction endpoint
def test_predict():
    response = requests.get(f'{base_url}/predict?type=requests&timestamp=2023-03-15T14:30:00')
    assert response.status_code == 200
    # Add more assertions as needed

# Test for forecast endpoint
def test_forecast():
    with open(sample_csv_data, 'rb') as file:
        response = requests.post(f'{base_url}/forecast', files={'file': file})
    assert response.status_code == 200
    # Add more assertions as needed

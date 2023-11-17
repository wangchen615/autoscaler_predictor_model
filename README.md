# autoscaler_predictor_model
The data synthesizer, forecaster and predictor model server used together with KEDA scaler or cluster autoscaler to achieve cluster autoscaling with diurnal pattern workload

## How to use the data synthesizer
### Set up python virtual environment
```bash
python3 -m venv autoscaler_predictor_model/venv
source autoscaler_predictor_model/venv/bin/activate
pip install -r requirements.txt
```
### Usage Instructions:
1. Configure the data synthesizer:
- Edit the `config.ini` file to set the peak and valley CPU/memory usage or requests/s load. You can also configure
the number of weeks to generate the data, the peak hour in a day and the variations of usage/load across the same time in a day.
2. Generate Data:
```bash
python data_synthesizer.py
```
3. The data is generated in the `data` folder. The data is generated in CSV format with the following columns:
- timestamp: The timestamp in milliseconds since epoch
- cpu: The CPU usage in millicores
- memory: The memory usage in bytes
- requests: The number of requests per second
The csv file name is in the format: `<type>-<year>-<month>-<day>-<hour>-<minute>.csv` and can be fed into the model server to fit the model.
The json file name is in the format: `<type>-<year>-<month>-<day>-<hour>-<minute>.json` and can be fed into the model server to fit the model or to forecast the next datapoint.

## How to use the model server
### Build and Run the Docker image
```bash
podman build -t model-server .
podman run -p 5000:5000 model-server
```

### Usage Instructions:
1. Fit the Model:
- Send a POST request to /fit-model with a CSV/JSON file containing timestamp and cpu/memory or requests columns.
- The server fits a polynomial model to this data.

An example `curl` command to fit the model:
```bash
curl -X POST http://localhost:5000/fit-model -F 'file=@/path/to/data.csv'
```

2. Get Predictions:

- Send a GET request to /predict with a type parameter (`requests` or `resource`) and a timestamp query parameter.
- The server returns the predicted cpu/memory or requests value(s) based on the fitted model.

An example `curl` command to get predictions:
```bash
curl -X GET "http://localhost:5000/predict?type=resource&timestamp=2023-03-15T14:30:00"
curl -X GET "http://localhost:5000/predict?type=requests&timestamp=2023-03-15T14:30:00"
```

3. Get Forecasts:

- Send a POST request to /forecast with a csv file or json object that contains any length of time series data.
- The server returns the predicted cpu/memory or requests value(s) based on SARIMA algorithm running on the given data.
Example `curl` command to get forecasts from a csv file:
```bash
 curl -X POST http://127.0.0.1:5000/forecast \
-H "Content-Type: multipart/form-data" \
-F "file=@./data/requests-23-11-16-22-51.csv"
```

Example `curl` command to get forecasts from a json object:
```bash
curl -X POST http://127.0.0.1:5000/forecast \
-H "Content-Type: application/json" \
-d '[{"timestamp":1700092800000,"requests":279},{"timestamp":1700093700000,"requests":257},{"timestamp":1700094600000,"requests":230}]'
```


#### Notes:
- The fit-model endpoint expects a CSV file with two columns: timestamp and requests or three columes: timestamp, cpu and memory.
- The predict endpoint requires a timestamp in a recognizable datetime format.
- The model fitting is simplistic and assumes a polynomial model. You may need to adjust the model fitting part based on your specific requirements.
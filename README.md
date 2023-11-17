# autoscaler_predictor_model
The data synthesizer, forecaster and predictor model server used together with KEDA scaler or cluster autoscaler to achieve cluster autoscaling with diurnal pattern workload

## How to use the model server
### Build and Run the Docker image
```bash
podman build -t model-server .
podman run -p 5000:5000 model-server
```

### Usage Instructions:
1. Fit the Model:
- Send a POST request to /fit-model with a CSV file containing timestamp and value columns.
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

#### Notes:
- The fit-model endpoint expects a CSV file with two columns: timestamp and requests or three columes: timestamp, cpu and memory.
- The predict endpoint requires a timestamp in a recognizable datetime format.
- The model fitting is simplistic and assumes a polynomial model. You may need to adjust the model fitting part based on your specific requirements.
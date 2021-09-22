# AppSheet Document AI Adapter

This service provides a REST API for AppSheet to integrate GCP Document AI services into AppSheet no-code apps.  It uses MongoDB to store the document AI results, and then sync to AppSheet through the API hosted in this service.

AppSheet connects to this service using the API data provider (Apigee provider), which can then synchronize document forms to the API and get the form processing results back to display to the user.

## Deployment

[![Run on Google Cloud](https://deploy.cloud.run/button.svg)](https://deploy.cloud.run)

You can run this service on any container platform, for example Google Cloud Run (see button above) or Google Kubernetes Engine.

Set these environment variables when deploying.

| Env name                         | Env description                                           |
| -------------------------------- | --------------------------------------------------------- |
| GOOGLE_APPLICATION_CREDENTIALS   | The path to your GCP service account credentials key file |
| MONGO_CONNECTION_STRING          | The connection string to your Mongo DB                    |
| GCP_PROJECT                      | The GCP project of the document AI processor              |
| GCP_DOCAI_REGION                 | The Document AI region (EU or US)                         |
| GCP_DOCAI_PROCESSOR_ID           | The Document AI processor ID                              |

## Configuration in AppSheet

Once the service is deployed, you can then configure your service endpoint as an API (Apigee) data source, and then connect into an app as a data source that can take a "File" type from a related table, so for example connecting to file attachments to get the document AI processing and display to the user.

# AppSheet Document AI Adapter

This service provides a REST API for AppSheet to integrate GCP Document AI services into AppSheet no-code apps.  It uses MongoDB to store the document AI results, and then sync to AppSheet through the API hosted in this service.

AppSheet connects to this service using the API data provider (Apigee provider), which can then synchronize document forms to the API and get the form processing results back to display to the user.

## Deployment

[![Run on Google Cloud](https://deploy.cloud.run/button.svg)](https://deploy.cloud.run)

You can run this service on any container platform, for example Google Cloud Run (see button above) or Google Kubernetes Engine.

Set these environment variables when deploying.

| Env name                         | Env description                                           |
| -------------------------------- | --------------------------------------------------------- |
| GCP_DOCAI_REGION                 | The Document AI region (eu or us)                         |
| GCP_DOCAI_PROCESSOR_ID           | The Document AI processor ID (from the GCP console)       |
| API_KEY                          | A secret that AppSheet can use to call this API          |

## Configuration in AppSheet

After deploying the service, add a new **Apigee** data source to your AppSheet account pointing to the deployed service URL + "/spec".

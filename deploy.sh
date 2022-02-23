export servicename=docaiservice
export PROJECT_ID=$(gcloud config get-value project)
export REGION=europe-west1
export ENV=GCP_DOCAI_REGION=eu,GCP_DOCAI_PROCESSOR_ID=26e59ef1d2cc780

docker build -t local/$servicename .
docker tag local/$servicename eu.gcr.io/$PROJECT_ID/$servicename
docker push eu.gcr.io/$PROJECT_ID/$servicename

gcloud run deploy $servicename --image eu.gcr.io/$PROJECT_ID/$servicename --platform managed --project $PROJECT_ID --region $REGION --update-env-vars $ENV --allow-unauthenticated

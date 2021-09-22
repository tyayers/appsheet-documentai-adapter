export servicename=docaiservice

docker build -t local/$servicename .
docker tag local/$servicename eu.gcr.io/$1/$servicename
docker push eu.gcr.io/$1/$servicename

gcloud run deploy $servicename --image eu.gcr.io/$1/$servicename --platform managed --project $1 --region europe-west1 --allow-unauthenticated

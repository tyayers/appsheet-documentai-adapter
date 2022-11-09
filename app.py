import pprint
from proto import fields
import web
import json
import logging
import urllib
import requests
import io
import os
from googleapiclient.http import MediaIoBaseDownload
from google.cloud import documentai_v1 as documentai
import os.path
from googleapiclient.discovery import build
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

import google.auth

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
location = os.getenv('GCP_DOCAI_REGION')
processor_id = os.getenv('GCP_DOCAI_PROCESSOR_ID')

urls = (
  '/formfields(.*)', 'formfields',
  '/(.*)', 'openapispec'
)
app = web.application(urls, globals())

class formfields:

  result = {
    "formfields": [
      {
        "formId": "bec38fd6",
        "documentId": "bec38fd6",
        "documentPath": "Document AI Forms_Files_/e111806a.Attachment.162159.pdf",
        "formFields": "\nEnglish=☑ \nFrançais=\nEsperanto=\nHouse nr=1\nPostcode=11111\nDeutsch=☐ \nLatin=☐ \nGender=Man\nCity=Hobbiton\nCountry=Britain\nGiven Name=Bilbo\nHeight (cm)=100\nAddress 1=Bag End\nAddress 2=Under Hill\nFamily Name=Baggins\nFavourite colour=Red\nDriving License=",
        "formThumbnail": "https://storage.googleapis.com/bruno-hosting/appsheet/form_thumb.png",
        "totalFields": 17,
        "filledFields": 14
      }
    ]
  }

  # Returns all of the formfields
  def GET(self, name):

    pprint.pprint(web.ctx.home + web.ctx.fullpath)
    
    pprint.pprint(self.result)

    web.header('Content-Type', 'application/json')
    return json.dumps(self.result)

  # Posts a new form to be processed
  def POST(self, name):

    data = json.loads(web.data())

    logging.info(json.dumps(data))

    docId, documentPath = "", ""
    if "documentId" in data:
      docId = data["documentId"]
    if "documentPath" in data:
      documentPath = data["documentPath"]

    newRecord = {
      "formId": data["formId"],
      "documentId": docId,
      "documentPath": documentPath
    }

    fieldsInfo = {
      "formFields": "",
      "formThumbnail": ""
    }

    if documentPath:
      fieldsInfo = callDocAI(documentPath)
      
    for key in fieldsInfo:
      newRecord[key] = fieldsInfo[key]

    self.result["formfields"].append(newRecord)
    
    pprint.pprint(newRecord)

    web.header('Content-Type', 'application/json')
    return json.dumps(newRecord)

# Returns the OpenAPI spec, filled in with the current server
class openapispec:

  #Returns the OpenAPI spec, filled in with the current server
  def GET(self, name):
    f = open("apispec.yaml", "r")
    spec = f.read()
    spec = spec.replace("SERVER_URL", web.ctx.home.replace("http://", "https://"))
    web.header('Content-Type', 'text/plain;charset=UTF-8')
    return spec

# Leftover for testing.. not used.
def quickstart(project_id: str, location: str, processor_id: str, file_path: str):

    # You must set the api_endpoint if you use a location other than 'us', e.g.:
    opts = {}
    if location == "eu":
      opts = {"api_endpoint": "eu-documentai.googleapis.com"}

    client = documentai.DocumentProcessorServiceClient(client_options=opts)

    # The full resource name of the processor, e.g.:
    # projects/project-id/locations/location/processor/processor-id
    # You must create new processors in the Cloud Console first
    name = f"projects/{project_id}/locations/{location}/processors/{processor_id}"

    # Read the file into memory
    with open(file_path, "rb") as image:
        image_content = image.read()

    document = {"content": image_content, "mime_type": "application/pdf"}

    # Configure the process request
    request = {"name": name, "raw_document": document}

    result = client.process_document(request=request)
    document = result.document

    document_pages = document.pages
    # For a full list of Document object attributes, please reference this page: https://googleapis.dev/python/documentai/latest/_modules/google/cloud/documentai_v1beta3/types/document.html#Document

    # Read the text recognition output from the processor
    print("The document contains the following paragraphs:")
    for page in document_pages:
        paragraphs = page.paragraphs
        formFields = page.form_fields

        for form_field in page.form_fields:
            print(
                "Field Name: {}\tConfidence: {}".format(
                    _get_text(form_field.field_name, document), form_field.field_name.confidence
                )
            )
            print(
                "Field Value: {}\tConfidence: {}".format(
                    _get_text(form_field.field_value, document), form_field.field_value.confidence
                )
            )
        # for block in page.lines:
        #   print(str(block))
        # for field in formFields:
        #   print(str(field))

        # for paragraph in paragraphs:
        #     #print(paragraph)
        #     paragraph_text = get_text(paragraph.layout, document)
        #     print(f"Paragraph text: {paragraph_text}")

# Helper function to get text from form fields
def _get_text(el, document):
    """Doc AI identifies form fields by their offsets
    in document text. This function converts offsets
    to text snippets.
    """
    response = ""
    # If a text segment spans several lines, it will
    # be stored in different text segments.
    for segment in el.text_anchor.text_segments:
        start_index = segment.start_index
        end_index = segment.end_index
        response += document.text[start_index:end_index]
    return response

# Helper function to get text from form fields
def get_text(doc_element: dict, document: dict):
    """
    Document AI identifies form fields by their offsets
    in document text. This function converts offsets
    to text snippets.
    """
    response = ""
    # If a text segment spans several lines, it will
    # be stored in different text segments.
    for segment in doc_element.text_anchor.text_segments:
        start_index = (
            int(segment.start_index)
            if segment in doc_element.text_anchor.text_segments
            else 0
        )
        end_index = int(segment.end_index)
        response += document.text[start_index:end_index]
    return response

# Method to call the Document AI API and get the form processing results
def callDocAI(documentPath: str):

  output = {
    "formFields": "",
    "formThumbnail": "",
    "totalFields": 0,
    "filledFields": 0
  }

  creds, project_id = google.auth.default(scopes=SCOPES)
  #creds = service_account.Credentials.default(scopes=SCOPES)

  service = build('drive', 'v3', credentials=creds)
  page_token = None

  response = service.files().list(q="name='" + documentPath.split("/")[-1] + "'",
                                        spaces='drive',
                                        fields='nextPageToken, files(id, name, thumbnailLink)',
                                        pageToken=page_token).execute()

  for file in response.get('files', []):
    # Process change
    print("Found file: " + file.get('name') + " and id: " + file.get('id'))
    request = service.files().get_media(fileId=file.get('id'))
    # fh = io.BytesIO()
    fh = io.FileIO('tempdoc.pdf', 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
      status, done = downloader.next_chunk()
      print("Download " + str(int(status.progress() * 100)))

    output["formThumbnail"] = file["thumbnailLink"]
    break

  opts = {"api_endpoint": "eu-documentai.googleapis.com"}

  client = documentai.DocumentProcessorServiceClient(client_options=opts)
  name = f"projects/{project_id}/locations/{location}/processors/{processor_id}"

  with open("tempdoc.pdf", "rb") as image:
      image_content = image.read()

  mime = "application/pdf"
  if documentPath.endswith(".png"):
    mime = "image/png"

  document = {"content": image_content, "mime_type": mime}

  # Configure the process request
  request = {"name": name, "raw_document": document}

  result = client.process_document(request=request)
  document = result.document

  document_pages = document.pages

  formFields = ""
  for page in document_pages:
    for form_field in page.form_fields:
      fieldLabel = _get_text(form_field.field_name, document).replace("\n", "").replace(":", "").strip()
      fieldValue = _get_text(form_field.field_value, document).replace("\n", "")
      formFields += "\n" + fieldLabel + "=" + fieldValue

      output["totalFields"] = output["totalFields"] + 1
      if fieldValue != "":
        output["filledFields"] = output["filledFields"] + 1

  output["formFields"] = formFields
  return output

# formFields = callDocAI("Customer_Files_/9a62a9a8.Document.184617.pdf")
# print(formFields)

if __name__ == "__main__":
  app.run()

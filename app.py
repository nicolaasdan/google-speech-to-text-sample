from google.cloud import storage
from flask import Flask, render_template, url_for, flash, redirect, request
import transcribe
import os
import io
app = Flask(__name__)

#make environment variable for the root folder of the app
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

#assign google credentials of the service account to a environment variable
credential_path = "./My Project 26709-e07b6ef1ad6a.json"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path


@app.route('/', methods=['POST', 'GET'])
def upload():
	'''
	Upload method uploads a local audio file into the folder 'app/audiofiles'
	Then the file is uploaded to google cloud storage and deleted in the folder 'app/audiofiles'.
	'''
	target = os.path.join(APP_ROOT, 'audiofiles/')

	#if folder does not yet exist, make folder
	if not os.path.isdir(target):
		os.mkdir(target)

	for file in request.files.getlist("file"):
		path = os.path.abspath(file.filename)
		filename = file.filename
		destination = "/".join([target, filename])
		file.save(destination)
		upload_blob("audiobestanden-nicolaasdanneels", destination, "uploadedFile.flac")
		os.remove(destination)
		return redirect("/translation")

	return render_template("upload.html")

@app.route("/translation")
def translation():
	'''
	method takes the audio file uploaded onto google cloud storage and transcribes the files
	by sending the file to the google speech to text api. The transcription is returned and passed in the template.
	'''
	transcription = transcribe.transcribe_gcs("gs://audiobestanden-nicolaasdanneels/uploadedFile.flac")
	return render_template('index.html', transcription=transcription)

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print('File {} uploaded to {}.'.format(
        source_file_name,
        destination_blob_name))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
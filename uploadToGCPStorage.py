# MODULE: uploadToGCPStorage.py

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#    http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os
import filetype
from PIL import Image
from gcloud import storage
from gcloudCredentials import credentials


BUCKET_NAME = 'mybucket'

def _resizeImage(file_path):
    """Make sure the image is the right size, we're only dealing with 160x160"""
    width = 160
    height = 160
    img_org = Image.open(file_path)
    img_anti = img_org.resize((width, height), Image.ANTIALIAS)
    img_anti.save(file_path, "PNG")

# external_id - the unique identifier
# filename - the local file name
# FileTypeCheck - check for the type of file we're passing, default to true
# LOCAL_TEMP_PATH - the folder where the local file exists on the machine - defaults to ./temp/
#
# Files will be saved in GS as "external_id/filename", external_id will 
# so this is kind of fun. Gcloud storage doesn't really have logical folders.
# they have a flat filesytem. That means external_id is not really a folder
# it's the full name of the resource from the bucket. 
# Just an interesting fact.
def uploadToGCPStorage(external_id, filename, FileTypeCheck=True, LOCAL_TEMP_PATH="./temp/") -> str:
    """Using the gcloud google storage API, upload the resource and by it's external id."""
    try:

        if external_id == '':
            print ("Error: External token id was empty and is required.")
            return
        
        file_path = LOCAL_TEMP_PATH + filename

        if os.path.exists(LOCAL_TEMP_PATH) == False:
            print ("Error: could not find the local path of " + LOCAL_TEMP_PATH)
            
        if (FileTypeCheck):
            ft = filetype.guess(file_path)
            
            if ft is None:
                print('could not guess file type!')
                return
            if ft.extension == "jpg" or ft.extension == "png" or ft.extension == "gif":
                # make sure it's 160x160
                _resizeImage(file_path)

        print ("Saving '" + file_path + "' to Google Cloud Storage...")
        client = storage.Client(credentials=credentials)
        bucket = client.get_bucket(BUCKET_NAME)
        blob = bucket.blob( external_id + '/' + filename)
        blob.upload_from_filename(filename=file_path)
        blob.make_public()
        print (filename + " uploaded to Google. 🌍")
        return blob.public_url

    except RuntimeError as err:
        print ("Error: ", err)
        return

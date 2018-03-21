# importAssetsFromSheet.py

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#    http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Pulls from Google Sheets using Sheetsu. Imports to Google Cloud Storage.
# http://www.sheetsu.com
# 
# Author: Gary MacDougall
# Date: December 21, 2017
from uploadToGCPStorage import uploadToGCPStorage
import os
import filetype
from sheetsu import SheetsuClient
import requests
import time
import pickle
import ntpath
import sys
import glob
from bs4 import BeautifulSoup

LOCAL_TEMP_PATH = './temp/'
LOCAL_LOGFILE_PATH = LOCAL_TEMP_PATH + "/importAssets.log"
SHEET_START_POINT = 0   # start at 1 to start from the begining.
SHEETSU_ID = "123456"

def _log(data):
    """Log to file"""
    with open(LOCAL_LOGFILE_PATH, 'a') as log:  
        log.write(data + "\n")
    print (data)

def _path_leaf(path):
    """Get basename of path."""
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

def _download_file(url, local_file_path):
    """Download from URL use stream to chunk the data."""
    # NOTE the stream=True parameter
    r = requests.get(url, stream=True)
    with open(local_file_path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
    return True

def _getDocument(assetData):
    """ Retrieve whitepaper regardless of filetype from URL."""
    #For testing purposes.
    # assetData['whitepaper_url'] = 'https://dfinity.network/pdfs/viewer.html'
    # assetData['external_id'] = 'trhub7k'

    r = None
    if os.path.exists(LOCAL_TEMP_PATH) == False:
         os.makedirs(LOCAL_TEMP_PATH)

    while r==None:
        try:
            print ("Checking '" + assetData['whitepaper_url'] + "'...")
            r = requests.head(assetData['whitepaper_url'])
            r.raise_for_status()

        except requests.exceptions.Timeout:
            # Maybe set up for a retry, or continue in a retry loop
            print ("================================")
            _log ("Error: Timeout for '" + assetData['external_id'] + "' failed loading from '" + assetData['whitepaper_url'] + "'")
            print ("================================")
            return False, "", False

        except requests.exceptions.TooManyRedirects:
            # Tell the user their URL was bad and try a different one
            print ("================================")
            _log ("Error: TooManyRedirects for '" + assetData['external_id'] + "' failed loading from '" + assetData['whitepaper_url'] + "'")
            print ("================================")
            return False, "", False
          
        except requests.exceptions.RequestException:
            # catastrophic error. bail.
            print ("================================")
            _log ("Error: RequestException for '" + assetData['external_id'] + "' failed loading from '" + assetData['whitepaper_url'] + "'")
            print ("================================")
            return False, "", False
        
        if r.status_code == 404:
            print ("================================")
            _log ("Error: " + assetData['whitepaper_url'] + " page not found.")
            print ("================================")
            return False, "", False

        try:
            if r.status_code == requests.codes.ok or r.status_code == 302 or r.status_code == 301:
                base_filename = assetData['external_id'] + "-whitepaper"
                local_file_path = LOCAL_TEMP_PATH + base_filename
                LocalFile = glob.glob("temp/" + base_filename + ".*")
                # if we have the file already.  No need to get it again.
                # if not LocalFile:
                if _download_file(assetData['whitepaper_url'], local_file_path):
                    print ("Document '" + local_file_path + "' saved. ✅")
                else:
                    print ("Document '" + local_file_path + "' failed to save. 🚫")
                    return False, base_filename, False
            
                kind = filetype.guess(local_file_path)
                if kind is None:
                    try:
                        with open(local_file_path, 'rb') as f:
                            data=f.read()
                        if BeautifulSoup(data, "html.parser").find():
                            base_filename = base_filename + ".html"
                            os.rename (local_file_path, local_file_path + ".html")
                        else: 
                            _log("Error: file type not valid to save. 🚫")
                            return False, base_filename, False
                    except RuntimeError as er:
                            print ("Error: " + err )
                            return False, base_filename, False
                else:
                    if kind.extension == "pdf":
                        base_filename = base_filename + ".pdf"
                        os.rename (local_file_path, local_file_path + ".pdf")
                
                    return True, base_filename, False
            else:
                _log ("Error: Invalid response code of " + str(r.status_code) + "' for " + assetData['external_id'] + "' failed loading from '" + assetData['whitepaper_url'] + "'")
                break

        except requests.exceptions.Timeout:
            # Maybe set up for a retry, or continue in a retry loop
            _log ("Error: Timeout for '" + assetData['external_id'] + "' failed loading from '" + assetData['whitepaper_url'] + "'")
            break

        except requests.exceptions.TooManyRedirects:
            # Tell the user their URL was bad and try a different one
            _log ("Error: TooManyRedirects for '" + assetData['external_id'] + "' failed loading from '" + assetData['whitepaper_url'] + "'")
            break
          
        except requests.exceptions.RequestException:
            # catastrophic error. bail.
            _log ("Error: RequestException for '" + assetData['external_id'] + "' failed loading from '" + assetData['whitepaper_url'] + "'")
            break
    
    return False, "", False

def _getImage(assetData) -> bool:
    """Retreive the image from URL, consider image type."""
    r = None
    if os.path.exists(LOCAL_TEMP_PATH) == False:
         os.makedirs(LOCAL_TEMP_PATH)
    while r==None:
        try:
            file_path = LOCAL_TEMP_PATH + assetData['logo']
            print ("Checking " + assetData['logo_url'])
            # check if we have a logo already in the local images folder.
            if os.path.exists(file_path) == False:
                r = requests.head(assetData['logo_url'])
                if r.status_code == requests.codes.ok:
                    r = requests.get(assetData['logo_url'])
                    with open(file_path, 'wb') as f:  
                        f.write(r.content)
                    print (file_path + " saved. 💥🔫")
                    return True
                else:
                    _log("'" + assetData['external_id'] + "' - (" + assetData['ticker'] + " : '" + assetData['logo'] + "' was not found.\n")
                    return False
            else:
                return True
        except:
            print("_saveImage: Connection refused by the server..")
            time.sleep(5)
            continue

def importAssetsFromSheet (SaveImages=True, SaveDocuments=True, UseLocalCache=True) ->bool:
    """Retreive the image from URL ."""
    client = SheetsuClient(SHEETSU_ID)
    db = None
    if (UseLocalCache):
        try:
            # Do we have a pickle?
            with open("./db.pkl", "rb") as f:
                db = pickle.load(f)
                if (len(db) <= 0):
                    print ("Error: Cache was empty. Please recreate the local cache.")
                    return
        except:
            print ("Reading from Sheetsu...")
            try:
                db = client.read(sheet="DB")
            except RuntimeError as err:
                print ("Error: " + err)
                return

        # Let's pickle the damn DB to save some time.
        with open("./db.pkl", "wb") as f:
            pickle.dump (db, f)
    else:
        print ("Reading from local cache...")
        db = client.read(sheet="DB")
        # Let's pickle the damn DB to save some time.
        with open("./db.pkl", "wb") as f:
            pickle.dump (db, f)

    start_index = SHEET_START_POINT
    print ("Starting at " + str(start_index))
    print (str(len(db)) + " Projects...")
    project_name = ''
    project_count = start_index

    for row in db[start_index:]:
        project_count = project_count + 1
        project_name = row['Project']
        external_id = row['external_id']
        print ("================================")
        print ("Working on '" + external_id + "'")
        print ("================================")
        ticker = row['Ticker']
        image_filename = row['Logo']
        whitepaper_url = row['Documentation']
        # check to see if that's a valid filename or not
        url = TOKEN_LOGOS_URL + image_filename
        assetData = {
            "logo": image_filename, 
            "external_id": external_id, 
            "project_name": project_name,
            "ticker": ticker,
            "logo_url": url,
            "whitepaper_url": whitepaper_url
        }

        if (SaveImages):
            if (image_filename != ''):
                if _getImage(assetData):
                    public_url = uploadToGCPStorage (external_id, image_filename, True)
                    if (public_url):
                        print (public_url)
                    else:
                        continue
        if (SaveDocuments):
            if (whitepaper_url != ''):
                Saved, filename, FileTypeCheck = _getDocument(assetData)
                if (Saved == True):
                    public_url = uploadToGCPStorage (external_id, filename, FileTypeCheck)
                    if (public_url):
                        print (public_url)
                else:
                    continue
            else:
                _log("Error: '" + external_id + "' has no white paper url.")
                continue
        print ("================================")
        print ("👉 " + str(project_count) + " of " + str(len(db)) + " Projects...")
        print ("================================")

    print ("Completed")
    return True
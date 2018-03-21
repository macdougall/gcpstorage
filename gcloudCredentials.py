import sys
from oauth2client.service_account import ServiceAccountCredentials
# Stubbed out for public consumption.  
# Replace with your own JSON generated from ServiceAccount.
creds_dict = {
  "type": "service_account",
  "project_id": "react-187015",
  "private_key_id": "#",
  "private_key": "#",
  "client_email": "#",
  "client_id": "#",
  "auth_uri": "#",
  "token_uri": "https://accounts.google.com/o/oauth2/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "#"
}
credentials = None

try:
  credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict)
except Exception as e:
  print ("Error: GCloud Credentials are invalid with error '" + str(e) + "'")
  sys.exit(0)

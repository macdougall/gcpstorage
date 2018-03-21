# GCP and Google Sheet (via SheetSu) example.

This code will pull data from a Google Sheet using the Sheetsu API.
It will look for specifically a URL to PDF or HTML.

Images are pulled from a URL (you have to set that).

Once saved locally, it will persist it to Google Cloud Storage.
It's meant to be used as a migration or import script that's run periodically.

Just a simple example of the GCP Storage usage and Google Sheets API via Sheetsu.

Requirements:
* GCP Account with a Service Account credentials
* GCloud Python Library
* SheetSu Account (to access Google Sheets)
* Temp folder

Feel free to use as you wish.

# caseTracker

### Run on local machine:

Before you start, you'll need the following:

-   Python 2.6 or greater (Python 3 recommended)
-   Pip/pip3 package management tool (comes standard with Python 2 >= 2.7.9 or Python 3 >= 3.4)

API Setup

* Login to your gmail account and visit the [Google Sheets API QuickStart Guide for Python](https://developers.google.com/sheets/api/quickstart/python)
* Click the blue `Enable Google Sheets API` button
* Select the `Desktop App` and click `Create`
* Click the blue `DOWNLOAD CLIENT CONFIGURATION` button
* Move `credentials.json` to the work directory. 
* Install Google's client library `pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib`

Run the program

`python casetracker.py {targetDirectory}`

Ex: `python casetracker.py /Users/Jean/Documents`


### Run on Colab:
1. Open the `caseTracker.ipynb` file
2. Click the `Open in Colab` button
3. Download the current version of the case tracker from Google drive and place in the `/content` folder (click on File icon in the left sidebar)
3. Click the Play button to the left of the code cell
4. Files will generated in the `/content` folder


### Direct access to the case tracer
1. Create a shortcut by right-click on a case tracker in shared drive
2. Create in your "My Drive"

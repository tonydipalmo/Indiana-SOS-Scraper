Scrapes the Indiana SOS for business information, in the future, we'd like to add additional states to be scrape.

For captcha solving, this script uses 2Captcha - more information on that can be found here: https://pypi.org/project/2captcha-python/

Make sure to update your Chrome Driver path, and 2Captcha API details in the .env file. Finally, install the dependencies required via the requirements.txt file.

Once everything is ready, try running the script using the test.py - if this runs fine, then you're good to  go!

run() will return JSON data of all the businesses found. You can use this data to create CSVs, add to DB, or send to API hooks for further processing.

Do NOT edit values in env file for SEARCH_MATCH and SEARCH_STATUS - more information about these values will be posted soon.

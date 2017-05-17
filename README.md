HouseHunterBot
================
> Use Python, Google Spreadsheet, Google Shortener and CALLR API to automate your apartment search in Paris.

### Synopsis

[Read the related article on the CALLR blog](https://www.callr.com/blog/python-house-hunter-bot/?utm_source=davy&utm_medium=github).

### Install

- create the necessary Google Developers and CALLR accounts to enable access to necessary APIs as described [in the article](https://www.callr.com/blog/python-house-hunter-bot/?utm_source=davy&utm_medium=github)

- install the requirements

- ```
  pip install -r requirements.txt
  ```

- create some environment variables
    - `SPREADSHEET_URL` for URL of the Google Spreadsheet you'll use
    - `LOGIN` and `PASSWORD` for the CALLR API credentials
    - `API_KEY` for the Google API key
    - `PHONE` for your telephone number in [E.164 format](https://en.wikipedia.org/wiki/E.164)

### Usage

Go to [PAP.fr](http://www.pap.fr) and search for an apartment. Save the URL of the result page, and set it as value for the `SEARCH_PAGE` variable in the script.

Run it with the  `python bot.py` command on your console. You should see the results pooring into your Google spreadsheet in near real-time.

Next time you run the bot, if new results not yet in your spreadsheet have appeared, you'll receive an SMS alert for each of them.

### License

MIT


# Maeil-AI

Can't keep up with the daily flood of emails? 

Introducing Mail Assistant, an application that filters out only important emails and provides quick one-line summaries.

### Description

This application fetches important emails from Gmail, summarizes each email, and displays the results using Streamlit for the user interface.

The email content is summarized using the OpenAI API.

Email data is fetched via Gmail API authentication, with the library handling authentication using Google OAuth.

In Google Cloud, the Gmail API is downloaded, and the OAuth client is downloaded and connected in VS Code. Each time the code is modified, the updated OAuth client is used, and the token.json file is used to store authentication information.

### Benefits

Ensures that you do not forget important emails.
Saves time by allowing you to quickly view important emails.

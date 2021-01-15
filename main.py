import requests
from twilio.rest import Client

'''
For a chosen stock, compare closing prices for yesterday and the day before yesterday.
If the stock is up or down 5 %, get articles about a company or an organization related to the stock.
The information is sent through twilio to the desired phone number.
In order to use twilio free trial, you have to SIGN UP and VERIFY your phone number.
For free trial account, messages can be sent only to verify phone numbers.
For more information, please read the documentations at the respective websites.
'''

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"

STOCK_API = "https://www.alphavantage.co/query"
# Generated from website linked --> https://www.alphavantage.co/documentation/.
STOCK_API_KEY = "Your_API_Key"

NEWS_API = "https://newsapi.org/v2/everything"
# Generated from website linked --> https://newsapi.org/docs.
NEWS_API_KEY = "Your_API_Key"

close_price = "4. close"

# Both are generated from twilio website linked --> https://www.twilio.com/
account_sid = "YOUR_SID"
auth_token = "YOUR_TOKEN"

# Parameter are used to authenticate for access to the websites.
stock_parameter = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK,
    "apikey": STOCK_API_KEY,
}
new_parameter = {
    "qInTitle": COMPANY_NAME,
    "apikey": NEWS_API_KEY
}

# Send a request to get stock information.
stock_response = requests.get(url=STOCK_API, params=stock_parameter)
stock_response.raise_for_status()
# Change the response_data in JSON format.
stock_data = stock_response.json()["Time Series (Daily)"]
# Separate dates and their corresponding data.
stock_data_list = [value for (index, value) in stock_data.items()]
stock_data_date = [index for (index, value) in stock_data.items()]
# Get closing prices.
last_day_price = float(stock_data_list[0][f"{close_price}"])
day_b4_last_day_price = float(stock_data_list[1][f"{close_price}"])
# Print to see what the closing prices are.
print(f"Close price for {STOCK} at {stock_data_date[0]} is: ${last_day_price}")
print(f"Close price for {STOCK} at {stock_data_date[1]} is: ${day_b4_last_day_price}")
# Get the difference between closing prices.
difference = last_day_price - day_b4_last_day_price
# Create a placeholder to add up/down emoji later when sending messages.
up_down_emoji = None
if difference > 0:
    up_down_emoji = "🔺"
else:
    up_down_emoji = "🔻"
# Get difference in percentage and round it.
diff_percentage = round((difference / last_day_price) * 100)

# If difference is greater than 5%, get news from website and send the messages to phone.
if abs(diff_percentage) > 5:
    # Access NEWS website with authentication key.
    new_response = requests.get(url=NEWS_API, params=new_parameter)
    article = new_response.json()["articles"]
    # Get the first 3 articles using slicing.
    three_articles = article[:3]
    # Create a variable to hold the message.
    my_articles = [f"{STOCK}: {up_down_emoji}{abs(diff_percentage)}%\n"
                   f"Headline: {article['title']}\n"
                   f"Brief: {article['description']}\n" for article in three_articles]
    client = Client(account_sid, auth_token)
    for article in my_articles:
        message = client.messages \
            .create(
            body=article,
            # Number is not real and just for a reference. Created in Twilio at https://www.twilio.com/
            from_='+1TWILIO_NUMBER',
            # Phone number has to be verified in order to receive the messages.
            to='+1YOUR_NUMBER'
        )
    # Check if messages are successfully sent.
    print(message.status)

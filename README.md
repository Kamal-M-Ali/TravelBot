# TravelBot

## Inspiration
I was interested in working on a chatbot after seeing the things ChatGPT is able to do. In keeping with the theme this year of 'Travel', I thought it would be fun to make a simple chatbot that can provide you with some information on a country.

## What it does
You send a text message to a Twilio number, and after going though some dialogue, it will respond with travel information about the country you're interested in.

## How I built it
I store the datasets (4 .csv files) on an AWS S3 bucket. The chatbot logic is made using AWS Lex V2. According to Amazon its a *"service for building conversational interfaces for applications using voice and text. Amazon Lex V2 provides the deep functionality and flexibility of natural language understanding (NLU) and automatic speech recognition (ASR) so you can build highly engaging user experiences with lifelike, conversational interactions, and create new categories of products."* I also do all the data parsing and send the "country travel report" using the Python library pandas from a AWS Lambda function. The SMS text integration is done with Twilio.

## Challenges I ran into
I initially wanted the chat bot to respond to various individual questions while remembering the specific country being talked about. I tried for a while to mess around with the TravelBot's "contexts" (which I think this is how you're supposed to accomplish it). I even tried, mid-project, to switch to Google's implementation of a similar software: Dialogflow. However, I could not get either to work in the time I had. I've also never worked with any cloud service before. I spent many hours bug fixing things that would probably have been a very quick fix had I any previous knowledge on AWS. In the end I spent a lot of time fumbling around learning about webhooks/cloud services. 

The bug/challenge that took me the longest to fix was: Why were my travel reports being generated (w/o errors in AWS) but I was seeing nothing in iMessage? Initially, I thought I was hitting a SMS character limit. I eventually narrowed it down to the word "visa." For some reason, whenever I included that word in the text messages everything would break. So that's why the bot says "wisa" instead.

## Accomplishments that I'm proud of
This is my first time attending a hackathon, and I also decided to do a solo project. Managing my time was difficult, but I'm quite happy with how well it turned out, all things considered.

## What I learned
I learned a lot about various different AWS services, and I now have a better understanding of how chat support bots are implemented by various companies. 

## What's next for TravelBot
I thought it would be cool if I added another intent to TravelBot to fetch ticket prices for the country you are interested in.

### Datasets used:
https://github.com/ilyankou/passport-index-dataset <br>
https://ourworldindata.org/explorers/coronavirus-data-explorer <br>
https://ourworldindata.org/explorers/population-and-demography <br>
https://www.kaggle.com/datasets/prasertk/public-holidays-in-every-country-in-2022?resource=download

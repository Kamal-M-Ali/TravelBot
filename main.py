import json
import boto3
import pandas as pd
from datetime import datetime
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def get_holiday_report(report, country, df):
    holidays = df.loc[df["Country"] == country]
    if holidays.empty:
        return f"Failed to get holiday data on {country.capitalize()}.\n"

    nearby = {}
    date_threshold = 4 # in weeks
    today = datetime.now().date()
    
    for holiday, date_string, holiday_type in zip(holidays["Holiday Name"], holidays["Date"], holidays["Type"]):
        date = datetime.strptime(date_string, "%Y-%m-%d").date().replace(year=today.year)
        if date < today: 
            continue # holiday in the past
        diff = date - today

        if diff.days > (date_threshold*7):
            break # no more holidays will be in range, data is sorted

        #nearby[0]=holiday type
        #nearby[1]=how many days until
        #nearby[2]=how long it lasts
        if holiday in nearby:
            nearby[holiday][2] += 1
        else:
            nearby[holiday] = [holiday_type, diff.days, 1]

    holiday_report = ""
    if nearby:
        holiday_report = f"Within the next {date_threshold} weeks:\n"
        count = 1

        for holiday, info in nearby.items():
            if info[1] == 0:
                holiday_report += f"{count}. [{info[0]}] {holiday} starts today!"
            else:
                holiday_report += f"{count}. [{info[0]}] {holiday} starts in {info[1]} days"

            if info[2] > 1: 
                #lasts for more than 1 day
                holiday_report += f". It will last for {info[2]} days!"
            
            holiday_report += '\n'
            count += 1
    else:
        holiday_report = f"Holidays: None within the next {date_threshold} weeks\n"
    
    return holiday_report

def get_passport_report(report, country, df):
    visa = df.loc[df["destination"] == country]
    if visa.empty:
        return f"Failed to get passport data on {country}.\n"

    passport_report = "Passport information:\n"
    response_map = {
        "visa free": "This country has wisa-free travel\n",
        "visa on arrival": "This country grants wisas on arrival (basically wisa-free)\n",
        "e-visa": "This country accepts an e-wisa.\n",
        "visa required": "A wisa is required to visit this country.\n",
        "covid ban": "This country has covid restriction on people incoming from the U.S.\n",
        "no admission": "This country is not accepting visitors.\n",
    }

    req = visa["req"].values[0]
    if req in response_map:
        passport_report += f"{response_map[req]}"
    else:
        if int(req) < -1:
            passport_report = "" # they're inside the us
        else:
            passport_report += f"You get {req} wisa free days.\n"
    
    return passport_report

def get_population_report(report, country, df):
    population = df.loc[df["Country name"] == country]
    if population.empty:
        return f"Failed to get population data on {country}.\n"

    population_report = "Populaton data (2021):\n"
    total_population = population['Population'].values[0]

    population_report += f"<20: {(population[['Population of children under the age of 1', 'Population aged 1 to 4 years', 'Population aged 5 to 9 years', 'Population aged 10 to 14 years', 'Population aged 15 to 19 years']].values.sum() / total_population)*100:.2f}%\n"
    population_report += f"20-60: {(population[['Population aged 20 to 29 years', 'Population aged 30 to 39 years', 'Population aged 40 to 49 years', 'Population aged 50 to 59 years']].values.sum() / total_population)*100:.2f}%\n"
    population_report += f"60-99: {(population[['Population aged 60 to 69 years', 'Population aged 70 to 79 years', 'Population aged 80 to 89 years', 'Population aged 90 to 99 years']].values.sum() / total_population)*100:.2f}%\n"
    population_report += f"100+: {population['Population older than 100 years'].values[0]:,.0f} people\n"
    population_report += f"Total population: {total_population:,}\n"

    return population_report

def get_covid_report(report, country, df):
    covid = df.loc[df["country"] == country]
    if covid.empty:
        return f"Failed to get covid data on {country}.\n"

    covid_report = "Covid data (as of Feb 3. 2023):\n"
    covid_report += f"Cases: {covid['total_cases'].values[0]:,.0f} (total) and {covid['new_cases'].values[0]:,.0f} (new)\n"
    covid_report += f"Cases (per million): {covid['total_cases_per_million'].values[0]:,.0f} (total) and {covid['new_cases_per_million'].values[0]:,.0f} (new)\n"
    covid_report += f"Deaths: {covid['total_deaths'].values[0]:,.0f} (total) and {covid['new_deaths'].values[0]:,.0f} (new)\n"
    covid_report += f"Deaths (per million): {covid['total_deaths_per_million'].values[0]:,.0f} (total) and {covid['new_deaths_per_million'].values[0]:,.0f} (new)\n"
    covid_report += f"ICU Patients: {covid['icu_patients'].values[0]:,.0f} (total) and {covid['icu_patients_per_million'].values[0]:,.0f} (per million)\n"
    covid_report += f"Hospital Patients: {covid['hosp_patients'].values[0]:,.0f} (total) and {covid['hosp_patients_per_million'].values[0]:,.0f} (per million)\n"
    covid_report += f"People vaccinated: {covid['people_vaccinated'].values[0]:,.0f}\n"
    covid_report += f"People fully vaccinated: {covid['people_fully_vaccinated'].values[0]:,.0f}"

    return covid_report

def lambda_handler(event, context):
    logger.debug('## EVENT')
    logger.info(event)
    
    s3 = boto3.resource('s3')
    bucket = s3.Bucket('travelbotdata')
    dataset = {}
    
    for summ in bucket.objects.all():
        dataset[summ.key.split('.',1)[0]] = pd.read_csv(summ.get()['Body'])
        
    country = event["sessionState"]["intent"]["slots"]["Country"]["value"]['interpretedValue'].lower()
    report = f"Travel Report on {country.capitalize()}:\n\n"
    report += get_holiday_report(report, country, dataset['holidays']) + '\n'
    report += get_passport_report(report, country, dataset['passport']) + '\n'
    report += get_population_report(report, country, dataset['population']) + '\n'
    report += get_covid_report(report, country, dataset['owid-covid-latest']) + '\n'
    report += "\n*nan represents unavailable data"
    
    logger.info(report)
    
    return {
        "sessionState": {
            "dialogAction": {
                "type": "Close",
            },
            "intent": {
                "name": "TravelIntent",
                "state": "Fulfilled"
            }
        },
        "messages": [
            {
                "contentType": "PlainText",
                "content": report
            }
        ]
    }

from django.shortcuts import render
from crop_recommend.views import get_weather
from community.views import HomeView,ArticleDetailView
from community.models import Post
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
import plotly.graph_objects as go



# Create your views here.
def home(request):
    location='India'
    data=get_weather(location)
    weather_description = data['days'][0]['conditions']
    temperature = data['days'][0]['temp']
    humidity = data['days'][0]['humidity']
    wind_speed = data['days'][0]['windspeed']
    current_date = datetime.now()
    day_of_week = current_date.strftime('%A')  
    
    df = pd.read_csv('models/goods_prices1.csv')
    fig = go.Figure(data=[
        go.Bar(name='MSP for 2022-2023', x=df['crops'], y=df['MSP for 2022-2023']),
        go.Bar(name='MSP for 2023-2024', x=df['crops'], y=df['MSP for 2023-2024'])
    ])
    fig.update_layout(title='An Overview of the Minimum Support prices of major crops given by the Government of India', xaxis_title='Crops', yaxis_title='Price')
    plot_html = fig.to_html(include_plotlyjs='cdn')
    
    blog_posts=Post.objects.all()
    
    return render(request,'home/index.html',{'temperature':temperature,'humidity':humidity,'wind_speed':wind_speed,'day_of_week':day_of_week,'weather_description':weather_description,'plot_html':plot_html,'blog_posts':blog_posts})
    
    # return render(request,'home/index.html',{})

def scrape_data():
    # Define the URL of the webpage to scrape
    url = "https://vikaspedia.in/agriculture/market-information/minimum-support-price"

    # Send an HTTP request to the URL
    response = requests.get(url)

    # Parse the HTML content of the page
    soup = BeautifulSoup(response.content, 'html.parser')

    # Locate the HTML table
    table = soup.find('table')

    # Initialize lists to hold the data
    crop = []
    variety=[]
    prices1 = []
    prices2 = []

    # Iterate through the rows of the table
    for row in table.find_all('tr'):
        # Get the columns (td elements) in each row
        cols = row.find_all('td')
        if len(cols) >= 3:
            # Get the good, price, and year from the columns
            good = cols[0].text.strip()
            varieties=cols[1].text.strip()
            price1 = cols[2].text.strip().replace('$', '')
            price2=cols[3].text.strip()
            
            # Append data to lists
            crop.append(good)
            variety.append(varieties)
            prices1.append(price1)
            prices2.append(price2)

    # Create a DataFrame from the data
    df = pd.DataFrame({
        'crops': crop,
        'variety':variety,
        'MSP for 2022-2023': prices1,
        'MSP for 2023-2024': prices2,
    })

    # Save the data to a CSV file (optional)
    df.to_csv('models/goods_prices.csv', index=False)
    
    
def plot_graph(request):
    if request.method=='POST':
        crop=request.POST['crop']
        scrape_data()
        # Load the data
        df = pd.read_csv('models/goods_prices.csv')
        # Plot the data
        # sns.set_theme(style="whitegrid")
        df.set_index('crops', inplace=True)
        price1 = int(df.loc[crop, 'MSP for 2022-2023'] if crop in df.index else None)
        
        price2 = int(df.loc[crop, 'MSP for 2023-2024'] if crop in df.index else None)

        years=['MSP for 2022-2023','MSP for 2023-2024']
        prices=[price1,price2]
        fig = go.Figure(data=[go.Bar(x=years, y=prices, name='Data')])
        fig.update_layout(title='Price of '+str(crop)+' over the years', xaxis_title='Price Over the years', yaxis_title='Prices')

        # Convert plotly graph to HTML
        plot_html = fig.to_html(include_plotlyjs='cdn')
        
        return render(request, 'home/plot.html', {'plot_html': plot_html})


        

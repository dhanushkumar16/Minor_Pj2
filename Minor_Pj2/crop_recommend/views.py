from django.shortcuts import render
import requests
import pandas as pd
import joblib

def crop_recommend(request):
    if request.method=='POST':
        location=request.POST['location']
        sub_division=request.POST['sub-division']
        weather_data=get_weather(location)
        
        ## Required Weather attributes
        weather_description = weather_data['days'][0]['conditions']
        temperature = weather_data['days'][0]['temp']
        humidity = weather_data['days'][0]['humidity']
        wind_speed = weather_data['days'][0]['windspeed']
        
        df=pd.read_csv('models/state_mean_rainfall.csv')
        df.set_index('State', inplace=True)
        mean_rainfall = df.loc[sub_division, 'Mean_Rainfall'] if sub_division in df.index else None
        
        new_data=[[temperature,humidity,mean_rainfall]]
        clf = joblib.load('models/decision_tree_model.pkl')
        prediction=clf.predict(new_data)

        
        ## to get the season
        
        df1=pd.read_csv('models/crop_season.csv')
        df1.set_index('Crop',inplace=True)
        season=df1.loc[prediction[0],'Season'] if prediction[0] in df1.index else None
        
        df2=pd.read_csv('models/crop_fertilizer.csv')
        df2.set_index('Crop', inplace=True)
        fertilizer = df2.loc[prediction[0], 'Fertilizer'] if prediction[0] in df2.index else None
        
        df3=pd.read_csv('models/water_requirements.csv')
        df3.set_index('Crop', inplace=True)
        water = df3.loc[prediction[0], 'Water_Requirement'] if prediction[0] in df3.index else None
        
        
        return render(request,'crop_recommend/crop_recommend.html',{'prediction':prediction[0],'season':season,'fertilizer':fertilizer,'water':water})
    else:
        return render(request,'crop_recommend/crop_recommend.html',{})
        
        
def get_weather(location):
    api_key = "J7VLNDNH5T8WF6EHLQE6UCCJS"
    url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{location}"
    params = {
        'unitGroup': 'metric',
        'key': api_key
    }
    response = requests.get(url, params=params)
    data = response.json()
    if response.status_code == 200:
        weather_description = data['days'][0]['conditions']
        temperature = data['days'][0]['temp']
        humidity = data['days'][0]['humidity']
        wind_speed = data['days'][0]['windspeed']

        # print(f"Weather in {location}:")
        # print(f"Description: {weather_description}")
        # print(f"Temperature: {temperature}°C")
        # print(f"Humidity: {humidity}%")
        # print(f"Wind Speed: {wind_speed} m/s")
        return data
    else:
        print("Failed to retrieve weather data. Please check your input and try again.")
        
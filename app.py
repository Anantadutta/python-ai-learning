import os
from dotenv import load_dotenv
from google import genai
import time
from google.genai import errors
import requests
from datetime import datetime

def get_weather(city: str) -> dict: #line 68 and city:str tells what kind of input is expected 
    """Fetches current weather for a given city using Open-Meteo (free, no API key)."""
    # Step 1: convert city name to latitude/longitude
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
    geo_response = requests.get(geo_url).json()

    if "results" not in geo_response:
        return {"error": f"Could not find city: {city}"}

    location = geo_response["results"][0]
    lat, lon = location["latitude"], location["longitude"]

    #actual calling of weather api using the coordinates 
    weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true" #tells api that just give me rn conditions and not a 7 day forecast
    weather_response = requests.get(weather_url).json()

    current = weather_response["current_weather"]

    weather_data = {
        "city": city,
        "temperature_celsius": current["temperature"],
        "windspeed_kmh": current["windspeed"],
        "weather_code": current["weathercode"],
        "timestamp": datetime.now().isoformat()
    } # my own dict 

    # prints the data to console 
    print("\n[LOG - Structured Data]:", weather_data, "\n")

    return weather_data # sends this dict back to whatever function called it . 

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

system_prompt = """
You are TripEase's AI-powered travel assistant.

Your job is to:
1. Greet the customer warmly and naturally when the conversation starts. 
   If their name is known, use it. Avoid robotic or repetitive greetings.
2. Help customers with weather-related travel queries only 
   (e.g., "What's the weather in Manali?" or "Should I carry an umbrella to Goa?").
3. Identify the city being referred to, even if mentioned indirectly or informally.
4. If the customer asks anything unrelated to greetings or weather 
   (e.g., booking flights, unrelated general questions), politely decline 
   and redirect them back to weather-related help.
5. You do NOT have real-time weather knowledge yourself. Whenever a weather 
   query is made, you MUST use the get_weather tool to fetch current data 
   instead of guessing or making up numbers.

Keep your tone friendly, helpful, and concise.
"""

chat = client.chats.create(
    model="gemini-3.6-flash",
    config={
        "system_instruction": system_prompt,
        "tools": [get_weather] # get weather becomes the tool name 
    }
)

def send_with_retry(chat, message, max_retries=3):
    for attempt in range(max_retries):
        try:
            return chat.send_message(message)
        except errors.ServerError:
            if attempt < max_retries - 1:
                print("(Server busy, retrying...)")
                time.sleep(3)
            else:
                raise

print("TripEase Assistant is ready! Type 'exit' to quit.\n")

while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        print("Bot: Thanks for chatting with TripEase. Have a safe trip!")
        break

    response = send_with_retry(chat, user_input)
    print("Bot:", response.text)
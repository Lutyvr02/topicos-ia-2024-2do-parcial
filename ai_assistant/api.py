from fastapi import FastAPI, Depends, Query
from llama_index.core.agent import ReActAgent
from ai_assistant.agent import TravelAgent
from ai_assistant.models import AgentAPIResponse
from ai_assistant.tools import ( 
    reserve_flight,
    reserve_bus,
    reserve_hotel,
    reserve_restaurant,
)
import json
from ai_assistant.config import get_agent_settings
from ai_assistant.utils import custom_serializer
from datetime import datetime

def get_agent() -> ReActAgent:
    return TravelAgent().get_agent()


app = FastAPI(title="AI Agent")


@app.get("/recommendations/places")
def recommend_cities(
    city: str ,notes: list[str] = Query(...), agent: ReActAgent = Depends(get_agent)
):
    prompt = f"""first of all the context will be based on the country named bolivia, 
    then you will have a city with the name: {city}, after the given name of the city 
    you should do a recomendation to places to go in the city, 
    You should recommend places to go given the city you received and the notes that are these: {notes}, if the
    notes are empty recommend the more popular places in the city {city}"""
    return AgentAPIResponse(status="OK", agent_response=str(agent.chat(prompt)))

@app.get("/recommendations/hotels")
def recommend_hotels(
    city: str, notes: list[str] = Query(None), agent: ReActAgent = Depends(get_agent)
):
    prompt = f"""first of all the context will be based on the country named bolivia, given the city {city}
                then you will have a city with the name: {city}, you should look for hotel recommendations that 
                are on the city {city} and based on the notes 
                {notes} that will be given to you, if the notes are ampty just show the more popular
                hotels in the city {city}"""
    return AgentAPIResponse(status="OK", agent_response=str(agent.chat(prompt)))

@app.get("/recommendations/activities")
def recommend_activities(
    city: str, notes: list[str] = Query(None), agent: ReActAgent = Depends(get_agent)
):
    prompt = f"""first of all the context will be based on the country named bolivia, given the city {city} you 
                then you will have a city with the name: {city}, you
                should look for activities to do in the city of {city}, remember show recomendations based in the notes {notes}, 
                if the notes are empty just show the more popular activities in the city {city}, answers in spanish"""
    return AgentAPIResponse(status="OK", agent_response=str(agent.chat(prompt)))


'''---------------------------------------------------------------------------------'''

@app.post("/reservations/flight")
def reserve_flight_api(
    date: str, departure: str, destination: str
):
    reservation = reserve_flight(date, departure, destination)
    return {"status": "OK", "reservation": reservation.dict()}

@app.post("/reservations/bus")
def reserve_bus_api(
    date: str, departure: str, destination: str
):
    reservation = reserve_bus(date, departure, destination)
    return {"status": "OK", "reservation": reservation.dict()}

@app.post("/reservations/hotel")
def reserve_hotel_api(
    checkin_date: str, checkout_date: str, hotel_name: str, city: str
):
    reservation = reserve_hotel(checkin_date, checkout_date, hotel_name, city)
    return {"status": "OK", "reservation": reservation.dict()}

@app.post("/reservations/restaurant")
def reserve_restaurant_api(
    reservation_time: str, restaurant: str, city: str
):
    reservation = reserve_restaurant(reservation_time, restaurant, city)
    return {"status": "OK", "reservation": reservation.dict()}


@app.get("/trip/report")
def trip_report(agent: ReActAgent = Depends(get_agent)):
    SETTINGS = get_agent_settings()
    log_file = SETTINGS.log_file

    try:
        # Leer el archivo de log
        with open(log_file, "r") as file:
            reservations = json.load(file)
        
        # Organizar actividades por lugar y fecha
        activities_by_location = {}
        total_cost = 0

        for reservation in reservations:
            location = reservation.get("destination") or reservation.get("city")
            date = reservation.get("date") or reservation.get("checkin_date") or reservation.get("reservation_time")

            if location not in activities_by_location:
                activities_by_location[location] = []

            activities_by_location[location].append({
                "date": date,
                "details": reservation
            })

            total_cost += reservation.get("cost", 0)

        # Generar un resumen del presupuesto y el reporte
        summary = f"Total budget: {total_cost} USD\n"
        report = summary + "\nDetails:\n"

        for location, activities in activities_by_location.items():
            report += f"\nLocation: {location}\n"
            for activity in activities:
                report += f"- Date: {activity['date']} - Details: {activity['details']}\n"
        
        # Usar el agente para agregar comentarios
        prompt = f"""Based on the following travel plan:
        {report}
       you should generate a detailed trip report based on the activity log file. 
       The report must include all activities organized by place and date, 
       as well as a summary of the total budget and comments on the places and activities carried out.
        """
        agent_response = agent.chat(prompt)

        # Extraer solo el atributo 'response' del objeto resultante
        return {
            "status": "OK",
            "recommendations": agent_response.response  # Ajuste aquí para acceder directamente al atributo 'response'
        }

    except Exception as e:
        return {
            "status": "ERROR",
            "message": str(e)
        }

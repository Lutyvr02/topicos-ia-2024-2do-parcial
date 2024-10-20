from random import randint
from datetime import date, datetime, time
from llama_index.core.tools import QueryEngineTool, FunctionTool, ToolMetadata
from ai_assistant.rags import TravelGuideRAG
from ai_assistant.prompts import travel_guide_qa_tpl, travel_guide_description
from ai_assistant.config import get_agent_settings
from ai_assistant.models import (
    TripReservation,
    TripType,
    HotelReservation,
    RestaurantReservation,
)
from ai_assistant.utils import save_reservation

SETTINGS = get_agent_settings()

travel_guide_tool = QueryEngineTool(
    query_engine=TravelGuideRAG(
        store_path=SETTINGS.travel_guide_store_path,
        data_dir=SETTINGS.travel_guide_data_path,
        qa_prompt_tpl=travel_guide_qa_tpl,
    ).get_query_engine(),
    metadata=ToolMetadata(
        name="travel_guide", description=travel_guide_description, return_direct=False
    ),
)


# Tool functions
def reserve_flight(date_str: str, departure: str, destination: str) -> TripReservation:
    """
    Make a flight reserve given the date, departure and destination.
    """
    print(
        f"Making flight reservation from {departure} to {destination} on date: {date}"
    )
    reservation = TripReservation(
        trip_type=TripType.flight,
        departure=departure,
        destination=destination,
        date=date.fromisoformat(date_str),
        cost=randint(200, 700),
    )

    save_reservation(reservation)
    return reservation


flight_tool = FunctionTool.from_defaults(fn=reserve_flight, return_direct=False)

# Reserva de bus
def reserve_bus(date_str: str, departure: str, destination: str) -> TripReservation:
    """
    Make a bus reservation with date, origin and destination.
    """
    print(f"Making bus reservation from {departure} to {destination} on date: {date_str}")
    reservation = TripReservation(
        trip_type=TripType.bus,
        departure=departure,
        destination=destination,
        date=date.fromisoformat(date_str),
        cost=randint(20, 150),
    )
    save_reservation(reservation)
    return reservation

bus_tool = FunctionTool.from_defaults(fn=reserve_bus, return_direct=False)

# Reserva de hotel
def reserve_hotel(checkin_date: str, checkout_date: str, hotel_name: str, city: str) -> HotelReservation:

    """
    Make a hotel reservation given check-in and check-out dates, hotel name and city.
    """
    print(f"Making hotel reservation at {hotel_name} in {city} from {checkin_date} to {checkout_date}")
    reservation = HotelReservation(
        checkin_date=date.fromisoformat(checkin_date),
        checkout_date=date.fromisoformat(checkout_date),
        hotel_name=hotel_name,
        city=city,
        cost=randint(100, 500),
    )
    save_reservation(reservation)
    return reservation

hotel_tool = FunctionTool.from_defaults(fn=reserve_hotel, return_direct=False)

# Reserva de restaurante
def reserve_restaurant(reservation_time_str: str, restaurant: str, city: str) -> RestaurantReservation:
    """
    Make a restaurant reservation given a date, time, restaurant and city.
    """
    reservation_time = datetime.fromisoformat(reservation_time_str)
    print(f"Making restaurant reservation at {restaurant} in {city} on {reservation_time}")
    reservation = RestaurantReservation(
        reservation_time=reservation_time,
        restaurant=restaurant,
        city=city,
        cost=randint(20, 100),
    )
    save_reservation(reservation)
    return reservation

restaurant_tool = FunctionTool.from_defaults(fn=reserve_restaurant, return_direct=False)

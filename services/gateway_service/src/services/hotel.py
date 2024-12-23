from src.services.base import BaseServiceClient
from src.schemas.hotel import HotelResponseSchema, HotelPaginationSchema
from src.config import Config


class HotelService(BaseServiceClient):
    def __init__(self):
        super().__init__()
        self.base_url = Config.RESERVATION_SERVICE_URL
        self.hotel_schema = HotelResponseSchema()
        self.pagination_schema = HotelPaginationSchema()

    def get_hotel(self, hotel_uid):
        return self.circuit_breaker_request("hotel", "GET", f"{self.base_url}/hotels/{hotel_uid}", schema=self.hotel_schema)

    def get_hotels(self, page, size):
        return self.circuit_breaker_request("hotel", "GET", f"{self.base_url}/hotels", params={"page": page, "size": size}, schema=self.pagination_schema)

from abc import ABC


class BaseScheduleService(ABC):
    def get_schedule(self, date, *args, **kwargs):
        raise Exception(f"Abstract method not implemented")


class FlightScheduleService(BaseScheduleService):
    def get_schedule(self, date, *args, **kwargs):
        dep = kwargs['dep']
        arr = kwargs['arr']
        depDate = kwargs['depDate']
        departure_time_range = kwargs['departure_time_range']

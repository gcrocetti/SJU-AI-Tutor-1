from tutor.common.DBManager import DBManager
import time

class Event():
    def __init__(self, user_id, event_type, event_value):
        self.user_id = user_id
        self.event_type = event_type
        self.event_value = event_value
        self.timestamp = int(time.time())

    def get_event_as_json(self):
        return {
                'user_id': self.user_id,
                'event_type': self.event_type,
                'event_value': self.event_value,
                'timestamp': self.timestamp
            }

class UserManager():

    @staticmethod
    def store_event(event: Event):
        db = DBManager('user_history')

        try:
            # Attempt to write the event to the database
            db.write_item(event.get_event_as_json())
            return True  # Return True if the write operation succeeds
        except Exception as e:
            # <TO DO: Instead of print the error use the Logger>
            print(f"Failed to store event: {e}")  # Logging can be replaced with a logging framework
            return False  # Return False if there is an exception


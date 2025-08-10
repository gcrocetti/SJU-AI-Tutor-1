import os
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from tutor.graph.config import AWS_REGION
class DBManager:
    def __init__(self, table_name):
        self.table_name = table_name
        self.dynamodb = boto3.resource(
            'dynamodb',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=AWS_REGION
        )
        self.table = self.dynamodb.Table(table_name)

    def write_item(self, item):
        """Write a new item to the DynamoDB table."""
        try:
            response = self.table.put_item(Item=item)
            return response
        except (BotoCoreError, ClientError) as error:
            print(f"Error writing item: {error}")
            return None

    def read_item(self, key):
        """Read a single item using its key."""
        try:
            response = self.table.get_item(Key=key)
            return response.get('Item')
        except (BotoCoreError, ClientError) as error:
            print(f"Error reading item: {error}")
            return None

    def query_items(self, key_condition_expression, expression_attribute_values):
        """Query multiple items using a KeyConditionExpression."""
        try:
            response = self.table.query(
                KeyConditionExpression=key_condition_expression,
                ExpressionAttributeValues=expression_attribute_values
            )
            return response.get('Items', [])
        except (BotoCoreError, ClientError) as error:
            print(f"Error querying items: {error}")
            return []

    def delete_item(self, key):
        """Delete an item from the table using its key."""
        try:
            response = self.table.delete_item(Key=key)
            return response
        except (BotoCoreError, ClientError) as error:
            print(f"Error deleting item: {error}")
            return None


class DBManagerSingleton:
    _instances = {}

    @classmethod
    def get_instance(cls, table_name):
        if table_name not in cls._instances:
            cls._instances[table_name] = DBManager(table_name)
        return cls._instances[table_name]

from boto3.dynamodb.conditions import Key
from tutor.common.DBManager import DBManager

db = DBManager('gc_test_table')

# Write an item
db.write_item({'id': '1234', 'name': 'Jane', 'age': 30})

# Read an item
item = db.read_item({'id': '1234', 'name': 'Jane'})
print(item)

# Query items
items = db.query_items(
    key_condition_expression=Key('id').eq('123'),
    expression_attribute_values={':id': '123'}
)
print(items)

# Delete item
db.delete_item({'id': '123'})

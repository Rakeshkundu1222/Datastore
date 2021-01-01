# Datastore
The methods of class Datastore(from datastore.py) are described below.
## Datastore.create(key, json[, time])
#### Parameters:
key: string, length of less than 32.
<br/>
json: string, json max size 16KB.
<br/>
time: float, time to live(seconds) for the created entry.

#### Returns:
Returns True if successful otherwise raises suitable error.


## Datastore.read(key)
#### Parameters:
key: string, length of less than 32

#### Returns:
Returns the stored json if successful otherwise raises suitable error.

## Datastore.delete(key)
#### Parameters:
key: string, length of less than 32

#### Returns:
Returns True if successful otherwise raises suitable error.

## Example
```python
from datastore import Datastore

datastore = Datastore('database.db')
key = "test_key"
json = '{"name":"value"}'
# time = 100

# create entry
# datastore.create(key, json, time)
datastore.create(key, json)

# read the entry
retrieved_data = datastore.read(key)

print(retrieved_data)

# delete the entry
datastore.delete(key)


```

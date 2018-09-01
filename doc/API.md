
## Item Catalog API Documentation

The Item Catalog API provides access to information about catalog items.

### Endpoint URI

http://localhost:5000/catalog.json/

### HTTP Method

GET

### Query Parameters

None

### Response format

The API responds with the *application/json* content­type. A successful response from the API endpoint is a JSON object  with the following format:

```json
[
  {
    "id": 1, 
    "items": [
      {
        "creation_date": "Sat, 01 Sep 2018 16:23:00 GMT", 
        "description": "Lorem ipsum dolor sit amet, ut in dui sagittis pellentesque fusce ultrices, massa est blandit, amet leo tortor amet ligula, interdum pellentesque. Mauris in ridiculus gravida. Aliquam et donec nunc, dignissim sed enim nam aliquam fusce odio, in arcu rhoncus molestiae bibendum, pede erat distinctio a lacus ullamcorper pharetra, fermentum nunc. Ac blandit sed mollis mauris, est nullam ligula. Enim quis habitasse enim et.", 
        "id": 1, 
        "name": "Ball"
      }
    ], 
    "name": "Soccer"
  }, 
  {
    "id": 2, 
    "items": [
      {
        "creation_date": "Sat, 01 Sep 2018 16:23:00 GMT", 
        "description": "Lorem ipsum dolor sit amet, ut in dui sagittis pellentesque fusce ultrices, massa est blandit, amet leo tortor amet ligula, interdum pellentesque. Mauris in ridiculus gravida. Aliquam et donec nunc, dignissim sed enim nam aliquam fusce odio, in arcu rhoncus molestiae bibendum, pede erat distinctio a lacus ullamcorper pharetra, fermentum nunc. Ac blandit sed mollis mauris, est nullam ligula. Enim quis habitasse enim et.", 
        "id": 2, 
        "name": "Googles"
      }, 
      {
        "creation_date": "Sat, 01 Sep 2018 16:23:00 GMT", 
        "description": "Lorem ipsum dolor sit amet, ut in dui sagittis pellentesque fusce ultrices, massa est blandit, amet leo tortor amet ligula, interdum pellentesque. Mauris in ridiculus gravida. Aliquam et donec nunc, dignissim sed enim nam aliquam fusce odio, in arcu rhoncus molestiae bibendum, pede erat distinctio a lacus ullamcorper pharetra, fermentum nunc. Ac blandit sed mollis mauris, est nullam ligula. Enim quis habitasse enim et.", 
        "id": 3, 
        "name": "Snowboard"
      }
    ], 
    "name": "Snowboarding"
  }
]
```
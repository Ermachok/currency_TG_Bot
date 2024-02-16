from database.common.models import db, History
from database.core import crud
from site_API.siteAPI_core import headers, params, site_api, url

db_write = crud.create()
db_read = crud.retrieve()

currency_list = site_api.get_currency_list()
response = currency_list(url, headers, timeout=3)
response = response.json()
#print(response)

data = [{"message": response[0], "currency": response[1]}]

db_write(db, History, data)

course = site_api.get_course()

response = course(url, headers, params, timeout=3)
response = response.json()
#print(response)

#data = [{"number": response.get("year"), "message": response.get("text")}]

#db_write(db, History, data)

#retrieved = db_read(db, History, History.number, History.message)

#for element in retrieved:
    #print(element.number, element.message)

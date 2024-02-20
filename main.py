from database.common.models import db, History
from database.core import crud
from site_API.siteAPI_core import headers, site_api, url

#db_write = crud.create()
#db_read = crud.retrieve()

currency_list = site_api.get_currency_list()
response = currency_list(url, headers, timeout=3)
response = response.json()
print(response[3])
#db_write(db, History, {'name':'wad', 'from_currency':'awdwd', 'to_currency':'dgdfg'})

course = site_api.get_course()

#retrieved = db_read(db, History, History.from_currency, History.to_currency)

#for element in retrieved:
 #   print(element.currency, element.message)

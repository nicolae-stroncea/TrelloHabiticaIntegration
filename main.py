##########################
############################
# Append today's date if all integration was successful to the file
# https://stackoverflow.com/questions/16511337/correct-way-to-try-except-using-python-requests-module
# https://stackoverflow.com/questions/47144606/requests-how-to-tell-if-youre-getting-a-success-message
'''
try:
 self.raise_for_status()
except requests.exceptions.RequestException as e:
  return False
'''
###########################
############################
import trelloPart as tp
import habiticaPart as hp
import user_details as ud
from datetime import datetime
import datetime

# get the list of dictionaries each representing an action that took place in the list
jsonList = tp.get_response_as_jsonList(ud.idOfList, ud.trello_apiKey, ud.trello_apiToken)
# get only the valid cards that have been finished since the last time app was ran.
validJsonElements = tp.get_done_cards_json(jsonList, ud.idOfList)
# send each card
counter = 0
while counter<len(validJsonElements):
 jsonElement = validJsonElements[counter]
 cardName = jsonElement.get("data").get("card").get("name")
 priority = tp.find_difficulty_level(cardName)
 (status_code1, status_code2) = hp.create_and_score_task(ud.habitica_user_key, ud.habitica_api_token, jsonElement, priority)
 # if 200<=status_code<400: check if successful
 counter +=1
# if at least one card was sent and scored on habitica, log the date, so that next time
# app will only take cards after this date.
if(len(validJsonElements) > 0):
 # log the date
 f = open('_date_run_last.txt', 'a+')  # open file to read
 # write the current date
 fmt = '%Y-%m-%dT%H-%M-%S'
 ## get time now in UTC time
 now = datetime.datetime.utcnow()
 date_now=now.strftime(fmt) + "\n"
 f.write(date_now)
 f.close() 



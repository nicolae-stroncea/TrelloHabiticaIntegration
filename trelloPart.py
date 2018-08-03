import requests
import json
import pytz

from datetime import datetime
import datetime
import dateutil.parser
import datetime as dt
from pytz import timezone
from datetime import timedelta  


def get_response_as_jsonList(idOfList, apiKey, apiToken):
    '''get the string which represents a list of json objects.
    Each json object represents an action that took place in the list with additional data about it.
    Convert the response to a list of dictionaries each representing an object.'''
    
    url = "https://api.trello.com/1/lists/" + idOfList + "/" + "actions"
    # put the id of the list in the url
    querystring = {"key": apiKey, "token": apiToken}
    
    # send the request
    response = requests.request("GET", url, params=querystring)
    textResponse = response.text[1:-1]
    # process the string that we get. convert it into a list of json objects
    counter = 0;
    listOfJson=[]
    jsonString=""    
    i=0
    while i<len(textResponse):
        char = textResponse[i]
        # add the character to the json String
        jsonString+=char
        if char =="{":
            counter+=1;
        elif char=="}":
            counter-=1;     
            # if it's at 0, that means everything previously was one complete json object
            # convert the json to a dictionary, add it to the list of json
        if counter == 0:    
            jsonObj=json.loads(jsonString)
            listOfJson.append(jsonObj)
            jsonString=""
            # if the next character right after this is a comma, then iterate i by one more,
            # so that we skip the comma and start with the next json object
            if(i+1)<len(textResponse): 
                if textResponse[i+1]==",":
                    i+=1;   
        i+=1       
    return listOfJson    

def get_done_cards_json(jsonList, idOfList):
    '''Return the json objects which contain the cards which were finished since the last time software was ran.'''
    # get the last time the integration took place, as we will only consider cards that happened after that.
    last_date = last_time_run()
    # if this is the first time integration takes place, take date as the date the list was created
    if len(last_date) == 0:
        # it's the last json object in the list
        listCreatedJson = jsonList[-1]
        dateListCreated = listCreatedJson.get("date")
        # convert to date object from string
        last_date = dateutil.parser.parse(dateListCreated)
    else: # last_date is in string format
        # convert the string to a dateTime object
        last_date = datetime.datetime.strptime(last_date, '%Y-%m-%dT%H-%M-%S' )
        # make the datetimeobject take into consideration time zone
        utc=pytz.UTC        
        last_date= utc.localize(last_date)
        
    validJsonElements=[]
    # iterate through every action, and check if a card has been moved to this list.
    # if it has, check the date for it. If it is the right date, add it to the list.
    # Date is in ISO 8601 format
    for jsonElement in jsonList:
        dataDictionary = jsonElement.get("data")
        # check if it has a key with listAfter. If it does, that means the card has changed lists.
        checkIfItemMove = dataDictionary.get("listAfter", None)
        if(checkIfItemMove!=None):
            idOfCurrentList = checkIfItemMove.get("id")
            # check if it's been moved here rather than from here, i.e if it has the same id as this list
            if idOfCurrentList==idOfList:
                nameOfCardMoved = dataDictionary.get("card").get("name")
                # get the date the card was moved
                dateOfCardMoved = jsonElement.get("date")
                # convert to date object                
                dateCardFinished = dateutil.parser.parse(dateOfCardMoved)
                # if the card was finished since the last date, then add the card to the list.
                if dateCardFinished > last_date:
                    validJsonElements.append(jsonElement)
    return validJsonElements


def find_difficulty_level(cardName):
    # difficulty level will be between brackets.
    indexOpenBracket = cardName.find("(")
    indexClosedBracket = cardName.find(")")
    if(indexOpenBracket!=-1 and indexClosedBracket!=-1):
        # if they're in the right order
        if(indexOpenBracket<indexClosedBracket):
            difficulty_level=cardName[indexOpenBracket+1:indexClosedBracket]
            # convert to lower case
            difficulty_level = difficulty_level.lower()
            # strip spaces
            difficulty_level = difficulty_level.strip()
            if("hard" in difficulty_level or "****" in difficulty_level):
                as_number= 2
            elif("medium" in difficulty_level or "***" in difficulty_level):
                as_number= 1.5            
            elif("trivial" in difficulty_level or "**" in difficulty_level):
                as_number= 0.1
            else: # consider the task easy
                as_number=1
        else:
            as_number=1
    else: # consider the task easy, which is 1
        as_number=1
    return str(as_number)


            
def last_time_run():
    '''Reads a file which stores the dates the integration took place.
    If integration has never taken place before, sends an empty string.'''
    file_name = '_date_run_last.txt'
    try: # in case it doesn't exist
        with open(file_name, "r") as f:
            all_lines = f.readlines()
            if(len(all_lines) != 0):
                last_date = all_lines[-1]
                # strip the newline character
                last_date = last_date[:-1]
            else:
                last_date = ""
            f.close()
    except IOError:
        last_date = ""
    return last_date
import requests
import json
from datetime import datetime
import datetime



def create_and_score_task(user_key, api_token, cardJson, priority):
    '''create and score the task on habitica, and returns the status code. Function logs the status codes to a file.'''
    
    # Create the task
    data = {
        "text": cardJson.get("data").get("card").get("name"),
        "type": "todo",
        "priority":priority,
        "alias": cardJson.get("id")
    }
    
    url = "https://habitica.com/api/v3/tasks/user"
    
    querystring = {"x-api-user":user_key,"x-api-key":api_token}
    
    response = requests.request("POST", url, headers=querystring, data = data)
    # get the status code to create the task
    status_code1 = response.status_code
    reason1 = response.reason
    
    
    url = "https://habitica.com/api/v3/tasks/" + cardJson.get("id") + "/score/up"

    querystring = {"x-api-user":user_key,"x-api-key":api_token}
    
    response = requests.request("POST", url, headers=querystring)
    
    # get the status code to score the task
    status_code2 = response.status_code
    reason2 = response.reason
    
    file_name = 'requests_to_habitica.txt'
    f = open(file_name, 'a+')  # open file in append mode
    fmt = '%Y-%m-%dT%H-%M-%S'
    # get time now in UTC time
    now = datetime.datetime.utcnow()
    date_now=now.strftime(fmt)    
    new_string = "Create Task: " + str(status_code1) + ", " + reason1 + ", Score Task: " + str(status_code2) + ", " + reason2 +  ", " + "date_today: " + date_now + ",  " + "card_name: "+  data.get("text") + "\n"
    f.write(new_string)
    f.close()    
    
    return (status_code1, status_code2)


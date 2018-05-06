'''
client id#  ae74622c-81cb-410d-a4a0-ab94c0e03a2e
client secret t0pZlh93Bprgn6JUvOJofca6F
auth url   https://home.nest.com/login/oauth2?client_id=ae74622c-81cb-410d-a4a0-ab94c0e03a2e&state=STATE

 https://home.nest.com/cameras/ae74622c-81cb-410d-a4a0-ab94c0e03a2e?auth=c.tTwDnxdnToHZrpWnhk5iH4q3JEebhvbeLqitUnsbyBgSupaWkrYlvX1b4374SwVi19akENZsFCmi8RG3AhiquFSpeTjtxtC93rIL1DFoLd69sWoJcPTbh0XXFv2esuVqJmP9eachNAw2wN7J
 https://home.nest.com/cameras/oauth2?client_id=ae74622c-81cb-410d-a4a0-ab94c0e03a2e&state=STATE





curl -v -L -H "Content-Type: application/json" -H "Authorization:  Bearer c.tTwDnxdnToHZrpWnhk5iH4q3JEebhvbeLqitUnsbyBgSupaWkrYlvX1b4374SwVi19akENZsFCmi8RG3AhiquFSpeTjtxtC93rIL1DFoLd69sWoJcPTbh0XXFv2esuVqJmP9eachNAw2wN7J" -X GET "https://developer-api.nest.com"


curl -X POST "https://api.home.nest.com/oauth2/access_token?client_id=ae74622c-81cb-410d-a4a0-ab94c0e03a2e&;code=2HNWPWSP&;client_secret=t0pZlh93Bprgn6JUvOJofca6F&;grant_type=authorization_code"

"access_token":"c.tTwDnxdnToHZrpWnhk5iH4q3JEebhvbeLqitUnsbyBgSupaWkrYlvX1b4374SwVi19akENZsFCmi8RG3AhiquFSpeTjtxtC93rIL1DFoLd69sWoJcPTbh0XXFv2esuVqJmP9eachNAw2wN7J","expires_in":315360000}

curl -L https://developer-api.nest.com/devices/cameras\?auth\=c.tTwDnxdnToHZrpWnhk5iH4q3JEebhvbeLqitUnsbyBgSupaWkrYlvX1b4374SwVi19akENZsFCmi8RG3AhiquFSpeTjtxtC93rIL1DFoLd69sWoJcPTbh0XXFv2esuVqJmP9eachNAw2wN7J

"device_id":"aKftwtb142trLSdvl87kPZxJokmXYmriK-jpahONPvB9Veuc8C1zMA",
"structure_id":"fuKIvBdMtxwTut_mDJiyAOL1LMm80TcWFoPQEnq94kU-3koZlc9D5Q",

curl -X GET "https://developer-api.nest.com/devices/cameras/aKftwtb142trLSdvl87kPZxJokmXYmriK-jpahONPvB9Veuc8C1zMA?auth="c.tTwDnxdnToHZrpWnhk5iH4q3JEebhvbeLqitUnsbyBgSupaWkrYlvX1b4374SwVi19akENZsFCmi8RG3AhiquFSpeTjtxtC93rIL1DFoLd69sWoJcPTbh0XXFv2esuVqJmP9eachNAw2wN7J"


https://home.nest.com/cameras/CjZhS2Z0d3RiMTQydHJMU2R2bDg3a1BaeEpva21YWW1yaUstanBhaE9OUHZCOVZldWM4QzF6TUESFmVrZjNxUGFoUDlCb09oYkJvamhmT3caNlZJWHNyaU10dHQ4Z0VBX0VSSy1LZEhaNFpiN2k3Yy1CWHMtaGxLMzNZbVI0T0tQWk01T3UzQQ?auth=1754l4cwfwHXnMoxb_C6XRYnHugwOZMfHwnaMkUNG7FcRywGCJl2TQgxfREBLIAW4iFwBlvEjTvcCP_waFZUqkJ1eYPi7CZkhhwMe5H9fKJ47jcHy4ZwQl9d2FYYXRf2aIenFDhkOzM9pybLWMJVO2CtbQL7izDgEWuCdDY4DYzin65kEEWmHSlLMe9tZBUR0D7rfSIz-IrZxw
'''



import requests
import http.client
from urllib.parse import urlparse
import time
import boto3
import datetime
import hashlib
import time

#AWS Info
ACCESS_KEY= "AKIAJVR3DFLUAJLFZKWA"
SECRET_KEY = "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"

#S3 Info
S3_REGION="us-east-1"
BUCKET = 'e88-final'
credentials = {"aws_access_key_id" : ACCESS_KEY, "aws_session_access_key" : SECRET_KEY}


#Nest Cam Info
TOKEN = "c.tTwDnxdnToHZrpWnhk5iH4q3JEebhvbeLqitUnsbyBgSupaWkrYlvX1b4374SwVi19akENZsFCmi8RG3AhiquFSpeTjtxtC93rIL1DFoLd69sWoJcPTbh0XXFv2esuVqJmP9eachNAw2wN7J"
DEVICE_ID= "aKftwtb142trLSdvl87kPZxJokmXYmriK-jpahONPvB9Veuc8C1zMA"
HEADERS =  {'authorization': "Bearer {0}".format(TOKEN)}

#returns live stream url
def live_stream(device_id, token, headers):
    uri = "/devices/cameras/{0}/web_url".format(device_id)
    conn = http.client.HTTPSConnection("developer-api.nest.com")
    conn.request("GET", uri, headers = headers)
    response = conn.getresponse()

    if response.status == 307:
        redirectLocation = urlparse(response.getheader("location"))
        conn = http.client.HTTPSConnection(redirectLocation.netloc)
        conn.request("GET", uri, headers=headers)
        response = conn.getresponse()
        if response.status != 200:
            raise Exception("Redirect with non 200 response")

    data = response.read()
    data = data.decode("utf-8")
    return(data)


#returns snapshot url
def snapshot_url(device_id, token, headers):
    uri = "/devices/cameras/{0}/snapshot_url".format(device_id)
    conn = http.client.HTTPSConnection("developer-api.nest.com")
    conn.request("GET", uri,  headers=headers)
    response = conn.getresponse()

    if response.status == 307:
        redirectLocation = urlparse(response.getheader("location"))
        conn = http.client.HTTPSConnection(redirectLocation.netloc)
        conn.request("GET", uri, headers=headers)
        response = conn.getresponse()
        if response.status != 200:
            raise Exception("Redirect with non 200 response")

    data = response.read()
    data = data.decode("utf-8")
    return(data)



#take a snapshot every {delay} seconds
def get_snap(s3):
    url = snapshot_url(DEVICE_ID, TOKEN, HEADERS)
    url = url.strip("\"")
    img_data = requests.get(url).content
    #unique hash for image name from current time
    hash = hashlib.sha1()
    cur_time = str(time.time())
    cur_time = cur_time.encode("utf-8")
    hash.update(cur_time)
    name = hash.hexdigest()
    img_name = 'snap_' + name + '.jpg'
    s3.put_object(Bucket=BUCKET, Key=img_name, Body=img_data)
    print('oh snap!')




#producer of snapshots from video
def snap_producer(delay,max,file):
    for snap in range(1,max+1):
        get_snap(file)
        time.sleep(delay)
    print('finished')


if __name__ == "__main__":
    #create connection s3 bucket to store snaps
    s3 = boto3.client(service_name ='s3', region_name = S3_REGION, aws_access_key_id = ACCESS_KEY,
                      aws_secret_access_key = SECRET_KEY)
    snap_producer(1, 5, s3)



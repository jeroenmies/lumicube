import requests
import json
import zipfile
import io
from requests.auth import HTTPBasicAuth

apiBase = "https://slack.com/api/"
#see secrets.md for token details
accesToken = "Bearer <slack-api-key>"

succeededColour = green
erroredColour = 0xffc099
abortedColour = 0x66481f
pausedColour = blue
pinnedColour = purple
failedColour = red
pendingColour = white
startedColour = yellow

alternate = True
isError = False

monitoredPipeLines = [
                      "wp-ontwikkel-osraoa",
                      "wp-integration-osraoa",
                      "aoa-design-system-osraoa",
                      "aoa-docker-osraoa",
                      "dummy",
                      "dummy",
                      "dummy",
                      "dummy",
                      "dummy",
                    #   "aoa-gateway-osraoa",
                    #   "aoa-usermanagement-osraoa",
                    #   "aoa-usermanagement-app-osraoa",
                    #   "wp-draat-osraoa",
                    #   "wp-file-store-osraoa",
                    #   "wp-projectmanagement-osraoa",
                    #   "wp-project-app-osraoa",
                      "aoa-common-java-osrpraoa",
                      "aoa-gateway-osrpraoa",
                      "aoa-usermanagement-osrpraoa",
                      "aoa-usermanagement-app-osrpraoa",
                      "wp-draat-osrpraoa",
                      "wp-file-store-osrpraoa",
                      "wp-projectmanagement-osrpraoa",
                      "wp-project-app-osrpraoa"
                      ]
monitoredSpecial = ["aoa-docker", "gdr-proxy-osraoa"]
monitoredJobs = [
    "trigger",                            #0
    "build-and-test",                     #1
    "deploy-ontwikkel",                   #2
    "deploy-e2e",                         #3
    "webportal-e2e",                      #4
    "webportal-e2e-full",                 #5
    "deploy-e2e-pr",                      #6
    "deploy-test",                        #7
    "deploy-acceptance",                  #8
    "deploy-production",                  #9
    "recreate-dependabot-pull-requests",  #10
    "pr-pre-build-and-test",              #11
    "pr-build-and-test",                  #12
    "pr-e2e-test",                        #13
    "pr-merge",                           #14
    "notify-new-version",                 #15
    "docker-build-aoa-concourse",         #16
    "docker-build-aoa-e2e"]               #17
checkDelay = 10
checkDelayCount = checkDelay

data = {}
def animate():
    global alternate
    global isError
    for location in data:
        if('next' in data[location]):
            if(alternate):
                display.set_led(location[0], location[1], getColour(data[location]['next']))
            else:
                display.set_led(location[0], location[1], getColour(data[location]['current']))
    if(isError):
        if(alternate):
            display.set_panel('top', [[red, red, red, red, red, red, red, red],
                                   [red, red, red, red, red, red, red, red],
                                   [red, red, red, red, red, red, red, red],
                                   [red, red, red, red, red, red, red, red],
                                   [red, red, red, red, red, red, red, red],
                                   [red, red, red, red, red, red, red, red],
                                   [red, red, red, red, red, red, red, red],
                                   [red, red, red, red, red, red, red, red]])
        else:
            display.set_panel('top', [[black, black, black, black, black, black, black, black],
                                   [black, black, black, black, black, black, black, black],
                                   [black, black, black, black, black, black, black, black],
                                   [black, black, black, black, black, black, black, black],
                                   [black, black, black, black, black, black, black, black],
                                   [black, black, black, black, black, black, black, black],
                                   [black, black, black, black, black, black, black, black],
                                   [black, black, black, black, black, black, black, black]])
    alternate = not alternate

def getData():
    global isError
    requestData = { "channel": "C04B02K7RA6" }
    r = requests.post(apiBase + "files.list", headers={'Authorization': accesToken, 'Content-Type': 'application/json'}, data=json.dumps(requestData))
    response = json.loads(r.text)
    screen.draw_rectangle(0,50, 320, 240, black)

    if(not 'files' in response):
        if('error' in response):
            screen.write_text(0,50, response['error'], 1, white, red)
        if('warning' in response):
            screen.write_text(0,75, response['warning'], 1, white, orange)
        isError = True
        return False
    files = response['files']
    files.sort(key=lambda x:x['timestamp'])
    count = len(files)
    if(count > 0):
        try:
            display.set_all(black)
            time.sleep(0.2)
            data.clear()
            for x in range(0, count):
                recentFile = files[count - x - 1]
                if(recentFile['name'] == 'concourse-status.zip'):
                    break;

            requestPath = recentFile['url_private_download']
            r = requests.get(requestPath, headers={'Authorization': accesToken})

            for x in range(0, count):
                file = files[x]
                requestData = { "file": file['id'] }
                req = requests.post(apiBase + "files.delete", headers={"Authorization": accesToken, "Content-Type": "application/json; charset=utf-8"}, data=json.dumps(requestData))

            z = zipfile.ZipFile(io.BytesIO(r.content))
            jobListText = z.read('concourse-status.json')
            jobsJson = json.loads(jobListText)

            pipelines = {}

            if(jobsJson):
                isError = False
                for job in jobsJson:
                    pipelineName = job["pipeline_name"]
                    if(pipelineName in monitoredPipeLines):
                        if(pipelineName in pipelines):
                            pipes = pipelines[pipelineName]
                        else:
                            pipes = {}
                            pipelines[pipelineName] = pipes

                        xIndex = monitoredPipeLines.index(pipelineName)

                        jobName = job["name"]

                        if(pipelineName.startswith("aoa-docker")):
                            yIndex:int = monitoredJobs.index(jobName) - 16
                        elif(jobName.startswith("recreate") and jobName in monitoredJobs):
                            yIndex:int = monitoredJobs.index(jobName) - 10
                        elif(jobName.startswith("pr-merge") and pipelineName.startswith("aoa-design-system")):
                            yIndex:int = monitoredJobs.index(jobName) - 11
                        elif(jobName.startswith("build-and-test") and pipelineName.startswith("aoa-design-system-osraoa")):
                            yIndex:int = monitoredJobs.index(jobName) + 4
                        elif(jobName.startswith("notify-new-version") and pipelineName.startswith("aoa-design-system-osraoa")):
                            yIndex:int = monitoredJobs.index(jobName) - 9
                        elif(jobName.startswith("pr") and jobName in monitoredJobs):
                            yIndex:int = monitoredJobs.index(jobName) - 10
                        elif(jobName in monitoredJobs):
                            if(jobName == "monitor-webportal-production"):
                                if(not pipelineName.endswith("osraoa")):
                                    continue
                            yIndex:int = monitoredJobs.index(jobName)
                        else:
                            continue

                        if(not (xIndex, yIndex) in data):
                            data[xIndex, yIndex] = {}

                        if('next_build' in job):
                            if(job['next_build']['status'] == "started"):
                                data[xIndex, yIndex]['next']  = "started"
                                pipes[yIndex] = "started"

                        if(not 'finished_build' in job):
                             data[xIndex, yIndex]['current'] = "pending"
                             pipes[yIndex] = "pending"
                        else:
                             data[xIndex, yIndex]['current'] = job['finished_build']['status']
                             pipes[yIndex] = "pending"
                return True
        except:
            screen.write_text(0,50, 'an error occurred', 1, white, red)
            isError = True
        return False
    return False

def showData():
    for x in range(16):
        for y in range(16):
            if((x, y) in data):
                display.set_led(x, y, getColour(data[x,y]['current']))
                time.sleep(0.1)

def getColour(status):
    if(status == "succeeded"):
        return succeededColour
    elif(status == "errored"):
        return erroredColour
    elif(status == "aborted"):
        return abortedColour
    elif(status == "paused"):
        return pausedColour
    elif(status == "pinned"):
        return pinnedColour
    elif(status == "failed"):
        return failedColour
    elif(status == "pending"):
        return pendingColour
    elif(status == "started"):
        return startedColour
    else:
        return pink

while True:
    if(checkDelayCount >= checkDelay):
        isNewData = getData()
        if(isNewData == True):
            showData()
        checkDelayCount = 0
    checkDelayCount += 1
    animate()
    time.sleep(1)
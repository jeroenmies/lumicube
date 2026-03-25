import requests
import json
import zipfile
import io
import time
from requests.auth import HTTPBasicAuth

apiBase = "https://slack.com/api/"
#see secrets.md for token details
accesToken = "Bearer token"

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
    "wp-all-osraoa",
    "wp-tasks-osraoa",
    "dummy",
    "aoa-docker-osraoa",
    "dummy",
    "aoa-gns-osrpraoa",
    "aoa-gns-osraoa",
    "aoa-gdr-proxy-osraoa",
    "aoa-common-java-osrpraoa",
    "aoa-gateway-osrpraoa",
    "aoa-usermanagement-osrpraoa",
    "wp-draat-osrpraoa",
    "wp-file-store-osrpraoa",
    "wp-projectmanagement-osrpraoa",
    "wp-project-app-osrpraoa",
    "wp-winfrabase-osrpraoa"
    ]
monitoredSpecial = [
    "rdy-to-shutdown-environments",
    "toggle-rdy-to-shutdown-environments",
    "manual-trigger",
    "webportal-sig-upload-daily",
    "gns-sig-upload-daily",
    "bim-provesy-upload-daily",
    "dummy",
    "concourse-monitor",
    "stop-e2e",
    "stop-e2e-pr",
    "stop-e2e-develop",
    "stop-smoketest",
    "stop-ontwikkel",
    "stop-test",
    "stop-acceptance",
    "stop-production",
    "startup-spaces",
    "start-e2e",
    "start-e2e-pr",
    "start-e2e-develop",
    "start-ontwikkel",
    "start-test",
    "start-acceptance",
    "start-production",
    "deploy-pipeline-webportal-tasks",
    "deploy-pipelines",
    "dummy",
    "stop-pr-pipelines",
    "start-pr-pipelines",
    "dummy",
    "redeploy-apps",
    "rebuild-apps",
    "gns-cleardb-ontwikkel",
    "gns-cleardb-test",
    "gns-cleardb-acceptatie",
    "dummy",
    "test-gns-ontwikkel",
    "test-gns-test",
    "test-gns-acc",
    "test-gns-prod"
    ]
monitoredJobs = [
    "build-and-test-develop-draat",
    "build-and-test-develop-file-store",
    "build-and-test-develop-gateway",
    "build-and-test-develop-project-app",
    "build-and-test-develop-ivon",
    "build-and-test-develop-projectmanagement",
    "build-and-test-develop-usermanagement",
    "build-and-test-develop-winfrabase",
    "build-and-test-develop-winfrabase-converter",
    "deploy-develop-draat",
    "deploy-develop-file-store",
    "deploy-develop-gateway",
    "deploy-develop-project-app",
    "deploy-develop-ivon",
    "deploy-develop-projectmanagement",
    "deploy-develop-usermanagement",
    "deploy-develop-winfrabase",
    "deploy-develop-winfrabase-converter",
    "deploy-e2e-develop-draat",
    "deploy-e2e-develop-file-store",
    "deploy-e2e-develop-gateway",
    "deploy-e2e-develop-project-app",
    "deploy-e2e-develop-ivon",
    "deploy-e2e-develop-projectmanagement",
    "deploy-e2e-develop-usermanagement",
    "deploy-e2e-develop-winfrabase",
    "deploy-e2e-develop-winfrabase-converter",
    "trigger-e2e-develop",
    "webportal-e2e-develop",
    "dummy",
    "dummy",
    "redeploy-ontwikkel",
    "build-and-test-draat",
    "build-and-test-file-store",
    "build-and-test-gateway",
    "build-and-test-project-app",
    "build-and-test-ivon",
    "build-and-test-projectmanagement",
    "build-and-test-usermanagement",
    "build-and-test-winfrabase",
    "build-and-test-winfrabase-converter",
    "deploy-e2e-draat",
    "deploy-e2e-file-store",
    "deploy-e2e-gateway",
    "deploy-e2e-project-app",
    "deploy-e2e-ivon",
    "deploy-e2e-projectmanagement",
    "deploy-e2e-usermanagement",
    "deploy-e2e-winfrabase",
    "deploy-e2e-winfrabase-converter",
    "dummy",
    "dummy",
    "dummy",
    "dummy",
    "dummy",
    "dummy",
    "trigger-e2e",
    "webportal-e2e",
    "deploy-pr",
    "deploy-test",
    "deploy-acceptance",
    "deploy-production"
    ]
monitoredPrJobs = [
    "recreate-dependabot-pull-requests",    #0
    "pr-pre-filter",                        #1
    "pr-pre-build-and-test",                #2
    "pr-build-and-test",                    #3
    "pr-e2e-test",                          #4
    "pr-merge",                             #5
    "docker-build-aoa-concourse",           #6
    "docker-build-aoa-e2e",                 #7
    "2docker-build-aoa-concourse-containers" #8
    ]
monitoredGNSJobs = [
    "build-and-test-develop",               #0
    "deploy-ontwikkel",                     #1
    "build-and-test",                       #2
    "smoke-test",                           #3
    "e2e-test",                             #4
    "deploy-e2e-pr",                        #5
    "publish-contracts",                    #6
    "deploy-test",                          #7
    "deploy-acceptance",                    #8
    "deploy-production"                     #9
    ]                    
monitoredGNSPrJobs = [
    "recreate-dependabot-pull-requests",    #0
    "pr-pre-build-and-test",                #1
    "pr-build-and-test",                    #2
    "pr-smoke-test",                        #3
    "pr-e2e-test",                          #4
    "pr-merge"                              #5
    ]                             
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
    requestData = { 'channel': 'C04B02K7RA6' }
    r = requests.post(apiBase + 'files.list', headers={'Authorization': accesToken, 'Content-Type': 'application/json'}, params=requestData)
    try:
        response = json.loads(r.text)
    except:
        display.scroll_text("Read error")
        isError = True
        return False

    if(not 'files' in response):
        if('error' in response):
            screen.write_text(0, 50, response['error'], 1, white, red)
        if('warning' in response):
            screen.write_text(0, 75, response['warning'], 1, white, orange)
        isError = True
        return False
    files = response['files']
    files.sort(key=lambda x:x['timestamp'])
    count = len(files)

    screen.draw_rectangle(0, 50, 320, 240, black)

    screen.write_text(0, 50, str(r.request.url)[28:], 1, white, red)
    screen.write_text(0, 75, str(r), 1, white, red)

    if(count > 0):
        print("Aantal files: " + str(count))
        try:
            screen.write_text(0, 100, str(count)+' files pending', 1, white, red)
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
                # time.sleep(1.2)
                file = files[x]
                requestData = { 'file': file['id'] }
                req = requests.post(apiBase + 'files.delete', headers={'Authorization': accesToken,'Content-Type':'application/x-www-form-urlencoded'}, params=requestData)
                screen.write_text(0, 125, str(req.request.url)[28:], 1, white, red)
                screen.write_text(0, 150, str(req), 1, white, red)

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

                        # Lower y with 9 in the list
                        if(pipelineName.startswith("aoa-docker")):
                            yIndex:int = monitoredPrJobs.index(jobName) + 8     if jobName in monitoredPrJobs else 0
                        # Top panel
                        elif(pipelineName.startswith("wp-tasks")):
                            yIndex:int = monitoredSpecial.index(jobName)%8 + 8  if jobName in monitoredSpecial else 0
                            xIndex = 0 + monitoredSpecial.index(jobName) // 8   if jobName in monitoredSpecial else 0
                        # Bottom left
                        elif(pipelineName.startswith("wp-all")):
                            yIndex:int = monitoredJobs.index(jobName)%8         if jobName in monitoredJobs else 0
                            xIndex = 0 + monitoredJobs.index(jobName) // 8      if jobName in monitoredJobs else 0
                        # Move first task to the bottom of the lights
                        elif(pipelineName.startswith("aoa-gdr-proxy") and jobName.startswith("create")):
                            yIndex:int = 8
                        # Move deploys to the bottom screen
                        elif(pipelineName.startswith("aoa-gdr-proxy")):
                            yIndex:int = monitoredJobs.index(jobName)%8 + 5     if jobName in monitoredJobs else 0
                        elif(pipelineName.startswith("aoa-gns") and jobName in monitoredGNSPrJobs):
                            yIndex:int = monitoredGNSPrJobs.index(jobName) + 8  if jobName in monitoredGNSPrJobs else 0
                        elif(pipelineName.startswith("aoa-gns") and jobName in monitoredGNSJobs):
                            yIndex:int = monitoredGNSJobs.index(jobName) + 8    if jobName in monitoredGNSJobs else 0
                        elif(jobName in monitoredPrJobs):
                            if(pipelineName.endswith("osrpraoa")):
                                yIndex:int = monitoredPrJobs.index(jobName)     if jobName in monitoredPrJobs else 0
                        elif(jobName in monitoredJobs):
                            if(not pipelineName.endswith("osraoa")):
                                continue
                            yIndex:int = monitoredJobs.index(jobName)           if jobName in monitoredJobs else 0
                        else:
                            continue
                        
                        # Move T,A,P deploys to the bottom screen and 1 column to the right
                        if(pipelineName.startswith("aoa-gns")):
                            if(yIndex > 14):
                                xIndex = xIndex + 1
                                yIndex = yIndex - 2

                        if(not (xIndex, yIndex) in data):
                            data[xIndex, yIndex] = {}

                        if (yIndex > 15) or (xIndex > 15):
                            continue

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
            print(exception)
            screen.write_text(0, 50, 'an error occurred', 1, white, red)
            isError = True
        return False
    else:
        screen.write_text(0, 100, 'No files available', 1, white, red)
        return False

def showData():
    for x in range(16):
        for y in range(16):
            if((x, y) in data):
                display.set_led(x, y, getColour(data[x,y]['current']))
                time.sleep(0.05)

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

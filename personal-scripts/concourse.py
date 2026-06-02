import requests
import json
import zipfile
import io
import time
from requests.auth import HTTPBasicAuth

apiBase = "https://slack.com/api/"
#see secrets.md for token details
accesToken = "Bearer token"

# Kleuren definities (Hex-waardes voor de LumiCube)
succeededColour = 0x00ff00  # Groen
erroredColour   = 0xffc099
abortedColour   = 0x66481f
pausedColour    = 0x0000ff  # Blauw
pinnedColour    = 0x800080  # Paars
failedColour    = 0xff0000  # Rood
pendingColour   = 0xffffff  # Wit
startedColour   = 0xffff00  # Geel
black           = 0x000000
red             = 0xff0000
white           = 0xffffff
orange          = 0xffa500

COLOUR_MAP = {
    "succeeded": succeededColour,
    "errored": erroredColour, 
    "aborted": abortedColour,
    "paused": pausedColour, 
    "pinned": pinnedColour, 
    "failed": failedColour,
    "pending": pendingColour, 
    "started": startedColour
}

def getColour(status_string):
    return COLOUR_MAP.get(status_string, white)

# Gemonitorde data configuratie (essentieel voor de juiste x/y positiebepaling)
monitoredPipeLines = [
    "wp-all-osraoa", "wp-tasks-osraoa", "dummy", "aoa-docker-osraoa", "dummy", "aoa-gns-osrpraoa",
    "dummy", "aoa-gdr-proxy-osraoa", "aoa-common-java-osrpraoa", "aoa-gateway-osrpraoa",
    "aoa-usermanagement-osrpraoa", "wp-draat-osrpraoa", "wp-file-store-osrpraoa",
    "wp-projectmanagement-osrpraoa", "wp-project-app-osrpraoa", "wp-winfrabase-osrpraoa"
]

monitoredSpecial = [
    "rdy-to-shutdown-environments", "toggle-rdy-to-shutdown-environments", "manual-trigger", "dummy", "dummy", "dummy", "dummy", "concourse-monitor", "stop-e2e", "stop-e2e-pr", "stop-e2e-develop", "dummy", "stop-ontwikkel", "stop-test", "stop-acceptance", "stop-production", "startup-spaces", "start-e2e", "start-e2e-pr", "start-e2e-develop", "start-ontwikkel", "start-test", "start-acceptance", "start-production", "deploy-pipeline-webportal-tasks", "deploy-pipelines", "dummy", "stop-pr-pipelines", "start-pr-pipelines", "dummy", "redeploy-apps", "rebuild-apps", "gns-cleardb-ontwikkel", "gns-cleardb-test", "gns-cleardb-acceptatie", "dummy", "test-gns-ontwikkel", "test-gns-test", "test-gns-acc", "test-gns-prod"
]

monitoredJobs = [
    "build-and-test-develop-draat", "build-and-test-develop-file-store", "build-and-test-develop-gateway", "build-and-test-develop-project-app", "build-and-test-develop-ivon", "build-and-test-develop-projectmanagement", "build-and-test-develop-usermanagement", "build-and-test-develop-winfrabase", "build-and-test-develop-winfrabase-converter", "deploy-develop-draat", "deploy-develop-file-store", "deploy-develop-gateway", "deploy-develop-project-app", "deploy-develop-ivon", "deploy-develop-projectmanagement", "deploy-develop-usermanagement", "deploy-develop-winfrabase", "deploy-develop-winfrabase-converter", "deploy-e2e-develop-draat", "deploy-e2e-develop-file-store", "deploy-e2e-develop-gateway", "deploy-e2e-develop-project-app", "deploy-e2e-develop-ivon", "deploy-e2e-develop-projectmanagement", "deploy-e2e-develop-usermanagement", "deploy-e2e-develop-winfrabase", "deploy-e2e-develop-winfrabase-converter", "trigger-e2e-develop", "webportal-e2e-develop", "dummy", "dummy", "redeploy-ontwikkel", "build-and-test-draat", "build-and-test-file-store", "build-and-test-gateway", "build-and-test-project-app", "build-and-test-ivon", "build-and-test-projectmanagement", "build-and-test-usermanagement", "build-and-test-winfrabase", "build-and-test-winfrabase-converter", "deploy-e2e-draat", "deploy-e2e-file-store", "deploy-e2e-gateway", "deploy-e2e-project-app", "deploy-e2e-ivon", "deploy-e2e-projectmanagement", "deploy-e2e-usermanagement", "deploy-e2e-winfrabase", "deploy-e2e-winfrabase-converter", "dummy", "dummy", "dummy", "dummy", "dummy", "dummy", "trigger-e2e", "webportal-e2e", "deploy-pr", "deploy-test", "deploy-acceptance", "deploy-production"
]

monitoredPrJobs = [
    "recreate-dependabot-pull-requests", "pr-pre-filter", "pr-pre-build-and-test", "pr-build-and-test", "pr-e2e-test", "pr-merge", "docker-build-aoa-concourse", "docker-build-aoa-concourse-postgresql", "2docker-build-aoa-concourse-containers"
]

monitoredGNSJobs = [
    "build-and-test-develop", "deploy-ontwikkel", "build-and-test", "smoke-test", "e2e-test", "deploy-e2e-pr", "publish-contracts", "deploy-test", "deploy-acceptance", "deploy-production"
]

monitoredGNSPrJobs = [
    "recreate-dependabot-pull-requests", "pr-pre-build-and-test", "pr-build-and-test", "pr-smoke-test", "pr-e2e-test", "pr-merge"
]

data = {}
pipelines = {}
alternate = True
isError = False
checkDelay = 66
checkDelayCount = checkDelay

def animate():
    global alternate
    if isError:
        error_colour = red if alternate else black
        display.set_panel('top', [[error_colour] * 8] * 8)
    else:
        for (x, y), status_dict in data.items():
            current_colour = getColour(status_dict['next'] if 'next' in status_dict and alternate else status_dict['current'])
            display.set_led(x, y, current_colour)
    alternate = not alternate

def get_job_coordinates(pipeline_name, job_name):
    """Berekent de juiste (x, y) coördinaten voor de LumiCube matrix."""
    # Handmatige override voor de 3 specifieke aoa-docker jobs op (6, 13-15)
    if pipeline_name.startswith("aoa-docker"):
        docker_coordinates = {
            "docker-build-aoa-concourse": (6, 13),
            "docker-build-aoa-concourse-postgresql": (6, 14),
            "2docker-build-aoa-concourse-containers": (6, 15)
        }
        if job_name in docker_coordinates:
            return docker_coordinates[job_name]

    # Bepaal de standaard xIndex op basis van de hoofdlijst
    if pipeline_name not in monitoredPipeLines:
        return None
    x = monitoredPipeLines.index(pipeline_name)
    y = 0

    # Berekening op basis van pipeline-type
    if pipeline_name.startswith("aoa-docker"):
        y = monitoredPrJobs.index(job_name) + 8 if job_name in monitoredPrJobs else 0
        
    elif pipeline_name.startswith("wp-tasks"):
        if job_name in monitoredSpecial:
            idx = monitoredSpecial.index(job_name)
            y = (idx % 8) + 8
            x = idx // 8
            
    elif pipeline_name.startswith("wp-all"):
        if job_name in monitoredJobs:
            idx = monitoredJobs.index(job_name)
            y = idx % 8
            x = idx // 8
            
    elif pipeline_name.startswith("aoa-gdr-proxy") and job_name.startswith("create"):
        y = 8
        
    elif pipeline_name.startswith("aoa-gdr-proxy"):
        y = (monitoredJobs.index(job_name) % 8) + 5 if job_name in monitoredJobs else 0
        
    elif pipeline_name.startswith("aoa-gns"):
        if job_name in monitoredGNSPrJobs:
            y = monitoredGNSPrJobs.index(job_name) + 8
        elif job_name in monitoredGNSJobs:
            y = monitoredGNSJobs.index(job_name) + 8
        else:
            return None
        if y > 14:
            x += 1
            y -= 2
            
    elif job_name in monitoredPrJobs and pipeline_name.endswith("osrpraoa"):
        y = monitoredPrJobs.index(job_name)
        
    elif job_name in monitoredJobs and pipeline_name.endswith("osraoa"):
        y = monitoredJobs.index(job_name)
        
    else:
        return None

    return x, y

def process_jobs(jobsJson):
    """Verwerkt de JSON-input en stuurt de statussen door naar de datamatrix."""
    global data, pipelines
    if not jobsJson:
        return False
        
    for job in jobsJson:
        pipelineName = job.get("pipeline_name", "")
        jobName = job.get("name", "")
        
        coords = get_job_coordinates(pipelineName, jobName)
        if not coords:
            continue
            
        xIndex, yIndex = coords

        # Strakke grenscontrole voor de LumiCube matrix (0 t/m 15)
        if not (0 <= xIndex <= 15 and 0 <= yIndex <= 15):
            continue

        pipes = pipelines.setdefault(pipelineName, {})

        if (xIndex, yIndex) not in data:
            data[xIndex, yIndex] = {}

        if "next_build" in job and job["next_build"].get("status") == "started":
            data[xIndex, yIndex]["next"] = "started"
            pipes[yIndex] = "started"

        status = job["finished_build"].get("status", "pending") if "finished_build" in job else "pending"
        data[xIndex, yIndex]["current"] = status
        pipes[yIndex] = status

    return True

def getData():
    """Haalt bestanden op van Slack, pakt de nieuwste zip uit en verwerkt de JSON."""
    global isError, checkDelayCount
    requestData = {'channel': 'C04B02K7RA6'}
    
    try:
        r = requests.post(
            apiBase + 'files.list', 
            headers={'Authorization': accesToken, 'Content-Type': 'application/json'},
            params=requestData,
            timeout=5
        )
        response = r.json()
    except Exception as e:
        display.scroll_text("Read error")
        print(f"Netwerkfout: {e}")
        isError = True
        return False

    if 'files' not in response:
        if 'error' in response:
            screen.write_text(0, 50, response['error'], 1, white, red)
        if 'warning' in response:
            screen.write_text(0, 75, response['warning'], 1, white, orange)
        isError = True
        return False
        
    files = response['files']
    if not files:
        return False
        
    files.sort(key=lambda x: x['timestamp'])
    latest_file = files[-1]
    
    screen.draw_rectangle(0, 50, 320, 240, black)
    screen.write_text(0, 50, str(r.request.url)[28:], 1, white, red)
    screen.write_text(0, 75, str(r.status_code), 1, white, red)
    
    success = False
    try:
        file_url = latest_file.get('url_private')
        if not file_url:
            return False
            
        file_response = requests.get(
            file_url, 
            headers={'Authorization': accesToken},
            timeout=10
        )
        
        with zipfile.ZipFile(io.BytesIO(file_response.content)) as z:
            for file_info in z.infolist():
                if file_info.filename.endswith('.json'):
                    with z.open(file_info) as f:
                        jobs_json_data = json.load(f)
                        process_jobs(jobs_json_data)
                        isError = False
                        success = True
                        
    except Exception as e:
        screen.write_text(0, 100, f"Zip error: {str(e)[:20]}", 1, white, red)
        print(f"Zip verwerkingsfout: {e}")
        isError = True
        return False

# 2. OPRUIMEN: Als het verwerken is gelukt, verwijder dan alle OUDERE bestanden
    if success and len(files) > 1:
        # Loop door alle bestanden heen, BEHALVE de allerlaatste (die we net gebruikt hebben)
        for old_file in files[:-1]:
            old_file_id = old_file.get('id')
            if old_file_id:
                try:
                    requests.post(
                        apiBase + 'files.delete',
                        headers={'Authorization': accesToken, 'Content-Type': 'application/json'},
                        json={'file': old_file_id},
                        timeout=5
                    )
                    print(f"Oud Slack-bestand verwijderd: {old_file_id}")
                except Exception as e:
                    print(f"Fout bij verwijderen van bestand {old_file_id}: {e}")

    return success


if __name__ == "__main__":
    getData()
    
    while True:
        try:
            animate()
            checkDelayCount -= 1
            if checkDelayCount <= 0:
                getData()
                checkDelayCount = checkDelay
                
            time.sleep(0.15)
        except KeyboardInterrupt:
            print("\nMonitor gestopt.")
            break

import requests
import json
import zipfile
import io
import time
import random
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
    "wp-projectmanagement-osrpraoa", "wp-project-app-osrpraoa", "wp-winfrabase-osrpraoa", "wp-ivon-osrpraoa"
]

monitoredSpecial = [
    "rdy-to-shutdown-environments", "toggle-rdy-to-shutdown-environments", "manual-trigger", "dummy", "dummy", "dummy", "dummy", "concourse-monitor", "stop-e2e", "stop-e2e-pr", "stop-e2e-develop", "dummy", "stop-ontwikkel", "stop-test", "stop-acceptance", "stop-production", "startup-spaces", "start-e2e", "start-e2e-pr", "start-e2e-develop", "start-ontwikkel", "start-test", "start-acceptance", "start-production", "deploy-pipeline-webportal-tasks", "deploy-pipelines", "dummy", "stop-pr-pipelines", "start-pr-pipelines", "dummy", "redeploy-apps", "rebuild-apps", "gns-cleardb-ontwikkel", "gns-cleardb-test", "gns-cleardb-acceptatie", "dummy", "test-gns-ontwikkel", "test-gns-test", "test-gns-acc", "test-gns-prod"
]

monitoredJobs = [
    "build-and-test-develop-draat", 
    "build-and-test-develop-file-store", 
    "build-and-test-develop-gateway", 
    "build-and-test-develop-ivon", 
    "build-and-test-develop-project-app", 
    "build-and-test-develop-projectmanagement", 
    "build-and-test-develop-usermanagement", 
    "build-and-test-develop-winfrabase",
    
    "deploy-develop-draat", 
    "deploy-develop-file-store", 
    "deploy-develop-gateway", 
    "deploy-develop-ivon", 
    "deploy-develop-project-app", 
    "deploy-develop-projectmanagement", 
    "deploy-develop-usermanagement",
    "deploy-develop-winfrabase", 

    "deploy-e2e-develop-draat", 
    "deploy-e2e-develop-file-store", 
    "deploy-e2e-develop-gateway", 
    "deploy-e2e-develop-ivon", 
    "deploy-e2e-develop-project-app", 
    "deploy-e2e-develop-projectmanagement",
    "deploy-e2e-develop-usermanagement", 
    "deploy-e2e-develop-winfrabase",
    
    "trigger-e2e-develop", 
    "webportal-e2e-develop", 
    "dummy", 
    "dummy", 
    "dummy", 
    "dummy", 
    "dummy", 
    "redeploy-ontwikkel",
    
    "build-and-test-draat", 
    "build-and-test-file-store", 
    "build-and-test-gateway", 
    "build-and-test-ivon", 
    "build-and-test-project-app", 
    "build-and-test-projectmanagement", 
    "build-and-test-usermanagement", 
    "build-and-test-winfrabase", 
    
    "deploy-e2e-draat", 
    "deploy-e2e-file-store", 
    "deploy-e2e-gateway", 
    "deploy-e2e-ivon", 
    "deploy-e2e-project-app", 
    "deploy-e2e-projectmanagement", 
    "deploy-e2e-usermanagement", 
    "deploy-e2e-winfrabase", 

    "dummy", 
    "dummy", 
    "dummy", 
    "build-and-test-develop-winfrabase-converter", 
    "deploy-develop-winfrabase-converter", 
    "deploy-e2e-develop-winfrabase-converter", 
    "build-and-test-winfrabase-converter", 
    "deploy-e2e-winfrabase-converter", 
    
    "trigger-e2e", 
    "webportal-e2e", 
    "deploy-pr", 
    "deploy-test", 
    "deploy-acceptance", 
    "deploy-production"
]

monitoredPrJobs = [
    "recreate-dependabot-pull-requests", "pr-pre-filter", "pr-pre-build-and-test", "pr-build-and-test", "pr-e2e-test", "pr-merge", "docker-build-aoa-concourse", "docker-build-aoa-concourse-postgresql", "docker-build-aoa-concourse-containers"
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

vorige_kleuren = {}
geluid_afgespeeld = False 
ververs_alles = True  # Start op True voor de eerste run

# Extra tellers voor het rustige blauwe knipperen (1 seconde interval)
slow_counter = 0
alternate_slow = True

def animate():
    global alternate, alternate_slow, slow_counter, vorige_kleuren, geluid_afgespeeld, ververs_alles
    
    # Update de langzame teller voor blauwe leds (2 loops van 0.5s = 1 seconde)
    slow_counter += 1
    if slow_counter >= 2:
        alternate_slow = not alternate_slow
        slow_counter = 0
    
    if isError:
        error_colour = red if alternate else black
        display.set_panel("right", [[error_colour] * 8] * 8)
        vorige_kleuren.clear()  # Reset LED geheugen bij error status
        ververs_alles = True    # Dwing verversing zodra de error weggaat
        
        if not geluid_afgespeeld:
            try:
                for frequency in range(400, 1200, 100):
                    speaker.tone(frequency, 0.02)
                speaker.say("Pipeline error detected")
            except Exception:
                pass
            geluid_afgespeeld = True
    else:
        geluid_afgespeeld = False
        
        for (x, y), status_dict in data.items():
            status = str(status_dict.get("current", "")).lower()
            
            if "next" in status_dict:
                current_colour = getColour(status_dict["next"] if alternate else status_dict["current"])
            elif status == "started":
                current_colour = startedColour if alternate else black
            # NIEUW: Als de status paused is, knipper rustig blauw
            elif status == "paused":
                current_colour = pausedColour if alternate_slow else black
            else:
                current_colour = getColour(status_dict["current"])
            
            # GEFIXT: Als ververs_alles True is, negeren we het geheugen en sturen we de led ALTIJD aan
            if ververs_alles or vorige_kleuren.get((x, y)) != current_colour:
                display.set_led(x, y, current_colour)
                vorige_kleuren[(x, y)] = current_colour
                
        # Reset de verversingsvlag na de eerste volledige loop
        ververs_alles = False
            
    alternate = not alternate

def process_jobs(jobsJson):
    """Verwerkt de JSON-input en ververst de datamatrix schoon."""
    global data, pipelines, ververs_alles
    if not jobsJson:
        return False
        
    # GEFIXT: Bouw eerst een tijdelijke matrix op zodat animate() nooit een lege data matrix ziet
    tijdelijke_data = {}
    
    for job in jobsJson:
        pipelineName = job.get("pipeline_name", "")
        jobName = job.get("name", "")
        
        coords = get_job_coordinates(pipelineName, jobName)
        if not coords:
            continue
            
        xIndex, yIndex = coords

        if not (0 <= xIndex <= 15 and 0 <= yIndex <= 15):
            continue

        pipes = pipelines.setdefault(pipelineName, {})

        if (xIndex, yIndex) not in tijdelijke_data:
            tijdelijke_data[xIndex, yIndex] = {}

        # NIEUW: Concourse Paused check toegevoegd
        if job.get("paused") == True:
            tijdelijke_data[xIndex, yIndex]["current"] = "paused"
            pipes[yIndex] = "paused"
        else:
            if "next_build" in job and job["next_build"].get("status") == "started":
                tijdelijke_data[xIndex, yIndex]["next"] = "started"
                pipes[yIndex] = "started"

            status = job["finished_build"].get("status", "pending") if "finished_build" in job else "pending"
            tijdelijke_data[xIndex, yIndex]["current"] = status
            pipes[yIndex] = status

    # Wissel de data in één klap om en activeer de geforceerde refresh van stabiele leds
    data = tijdelijke_data
    ververs_alles = True
    return True

def get_job_coordinates(pipeline_name, job_name):
    """
    Berekent exact de (x, y) coördinaten voor de LumiCube volgens DOCUMENTATION.md.
    - Links (x: 0-7, y: 0-7): wp-all-osraoa
    - Rechts (x: 0-7, y: 8-15): wp-tasks-osraoa & aoa-docker (strak in kolom 7)
    - Boven (x: 8-15, y: 0-7): De 8 hoofd -osrpraoa backend pipelines
    """
    p_name = pipeline_name.lower()

    # ==========================================================================
    # 1. RECHTER PANEEL (x: 0-7, y: 8-15) -> Speciale Taken & Docker
    # ==========================================================================
    if "aoa-docker" in p_name:
        # Docker strak onder elkaar in de uiterst rechter kolom (kolom 7)
        docker_coordinates = {
            "docker-build-aoa-concourse": (7, 13),           # DOCKER-A (onder)
            "docker-build-aoa-concourse-postgresql": (7, 14), # DOCKER-B (midden)
            "docker-build-aoa-concourse-containers": (7, 15)  # DOCKER-C (boven)
        }
        return docker_coordinates.get(job_name)

    if "wp-tasks" in p_name:
        if job_name in monitoredSpecial:
            idx = monitoredSpecial.index(job_name)
            
            # Groep 1: Shutdowns (y: 8)
            if idx < 3:
                return (idx, 8)
                
            # Groep 2: E2E Triggers & Stoppen (Aaneengesloten op y: 9 t/m 12)
            elif 7 <= idx <= 10:
                return (3 + (idx - 7), 9)
            elif 12 <= idx <= 15:
                return (3 + (idx - 12), 10)
            elif 16 <= idx <= 19:
                return (3 + (idx - 16), 11)
            elif 20 <= idx <= 23:
                return (3 + (idx - 20), 12)
                
            # Groep 3: Deploys & Rebuilds (Strak in kolom 0 en 1)
            elif idx == 24: return (0, 14)  # deploy-pipeline-webportal-tasks
            elif idx == 25: return (1, 14)  # deploy-pipelines
            elif idx == 27: return (0, 15)  # stop-pr-pipelines
            elif idx == 28: return (1, 15)  # start-pr-pipelines
            elif idx == 30: return (0, 13)  # redeploy-apps
            elif idx == 31: return (1, 13)  # rebuild-apps
                
            # Groep 4: GNS Cleardb (Rij 14) & GNS Tests (Rij 15)
            # Exact uitgelijnd volgens de documentatie-matrix!
            elif 32 <= idx <= 34:  # gns-cleardb (ontwikkel, test, acceptatie)
                return (3 + (idx - 32), 14) # Kolom 3, 4, 5 op rij 14
            elif 36 <= idx <= 39:  # test-gns (ontwikkel, test, acc, prod)
                return (3 + (idx - 36), 15) # Kolom 3, 4, 5, 6 op rij 15
                
        return None

    # ==========================================================================
    # 2. BOVENSTE PANEEL (Top) -> STATISCH BINNEN x: 8-15 en y: 0-7
    # ==========================================================================
    if "osrpraoa" in p_name or any(base in p_name for base in ["aoa-gns", "aoa-common", "aoa-gateway", "aoa-user", "wp-draat", "wp-file", "wp-project"]):
        
        osrpraoa_mapping = [
            "aoa-gns",              # x: 8
            "aoa-common",           # x: 9
            "aoa-gateway",          # x: 10
            "aoa-usermanagement",   # x: 11
            "wp-draat",             # x: 12
            "wp-file-store",        # x: 13
            "wp-projectmanagement", # x: 14
            "wp-project-app"        # x: 15
        ]
        
        xIndex = 15
        for i, base_name in enumerate(osrpraoa_mapping):
            if base_name in p_name:
                xIndex = 8 + i
                break

        y_idx = 0
        if job_name in monitoredPrJobs:
            y_idx = min(monitoredPrJobs.index(job_name), 7)
        elif job_name in monitoredJobs:
            y_idx = min(monitoredJobs.index(job_name), 7)
            
        return (xIndex, y_idx)

    # ==========================================================================
    # 3. LINKER PANEEL (x: 0-7, y: 0-7) -> wp-all-osraoa
    # ==========================================================================
    if "wp-all" in p_name or "osraoa" in p_name:
        if job_name in monitoredJobs:
            idx = monitoredJobs.index(job_name)
            if idx < 8:
                return (0, idx)
            elif idx < 16:
                return (1, idx - 8)
            elif idx < 24:
                return (2, idx - 16)
            elif idx < 32:
                return (3, idx - 24)
            elif idx < 40:
                return (4, idx - 32)
            elif idx < 48:
                return (5, idx - 40)
            elif idx < 56:
                return (6, idx - 48)
            else:
                return (7, min(idx - 56, 7))

    return None


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
                    # requests.post(
                    #     apiBase + 'files.delete',
                    #     headers={'Authorization': accesToken, 'Content-Type': 'application/json'},
                    #     json={'file': old_file_id},
                    #     timeout=5
                    # )
                    print(f"Oud Slack-bestand verwijderd: {old_file_id}")
                except Exception as e:
                    print(f"Fout bij verwijderen van bestand {old_file_id}: {e}")

    return success


if __name__ == "__main__":
    getData()
    laatste_api_check = time.time()
    
    while True:
        animate()
        
        nu = time.time()
        if nu - laatste_api_check >= 60.0:
            getData()
            laatste_api_check = nu
            
        time.sleep(0.5)
        

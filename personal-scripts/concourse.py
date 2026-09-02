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

data = {}
pipelines = {}
isError = False

vorige_kleuren = {}
geluid_afgespeeld = False 
ververs_alles = True  # Start op True voor de eerste run

# --- GLOBALE ANIMATIE VARIABELEN
alternate = True        # Voor de 'next' wissels (0.5s)
alternate_yellow = True # NIEUW: Voor started/geel (2.0s - factor 4 langzamer)
alternate_slow = True   # Voor paused/blauw (1.0s)

slow_counter = 0        # Teller voor blauw
slow_counter_yellow = 0 # NIEUW: Teller voor geel
heartbeat_timer = 0     # NIEUW: Vertrager voor de hartslag (1 stap per seconde)
heartbeat_counter = 0   # De 12 paarsstappen

# ============================================================================
# RECHTERPANEEL CARROUSEL
# ============================================================================

PIPELINE_GROUPS = [
    [
        "aoa-gateway",
        "aoa-usermanagement",
        "wp-file-store",
        "wp-projectmanagement",
        "wp-project-app",
        "wp-winfrabase",
        "wp-ivon",
        "aoa-gns"
    ],
    [
        "aoa-common-java",
        "wp-draat",
        "dummy",
        "dummy",
        "dummy",
        "provesy-asphalt-mixture",
        "provesy-backend-gateway",
        "provesy-contract",
    ],
    [
        "provesy-event",
        "provesy-fme-gateway",
        "provesy-geo-gateway",
        "provesy-ivon-gateway",
        "provesy-master-data",
        "provesy-pavement",
        "provesy-test-section",
        "provesy-warranty"
    ]
]

ALL_CAROUSEL_PIPELINES = {}

for group in PIPELINE_GROUPS:
    for idx, pipeline in enumerate(group):
        ALL_CAROUSEL_PIPELINES[pipeline] = idx
        
active_group = 0

GROUP_SWITCH_SECONDS = 10
GROUP_SWITCH_CYCLES = 20

group_timer = 0

def build_pipeline_column_map():
    global pipeline_column_map

    pipeline_column_map = {
        pipeline: 8 + idx
        for idx, pipeline in enumerate(
            PIPELINE_GROUPS[active_group]
        )
    }
    print(
        f"Active group: {active_group} -> "
        f"{PIPELINE_GROUPS[active_group]}"
    )
        
pipeline_column_map = {} 

build_pipeline_column_map()

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


def get_pipeline_group_position(pipeline_name):
    # Geeft de zichtbare kolom terug voor de huidige actieve groep.
    p_name = pipeline_name.lower()
    for configured_name, col in pipeline_column_map.items():

        if configured_name in p_name:
            return col

    return None
    
def animate():
    global alternate
    global alternate_yellow
    global alternate_slow
    global slow_counter
    global slow_counter_yellow
    global heartbeat_timer
    global heartbeat_counter
    global vorige_kleuren
    global geluid_afgespeeld
    global ververs_alles

    global active_group
    global group_timer

    # ==========================================================
    # TIMER BLAUW (paused)
    # ==========================================================
    slow_counter += 1

    if slow_counter >= 2:
        # indien je paused wilt laten knipperen:
        # alternate_slow = not alternate_slow
        slow_counter = 0

    # ==========================================================
    # TIMER GEEL (started)
    # ==========================================================
    slow_counter_yellow += 1

    if slow_counter_yellow >= 4:
        alternate_yellow = not alternate_yellow
        slow_counter_yellow = 0

    # ==========================================================
    # RECHTERPANEEL CARROUSEL
    # ==========================================================
    group_timer += 1

    if group_timer >= GROUP_SWITCH_CYCLES:
    
        old_group = active_group
    
        # 0 -> 1 -> 2 -> 0 -> 1 -> ...
        active_group = (
            active_group + 1
        ) % len(PIPELINE_GROUPS)
    
        build_pipeline_column_map()
    
        # data opnieuw opbouwen voor deze groep
        getData()

        # rechterpaneel volledig leegmaken
        for x in range(8, 16):
            for y in range(8):
                display.set_led(
                    x,
                    y,
                    black
                )

                vorige_kleuren.pop(
                    (x, y),
                    None
                )
    
        ververs_alles = True
        group_timer = 0

    # ==========================================================
    # ERROR SCREEN
    # ==========================================================
    if isError:
        error_colour = red if alternate else black

        display.set_panel(
            "right",
            [[error_colour] * 8] * 8
        )

        vorige_kleuren.clear()
        ververs_alles = True

        if not geluid_afgespeeld:
            try:
                for frequency in range(400, 1200, 100):
                    speaker.tone(frequency, 0.02)

                speaker.say("Pipeline error detected")
            except Exception:
                pass

            geluid_afgespeeld = True
    else:
        if geluid_afgespeeld:
            try:
                display.set_panel(
                    "right",
                    [[black] * 8] * 8
                )
                vorige_kleuren.clear()
                ververs_alles = True
            except Exception:
                pass

            geluid_afgespeeld = False

        # ======================================================
        # TEKEN ALLE JOBS
        # ======================================================
        for (x, y), status_dict in data.items():
            if x >= 8:
                zichtbare_kolommen = range(8, 16)
                if x not in zichtbare_kolommen:
                    continue
                
            status = str(
                status_dict.get("current", "")
            ).lower()

            next_status = str(
                status_dict.get("next", "")
            ).lower()

            # started -> geel knipperen
            if status == "started" or next_status == "started":
                current_colour = (
                    startedColour
                    if alternate_yellow
                    else getColour(
                        status_dict.get("current")
                    )
                )
            # next status aanwezig
            elif "next" in status_dict:
                current_colour = getColour(
                    status_dict["next"]
                    if alternate
                    else status_dict["current"]
                )
            # paused
            elif status == "paused":
                current_colour = (
                    pausedColour
                    if alternate_slow
                    else black
                )
            # stabiele status
            else:
                current_colour = getColour(
                    status_dict["current"]
                )

            target_x = x

            if (
                ververs_alles
                or vorige_kleuren.get((target_x, y))
                != current_colour
            ):
                display.set_led(
                    target_x,
                    y,
                    current_colour
                )

                vorige_kleuren[(target_x, y)] = current_colour

        # ======================================================
        # HEARTBEAT
        # ======================================================
        heartbeat_timer += 1

        if heartbeat_timer >= 2:
            heartbeat_counter = (
                heartbeat_counter + 1
            ) % 12

            heartbeat_timer = 0

            if heartbeat_counter in (0, 6):
                heartbeat_colour = 0x000000
            elif heartbeat_counter in (1, 11):
                heartbeat_colour = 0x220044
            elif heartbeat_counter in (2, 10):
                heartbeat_colour = 0x5511aa
            elif heartbeat_counter in (3, 9):
                heartbeat_colour = 0x8822ee
            elif heartbeat_counter in (4, 8):
                heartbeat_colour = 0xbb33ff
            else:
                heartbeat_colour = 0x660099

            display.set_led(
                7,
                8,
                heartbeat_colour
            )

            vorige_kleuren[(7, 8)] = heartbeat_colour

        ververs_alles = False

    alternate = not alternate


def process_jobs(jobsJson):
    global data
    global pipelines
    global ververs_alles

    if not jobsJson or not isinstance(jobsJson, dict):
        return False

    tijdelijke_data = {}
    paused_columns = set()

    # --------------------------------------------------------
    # PIPELINES OP PAUSE
    # --------------------------------------------------------
    pipelines_lijst = jobsJson.get("pipelines", [])

    for pipeline in pipelines_lijst:
        p_name = pipeline.get("name", "").lower()
        if pipeline.get("paused") is not True:
            continue

        col = get_pipeline_group_position(p_name)

        if col is not None:
            paused_columns.add(col)

    # --------------------------------------------------------
    # JOBS
    # --------------------------------------------------------
    jobs_lijst = jobsJson.get("jobs", [])

    for job in jobs_lijst:
        if not isinstance(job, dict):
            continue

        pipelineName = job.get("pipeline_name", "")
        jobName = job.get("name", "")

        coords = get_job_coordinates(
            pipelineName,
            jobName
        )

        if coords is None:
            continue

        xIndex, yIndex = coords

        if not (
            0 <= xIndex <= 15
            and
            0 <= yIndex <= 15
        ):
            continue

        pipes = pipelines.setdefault(
            pipelineName,
            {}
        )

        if (xIndex, yIndex) not in tijdelijke_data:
            tijdelijke_data[(xIndex, yIndex)] = {}

        # ----------------------------------------------------
        # PAUSED JOB
        # ----------------------------------------------------
        if job.get("paused") is True:
            tijdelijke_data[(xIndex, yIndex)]["current"] = "paused"

            pipes[yIndex] = "paused"

            col = get_pipeline_group_position(
                pipelineName.lower()
            )

            if col is not None:
                paused_columns.add(col)

            continue

        # ----------------------------------------------------
        # NEXT BUILD
        # ----------------------------------------------------
        next_build = job.get("next_build")

        if (
            next_build
            and
            next_build.get("status") == "started"
        ):
            tijdelijke_data[(xIndex, yIndex)]["next"] = "started"

            pipes[yIndex] = "started"

        # ----------------------------------------------------
        # CURRENT BUILD
        # ----------------------------------------------------
        finished_build = (
            job.get("finished_build")
            or {}
        )

        status = finished_build.get(
            "status",
            "pending"
        )

        tijdelijke_data[(xIndex, yIndex)]["current"] = status

        pipes[yIndex] = status

    # --------------------------------------------------------
    # PAUSE INDICATORS
    # --------------------------------------------------------
    for paused_column in paused_columns:
        tijdelijke_data[(paused_column, 6)] = {
            "current": "paused"
        }

    data = tijdelijke_data
    ververs_alles = True

    return True


def get_job_coordinates(pipeline_name, job_name):
    """
    Berekent exact de (x, y) coördinaten voor de LumiCube volgens DOCUMENTATION.md.
    - Links  (x: 0-7, y: 0-7) : wp-all-osraoa
    - Top    (x: 0-7, y: 8-15): wp-tasks-osraoa & aoa-docker
    - Rechts (x: 8-15, y: 0-7): De 8 hoofd -osrpraoa backend pipelines
    """
    p_name = pipeline_name.lower()

    # ==========================================================================
    # 1. TOP PANEEL (x: 0-7, y: 8-15) -> Speciale Taken & Docker
    # ==========================================================================
    if "aoa-docker" in p_name:
        docker_coordinates = {
            "docker-build-aoa-concourse": (7, 13),            # DOCKER-A (onder)
            "docker-build-aoa-concourse-postgresql": (7, 14), # DOCKER-B (midden)
            "docker-build-aoa-concourse-containers": (7, 15)  # DOCKER-C (boven)
        }
        return docker_coordinates.get(job_name)

    if "aoa-start-apps" in p_name:
        start_apps = {
            "build-and-test-aoa-start-apps": (0, 10),
            "deploy-production": (0, 11)
        }
        return start_apps.get(job_name)

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
    # 2. RECHTER PANEEL
    # ==========================================================================
    if (
        "osrpraoa" in p_name
        or "aoa-gns" in p_name
        or "aoa-common" in p_name
        or "aoa-gateway" in p_name
        or "aoa-usermanagement" in p_name
        or "wp-draat" in p_name
        or "wp-file-store" in p_name
        or "wp-projectmanagement" in p_name
        or "wp-project-app" in p_name
        or "wp-winfrabase" in p_name
        or "wp-ivon" in p_name
        or "provesy" in p_name
    ):

        xIndex = get_pipeline_group_position(
            p_name
        )
        
        if xIndex is None:
            return None
            
        # ------------------------------------------------------
        # Carrousel groep
        # ------------------------------------------------------
        if xIndex is None:
            for pipeline_name, col in pipeline_column_map.items():
                if pipeline_name in p_name:
                    xIndex = col
                    break
                if xIndex is None:
                    return None

        # ------------------------------------------------------
        # Job-naar-rij vertaling
        # ------------------------------------------------------
        y_idx = None

        if job_name in monitoredPrJobs:
            y_idx = min(
                monitoredPrJobs.index(job_name),
                7
            )
        elif job_name in monitoredJobs:
            y_idx = min(
                monitoredJobs.index(job_name),
                7
            )
        elif job_name in monitoredGNSPrJobs:
            y_idx = min(
                monitoredGNSPrJobs.index(job_name),
                7
            )
        elif job_name in monitoredGNSJobs:
            y_idx = min(
                monitoredGNSJobs.index(job_name),
                7
            )

        if y_idx is None:
            return None

        if y_idx == 0:
            print(
                f"GROUP={active_group} "
                f"PIPELINE={pipeline_name} "
                f"X={xIndex}"
            )
        return (xIndex, y_idx)
        
    # ==========================================================================
    # 3. LINKER PANEEL (x: 0-7, y: 0-7) -> wp-all-osraoa
    # ==========================================================================
    if ("wp-all" in p_name or "osraoa" in p_name) and "bp-all-osraoa" not in p_name:
        if job_name in monitoredJobs:
            idx = monitoredJobs.index(job_name)
            if idx < 56:
                return (idx // 8, idx % 8)
            else:
                return (7, min(idx - 56, 7))

    return None


def getData():
    # Haalt bestanden op van Slack, pakt de nieuwste zip uit en verwerkt de JSON.
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
    laatste_api_check = time.time()
    
    while True:
        animate()
        
        nu = time.time()
        if nu - laatste_api_check >= 120.0:
            getData()
            laatste_api_check = nu
            
        time.sleep(0.5)
 

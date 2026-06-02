# 🧊 LumiCube CI/CD Pipeline Monitor - Documentatie

Dit bestand beschrijft de geografische indeling en de matrix-architectuur van de CI/CD-monitor op de **Abstract Foundry LumiCube**. De LumiCube bestaat uit 3 LED-panelen van elk 8x8 pixels (in totaal 192 LED's) die samen een halve kubus vormen.

---

## 🧭 Hardware-adressering & Oriëntatie

Binnen de software-API van de LumiCube worden de panelen aangestuurd via een gecombineerd grid. Omdat de matrix van **beneden naar boven** (verticaal) en van **links naar rechts** (horizontaal) telt, geldt de volgende basisstructuur:
* **Y-as (Verticaal):** Index `0` bevindt zich onderaan (dicht bij de tafel) en `15` is het hoogste punt.
* **X-as (Horizontaal):** Index `0` start uiterst links en `15` bevindt zich uiterst rechts.

### Fysieke Paneelverdeling
1. **Linker Paneel:** `x: 0 tot 7`, `y: 0 tot 7`
2. **Rechter Paneel:** `x: 0 tot 7`, `y: 8 tot 15`
3. **Bovenste Paneel (Top):** `x: 8 tot 15`, `y: 0 tot 7`

---

## 📊 Matrix Overzichten per Paneel

In de onderstaande diagrammen staat de hoogste verticale index (`7` of `15`) **bovenaan** weergegeven. De lege plekken (`.` of `...`) representeren geprogrammeerde inactieve LED's die zorgen voor visuele rust en ademruimte op de kubus.

### 🟩 1. Linker Paneel (`x: 0-7`, `y: 0-7`)
**Inhoud:** Uitsluitend de sub-jobs van de `wp-all-osraoa` pipeline (`monitoredJobs`), overzichtelijk verdeeld in verticale kolommen (straten). De stappen bouwen chronologisch vanaf de onderkant van de kubus omhoog op.

```text
[y:7]  Job 07    Job 15    Job 23    Job 31    Job 39    Job 47    Job 55    Job 63
[y:6]  Job 06    Job 14    Job 22    Job 30    Job 38    Job 46    Job 54    Job 62
[y:5]  Job 05    Job 13    Job 21    Job 29    Job 37    Job 45    Job 53    Job 61
[y:4]  Job 04    Job 12    Job 20    Job 28    Job 36    Job 44    Job 52    Job 60
[y:3]  Job 03    Job 11    Job 19    Job 27    Job 35    Job 43    Job 51    Job 59
[y:2]  Job 02    Job 10    Job 18    Job 26    Job 34    Job 42    Job 50    Job 58
[y:1]  Job 01    Job 09    Job 17    Job 25    Job 33    Job 41    Job 49    Job 57
[y:0]  Job 00    Job 08    Job 16    Job 24    Job 32    Job 40    Job 48    Job 56
       --------------------------------------------------------------------------
       [x:0]     [x:1]     [x:2]     [x:3]     [x:4]     [x:5]     [x:6]     [x:7]


       |------- DEVELOP DEPLOYS -------|       |------- REGULIERE BUILDS ------|
```

---

### 🟦 2. Bovenste Paneel (Top) (`x: 8-15`, `y: 0-7`)
**Inhoud:** De 8 hoofd-backend pipelines (`-osrpraoa`). Elke verticale kolom representeert één complete pipeline. De eerste job in de pijplijn (index 0) start aan de voorrand van de kubus (`y:0`) en bouwt naar achteren (`y:7`) op. Kortere pipelines laten aan de achterzijde automatisch lege LED's (`.`) over.

```text
[y:7]  job 7     job 7     job 7     job 7     job 7     job 7     job 7     job 7
[y:6]  job 6     job 6     job 6     job 6     job 6     job 6     job 6     job 6
[y:5]  job 5     job 5     job 5     job 5     job 5     job 5     job 5     job 5
[y:4]  job 4     job 4     job 4     job 4     job 4     job 4     job 4     job 4
[y:3]  job 3     job 3     job 3     job 3     job 3     job 3     job 3     job 3
[y:2]  job 2     job 2     job 2     job 2     job 2     job 2     job 2     job 2
[y:1]  job 1     job 1     job 1     job 1     job 1     job 1     job 1     job 1
[y:0]  aoa-gns   aoa-comm  aoa-gate  aoa-user  wp-draat  wp-file   wp-proj   wp-proj-app
       --------------------------------------------------------------------------
       [x:8]     [x:9]     [x:10]    [x:11]    [x:12]    [x:13]    [x:14]    [x:15]
```

---

### 🟨 3. Rechter Paneel (`x: 0-7`, `y: 8-15`)
**Inhoud:** `wp-tasks-osraoa` (`monitoredSpecial`) verdeeld in 4 strak gescheiden functionele blokken + de specifieke `aoa-docker` builds in de rechterbovenhoek. 

* *Kolom 2 (`x:2`) en kolom 6 (`x:6, y:15`) fungeren als volledig inactieve buffer-straten voor extra visuele rust.*

```text
[y:15] [stop-pr ] [start-pr]  .  [gns-ontw] [gns-test] [gns-acc ] [gns-prod] [DOCKER-C]
[y:14] [tasks   ] [pipeline]  .  [clear-on] [clear-te] [clear-ac]    .       [DOCKER-B]
[y:13] [redeploy] [rebuild ]  .       .          .          .        .       [DOCKER-A]
[y:12] .         .         .     [-----------------------------------------]
[y:11] .         .         .     [--------- GROEP 2: E2E TESTING ----------]
[y:10] .         .         .     [--------- EN ENVIRONMENT CONTROL --------]
[y:9]  .         .         .     [--------- (TEST / ACC / PROD) -----------]
[y:8]  [-- GR. 1: SHUTDOWN -] .       .          .          .        .       .
       --------------------------------------------------------------------------------
       [x:0]     [x:1]     [x:2] [x:3]      [x:4]      [x:5]      [x:6]      [x:7]
```

#### Legenda van de Functionele Groepen (Rechter Paneel)
* **Groep 1 (Shutdowns):** `x: 0-2, y: 8`. Handmatige triggers en scripts om omgevingen gecontroleerd af te sluiten.
* **Groep 2 (E2E & Environment Control):** `x: 3-6, y: 9-12`. Uitgebreide testomgevingen, e2e controllers en start/stop functionaliteiten voor test, acceptatie en productie.
* **Groep 3 (Deploys & Rebuilds):** `x: 0-1, y: 13-15`. Bevat de pipeline-deploys en app-(re)deploy-stappen onder elkaar.
* **Groep 4 (GNS Cleardb & Tests):** `x: 3-5, y: 14-15`. Database-clears (rij 14) en de bijbehorende functionele tests (rij 15).
* **Docker-Builds (DOCKER):** Gekoppeld aan de rechterbovenhoek. Bestaat uit:
  * `DOCKER-A` (`docker-build-aoa-concourse`) op **`(6, 14)`**
  * `DOCKER-B` (`docker-build-aoa-concourse-postgresql`) op **`(7, 14)`**
  * `DOCKER-C` (`docker-build-aoa-concourse-containers`) op **`(7, 15)`**

---

## 🎨 Kleur- en Statusindicatoren

De monitor vertaalt de CI/CD statusstrings direct naar de volgende hexadecimale kleuren op de kubus:


| Status | Kleur | Hex Waarde | Gedrag bij actieve build (`next_build`) |
| :--- | :--- | :--- | :--- |
| **Succeeded** | 🟩 Groen | `0x00ff00` | Statisch groen |
| **Started** / Running | 🟨 Geel | `0xffff00` | Wisselt elke **0.15 seconden** af met de huidige status |
| **Failed** | 🟥 Rood | `0xff0000` | Statisch rood |
| **Errored** | 🪶 Lichtoranje | `0xffc099` | Statisch lichtoranje |
| **Aborted** | 🟫 Bruin | `0x66481f` | Statisch bruin |
| **Paused** | 🟦 Blauw | `0x0000ff` | Statisch blauw |
| **Pinned** | 🟪 Paars | `0x800080` | Statisch paars |
| **Pending** | ⬜ Wit | `0xffffff` | Statisch wit |

### Foutmodus (`isError`)
Indien het script geen verbinding kan maken met de Slack API of wanneer het gedownloade zip-bestand corrupt is, treedt de **Foutmodus** in werking. Ter notificatie zal het complete **Rechter Paneel** fel rood/zwart gaan knipperen met een interval van 0.15 seconden totdat de verbinding is hersteld.

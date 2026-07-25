# Sprint 003 — Második projekt acceptance bizonyíték

**Dátum:** 2026-07-25
**Cél:** annak bizonyítása, hogy a kanonikus Sprint 003 bootstrap-folyamat egy AI Bridge-től független második projektet is képes regisztrálni és Contexttel ellátni.

## Izolált tesztprojekt és döntés

A tesztprojekt egy ideiglenes, külön Git-repositoryban készült ezen az útvonalon:

```text
C:\Users\User\AppData\Local\Temp\ai-bridge-sprint003-bridge-demo
```

Ez nem fixture, seed vagy a termék-repositoryba felvett tesztprojekt volt. Az izoláció szükséges, mert a kanonikus loader a Definitionben megadott dokumentumokat, a repository Git-remote identityt és a repository commitját is ellenőrzi. A teszt repository `main` ága ezen a commiton állt:

```text
9724deddeb128d27bf4a450f7db1015b1bbfc31d
```

A Definition érdemi értékei:

```yaml
project.id: bridge-demo
project.name: Bridge Demo
repository.full_name: zsambokia/bridge-demo
repository.default_branch: main
repository.integration_branch: main
paths.constitution: docs/constitution/CONSTITUTION.md
paths.roadmap: docs/roadmap/ROADMAP.md
paths.primary_current_state: docs/akb/CURRENT_STATE.md
```

Az `AGENTS.md`, Constitution, Evidence-Driven workflow, Execution Contract, Roadmap, jóváhagyott aktuális sprint és AKB állapotfájl a Definitionben megadott relatív útvonalakon ténylegesen létezett. A tesztprojekt nem tartalmaz AI Bridge-azonosítóra, slugra vagy névre épülő kivételt.

## Első bootstrap

A kizárólagos végrehajtási út a termék saját parancsa volt:

```powershell
.venv\Scripts\python.exe manage.py bootstrap_project `
  --definition .bridge/project.yaml `
  --sprint-path docs/sprints/CURRENT_SPRINT.md `
  --repository-root C:\Users\User\AppData\Local\Temp\ai-bridge-sprint003-bridge-demo `
  --settings=bridge.settings.local
```

Eredmény:

```json
{
  "context_created": true,
  "context_status": "VALID",
  "errors": [],
  "onboarding_status": "READY",
  "project_id": "bridge-demo",
  "registry_created": true,
  "success": true
}
```

Az ORM-lekérdezés ekkor két Project rekordot adott: `ai-bridge` (`READY`, `zsambokia/ai-bridge`) és `bridge-demo` (`READY`, `zsambokia/bridge-demo`). A `bridge-demo` egyetlen Contextje `VALID` volt, és ennek `constitution_path`, `roadmap_path`, `sprint_path` és `current_state_path` mezői rendre a Bridge Demo saját relatív dokumentumútjait tartalmazták. A forrás commitja `9724deddeb128d27bf4a450f7db1015b1bbfc31d` volt. Ez bizonyítja, hogy a Context dokumentumai nem az AI Bridge-re mutatnak.

## Idempotencia és izoláció

Ugyanez a parancs változatlan Definitionnel ismét lefutott. Eredménye:

```json
{
  "context_created": false,
  "context_status": "VALID",
  "errors": [],
  "onboarding_status": "READY",
  "project_id": "bridge-demo",
  "registry_created": false,
  "success": true
}
```

A lekérdezett számlálók: `Project = 2`, `bridge-demo ProjectContext = 1`. Nem jött létre harmadik Project vagy második Bridge Demo Context. Az AI Bridge Registry rekordja a vizsgálat alatt változatlanul `READY` maradt, és egy `VALID` Contextje elérhető volt.

## Hibás Definition

Külön `bridge-demo-invalid` Definitionnel két szándékos hiba szerepelt:

- `repository.full_name: zsambokia/bridge-demo-invalid`, miközben a külön Git repository remote-ja `zsambokia/bridge-demo` volt;
- `paths.roadmap: docs/roadmap/MISSING.md`.

Ugyanaz a `bootstrap_project` parancs a várt, strukturált eredményt adta és nemnulla kilépési kóddal zárult:

```json
{
  "context_created": false,
  "context_status": null,
  "errors": [
    "repository identity is missing, ambiguous, or does not match",
    "required governance document is unavailable: docs/roadmap/MISSING.md"
  ],
  "onboarding_status": "INVALID",
  "project_id": "bridge-demo-invalid",
  "registry_created": true,
  "success": false
}
```

Az ellenőrzés szerint a hibás projekthez `0` Context készült; a korábban regisztrált `ai-bridge` és `bridge-demo` rekordok `READY` állapotúak maradtak, és mindkettőnek volt egy `VALID` Contextje. Az eredeti, érvényes Bridge Demo Definition nem módosult.

## Django Admin és tesztadat-kezelés

A `projects` alkalmazás nem regisztrál modellt a Django Adminban (nincs `projects/admin.py`), ezért Admin-felületen végzett vizuális ellenőrzés nem alkalmazható. A bizonyítékot a kanonikus parancs JSON-kimenete és az ORM állapotlekérdezések adják.

A helyi `db.sqlite3` fejlesztői, nem verziókezelt futtatási adat. A teszt végén kontrollált ORM-törléssel eltávolítottuk a `bridge-demo` és `bridge-demo-invalid` Project rekordokat, valamint a kaszkádolt egyetlen Bridge Demo Contextet. Az ellenőrzött törlés eredménye `3` objektum volt (2 Project, 1 ProjectContext); utána egyik acceptance Project sem maradt, az AI Bridge onboarding státusza `READY` maradt. Az ideiglenes külön Git-repository is törölve lett. Így a bizonyítás megmarad ebben a dokumentumban, de a helyi fejlesztői adat nem őriz tesztprojektet.

## Következtetés

A `Project` Registry, a statikus Project Definition loader, az onboarding értékelés, a `bootstrap_project` szolgáltatás/parancs és a `ProjectContext` létrehozás egyazon kanonikus folyamatban második, független projekttel is determinisztikusan működött. Nem történt közvetlen adatbázis-rekordlétrehozás, fixture/seed használat vagy AI Bridge-specifikus elágazás.

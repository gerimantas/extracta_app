## 0. Įvadas
Ši instrukcija apibrėžia universalią Spec-Driven Development (SDD) discipliną, naudojant DI agentą (pvz. GitHub Copilot) ir specify-cli (Spec-Kit). Tikslas – pakeisti atsitiktinį „vibe coding" struktūruotu, atsekamu procesu: reikalavimai → analizė → planas → užduotys → įgyvendinimas → kokybės vartai → priėmimas → išleidimas.

Visi paaiškinimai lietuvių kalba; visi komandų, prompt'ų ir šablonų pavyzdžiai anglų kalba.

---
## 1. Pagrindiniai Principai
1.1. Determinizmas – tas pats įvesties rinkinys → identiškas rezultatas.
1.2. Atsekamumas – kiekviena kodo eilutė turi kilmę (spec → plan → task → test).
1.3. Mažos iteracijos – kiekviena fazė užrakinama prieš pereinant prie kitos.
1.4. Skaidrumas – dokumentai versijuojami (Git) ir nekeičia istorijos.
1.5. Test-First – specifiniai testai arba stub'ai atsiranda prieš įgyvendinimą.

---
## 2. Aplinkos Paruošimas
2.1. Būtinos priemonės:
	- Git, Python ≥3.11, VS Code (ar ekvivalentas), Copilot Chat, `uv` arba `pip`.
2.2. Įrankių diegimas:
```bash
pip install uv
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git
spec --help
```
2.3. Windows PATH pastaba – pridėti: `%USERPROFILE%\.uv\tools\bin`.
2.4. Virtuali aplinka (rekomenduotina):
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

---
## 3. Konstitucija (constitution.md)
3.1. Privaloma prieš pirmą /specify. Vieta: `.specify/memory/constitution.md`.
3.2. Minimalus stub'as (kuriamas vieną kartą, vėliau papildomas PR'u):
```markdown
# Project Constitution
Principles: Determinism, Reproducibility, Observability, Security
Versioning: Semantic Versioning (SemVer) + schema version table
Testing Policy: Unit → Integration → Contract → Acceptance → (Perf optional)
Quality Gates: Lint, Type-check, Tests >= threshold, Determinism guard, Schema validation
Change Control: Any modification to constitution via PR labelled 'constitution-change'
Rollback Policy: Only additive migrations; destructive changes require RFC
```
3.3. Keičiant – atnaujinti CHANGELOG / release notes.

---
## 4. Branching ir Commit Konvencijos
4.1. Branch formatas: `feature/<nnn>-<kebab-name>` arba `fix/<ticket-id>-<short>`.
4.2. Commit prefiksai:
```
feat(123): add counterparty merge logic
fix(123): correct null handling in parser
test(123): add determinism guard case
refactor(123): extract common repository util
docs(123): update plan clarifications
chore: bump dependencies
```
4.3. Vienas commit = vienas semantinis tikslas.
4.4. Revert'ai su prefiksu `revert:` + commit hash nuoroda.

---
## 5. Funkcijos Gyvavimo Ciklas (Aukšto Lygio)
1) /specify → 2) /clarify → 3) /analyze → 4) /plan → 5) /tasks → 6) Implement & Tests → 7) Quality Gates → 8) /accept (priėmimas) → 9) PR → 10) Release.

Diagrama (paprasta seka):
```
Idea → specify → clarify ↺ (kol nėra atvirų klausimų) → analyze → plan (lock) → tasks (lock) → code+tests → quality gates → acceptance → merge → release
```

---
## 6. /specify Fazė
6.1. Tikslas – išorinė vertė, ne implementacijos detalės.
6.2. Šablonas (prompt pavyzdys Copilot Chat lange):
```text
/specify
# Feature: Unified Reporting DSL
## 1. Goal
As a financial analyst I want ...
## 2. Core Capabilities
- ...
## 3. User Flows
1. ...
## 4. Edge Cases
- ...
## 5. Non-Goals
- ...
## 6. Open Questions
- Q1: ...
```
6.3. Output: `specs/<nnn>-<slug>/spec.md`.
6.4. LOCK kriterijai: nėra neatsakytų „Open Questions“ ir yra aiški Non-Goals sekcija.

---
## 7. /clarify Fazė
7.1. Naudojama klausimams iš „Open Questions“ sukonkretinti.
7.2. Pavyzdys:
```text
/clarify
Resolve open questions Q1,Q3. Provide concise decisions.
```
7.3. Output: spec.md atnaujinamas; pridedama sekcija „Decisions“.
7.4. LOCK: visos Q suplanuotos arba pažymėtos kaip „Deferred“.

---
## 8. /analyze Fazė
8.1. Gylio analizė: rizikos, alternatyvos, trade-offs.
8.2. Pavyzdys:
```text
/analyze
List key risks, propose mitigations, and enumerate 2 alternative architectures.
```
8.3. Output: `analysis.md` tame pačiame kataloge.
8.4. LOCK: identifikuotos mitigacijos aukšto/vidutinio lygio rizikoms.

---
## 9. /plan Fazė
9.1. Techninis dizainas: moduliai, duomenų modelis, migracijos, determinizmo poveikis.
9.2. Prompt pavyzdys:
```text
/plan
Generate a technical plan referencing constitution constraints and list schema changes.
```
9.3. Output: `plan.md`.
9.4. Plan turi turėti: Architektūrinę schemą (tekstinę), Data model, API sąrašą, Versijavimo poveikį, Atviras rizikas (jei liko → STOP).
9.5. LOCK: nebeliko „TBD“ žymių.

---
## 10. /tasks Fazė
10.1. Tikslas – sukurti atsekamą, test-first užduočių sąrašą.
10.2. Prompt pavyzdys:
```text
/tasks
Produce granular TDD-ordered tasks (unit before integration where feasible) with IDs.
```
10.3. Output: `tasks.md` (su numeracija: Phase → Task ID).
10.4. Re-generavimas: jei spec/plan keičiasi po užrakinimo – pridėti sekciją "Delta Changes" gale.
10.5. LOCK: visos užduotys turi aiškų apibrėžtą rezultatą (Done = objektyvus).

---
## 11. Implementavimo Fazė
11.1. Strategijos:
	- Greita: „batch“ kelioms užduotims (rizika – difuzija).
	- Griežta TDD: viena užduotis → raudonas testas → implementacija → žalias → refactor.
11.2. Standartinis darbo ciklas:
```text
1. Read task definition
2. Add/extend failing test
3. Implement minimal code
4. Run tests (expect green)
5. Refactor (no behavior change)
6. Commit (feat/test/refactor prefix)
```
11.3. Testų kategorijos:
	- Unit (mažos vienetų funkcijos)
	- Integration (cross‑module, DB, IO)
	- Contract (schema, API shape)
	- Acceptance (end-to-end scenarijus)
	- Performance (pasirinktinis; gali būti skipped kol MVP)
11.4. Determinizmo Guard – bent vienas testas palygina hash/ID rinkinius tarp run'ų.

---
## 12. Kokybės Vartai (Quality Gates)
12.1. Minimalus rinkinys prieš PR:
| Gate | Komanda (pavyzdys) | Kriterijus |
|------|--------------------|------------|
| Lint | `ruff check .` | 0 klaidų (arba aiškiai ignored) |
| Format | `ruff format --check .` | Neformatuotų failų nėra |
| Types | `mypy src/` | 0 errors (arba žinomi suppress) |
| Tests | `pytest -q` | Visi žali, optional skipped ≤ n |
| Contract | `pytest tests/contract` | Visi žali |
| Determinism | `pytest -k determinism` | Hash stabilus |
| Schemos Migracija | `init_db` (ar ekvivalentas) | Idempotentiška |
12.2. Jei kuris nors gate FAIL → PR blokas.

---
## 13. Acceptance / Priėmimas
13.1. Acceptance test failas privalo apimti:
	- Pagrindinį user flow
	- Kritinius log event'us
	- Deterministinį rezultatą
13.2. Pavyzdinis stub'as:
```python
def test_acceptance_reporting_flow():
		# 1. Seed input
		# 2. Run pipeline
		# 3. Assert outputs
		# 4. Assert hashes stable
		# 5. Assert log events present
```

---
## 14. Traceability (Sekimas)
14.1. Rekomenduojama `traceability.md` lentelė:
```markdown
| Feature | Spec Section | Plan Ref | Task ID | Test File | Notes |
|---------|--------------|----------|---------|-----------|-------|
```
14.2. Automatinė generacija (pasirinktinė) – galima parašyti skriptą, kuris sujungia tasks + test failų pavadinimus.

---
## 15. Versijavimas ir Migracijos
15.1. SemVer: PATCH (fix), MINOR (backward-compatible feature), MAJOR (breaking).
15.2. DB migracijos – tik forward/additive.
15.3. Rollback strategija: naujas „fix“ migracijos failas, kuris koreguoja anomalijas (NE trina struktūrų).
15.4. Versijos failas (pvz. `VERSION`) atnaujinamas per PR su validacija testuose.

---
## 16. Logika vs Konfigūracija
16.1. Skirti „logic version“ ir „mapping/config version“ jei deterministinis hashing.
16.2. Keičiant mapping – padidinti mapping_version, bet nekeisti logic_version be priežasties.

---
## 17. Saugumas ir Privatumas
17.1. Nesaugokite žalių slaptažodžių spec ar plan failuose.
17.2. Pavyzdinės reikšmės – pseudonimizuotos.
17.3. Jei duomenys jautrūs – pridėti „Data Handling“ sekciją spec'e.

---
## 18. Klaidų Valdymas
18.1. Spec edge cases → testų edge cases.
18.2. Exception‘ai turi būti žemėlapio lygio (domain-specific) aukštesniame sluoksnyje.
18.3. Log event turi turėti: `event_type`, `status`, `duration_ms`, `error_count`.

---
## 19. Performance (Pasirinktinis)
19.1. Kai funkcionalumas stabilus – pridėti `tests/perf/` (skipped by default):
```python
import pytest, time
@pytest.mark.skip("perf baseline")
def test_large_merge_baseline():
		start = time.time()
		# run heavy op
		assert (time.time() - start) < 5
```
19.2. Palaipsniui unskip su CI žyma (pvz. PERF=1 env).

---
## 20. Pull Request Šablonas (siūloma)
20.1. PR aprašyme:
```
Title: feat(<id>): <short>
Summary: ...
Scope: Added modules X,Y; migrations: yes/no
Determinism: unaffected / updated hash fields
Quality Gates: all green
Risks & Mitigations: ...
Deferred: ...
```
20.2. Prisegti acceptance artefaktą (pvz. sugeneruotą report failą).

---
## 21. Continuous Improvement
21.1. Po kiekvieno releaso – retro: kas strigo (spec clarity, tests, gating). 
21.2. Nedubliuoti – jei dažnai kartojasi rake types, perkelti į šablonus / generatorius.

---
## 22. Dažniausios Klaidos ir Prevencija
| Klaida | Prevencija |
|--------|-----------|
| Keičiamas kodas be plan.md atnaujinimo | PR check: plan hash / signature |
| Neužrakinta spec su TBD | CI blokas: grep 'TBD' failuose |
| Nėra determinism test | Šablone privaloma sekcija |
| Migracija ne idempotentinė | Dvigubas init testas |
| Acceptance test praleistas | Git hook tikrina failo egzistavimą |

---
## 23. Greita „Cheat Sheet“ Santrauka
```text
1. Create constitution
2. /specify feature
3. /clarify open questions
4. /analyze risks
5. /plan technical design
6. /tasks TDD list
7. Implement (red → green → refactor)
8. Run quality gates
9. Acceptance test passes
10. Generate report artifact
11. Open PR (attach evidence)
12. Merge & tag release
```

---
## 24. Adaptacija Kitiems Projekto Tipams
24.1. Lib / SDK – daugiau dėmesio API stabilumui ir semver testams.
24.2. CLI – pridėti naudotojo scenarijų seką su pavyzdiniais komandų iškvietimais.
24.3. Web API – kontraktų testai OpenAPI/JSON Schema lygmenyje.
24.4. ML komponentai – reproducibility: seed’ai, modelio versijos, artefaktų hash’ai.

---
## 25. Kada Naudoti /kitas (laisvos formos) iteracijas
25.1. Jei reikia generuoti papildomą dokumentą (pvz. RFC), galima duoti tiesioginį prompt:
```text
Generate an RFC comparing approach A vs B for streaming ingestion.
```

---
## 26. Uždarymas
Šis dokumentas aprašo pilną ciklą nuo idėjos iki išleidimo. Adaptuokite sekcijas pagal projekto brandą – tačiau NIEKADA nepraleiskite spec → plan → tasks → tests → quality gates grandinės.

---
*(Atnaujinta pagal gerąsias praktikas ir išplėstą agentinio darbo ciklą.)*
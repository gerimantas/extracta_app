Universali GitHub Spec-Kit Naudojimo Instrukcija Projektų Planavimui
Šis gidas yra žingsnis po žingsnio instrukcija, kaip naudoti GitHub Spec-Kit (specify-cli) įrankį, siekiant struktūrizuotai planuoti ir kurti programinę įrangą bendradarbiaujant su Dirbtinio Intelekto (DI) agentais, tokiais kaip GitHub Copilot.

1. Įvadas: Ką sprendžia Spec-Kit?
Spec-Kit yra įrankių rinkinys ir metodologija, sukurta pakeisti chaotišką "vibe coding" (kūrimą iš nuojautos) į disciplinuotą, specifikacijomis paremtą procesą (Spec-Driven Development). Jis sukuria aiškią struktūrą, kurioje jūs, kaip projekto architektas, ir DI, kaip jūsų programuotojas, galite efektyviai bendradarbiauti. Visų sprendimų pagrindas tampa ne momentinės idėjos, o aiškiai apibrėžti, versijuojami dokumentai.

2. Fazė 0: Pasiruošimas
Šioje fazėje paruošime viską, ko reikia sklandžiam darbui.

2.1. Būtinosios Sąlygos
2.1.1. Kodų Redaktorius: Visual Studio Code (arba kitas, palaikantis DI agentus).
2.1.2. DI Agentas: Integruotas DI asistentas, pvz., GitHub Copilot su Copilot Chat.
2.1.3. Git: Įdiegta versijavimo sistema (git --version).
2.1.4. Python: Įdiegta Python versija (python --version).

2.2. Įrankių Diegimas
Visos komandos vykdomos projekto terminale.

2.2.1. Įdiekite uv (Python paketų tvarkyklę):

pip install uv

2.2.2. Įdiekite specify-cli:

uv tool install specify-cli --from git+[https://github.com/github/spec-kit.git](https://github.com/github/spec-kit.git)

2.2.3. Patikrinkite diegimą: Uždarykite ir iš naujo atidarykite terminalą, tada vykdykite:

spec --help

Jei matote pagalbos meniu, diegimas pavyko. Jei ne, patikrinkite, ar C:\Users\<JūsųVartotojoVardas>\.uv\tools\bin yra pridėtas prie jūsų sistemos PATH kintamųjų.

3. Fazė 1: Projekto Pamatai
Šioje fazėje sukuriame projekto "konstituciją" ir pradinę struktūrą.

3.1. Projekto Inicializavimas (spec init)
3.1.1. Atsidarykite aplanką, kuriame bus jūsų projektas.
3.1.2. Terminale vykdykite komandą, pakeisdami projekto_pavadinimas į savo:

spec init projekto_pavadinimas

3.1.3. Interaktyviame vedlyje:

Pasirinkite DI agentą: Copilot.

Pasirinkite skriptų tipą: PowerShell (Windows) arba Shell (Linux/macOS).
3.1.4. Įrankis sukurs subaplanką (projekto_pavadinimas) su visa reikiama struktūra. Būtinai pereikite į šį aplanką (cd projekto_pavadinimas), nes visos kitos komandos veiks tik jame.

3.2. Konstitucijos Sukūrimas (constitution.md)
Konstitucija – tai jūsų projekto "įstatymų" rinkinys. Ji yra pasirinktina, bet labai rekomenduojama.

3.2.1. Projekto viduje sukurkite aplanką ir failą šiuo keliu: .specify/memory/constitution.md.
3.2.2. Užpildykite jį pagrindiniais projekto principais. Tai jūsų ilgalaikės taisyklės. Įtraukite tokias sritis kaip:

Pagrindiniai Principai: Duomenų vientisumas, saugumas, paprastumas.

Techniniai Reikalavimai: Palaikomi duomenų šaltiniai, technologijos.

Kūrimo Procesas ir Kokybė: Testavimo reikalavimai (pvz., TDD), kodo peržiūros, versijavimas.

Valdymas: Kaip keičiama pati konstitucija.

Patarimas: Galite paprašyti Copilot padėti užpildyti šį failą, pateikdami jam bendrinę užklausą.

4. Fazė 2: Funkcijos Apibrėžimas (/specify)
Kiekviena nauja funkcija, pakeitimas ar klaidos taisymas pradedamas nuo specifikacijos.

4.1. Specifikacijos Kūrimas
4.1.1. VSC Copilot Chat lange įveskite komandą /specify.
4.1.2. Po komandos pateikite išsamų funkcijos aprašymą. Naudokite šabloną:

/specify

# Funkcijos "[Pavadinimas]" Specifikacija

## 1. Apžvalga ir Tikslas
(Naudokite formatą: "Kaip [rolė], aš noriu [atlikti veiksmą], kad galėčiau [gauti vertę/pasiekti tikslą].")

## 2. Pagrindinės Savybės
(Punktų sąrašas, KĄ tiksliai funkcija turi daryti.)

## 3. Vartotojo Scenarijai
(Aprašykite, kaip vartotojas sąveikaus su funkcija žingsnis po žingsnio.)

## 4. Ribiniai Atvejai ir Klaidų Valdymas
(Kas nutiks, jei vartotojas padarys klaidą? Kokie yra netipiniai scenarijai?)

## 5. Tikslai, kurie NĖRA įtraukti (Non-Goals)
(Aiškiai apibrėžkite, ko ši funkcija NETURI daryti, kad išvengtumėte dviprasmybių.)

4.2. Rezultato Analizė
specify-cli automatiškai sukurs naują subaplanką, pvz., specs/001-funkcijos-pavadinimas/, ir jame patalpins spec.md failą. Atidžiai peržiūrėkite Copilot sugeneruotą specifikaciją.

5. Fazė 3: Techninis Projektavimas (/plan)
Kai specifikacija patvirtinta, kuriame techninį brėžinį.

5.1. Plano Generavimas
5.1.1. Copilot Chat lange įveskite /plan.
5.1.2. Po komandos galite pridėti trumpą komentarą, pvz.:

/plan
Generate a detailed technical plan for the feature described in the latest spec.

5.1.3. Copilot nuskaitys constitution.md ir naujausią spec.md failą ir pradės pildyti plan.md failą tame pačiame funkcijos aplanke.

5.2. Rezultato Analizė
Peržiūrėkite plan.md. Atkreipkite dėmesį į:

Technologijų Rinkinį

Architektūrą

Atitiktį Konstitucijai

Iteracija: Jei planas netenkina, patikslinkite spec.md ir vėl paleiskite /plan.

6. Fazė 4: Darbų Suskaidymas (/tasks)
Kai planas patvirtintas, paverčiame jį konkrečių darbų sąrašu.

6.1. Užduočių Generavimas
6.1.1. Copilot Chat lange įveskite /tasks.
6.1.2. Po komandos galite nurodyti pageidaujamą tvarką:

/tasks
Generate a detailed list of tasks based on the created plan. Use Test-Driven Development (TDD) ordering.

6.1.3. Copilot sugeneruos tasks.md failą su detaliu, numeruotu darbų sąrašu.

6.2. Rezultato Analizė
Peržiūrėkite tasks.md. Įvertinkite, ar darbai suskaidyti logiškai, ar jų eiliškumas teisingas, ar apimtis yra valdoma.

7. Fazė 5: Įgyvendinimas ir Iteracijos
Kai turite užduočių sąrašą, galite pradėti rašyti kodą.

7.1. Kodo Kūrimas
Yra du pagrindiniai būdai:

7.1.1. Prižiūrima Automatizacija (greitas, bet reikalauja priežiūros):
Copilot Chat lange duokite bendrą komandą, apimančią visą procesą:

Implement all tasks from tasks.md. Update the task list as you go.

Stebėkite, kaip DI agentas kuria kodą ir pats žymi įvykdytas užduotis.

7.1.2. Žingsnis po Žingsnio (lėtas, bet suteikia maksimalią kontrolę):
Duokite DI agentui po vieną užduotį iš tasks.md sąrašo:

Execute Task #5 from tasks.md: "Write JSON Schema draft for Transaction..."

Po kiekvieno žingsnio peržiūrėkite rezultatą ir tik tada pereikite prie kitos užduoties.

7.2. Naujų Funkcijų Pridėjimas (Iteracijos)
Kai norite pridėti naują funkciją, klaidą ar pakeitimą, kartokite procesą nuo Fazės 2 (punkto 4):

7.2.1. Sukurkite naują specifikaciją su /specify.
7.2.2. spec-kit sukurs naują funkcijos aplanką (pvz., specs/002-another-feature/).
7.2.3. Toliau kartokite /plan -> /tasks -> Įgyvendinimas ciklą.
7.2.4. Konstitucija visada lieka ta pati ir galioja visoms naujoms funkcijoms.
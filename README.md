# Introduktion til VP_evner.exe
Dette program lader dig skabe en karakter. Når du åbner programmet kan du trykke "Indlæs karakter" for at indlæse din karakters evner fra en passende .json-fil. Derefter vil du se en menu med alle de evner fra Specialkaraktersystemet som du kan købe. Evner dukker kun op når du opfylder kravene til dem. For eksempel kan du ikke se Koordination niveau 2 før du har købt Koordination niveau 1, eller Kaste/skrive Magi før du har købt Læse Magi. Hvis du køber en evne der giver dig adgang til en klasse (såsom Hellig Ed for præster) vil du se en ny knap i højre side af vinduet der giver dig adgang til evnerne fra den klasse. Første gang du trykker på denne knap vil du se en menu der lader dig vælge gratis startevner hvis relevant. 

Filer for startkarakterer kan findes i mappen "Nye karakterer". Hvis du ønsker en karakter der har evner og EP udover det som nye karakterer starter med, vil jeg foreslå at kopiere filen for en ny karakter af passende race og derefter manuelt opdatere feltet 'total_ep' så du har råd til at købe de evner du vil.

# Introduktion til karakterark.exe
Dette program genererer et karakterark som en .pdf-fil. Vælg blot din karakters .json-fil, og vælg derefter hvor din .pdf-fil skal gemmes samt hvad den skal hedde.

# Noter til brug af VP_evner.exe
- Programmet gør mærkelige ting hvis du prøver at indlæse en karakter efter allerede at have indlæst en. Genstart programmet inden du indlæser en ny karakter.
- Halvelverfilen har ikke fra start en valgfri evne. Den bliver man nødt til at indtaste i selve filen.
- Udover at præster og paladiner ikke kan vælge forskellige guder i hvert system er der ingen restriktioner på hvilke klasser du kan vælge. Du kan godt være heks og Nimarpræst, eller dværg og troldmand, for eksempel.
- Klassemenuerne lukker af sig selv efter at man har valgt sine gratis besværgelser. Dette er med vilje, og menuerne kan med det samme åbnes igen.
- Hvis du åbner en menu for at få gratis besværgelser og enten lukker den, eller klikker videre uden at vælge en besværgelse, sker der en fejl (i hvert fald i baggrunden).

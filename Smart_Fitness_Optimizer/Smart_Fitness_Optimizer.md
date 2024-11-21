# Smart Fitness Optimizer: Analyse van Vermoeidheid en Prestaties

## Use Case
Dit systeem helpt gebruikers hun vermoeidheid en prestaties tijdens trainingen te monitoren en optimaliseren. Het combineert hartslag en ademhalingsfrequentie om indicatoren van fysieke vermoeidheid te berekenen. Persoonsgegevens zoals leeftijd, geslacht en trainingsniveau worden gebruikt om de analyses te personaliseren.

---

## Datasoorten

### **Hartslag (HR - Heart Rate):**
- **Reële waarden:** 60-200 bpm (beats per minute), afhankelijk van de intensiteit van de training.
- Bij een verhoging boven een bepaalde drempel (bijvoorbeeld 85% van de maximale hartslag) kan dit wijzen op vermoeidheid.

### **Ademhalingsfrequentie (RR - Respiratory Rate):**
- **Reële waarden:** 12-50 ademhalingen per minuut, variërend van rust tot intensieve inspanning.
- Een disproportioneel hoge RR ten opzichte van de HR kan wijzen op inefficiënt zuurstofgebruik of overbelasting.

### **Persoonsgegevens:**
- **Leeftijd:** Voor berekening van de maximale hartslag met de formule `220 - leeftijd`.
- **Trainingsniveau:** Beginner, gemiddeld, of gevorderd, voor meer gepersonaliseerde interpretaties.

---

## Samenhang en Analyse
Het systeem bepaalt vermoeidheid en trainingsprestaties op basis van de verhouding tussen HR en RR. Voorbeelden:

- **Normale staat:** HR en RR stijgen proportioneel tijdens de training.
- **Overbelasting:** HR stijgt sterk terwijl RR niet evenredig volgt, wat kan wijzen op cardiovasculaire stress.
- **Inefficiëntie:** RR stijgt sterk terwijl HR relatief laag blijft, wat kan wijzen op ademhalingsproblemen of inefficiënt zuurstofgebruik.

---

## Node Ontwerp
De wearable genereert virtuele data voor HR en RR:
- **HR:** Een array zoals `[72, 75, 130, 140, 150, 165, 180]` bpm.
- **RR:** Een array zoals `[14, 16, 25, 30, 35, 40, 45]` ademhalingen per minuut.

De node berekent de verhouding `RR / HR` en markeert waarden buiten een gezonde drempel (bijv. >0.25 of <0.1) als "onbalans."

---

## Cloud-gebaseerde Dataverwerking
De cloud combineert de HR, RR en persoonsgegevens om:
1. **De gemiddelde en maximale waarden per sessie te berekenen.**
2. **Vermoeidheidsindexen te genereren:** bijv. percentage tijd in "onbalans."
3. **Trainingssuggesties te geven:** zoals *"neem een pauze"* of *"intensiteit verhogen mogelijk."*

---

## Data-visualisatie
Een interactieve app toont:
- **Live HR- en RR-trends** tijdens de training.
- **Waarschuwingen** bij detectie van overbelasting of inefficiëntie.
- **Persoonlijke voortgang over tijd,** inclusief suggesties voor verbetering.

---

## Waarom logisch?
De samenhang tussen HR en RR is bewezen in inspanningsfysiologie. De analyse biedt waardevolle inzichten voor zowel sporters als mensen die hun gezondheid monitoren. Dit systeem combineert fysiologische kennis met praktische toepassingen, terwijl de gegevens logisch en intuïtief blijven.

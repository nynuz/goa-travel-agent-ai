# 🌴 Goa Travel Agent AI

Un sistema multi-agente intelligente per la pianificazione di viaggi a Goa (India), che combina **Retrieval Augmented Generation (RAG)** con ricerca web in tempo reale per fornire raccomandazioni personalizzate su hotel, attrazioni turistiche e itinerari completi.

## ✨ Features Principali

### 🤖 Sistema Multi-Agente
- **Raj (Travel Planner)**: Pianificatore principale che crea itinerari dettagliati giorno-per-giorno con ottimizzazione geografica e breakdown di budget
- **Marco (Hotel Expert)**: Specialista in hotel e alloggi con verifica in tempo reale della disponibilità e stato operativo
- **Priya (Discovery Guide)**: Esperta di attrazioni turistiche, spiagge, nightlife, cultura e gastronomia locale

### 🔍 Ricerca Ibrida Avanzata
- **Dense Embeddings**: Ricerca semantica tramite Sentence Transformers (all-MiniLM-L6-v2)
- **Sparse Embeddings**: Ricerca keyword-based tramite TF-IDF
- **Reciprocal Rank Fusion (RRF)**: Fusione ottimale dei risultati dense + sparse
- **Cross-Encoder Reranking**: Riordino finale con modello ms-marco-MiniLM-L-6-v2 per massima rilevanza

### 💬 Conversazioni Contestuali
- Memoria conversazionale persistente per ogni agente
- Contesto condiviso quando si cambia agente durante la conversazione
- Gestione intelligente di riferimenti impliciti e pronomi

### 🌐 Ricerca Web Real-Time
- Integrazione con Tavily API per informazioni aggiornate (orari, prezzi, eventi correnti)
- Verifica automatica dello stato operativo degli hotel
- Combinazione trasparente di dati storici (RAG) e informazioni attuali (web)

### 🎨 Interfaccia Utente Moderna
- Web UI sviluppata con Streamlit
- Chat interattiva con selezione agente
- Quick actions per domande frequenti
- Visualizzazione ottimizzata di itinerari e raccomandazioni

---

## 🏗️ Architettura

Il progetto utilizza un'**architettura gerarchica multi-agente**:

```
USER INTERFACE (Streamlit)
        ↓
    RAJ (Orchestrator)
    ↙            ↘
MARCO           PRIYA
(Hotels)      (Attractions)
    ↓              ↓
RAG + Web    RAG + Web
(Qdrant)     (Qdrant)
```

- **Raj** può delegare compiti specifici a Marco e Priya per ottenere informazioni specializzate
- Ogni agente mantiene il proprio contesto conversazionale
- La comunicazione tra agenti avviene tramite il meccanismo di **tool calling** del framework

---

## 🛠️ Tecnologie e Framework

### Framework AI: datapizza-ai
Il progetto è costruito su **[datapizza-ai](https://github.com/datapizza-labs/datapizza-ai)**, un framework modulare per la creazione di agenti AI che supporta:

- **Client LLM multipli**: OpenAI (GPT-3.5-turbo, GPT-4-turbo)
- **Tool Calling**: Conversione automatica di funzioni Python in strumenti invocabili dall'LLM
- **Memory Management**: Gestione avanzata della cronologia conversazionale con modalità stateful/stateless
- **Multi-Agent Orchestration**: Pattern di delegazione gerarchica tra agenti specializzati

**Come viene utilizzato nel progetto:**
- Ogni agente (Raj, Marco, Priya) è un'istanza della classe `Agent` con client OpenAI dedicato
- I tool (ricerca RAG, web search, verifica hotel) sono funzioni Python decorate con `@tool`
- La memoria conversazionale è gestita automaticamente dal framework con `stateless=False`
- Raj può invocare Marco e Priya come "sub-agenti" grazie al metodo `can_call()`

### Vector Database: Qdrant
**Qdrant** è utilizzato come database vettoriale per memorizzare e ricercare hotel e attrazioni turistiche:

- **Due collezioni**: `goa_hotels` (500+ strutture) e `goa_places` (migliaia di POI)
- **Dual-vector storage**: Ogni documento ha sia dense vector (384-dim) che sparse vector (TF-IDF)
- **Metadata filtering**: Filtri su categoria, località, rating, stelle
- **Hybrid search**: Combinazione di ricerca semantica e keyword matching con RRF

### Altri Componenti
- **LLM**: OpenAI GPT-3.5-turbo (Marco, Priya) e GPT-4-turbo (Raj)
- **Embeddings**: Sentence Transformers, TF-IDF (scikit-learn)
- **Reranking**: Cross-Encoder
- **Web Search**: Tavily API
- **UI**: Streamlit
- **Data**: Kaggle datasets (Hotels on Goibibo, Indian Places to Visit)

---

## 📸 Screenshots

### Home Page
![Home Page](screenshots/home.png)
*Dashboard principale con statistiche e quick start*

### Chat Interface
![Chat Interface](screenshots/chat.png)
*Interfaccia chat con selezione agente e memoria conversazionale*

### Itinerary Planning
![Itinerary](screenshots/itinerary.png)
*Esempio di itinerario dettagliato generato da Raj*

---

## 🚀 Installazione

### Prerequisiti
- Python 3.10+
- Account OpenAI con API key
- Account Qdrant Cloud (gratuito) o istanza locale
- Account Tavily per web search (opzionale ma consigliato)
- Account Kaggle per download dataset

### 1. Clona il Repository
```bash
git clone https://github.com/yourusername/goa-travel-agent.git
cd goa-travel-agent
```

### 2. Installa Dipendenze

Il progetto utilizza `uv` per la gestione delle dipendenze (più veloce di pip):

```bash
# Installa uv se non presente
pip install uv

# Installa dipendenze del progetto
uv sync
```

Oppure con pip tradizionale:
```bash
pip install -r requirements.txt
```

### 3. Configura Credenziali Kaggle

Scarica `kaggle.json` dal tuo profilo Kaggle e posizionalo in:
- **Linux/Mac**: `~/.kaggle/kaggle.json`
- **Windows**: `C:\Users\<username>\.kaggle\kaggle.json`

Assicurati che abbia i permessi corretti:
```bash
chmod 600 ~/.kaggle/kaggle.json
```

### 4. Configura Variabili d'Ambiente

Crea un file `.env` nella root del progetto:

```env
# OpenAI API
OPENAI_API_KEY=sk-...

# Qdrant (Cloud o locale)
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your-api-key

# Tavily (opzionale)
TAVILY_API_KEY=tvly-...
```

Per Qdrant locale:
```env
QDRANT_URL=http://localhost:6333
# QDRANT_API_KEY non necessaria per localhost
```

---

## ▶️ Esecuzione

### Prima Esecuzione: Setup Completo

Il primo avvio esegue automaticamente:
1. Download dataset da Kaggle (hotels, places)
2. Preprocessing e pulizia dati
3. Fitting TF-IDF sul corpus completo
4. Generazione embeddings dense e sparse
5. Upload su Qdrant

```bash
# CLI interattiva
uv run python main.py

# Web UI
uv run python main.py --ui
```

**Nota**: Il setup iniziale può richiedere 5-10 minuti a seconda della connessione e hardware.

### Esecuzioni Successive

Se i dati sono già stati processati e caricati su Qdrant, l'avvio è immediato:

```bash
# Avvia direttamente la Web UI
uv run python main.py --ui

# Oppure usa Streamlit direttamente
uv run streamlit run goa_travel_agent/ui/app.py
```

### CLI Interattiva

Per una versione command-line senza UI:
```bash
uv run python main.py
```

Potrai selezionare l'agente con cui conversare e interagire via terminale.

---

## 📁 Struttura Progetto

```
goa_travel_agent/
├── config/
│   └── settings.py              # Configurazione centralizzata
├── data/
│   ├── raw/                     # Dataset Kaggle originali
│   ├── processed/               # CSV preprocessati
│   └── cache/                   # TF-IDF model, embeddings
├── src/
│   ├── data_management/         # Download e preprocessing Kaggle
│   ├── embeddings/              # Hybrid embedder (dense + sparse)
│   ├── vector_db/               # Qdrant manager e hybrid searcher
│   ├── tools/                   # Tool per agenti (RAG, web, budget)
│   ├── agents/                  # Definizione agenti (Raj, Marco, Priya)
│   └── utils/                   # Logger, helpers
└── ui/
    ├── app.py                   # Entry point Streamlit
    ├── components/              # Componenti UI riutilizzabili
    ├── views/                   # Pagine (Home, Chat, Hotels, etc.)
    └── styles/                  # CSS custom
```

---

## 🎯 Utilizzo

### Scenario 1: Ricerca Hotel
1. Seleziona **Marco** nella chat
2. Chiedi: "Cerca hotel di lusso vicino alla spiaggia di Baga con piscina"
3. Marco eseguirà:
   - Ricerca RAG su Qdrant con filtri
   - Verifica web (Tavily) per ogni hotel trovato
   - Restituisce 3-5 hotel verificati con raccomandazioni

### Scenario 2: Scoperta Luoghi
1. Seleziona **Priya** nella chat
2. Chiedi: "Migliori luoghi per tramonto romantico"
3. Priya eseguirà:
   - Ricerca RAG semantica su attrazioni
   - Ricerca web per info aggiornate (orari, eventi)
   - Combina risultati storici + attuali

### Scenario 3: Pianificazione Completa
1. Seleziona **Raj** nella chat
2. Chiedi: "Crea itinerario 5 giorni per coppia, budget medio, interesse in cultura e spiagge"
3. Raj eseguirà:
   - Delega a Marco per trovare hotel
   - Delega a Priya per trovare attrazioni
   - Ottimizza geograficamente l'itinerario
   - Calcola budget breakdown dettagliato
   - Genera piano giorno-per-giorno

### Scenario 4: Conversazione Iterativa
1. Inizia con Priya: "Dimmi di Margao Market"
2. Cambia a Marco: "Cerca hotel vicino" → Marco riceve il contesto e cerca hotel vicini a Margao Market
3. Torna a Priya: "Cosa mangiare lì?" → Priya ricorda che si parlava di Margao Market

---

## 🐛 Troubleshooting

### Errore: "Qdrant collection not found"
Elimina la cache e riavvia per ricreare le collezioni:
```bash
rm -rf goa_travel_agent/data/cache/*
uv run python main.py
```

### Errore: "TF-IDF not fitted"
Il modello TF-IDF non è stato salvato correttamente. Rimuovi la cache:
```bash
rm goa_travel_agent/data/cache/tfidf_model.pkl
uv run python main.py
```

### Errore Kaggle: "401 Unauthorized"
Verifica che `kaggle.json` sia nella posizione corretta e abbia i permessi giusti.

### Performance lente
- Usa Qdrant Cloud invece di localhost per latency migliore
- Riduci `top_k` nei parametri di ricerca
- Considera di usare solo dense search disabilitando sparse (meno accuracy, più veloce)

---

## 🤝 Contributing

Contributi benvenuti! Per favore:
1. Fai fork del repository
2. Crea un branch per la tua feature (`git checkout -b feature/amazing-feature`)
3. Commit delle modifiche (`git commit -m 'Add amazing feature'`)
4. Push al branch (`git push origin feature/amazing-feature`)
5. Apri una Pull Request

---

## 📄 License

Questo progetto è rilasciato sotto licenza MIT. Vedi il file `LICENSE` per dettagli.

---

## 🙏 Credits

- **Framework AI**: [datapizza-ai](https://github.com/datapizza-labs/datapizza-ai)
- **Vector Database**: [Qdrant](https://qdrant.tech/)
- **LLM**: OpenAI GPT-3.5-turbo e GPT-4-turbo
- **Web Search**: [Tavily](https://tavily.com/)
- **Datasets**: Kaggle (Hotels on Goibibo, Indian Places to Visit)

---

## 📧 Contact

Per domande o supporto, apri una issue su GitHub.

---

**Buon viaggio a Goa! 🌴✈️**

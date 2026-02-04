# Contributing to Goa Travel Agent AI

Grazie per il tuo interesse nel contribuire al progetto! 🎉

## Come Contribuire

### 1. Fork del Repository
Fai un fork del repository sul tuo account GitHub.

### 2. Clona il Fork
```bash
git clone https://github.com/your-username/goa-travel-agent.git
cd goa-travel-agent
```

### 3. Crea un Branch
Crea un branch per la tua feature o bugfix:
```bash
git checkout -b feature/nome-feature
# oppure
git checkout -b fix/nome-bug
```

### 4. Installa l'Ambiente di Sviluppo
```bash
uv sync
```

### 5. Fai le Tue Modifiche
- Scrivi codice pulito e commentato
- Segui lo stile del progetto esistente
- Testa le tue modifiche localmente

### 6. Commit
Usa commit message chiari e descrittivi:
```bash
git add .
git commit -m "Add: descrizione della feature"
# oppure
git commit -m "Fix: descrizione del bug risolto"
```

Convenzioni commit message:
- `Add:` per nuove feature
- `Fix:` per bugfix
- `Update:` per miglioramenti a codice esistente
- `Docs:` per modifiche alla documentazione
- `Refactor:` per refactoring senza cambio funzionalità

### 7. Push e Pull Request
```bash
git push origin feature/nome-feature
```

Apri una Pull Request su GitHub con:
- Titolo chiaro e descrittivo
- Descrizione dettagliata delle modifiche
- Riferimenti a eventuali issue correlate

## Linee Guida

### Codice
- Usa type hints per le funzioni
- Documenta le funzioni complesse con docstring
- Mantieni le funzioni piccole e focalizzate
- Evita dipendenze non necessarie

### Testing
- Testa manualmente le modifiche nell'UI
- Verifica che non ci siano regressioni
- Considera di aggiungere test unitari (se applicabile)

### Documentazione
- Aggiorna il README.md se necessario
- Documenta nuove features o cambi API
- Aggiungi commenti dove il codice non è autoesplicativo

## Aree di Contribuzione

### Feature Richieste
- Nuovi tool per gli agenti (calcolo distanze, ottimizzazione percorsi)
- Supporto per altre destinazioni oltre Goa
- Export itinerari in PDF/DOCX
- Integrazione con servizi di booking
- Supporto multilingua

### Miglioramenti
- Ottimizzazione performance ricerca
- UI/UX miglioramenti
- Gestione errori più robusta
- Test coverage

### Documentazione
- Tutorial video
- Guide per casi d'uso specifici
- Traduzione documentazione in altre lingue

## Domande?

Apri una issue su GitHub per discutere:
- Nuove feature da implementare
- Bug da risolvere
- Miglioramenti architetturali

## Codice di Condotta

Sii rispettoso e costruttivo nelle interazioni con gli altri contributor. Questo è un progetto open source fatto per imparare e collaborare! 🤝

# whatsapp-ft-formatter

Pipeline avanzata per trasformare chat WhatsApp in JSON strutturato, con segmentazione semantica, parsing NLP e validazione.

## Flusso Dati

1. **Upload Chat**: L'utente carica un file di chat WhatsApp (.txt) tramite l'interfaccia Gradio.
2. **Salvataggio**: Il file viene salvato in `data/raw/`.
3. **Parsing**: Il file .txt viene parsato per estrarre messaggi individuali (timestamp, autore, testo).
4. **Segmentazione**: I messaggi vengono raggruppati in conversazioni logiche.
5. **Assegnazione Ruoli**: Ai partecipanti alla chat vengono assegnati ruoli (es. "cliente", "agente").
6. **Estrazione NLP**: Da ogni messaggio vengono estratte entità rilevanti (date, numeri) e l'intento.
7. **Formattazione JSON**: Le informazioni elaborate vengono strutturate in un formato JSON standard.
8. **Validazione**: Il JSON generato viene validato contro uno schema predefinito (`schema.json`).
9. **Upload GCS**: Il JSON validato viene opzionalmente caricato su Google Cloud Storage.

## Setup rapido

1.  **Clona il repository:**
    ```bash
    git clone https://huggingface.co/spaces/acmc/whatsapp-chats-finetuning-formatter # Sostituisci con l'URL del tuo repo GitHub se lo hai spostato
    cd whatsapp-ft-formatter
    ```

2.  **Installa le dipendenze:**
    ```bash
    pip install -r requirements.txt
    ```
    Assicurati di avere Python 3.8+ installato.

3.  **Configura Google Cloud Storage (Opzionale):**
    *   Crea un bucket GCS.
    *   Scarica le credenziali del service account (file JSON).
    *   Imposta le variabili d'ambiente:
        ```bash
        export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/credentials.json"
        export GCS_BUCKET_NAME="your-gcs-bucket-name"
        ```
    *   Puoi anche configurare questi valori nel file `config/settings.py` o tramite `space.yaml` per Hugging Face Spaces.

## Esempio di utilizzo in Hugging Face Space

Una volta deployato su Hugging Face Spaces:

1.  Accedi allo Space.
2.  Trascina o seleziona il tuo file di chat WhatsApp (`.txt`).
3.  Clicca sul pulsante "Processa".
4.  Attendi l'elaborazione: i log appariranno nell'interfaccia.
5.  Il JSON risultante sarà disponibile per il download e, se configurato, caricato sul bucket GCS specificato.

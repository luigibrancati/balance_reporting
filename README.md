Istruzioni:

Ho installato quello che serve sul tuo pc, per farlo funzionare la prima volta segui le istruzioni:
1. Premi il tasto windows, cerca Anaconda e apri Anaconda Prompt (miniconda3), ti si dovrebbe aprire un terminale
2. Usa il comando "cd cartella" per muoverti dentro questa cartella dal terminale, es. se hai messo questa cartella in Downloads, dovrai scrivere "cd Downloads\ContoBancario" e premere invio
3. Scrivi "setup.bat" nel terminale per avviare una serie di configurazioni
Potrebbe metterci un pò perchè installa molti pacchetti python, se vedi che il terminale si blocca premi invio, se non succede nulla aspetta che si sblocchi e riprova a premere invio
4. Una volta che ha finito di installare tutto, prima di aprire il report apri il file config.json nella cartella config e sistema la configurazione
5. Scrivi "cd Dash" e premi invio, ora puoi far partire tutto scrivendo "python report_account.py"; ALTERNATIVAMENTE puoi girare lo script run.bat direttamente da dove sei
6. Dovrebbero uscirti delle scritte, tra queste dovrebbe esserci un indirizzo internet simile a http://127.0.0.1:8050/
Se non vedi questo indirizzo, probabilmente c'è un qualche errore
7. Vai all'indirizzo indicato con firefox

Per usare il report dopo la prima volta:
1. Apri Anaconda Prompt (miniconda3) come al punto 1 di prima, vai nella cartella ContoBancario con il comando cd e segui i punti 5-7 scritti prima, oppure fai girare lo script run.bat.

NOTA: la prima volta che lo giri, lo script python prende l'estratto conto, ci fa varie cose e poi lo salva nel file fulldf.csv nella cartella Data. D'ora in avanti userà sempre quel file, quindi se vuoi aggiornare il tuo estratto conto devi cancellarlo.
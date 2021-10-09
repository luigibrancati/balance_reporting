Istruzioni:

Ho installato quello che serve sul tuo pc, per farlo funzionare la prima volta segui le istruzioni:
1. Premi il tasto windows, cerca Anaconda e apri Anaconda Prompt (miniconda3), ti si dovrebbe aprire un terminale
2. Usa il comando "cd cartella" per muoverti dentro questa cartella dal terminale, es. se hai messo questa cartella in Downloads, dovrai scrivere "cd Downloads\ContoBancario" e premere invio
2.1 Per tornare nella cartella precedente, usa "cd .."
3. Prima di far partire il report, apri il file config.json nella cartella config e sistema la configurazione
4. Scrivi "run.bat" nel terminale per avviare una serie di configurazioni
Potrebbe metterci un pò la prima volta che lo fai perchè crea un ambiente e ci installa molti pacchetti python
Se vedi che il terminale si blocca premi invio, se non succede nulla aspetta che si sblocchi e riprova a premere invio
5. Una volta che ha finito, dovresti vedere delle scritte, tra queste dovrebbe esserci un indirizzo internet simile a http://127.0.0.1:8050/
Se non vedi questo indirizzo, probabilmente c'è un qualche errore
6. Vai all'indirizzo indicato con firefox
7. Una volta che hai finito, per chiudere il report chiudi la pagina del browser, clicca sul terminale ancora aperto e premi Ctrl+C (cioè il tasto ctrl e c insieme)

Per usare il report dopo la prima volta:
1. Apri Anaconda Prompt (miniconda3) come al punto 1 di prima e segui i punti 3-6 scritti prima.

NOTA: la prima volta che lo giri, lo script python prende l'estratto conto, ci fa varie cose e poi lo salva nel file fulldf.csv nella cartella Data. D'ora in avanti userà sempre quel file, quindi se vuoi aggiornare il tuo estratto conto devi cancellarlo.
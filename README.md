Istruzioni:

Ho installato quello che serve sul tuo pc, per farlo funzionare segui le istruzioni:
1. Premi il tasto windows, cerca Anaconda e apri Anaconda Prompt (miniconda3), ti si dovrebbe aprire un terminale
2. Usa il comando "cd <cartella>" per muoverti dentro questa cartella dal terminale, es. io ti ho messo questa cartella in Desktop quindi scrivi "cd Desktop\balance_reporting", se la sposti cambia questo comando in base a dove la metti
2.1 Se serve, per tornare nella cartella precedente usa "cd .."
3. Prima di far partire il report, apri il file config.json nella cartella Data\DataCristina e sistema la configurazione
4. Scrivi "cd windows scripts", premi invio
5. Scrivi "update.bat" per scaricare una nuova versione del report nel caso sia disponibile
6. Scrivi "run.bat" nel terminale per avviare una serie di configurazioni e premi invio
Potrebbe metterci un pò la prima volta che lo fai perchè crea un ambiente e ci installa molti pacchetti python
Se vedi che il terminale si blocca premi invio, se non succede nulla aspetta che si sblocchi e riprova a premere invio
7. Una volta che ha finito, dovresti vedere delle scritte, tra queste dovrebbe esserci un indirizzo internet simile a http://127.0.0.1:8050/
Se non vedi questo indirizzo, probabilmente c'è un qualche errore
8. Vai all'indirizzo indicato con firefox
9. Una volta che hai finito, per chiudere il report chiudi la pagina del browser, clicca sul terminale ancora aperto e premi Ctrl+C 2 volte (cioè il tasto ctrl e c insieme)

NOTA: la prima volta che lo giri, lo script python prende l'estratto conto, ci fa varie cose e poi lo salva nel file fulldf.csv nella cartella Data. D'ora in avanti userà sempre quel file, quindi se vuoi aggiornare il tuo estratto conto devi cancellarlo.
# Barbadillo RSS per Feedly

Questo repository crea un feed RSS non ufficiale degli ultimi articoli pubblicati su
https://www.barbadillo.it/ e lo aggiorna automaticamente con GitHub Actions.

## Installazione — passo per passo

1. Crea un account gratuito su https://github.com/ se non ne hai già uno.
2. Su GitHub crea un nuovo repository chiamato esattamente `barbadillo-rss`.
   Impostalo **Public**.
3. Carica **tutto il contenuto di questo ZIP**, mantenendo anche la cartella
   `.github/workflows/`.
4. Apri nel repository **Settings → Pages**.
5. In **Build and deployment → Source** scegli **Deploy from a branch**.
6. Seleziona:
   - Branch: `main`
   - Folder: `/ (root)`
   e premi **Save**.
7. Apri la scheda **Actions** del repository, scegli **Aggiorna feed RSS** e premi
   **Run workflow**. Questo crea subito il primo `feed.xml`.
8. Dopo il primo aggiornamento, il feed pubblico sarà:

   `https://TUO-USERNAME.github.io/barbadillo-rss/feed.xml`

   Sostituisci `TUO-USERNAME` con il tuo nome utente GitHub.

## Aggiungerlo a Feedly

In Feedly scegli **Follow Sources** e incolla l'URL del feed:

`https://TUO-USERNAME.github.io/barbadillo-rss/feed.xml`

## Aggiornamento

GitHub Actions esegue automaticamente lo script circa una volta all'ora.
Gli orari pianificati di GitHub Actions possono subire piccoli ritardi.

## Se Barbadillo cambia grafica

Il parser usa diversi selettori e filtri per essere abbastanza resistente ai cambiamenti
del sito. Se un giorno il feed smette di aggiornarsi, controlla la scheda **Actions**:
un errore lì di solito indica che la struttura HTML del sito è cambiata.

## Note

Questo progetto non è affiliato a Barbadillo.it. Il feed contiene titolo, link e metadati
pubblicamente esposti dal sito e rimanda sempre all'articolo originale.

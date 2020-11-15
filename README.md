# installation
## on mobile (only Android Devices):
da Google Play scaricate Termux, apritelo e scrivete
```linux
pkg install git
```
terminata l'installazione scrivete:
```linux
pkg install python
```
finito anche questo potete eseguire hab! scrivete
```linux
cd hab5 && python main.py
```
per avviare il gioco, se volete creare potete creare un alias così che aperto termux basterà scrivere hab per eseguire lo script
### creare un alias
scrivete
```linux
nano /data/data/com.termux/files/usr/etc/bash.bashrc
```
e alla fine del file aggiungete questa riga:
```linux
alias hab="cd && cd hab5 && python main.py"
```
ora il file dovrebbe essere simile o uguale a questo:
```
non ho sbatti, dopo copio e incollo.
```
## on Windows
 scarica questi file andado su Code->download zip. fatto questo estrarre i file sul desktop. 
 
 aprite il prompt dei comandi cercando cmd nella barra di ricerca in basso a sinistra e cliccate invio, adesso scrivete 
 ```linux
 cd Desktop/hab5-main
 ```
 e poi
 ```
 python main.py
 ```
 se python non è installato seguite il procedimento qui sotto e ricordate di cliccare "Add to PATH" durante l'installazione.


<h1>How To Run</h1>
se non si dispone di python 3.x sul proprio computer installarlo da https://www.python.org/ftp/python/3.9.0/python-3.9.0-amd64.exe

installato python fare doppio click su main.py oppure usando un terminale entrate nel percorso dei file scaricati con il comando "cd" e 
scrivere python main.py nella cartella hackabot2A/

<h1>Start</h1>
all'avvio vengono generati dei bot in posizioni casuali che cercheranno di attaccarti o difendersi

il tuo obiettivo è quello di spegnerli o distruggerli.

# Global sheet
i comandi globali sono quei comandi che vengono eseguiti nella mappa.

## select
usage:
```python
select -m MODE VAL
```
usando MODE (ossia "id" o "pos") seleziona un Robot dalla mappa

esempio:
```python
select -m id 54
```
per selezionare il bot con id=54, oppure
```python
select -m pos 1,2
```
per selezionare il bot con coordinate x=1, y=2

## show
usage:
```python
show VAL
```
nella mappa mostra VAL.
VAL può essere:
- id / ids --> mostra gli id dei bots
- pos  ------> mostra le coordinate
- null ------> default, non mostrare niente


# BOT Sheet

un Robot ha _sempre_ due porte, 80 e 443, più altre generate a caso (le altre porte devo ancora implementarle).

## hacking
hackerare un bot significa prendere il controllo e poter eseguire script nella sua MShell

dopo aver selezionato un robot cerchiamo di entrare nella sua MShell in questo modo:

```python
hash -port
```
questo ci mostrerà le porte e i loro stati, ora scriviamo:

```python
decoder -text t
```
decoder è l'utilità che ci permette di decodificare un hash criptato. sostituisci t con il tuo hash da decifrare (quello della porta che hai scelto)

adesso possiamo bypassare una porta usando l'hash decifrato
```python
hash -res h -port p
```
sostituisci h e p rispettivamente con hash decodificato e porta scelta.

adesso abbiamo sbloccato una porta, sfruttiamo questa porta sbloccata per entrate nella MShell scrivendo:
```python
hack numeroporta
```
dove numero porta è la porta della quale abbiamo decifrato gli hash.

## distruzione e vittoria
per vincere bisogna distruggere ogni robot sulla mappa, per farlo bisogna scrivere
```python
shutdown
```
oppure
```python
destroy
```
nella sua MShell. elimina tutti i bot per vincere!

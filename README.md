popolarenetwork
===============

Il pacchetto è composto da due daemon:

* recorder for popolare network radio broadcast
* scheduler per l'abilitazione della messa in onda del notiziario

entrambi i pacchetti utilizzano un arduino ciascuno collegato al server 
tramite porta USB

recorder for popolare network radio broadcast
---------------------------------------------

Il registratore realizzato con gstreamer viene attivato tramite json RPC.
Il software python è il server rpc mentre il firmware su arduino è il client.
Il server esegue due RPC

* ping : necessario per confermare la regolare attività del firmware
* record : attivare e disattivare la registrazione

scheduler per l'abilitazione della messa in onda del notiziario
---------------------------------------------------------------

Il firmware su arduino funge da server RPC; l'RPC disponibile

* onair con parametro "status" di tipo boolean

il client in python:

estrae dal DB di autoradio (django) la programmazione per i notiziari
selezionando di show con tipo 1a (notiziario/telegiornale)

per ogni programmazione crea un thread di tipo timer temporizzato per
il momento esatto di inizio notiziario e un altro thread temporizzato
per la fine; il primo viene alticipato di un certo tempo "tolleranza"
così come il secondo viene posticipato.

All'avvio il daemon recupera le programmazioni dei 20 minuti
precedenti fino ai 20 minuti successivi; tutte le volte successive
vengono elaborate due ore per volta che iniziano sempre 20 minuti dopo
il tempo attuale.

L'accesso alla porta seriale USB viene gestito tramite un lock
esclusivo per evitare conflitti.

Le rpc con status disattivo vengono ritardate di qualche secondo in
modo da essere sempre successive a quelle di attivazione; questo è
importante nel caso le programmazioni siano relative ai 20 minuti già
trascorsi e con programmazioni di recupero e quindi che potrebbero
essere eseguite senza ritardo.


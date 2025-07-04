mejora realizada, cada 3 dias sigue varias personas para evitar sospechas... acutalmente utilice NSSM para automatizar y tener el servidor activo.


 
NSSM para ejecutar el servicio
Se necesita chocolatey

Instalar NSSM:
powershell
choco install nssm

ejecutar el CMD como administrador y:
sc start InstagramBot


iniciar el servicio automaticamente cuando se enciende el compu:
sc config InstagramBot start= auto
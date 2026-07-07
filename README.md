
## 🎥 Demostración

[![Ver demostración](Captura%20de%20pantalla%202026-07-07%20123506.png)](https://youtu.be/2Umxo954krM)

###### 

Si se quiere configurar como servicio:

 NSSM:
asi se ejecuta para ver si funciona:
C:\Users\luisg\AppData\Local\Programs\Python\Python312\python.exe C:\xampp\htdocs\python_web\app.py


La ruta del NSSM esta en :
C:\ProgramData\chocolatey\lib\NSSM\tools



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


Bueno, parecia funcionar, programe la ejecucion como una tarea pero tiempo despues note que aun con la contraseña correcta instagram no me permite ingresar, cosa que no pasaba si lo ejecutaba yo mismo anteriormente,
es decir, no se exactamente la razon, dado que ejecutando el programa por mi mismo se llego a aseguir a mas de 1000 personas y se bloqueo la cuenta por la rapidez de esta accion, pero no es comprensible porque pasa esto ahora
si los tiempos son razonables, por que no me bloquean la cuenta, si no que directamente no puedo acceder desde el driver, pero si desde google normal.

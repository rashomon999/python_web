necesario ademas de instalar python:

pip install flask

pip install flask-mysql

pip install selenium

pip install webdriver-manager

una vez hecho lo anterior, para ejecutar : python app.py, que te deja el link a : http://127.0.0.1:5000/

crear en phpMyAdmin la base de datos de nombre python_libros con 4 columnas: id (autoincremental (se selecciona automaticamente primary key)), nombre (VARCHAR 255), imagen (VARCHAR 255), url (VARCHAR 500).

luego dirigirse a http://127.0.0.1:5000/admin/libros (revisar bien el codigo de app.py, pero pues: user:barcelona, password:999) y crear en la base de datos el primer libro (pagina creada) simplemente acccedes a la pagina (ya creada) entonces creas un libro con el nombre que sea, imagen que sea pero con url /bot (ya esta creada en el codigo, esto solo es para acceder a ella con un button).

El codigo de la pagina bot esta desactualizado, antes era un bot que seguia a todos los seguidores de "victima". Ahora instagram es mas cuidadoso, en poco tiempo a mejorado esto, las soluciones (igual toca actualizar mucho) serian ampliar el tiempo de seguir a una persona........... en credenciales pones tu informacion de login.

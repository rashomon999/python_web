from flask import Flask, render_template, request, redirect, session, send_from_directory
from flaskext.mysql import MySQL
from datetime import datetime
import os
import threading
import time
import json

# Configuración Selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (NoSuchElementException, 
                                      ElementClickInterceptedException,
                                      StaleElementReferenceException,
                                      TimeoutException)
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.driver_cache import DriverCacheManager

from datetime import datetime

app = Flask(__name__)
app.secret_key = "barcelona"

# Configuración MySQL
mysql = MySQL()
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'python'
mysql.init_app(app)

# Configuración del Bot
bot_config = {
    'username': None,
    'password': None,
    'target_url': None,
    'last_run': None,
    'status': 'idle',
    'message': ''
}

# Función para guardar configuración
def save_bot_config():
    with open('bot_config.json', 'w') as f:
        json.dump(bot_config, f)

# Función para escribir logs del bot
def append_bot_log(message):
    timestamp = datetime.now().isoformat(timespec='seconds')
    with open('bot.log', 'a', encoding='utf-8') as f:
        f.write(f'[{timestamp}] {message}\n')

# Función para leer las últimas líneas del log
def tail_bot_log(lines=20):
    try:
        with open('bot.log', 'r', encoding='utf-8') as f:
            return f.readlines()[-lines:]
    except FileNotFoundError:
        return []

# Función para cargar configuración al iniciar
def load_bot_config():
    try:
        with open('bot_config.json') as f:
            config = json.load(f)
            bot_config.update(config)
    except FileNotFoundError:
        pass

# Cargar configuración al inicio
load_bot_config()

# =============================================
# Rutas principales (originales preservadas)
# =============================================

@app.route('/')
def inicio():
    return render_template('sitio/index.html')

@app.route('/img/<imagen>')
def imagenes(imagen):
    return send_from_directory(os.path.join('templates/sitio/img'), imagen)

@app.route('/admin/cerrar')
def admin_login_cerrar():
    session.clear()
    return redirect('/admin/login')

@app.route("/css/<archivoscss>")
def css_link(archivoscss):
    return send_from_directory(os.path.join('templates/sitio/css'), archivoscss)

# =============================================
# Sección de Libros (original preservada)
# =============================================

@app.route('/libros')
def libros():
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM `python_libros`")
    libros = cursor.fetchall()
    conexion.commit()
    return render_template('sitio/libros.html', libros=libros)

@app.route('/admin/libros')
def admin_libros():
    if not 'login' in session:
        return redirect("admin/login")
    
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM `python_libros`")
    libros = cursor.fetchall()
    conexion.commit()
    return render_template('admin/libros.html', libros=libros)

@app.route('/admin/libros/guardar', methods=["POST"])
def admin_libros_guardar():
    if not 'login' in session:
        return redirect("admin/login")
    
    _nombre = request.form['txtNombre']
    _url = request.form['txtUrl']
    _archivo = request.files['txtImagen']
    
    tiempo = datetime.now()
    horaActual = tiempo.strftime('%Y%H%M%S')
    
    if _archivo.filename != '':
        nuevoNombre = horaActual + '_' + _archivo.filename
        _archivo.save("templates/sitio/img/" + nuevoNombre)
    
    sql = "INSERT INTO `python_libros`(`id`, `nombre`, `imagen`, `url`) VALUES (NULL,%s,%s,%s);"
    datos = (_nombre, nuevoNombre, _url)
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute(sql, datos)
    conexion.commit()
    return redirect('/admin/libros')

@app.route('/admin/libros/borrar', methods=['POST'])
def admin_libros_borrar():
    if not 'login' in session:
        return redirect("admin/login")
    
    _id = request.form['txtID']
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute("SELECT imagen FROM `python_libros` WHERE id=%s", (_id))
    libros = cursor.fetchall()
    conexion.commit()
    
    if os.path.exists("templates/sitio/img/" + str(libros[0][0])):
        os.unlink("templates/sitio/img/" + str(libros[0][0]))
    
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM `python_libros` WHERE id=%s", (_id))
    conexion.commit()
    return redirect('/admin/libros')

# =============================================
# Funciones del Bot Instagram (mejoradas)
# =============================================

# ==================== FUNCIONES DEL BOT ====================

def crear_driver(detach=True, ancho=500, alto=1000):
    """Configura y retorna una instancia del navegador Chrome."""
    opciones = webdriver.ChromeOptions()
    if detach:
        opciones.add_experimental_option("detach", True)

    cache_dir = os.path.join(os.path.dirname(__file__), '.wdm')
    os.makedirs(cache_dir, exist_ok=True)
    cache_manager = DriverCacheManager(root_dir=cache_dir)

    service = Service(ChromeDriverManager(cache_manager=cache_manager).install())
    driver = webdriver.Chrome(service=service, options=opciones)
    driver.set_window_size(ancho, alto)
    return driver

def abrir_instagram(driver):
    """Abre la página de Instagram"""
    driver.get("https://instagram.com")
    time.sleep(5)

def iniciar_sesion(driver, username, password):
    """Realiza el login en Instagram"""
    try:
        driver.find_element(By.NAME, "email").send_keys(username)
        driver.find_element(By.NAME, "pass").send_keys(password)
        driver.find_element(By.XPATH, '//*[@id="login_form"]/div/div/div/div[3]/div/div').click()
        time.sleep(8)
    except Exception as e:
        print(f"Error durante login: {e}")

def ignorar_ventanas_emergentes(driver):
    """Cierra ventanas emergentes de Instagram"""
    try:
        driver.find_element(By.XPATH, "//div[@role='button']").click()
        time.sleep(3)
    except:
        pass
    
    try:
        botones = driver.find_elements(By.XPATH, "//*[contains(text(), 'Ahora no')]")
        for btn in botones:
            btn.click()
        time.sleep(3)
    except:
        pass

def abrir_seguidos(driver, target_url, reintentos=3):
    """Abre la lista de seguidos de un perfil"""
    for intento in range(reintentos):
        try:
            driver.get(target_url)
            time.sleep(5)
            
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '(//a[contains(@href, "#")])[3]'))
            ).click()
            
            time.sleep(3)
            return True
            
        except Exception as e:
            print(f"Intento {intento+1} fallido: {str(e)}")
            time.sleep(5)
    
    return False

def extraer_seguidos(driver, max_scrolls=15, scroll_delay=1.5):
    """Extrae los perfiles de la lista de seguidos"""
    try:
        modal = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[role="dialog"]'))
        )
        
        scroll_box = modal.find_element(By.CSS_SELECTOR, 'div > div:nth-child(2)')
        
        last_height = driver.execute_script("return arguments[0].scrollHeight", scroll_box)
        for _ in range(max_scrolls):
            driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight)", scroll_box)
            time.sleep(scroll_delay)
            new_height = driver.execute_script("return arguments[0].scrollHeight", scroll_box)
            if new_height == last_height:
                break
            last_height = new_height
        
        perfiles = set()
        for elemento in scroll_box.find_elements(By.TAG_NAME, 'a'):
            href = elemento.get_attribute('href')
            if href and "/" in href:
                perfiles.add(href)
                
        return perfiles
        
    except Exception as e:
        print(f"Error extrayendo seguidos: {str(e)}")
        return set()

def seguir_perfiles(driver, lista_perfiles, max_intentos=3):
    """Sigue una lista de perfiles"""
    for perfil in lista_perfiles:
        for intento in range(max_intentos):
            try:
                driver.get(perfil)
                time.sleep(2)
                
                boton_seguir = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, '//div[text()="Seguir"]'))
                )
                boton_seguir.click()
                print(f"✅ Seguido: {perfil}")
                time.sleep(2)
                break
                
            except Exception as e:
                print(f"⚠️ No se pudo seguir {perfil} (intento {intento+1}): {str(e)}")
                time.sleep(3)

def ejecutar_bot(username, password, target_url):
    """Función principal que ejecuta todo el flujo del bot"""
    driver = None
    bot_config['status'] = 'running'
    bot_config['message'] = 'Iniciando bot...'
    save_bot_config()

    try:
        msg = "🚀 Iniciando bot..."
        print(msg)
        append_bot_log(msg)
        bot_config['message'] = 'Creando driver de Chrome...'
        save_bot_config()
        driver = crear_driver()
        abrir_instagram(driver)
        iniciar_sesion(driver, username, password)
        ignorar_ventanas_emergentes(driver)

        if abrir_seguidos(driver, target_url):
            perfiles = extraer_seguidos(driver)
            print(f"🔍 Encontrados {len(perfiles)} perfiles para seguir")

            if perfiles:
                seguir_perfiles(driver, perfiles)

        bot_config['last_run'] = datetime.now().isoformat()
        bot_config['status'] = 'idle'
        bot_config['message'] = 'Bot completado exitosamente'
        save_bot_config()
        msg = "✅ Bot completado exitosamente"
        print(msg)
        append_bot_log(msg)

    except Exception as e:
        bot_config['status'] = 'idle'
        bot_config['message'] = f'Error en ejecución: {e}'
        save_bot_config()
        msg = f"❌ Error en ejecución del bot: {e}"
        print(msg)
        append_bot_log(msg)

    finally:
        try:
            if driver:
                driver.delete_all_cookies()
                driver.quit()
        except Exception:
            pass

# =============================================
# Rutas del Bot (mejoradas)
# =============================================

@app.route('/bot', methods=['GET', 'POST'])
def admin_bot():
    global bot_config

    if request.method == 'POST':
        action = request.form.get('action')

        bot_config.update({
            'username': request.form['username'],
            'password': request.form['password'],
            'target_url': request.form['target_url']
        })
        save_bot_config()

        if action == 'run_now':
            try:
                bot_config['status'] = 'starting'
                bot_config['message'] = 'Bot iniciándose...'
                save_bot_config()

                threading.Thread(
                    target=ejecutar_bot,
                    args=(bot_config['username'], bot_config['password'], bot_config['target_url']),
                    daemon=True
                ).start()
                return redirect('/bot?success=Bot+iniciado+manualmente')
            except Exception as e:
                bot_config['status'] = 'idle'
                bot_config['message'] = f'Error al iniciar el bot: {e}'
                save_bot_config()
                return redirect(f'/bot?error=Error+al+iniciar+el+bot%3A+{str(e)}')

        return redirect('/bot?success=Configuraci%C3%B3n+guardada+correctamente')

    return render_template('sitio/bot.html', config=bot_config, bot_log=tail_bot_log(20))

@app.route('/bot/control', methods=['POST'])
def control_bot():
    # Deprecated: kept for compatibility but not used by bot.html anymore.
    return redirect('/bot')

# =============================================
# Tarea programada y rutas administrativas
# =============================================

if __name__ == '__main__':
    app.run(debug=True)

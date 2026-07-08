from flask import Flask, render_template, request, redirect, session, send_from_directory
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


def comentar_publicacion(driver, mensaje="interesante"):
    try:
        time.sleep(5)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//form//textarea'))
        )

        for intento in range(2):
            try:
                textarea = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//form//textarea'))
                )
                textarea.click()
                time.sleep(3)
                textarea.send_keys(mensaje)
                time.sleep(3)

                publicar_btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@role="button" and normalize-space()="Publicar"]'))
                )
                publicar_btn.click()
                time.sleep(2)
                print("✅ Comentario publicado")
                return True

            except StaleElementReferenceException:
                print("🔄 Elemento obsoleto, intentando nuevamente...")

        print("❌ No se pudo comentar después de reintentos.")
        return False

    except Exception as e:
        print(f"❌ Error comentando: {e}")
        return False
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.driver_cache import DriverCacheManager

from datetime import datetime

app = Flask(__name__)
app.secret_key = "barcelona"

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

# Configuración del Bot Comentador
comenta_config = {
    'username': None,
    'password': None,
    'target_url': None,
    'comment': None,
    'last_run': None,
    'status': 'idle',
    'message': ''
}

# Función para guardar configuración del comentador
def save_comenta_config():
    with open('comenta_config.json', 'w') as f:
        json.dump(comenta_config, f)

# Función para escribir logs del bot comentador
def append_comenta_log(message):
    timestamp = datetime.now().isoformat(timespec='seconds')
    with open('comenta.log', 'a', encoding='utf-8') as f:
        f.write(f'[{timestamp}] {message}\n')

# Función para leer las últimas líneas del log del comentador
def tail_comenta_log(lines=20):
    try:
        with open('comenta.log', 'r', encoding='utf-8') as f:
            return f.readlines()[-lines:]
    except FileNotFoundError:
        return []

# Función para cargar configuración del comentador al iniciar
def load_comenta_config():
    try:
        with open('comenta_config.json') as f:
            config = json.load(f)
            comenta_config.update(config)
    except FileNotFoundError:
        pass

# Cargar configuración del comentador al inicio
load_comenta_config()

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

@app.route('/libros')
def libros():
    # Renderiza la página de bots y descargas sin depender de la base de datos.
    return render_template('sitio/libros.html', libros=[])

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
    """Cierra ventanas emergentes de Instagram intentando varias opciones en paralelo."""
    try:
        driver.find_element(By.XPATH, "//div[@role='button']").click()
        time.sleep(1)
    except Exception:
        pass

    for intento in range(4):
        try:
            botones = driver.find_elements(By.XPATH, "//*[contains(text(), 'Ahora no')]")
            for btn in botones:
                if btn.is_displayed():
                    btn.click()
                    time.sleep(1)
                    print("✅ Se hizo clic en 'Ahora no'")
                    return
        except Exception as e:
            print(f"⚠️ Error al intentar 'Ahora no': {e}")

        try:
            fallback = driver.find_elements(
                By.XPATH,
                "(//div[@data-visualcompletion='ignore' and contains(@style, 'inset')])[1]"
            )
            if fallback:
                elemento = fallback[0]
                if elemento.is_displayed():
                    elemento.click()
                    time.sleep(1)
                    print("✅ Se hizo clic en el fallback del selector alternativo")
                    return
        except Exception as e:
            print(f"⚠️ Error al revisar el fallback alternativo: {e}")

        time.sleep(1)

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

def ejecutar_comenta_bot(username, password, target_url, comment_message):
    """Función principal que ejecuta el bot comentador en Instagram"""
    driver = None
    comenta_config['status'] = 'running'
    comenta_config['message'] = 'Iniciando bot comentador...'
    save_comenta_config()

    try:
        msg = "🚀 Iniciando bot comentador..."
        print(msg)
        append_comenta_log(msg)
        
        comenta_config['message'] = 'Creando driver de Chrome...'
        save_comenta_config()
        driver = crear_driver()
        
        msg = "📱 Abriendo Instagram..."
        print(msg)
        append_comenta_log(msg)
        abrir_instagram(driver)
        
        msg = "🔐 Iniciando sesión..."
        print(msg)
        append_comenta_log(msg)
        iniciar_sesion(driver, username, password)
        
        ignorar_ventanas_emergentes(driver)
        
        msg = f"🎯 Accediendo al perfil: {target_url}"
        print(msg)
        append_comenta_log(msg)
        driver.maximize_window()
        driver.get(target_url)
        time.sleep(4)
        
        msg = "📸 Buscando publicaciones..."
        print(msg)
        append_comenta_log(msg)
        
        # Obtener publicaciones
        fotos = driver.find_elements(By.XPATH, '(//a[contains(@href, "/p/") or contains(@href, "/reel/")])')
        fotos_urls = set()
        
        for foto in fotos:
            try:
                href = foto.get_attribute('href')
                if href:
                    fotos_urls.add(href)
            except:
                pass
        
        # Hacer scroll para obtener más publicaciones
        sin_nuevas = 0
        while len(fotos_urls) < 20 and sin_nuevas < 3:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(4)
            
            anteriores = len(fotos_urls)
            posts = driver.find_elements(
                By.XPATH,
                '//a[contains(@href,"/p/") or contains(@href,"/reel/")]'
            )
            
            for post in posts:
                try:
                    href = post.get_attribute("href")
                    if href:
                        fotos_urls.add(href)
                except:
                    pass
            
            if len(fotos_urls) == anteriores:
                sin_nuevas += 1
            else:
                sin_nuevas = 0
            
            msg = f"📊 Publicaciones encontradas: {len(fotos_urls)}"
            print(msg)
            append_comenta_log(msg)
        
        msg = f"✅ Total de publicaciones a comentar: {len(fotos_urls)}"
        print(msg)
        append_comenta_log(msg)
        
        # Comentar en cada publicación
        comentadas = 0
        for url in fotos_urls:
            try:
                msg = f"📝 Visitando: {url}"
                print(msg)
                append_comenta_log(msg)
                driver.get(url)
                time.sleep(7)
                
                # Buscar y hacer click en el área de comentarios
                try:
                    if comentar_publicacion(driver, comment_message):
                        msg = f"✅ Comentario publicado: {comment_message}"
                        print(msg)
                        append_comenta_log(msg)
                        comentadas += 1
                    else:
                        msg = f"⚠️ No se pudo comentar en {url}"
                        print(msg)
                        append_comenta_log(msg)
                except StaleElementReferenceException:
                    msg = "⚠️ Elemento obsoleto, reintentando..."
                    print(msg)
                    append_comenta_log(msg)
                except Exception as e:
                    msg = f"⚠️ No se pudo comentar en {url}: {e}"
                    print(msg)
                    append_comenta_log(msg)
                
                time.sleep(3)
                
            except Exception as e:
                msg = f"❌ Error al procesar {url}: {e}"
                print(msg)
                append_comenta_log(msg)
        
        comenta_config['last_run'] = datetime.now().isoformat()
        comenta_config['status'] = 'idle'
        comenta_config['message'] = f'Bot completado: {comentadas} comentarios publicados'
        save_comenta_config()
        
        msg = f"✅ Bot completado: {comentadas} comentarios publicados exitosamente"
        print(msg)
        append_comenta_log(msg)

    except Exception as e:
        comenta_config['status'] = 'idle'
        comenta_config['message'] = f'Error en ejecución: {e}'
        save_comenta_config()
        msg = f"❌ Error en ejecución del bot comentador: {e}"
        print(msg)
        append_comenta_log(msg)

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
# Rutas del Bot Comentador
# =============================================

@app.route('/comenta', methods=['GET', 'POST'])
def comenta_bot():
    global comenta_config

    if request.method == 'POST':
        action = request.form.get('action')

        comenta_config.update({
            'username': request.form['username'],
            'password': request.form['password'],
            'target_url': request.form['target_url'],
            'comment': request.form['comment']
        })
        save_comenta_config()

        if action == 'run_now':
            try:
                comenta_config['status'] = 'starting'
                comenta_config['message'] = 'Bot de comentarios iniciándose...'
                save_comenta_config()

                threading.Thread(
                    target=ejecutar_comenta_bot,
                    args=(comenta_config['username'], comenta_config['password'], 
                          comenta_config['target_url'], comenta_config['comment']),
                    daemon=True
                ).start()
                return redirect('/comenta?success=Bot+de+comentarios+iniciado+manualmente')
            except Exception as e:
                comenta_config['status'] = 'idle'
                comenta_config['message'] = f'Error al iniciar el bot: {e}'
                save_comenta_config()
                return redirect(f'/comenta?error=Error+al+iniciar+el+bot%3A+{str(e)}')

        return redirect('/comenta?success=Configuraci%C3%B3n+guardada+correctamente')

    return render_template('sitio/comenta.html', config=comenta_config, comenta_log=tail_comenta_log(20))

@app.route('/comenta/control', methods=['POST'])
def control_comenta():
    # Control endpoint for comment bot
    return redirect('/comenta')

# =============================================
# Tarea programada y rutas administrativas
# =============================================

if __name__ == '__main__':
    app.run(debug=True)

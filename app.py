import os, sqlite3, requests
from datetime import datetime
from flask import Flask, request

TOKEN = os.environ["WA_TOKEN"]
PHONE_ID = os.environ["WA_PHONE_ID"]
VERIFY = os.environ["WA_VERIFY"]
GRAPH = "https://graph.facebook.com/v20.0"
HEAD = {"Authorization": f"Bearer {TOKEN}"}

app = Flask(__name__)
db = sqlite3.connect("pedidos.db", check_same_thread=False)
db.execute("""CREATE TABLE IF NOT EXISTS pedidos (
    telefono TEXT PRIMARY KEY, idioma TEXT, estado TEXT,
    gramos REAL, fotos TEXT, actualizado TEXT)""")
db.commit()

TEXTOS = {
    "en": {"cantidad": "How many grams do you have?",
           "fotos": "Send one photo at a time. Type 'done' when you finish.",
           "gracias": "Thank you! Your request was saved. We will contact you with a quote.",
           "error": "Please send a number, for example 250."},
    "zh": {"cantidad": "請問您有多少克？",
           "fotos": "請逐張傳送照片，完成後輸入「完成」。",
           "gracias": "謝謝！您的需求已儲存，我們會與您聯繫報價。",
           "error": "請輸入數字，例如 250。"},
    "es": {"cantidad": "¿Cuántos gramos tienes?",
           "fotos": "Envía una foto a la vez. Escribe 'listo' cuando termines.",
           "gracias": "¡Gracias! Tu solicitud quedó guardada. Te contactaremos con la cotización.",
           "error": "Por favor escribe un número, por ejemplo 250."},
}
IDIOMAS = {"1": "en", "2": "zh", "3": "es"}
MENU = ("Choose your language / 請選擇語言 / Elige tu idioma:\n"
        "1) English\n2) 繁體中文\n3) Español")

def enviar(to, texto):
    r = requests.post(f"{GRAPH}/{PHONE_ID}/messages", headers=HEAD, json={
        "messaging_product": "whatsapp", "to": to,
        "type": "text", "text": {"body": texto}})
    print("ENVIO:", r.status_code, r.text)

def guardar(tel, **campos):
    campos["actualizado"] = datetime.now().isoformat()
    filas = db.execute("SELECT 1 FROM pedidos WHERE telefono=?", (tel,)).fetchone()
    if not filas:
        db.execute("INSERT INTO pedidos (telefono, estado, fotos) VALUES (?, 'inicio', '')", (tel,))
    for k, v in campos.items():
        db.execute(f"UPDATE pedidos SET {k}=? WHERE telefono=?", (v, tel))
    db.commit()

def estado(tel):
    return db.execute("SELECT estado, idioma FROM pedidos WHERE telefono=?", (tel,)).fetchone()

def descargar_foto(tel, media_id):
    url = requests.get(f"{GRAPH}/{media_id}", headers=HEAD).json()["url"]
    datos = requests.get(url, headers=HEAD).content
    carpeta = f"fotos/{tel}"
    os.makedirs(carpeta, exist_ok=True)
    ruta = f"{carpeta}/{media_id}.jpg"
    with open(ruta, "wb") as f:
        f.write(datos)
    return ruta

@app.get("/webhook")
def verificar():
    if request.args.get("hub.verify_token") == VERIFY:
        return request.args.get("hub.challenge")
    return "error", 403

@app.post("/webhook")
def recibir():
    try:
        msg = request.json["entry"][0]["changes"][0]["value"]["messages"][0]
    except (KeyError, IndexError):
        return "ok"  # eventos de estado, no mensajes

    tel = msg["from"]
    st, idioma = estado(tel) or (None, None)
    tipo = msg["type"]
    texto = msg.get("text", {}).get("body", "").strip().lower()

    if st in (None, "inicio", "completo"):
        guardar(tel, estado="idioma", gramos=None, fotos="")
        enviar(tel, MENU)
    elif st == "idioma":
        if texto in IDIOMAS:
            idioma = IDIOMAS[texto]
            guardar(tel, idioma=idioma, estado="cantidad")
            enviar(tel, TEXTOS[idioma]["cantidad"])
        else:
            enviar(tel, MENU)
    elif st == "cantidad":
        try:
            guardar(tel, gramos=float(texto), estado="fotos")
            enviar(tel, TEXTOS[idioma]["fotos"])
        except ValueError:
            enviar(tel, TEXTOS[idioma]["error"])
    elif st == "fotos":
        if tipo == "image":
            ruta = descargar_foto(tel, msg["image"]["id"])
            fila = db.execute("SELECT fotos FROM pedidos WHERE telefono=?", (tel,)).fetchone()[0]
            guardar(tel, fotos=(fila + "," if fila else "") + ruta)
        elif texto in ("listo", "done", "完成"):
            guardar(tel, estado="completo")
            enviar(tel, TEXTOS[idioma]["gracias"])

    return "ok"

if __name__ == "__main__":
    app.run(port=5000)
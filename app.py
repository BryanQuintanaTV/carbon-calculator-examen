from flask import Flask, render_template, request, session
from datetime import datetime

app = Flask(__name__)

app.secret_key = "tu_clave_secreta_aquí"


TRANSPORT_EMISSIONS = {
    "coche": 0.192,
    "autobús": 0.105,
    "metro": 0.041,
    "bicicleta": 0.0,
    "motocicleta": 0.103
}

def get_recommendations(co2, transport):
    recs = []
    if co2 == 0:
        recs.append("¡Genial! Con bicicleta no emites CO₂.")
    if transport == "coche" and co2 > 20:
        recs.append("Comparte vehículos: Si necesitas usar un vehículo, considera compartirlo con amigos o familiares. Esto reduce el número de vehículos en la carretera y la cantidad de contaminantes que se emiten.")
    if transport in ["coche", "motocicleta"] and co2 > 50:
        recs.append("Usa transporte público: El transporte público es una de las formas más sostenibles de viajar. Puedes usar autobuses, trenes o metro para desplazarte.")
    if co2 > 100:
        recs.append("Tu huella es alta: Se recomienda usar transporte público o bicicleta para reducir tu huella de carbono, Si estas trabajando considera hacer teletrabajo o video llamadas.")
    recs.append("Otras recomendaciones:")
    recs.append("Cicla o camina: Si la distancia es corta, considera caminar o montar en bicicleta. Estas formas de transporte no emiten contaminantes y te ayudan a mantener la forma.")
    
    return recs

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    recommendations = []


    if "history" not in session:
        session["history"] = []

    if request.method == "POST":
        try:
            transport = request.form["transport"]
            km = float(request.form["km"])
            factor = TRANSPORT_EMISSIONS.get(transport, 0)
            huella = km * factor
            result = f"Tu huella de la semana en {transport} es {huella:.2f} kg de CO₂"

            
            recommendations = get_recommendations(huella, transport)


            entry = {
                "transport": transport,
                "km": km,
                "co2": f"{huella:.2f}"
            }
            history = session["history"]
            history.insert(0, entry)
            session["history"] = history[:10]

        except ValueError:
            result = "ERROR: Por favor, introduce un número válido para los kilómetros."

    history = session.get("history", [])
    return render_template(
        "index.html",
        result=result,
        history=history,
        recommendations=recommendations
    )

if __name__ == "__main__":
    app.run(debug=True)

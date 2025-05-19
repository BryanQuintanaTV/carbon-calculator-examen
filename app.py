from flask import Flask, render_template, request, session
from datetime import datetime

app = Flask(__name__)
# Clave para firmar la cookie de sesión
app.secret_key = "tu_clave_secreta_aquí"

# 1) Factores de emisión (kg CO₂/km) para distintos medios
TRANSPORT_EMISSIONS = {
    "coche": 0.192,
    "autobús": 0.105,
    "tren": 0.041,
    "bicicleta": 0.0,
    "motocicleta": 0.103,
    "avión": 0.255,
}

def get_recommendations(co2, transport):
    """
    3) Genera recomendaciones basadas en la huella calculada.
    """
    recs = []
    if co2 == 0:
        recs.append("¡Genial! Con bicicleta no emites CO₂.")
    if transport == "coche" and co2 > 20:
        recs.append("¿Has probado el coche compartido para reducir tu huella?")
    if transport in ["coche", "motocicleta"] and co2 > 50:
        recs.append("Considera usar transporte público o bicicleta para distancias cortas.")
    if co2 > 100:
        recs.append("Tu huella es alta: plantéate alternar con videoconferencias o teletrabajo.")
    recs.append("Revisa opciones de compensación de CO₂ mediante proyectos de reforestación.")
    return recs

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    recommendations = []

    # 2) Inicializa el historial en sesión si no existe
    if "history" not in session:
        session["history"] = []

    if request.method == "POST":
        try:
            transport = request.form["transport"]
            km = float(request.form["km"])
            factor = TRANSPORT_EMISSIONS.get(transport, 0)
            huella = km * factor
            result = f"Tu huella semanal en {transport} es {huella:.2f} kg de CO₂"

            # 3) Generar recomendaciones
            recommendations = get_recommendations(huella, transport)

            # 2) Guardar entrada al historial (solo en sesión)
            entry = {
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "transport": transport,
                "km": km,
                "co2": f"{huella:.2f}"
            }
            history = session["history"]
            history.insert(0, entry)
            # Conserva sólo las 5 entradas más recientes
            session["history"] = history[:5]

        except ValueError:
            result = "Por favor, ingresa un número válido."

    history = session.get("history", [])
    return render_template(
        "index.html",
        result=result,
        history=history,
        recommendations=recommendations
    )

if __name__ == "__main__":
    app.run(debug=True)

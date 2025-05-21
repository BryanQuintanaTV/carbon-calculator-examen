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
    Genera recomendaciones personalizadas en función de la huella de carbono estimada
    y el medio de transporte seleccionado.
    """
    recs = []

    if co2 == 0:
        recs.append("¡Excelente! Usar bicicleta es una opción totalmente libre de emisiones.")

    # Recomendaciones por tipo de transporte
    if transport == "coche":
        if co2 > 20:
            recs.append("Compartir el coche con otras personas ayuda a reducir tu impacto ambiental.")
        recs.append("Mantener tu coche afinado y con neumáticos inflados mejora la eficiencia y reduce emisiones.")

    elif transport == "autobús":
        recs.append("El autobús es una opción eficiente, especialmente si va con alta ocupación.")
        recs.append("Usarlo en lugar del coche particular ya representa una mejora en tu huella de carbono.")

    elif transport == "tren":
        recs.append("Los trenes eléctricos son de las opciones más limpias para viajes largos.")
        recs.append("Viajar en tren ayuda a disminuir significativamente el CO₂ por pasajero.")

    elif transport == "bicicleta":
        recs.append("Además de no emitir CO₂, mejora tu salud física y mental.")
        recs.append("¡Sigue pedaleando! Es una forma ecológica y saludable de moverte.")

    elif transport == "motocicleta":
        if co2 > 50:
            recs.append("Si usas motocicleta con frecuencia, considera cambiarla por una eléctrica o por transporte público.")
        recs.append("El uso moderado y responsable de motocicletas puede reducir emisiones respecto al coche, pero aún así genera CO₂.")

    elif transport == "avión":
        recs.append("El avión genera una gran cantidad de emisiones. Intenta evitar vuelos cortos si hay alternativas por tierra.")
        if co2 > 100:
            recs.append("Considera compensar el CO₂ de tus vuelos apoyando proyectos ambientales certificados.")

    # Recomendación final general
    recs.append("También puedes contribuir apoyando programas de reforestación y conservación ambiental.")
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

from collections import Counter

def generar_recomendacion_trimestre(resultados, inscripciones):
    if not resultados:
        return "No hay suficientes datos para generar una recomendación."

    trimestres_con_inscripciones = [r for r in resultados if r['inscripciones'] > 0]
    if not trimestres_con_inscripciones:
        return "No se registraron inscripciones en ningún trimestre todavía."

    # Trimestre más inscripciones
    trimestre_max = max(trimestres_con_inscripciones, key=lambda r: r['inscripciones'])

    # Calcular categoría más inscrita
    categoria_counter = Counter()
    modalidad_counter = Counter()

    for i in inscripciones:
        if i.curso.categoria:
            categoria_counter[i.curso.categoria.nombre] += 1
        modalidad_counter[i.curso.modalidad] += 1

    categoria_top = categoria_counter.most_common(1)[0][0] if categoria_counter else "desconocida"
    modalidad_top = modalidad_counter.most_common(1)[0][0] if modalidad_counter else "desconocida"

    return (
        f"Se recomienda priorizar la creación de cursos en el trimestre {trimestre_max['nombre']}, "
        f"preferentemente de la categoría '{categoria_top}' y en modalidad '{modalidad_top}', "
        f"que han mostrado mayor interés por parte de los estudiantes."
    )

class MembresiaStrategy:
    def validar(self, user, curso, plan):
        raise NotImplementedError("Debes implementar este método")

class GratuitaStrategy(MembresiaStrategy):
    def validar(self, user, curso, plan):
        if curso.precio > 0:
            return False, f"Tu plan '{plan.nombre}' solo permite cursos gratuitos."
        return True, ""

class BasicaStrategy(MembresiaStrategy):
    def validar(self, user, curso, plan):
        if curso.precio > plan.limite_precio_curso:
            return False, f"Tu plan '{plan.nombre}' solo permite cursos hasta ${plan.limite_precio_curso}."
        return True, ""

class PremiumStrategy(MembresiaStrategy):
    def validar(self, user, curso, plan):
        return True, ""

def get_strategy_for_plan(plan):
    nombre = plan.nombre.lower()
    if nombre == "gratuita":
        return GratuitaStrategy()
    elif nombre == "básica":
        return BasicaStrategy()
    elif nombre == "premium":
        return PremiumStrategy()
    else:
        return GratuitaStrategy()

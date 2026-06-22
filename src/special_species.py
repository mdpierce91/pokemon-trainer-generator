
from consts import BASE_FORM


class SpecialSpecies():

    @staticmethod
    def rotom(rotom_object):
        # rotom specific conversion
        if rotom_object.get("species", None) == 'rotom':
            form = rotom_object.get("form", BASE_FORM)
            if form != BASE_FORM:
                aspects = rotom_object.get("aspects", None)
                if not aspects:
                    rotom_object["aspects"] = [f'{form}-appliance']
                else:
                    rotom_object["aspects"].append(f'{form}-appliance')

    species_functions = {
        "rotom": rotom,
    }


    @classmethod
    def check_and_apply(cls, species_object):
        name = species_object.get("species", None)
        if name and name in cls.species_functions.keys():
            cls.species_functions[name](species_object)

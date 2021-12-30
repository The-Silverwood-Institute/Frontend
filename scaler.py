import re

from fractions import Fraction

def get_scale_factor(req_params):
    if 'scale' not in req_params:
        return None

    raw_scale = req_params['scale']

    try:
        scale = float(raw_scale)
    except ValueError:
        return None

    if scale == 1 or scale == 0:
        return None

    if scale > 50 or scale < 0:
        return None

    return scale

quantity_parser             = re.compile('^([0-9]+)( {0,1}[a-z]+){0,1}$', re.IGNORECASE)
fraction_quantity_parser    = re.compile('^([0-9]+/[0-9]+)( {0,1}[a-z]+){0,1}$', re.IGNORECASE)

def get_simple_quantity(raw_quantity):
    match = quantity_parser.match(raw_quantity)

    if match:
        quantity    = int(match.group(1))
        suffix      = match.group(2)

        return (quantity, suffix)
    else:
        return (None, None)

def get_fraction_quantity(raw_quantity):
    match = fraction_quantity_parser.match(raw_quantity)

    if match:
        quantity    = Fraction(match.group(1))
        suffix      = match.group(2)

        return (quantity, suffix)
    else:
        return (None, None)

def scale_ingredient(ingredient, factor):
    if ingredient['quantity'] is None:
        return ingredient
    else:
        (quantity, suffix) = get_simple_quantity(ingredient['quantity'])

        if quantity is None:
            (quantity, suffix) = get_fraction_quantity(ingredient['quantity'])

        if quantity is None:
            return ingredient['quantity']

        scaled_ingredient   = quantity * factor
        str_suffix          = suffix if suffix is not None else ''

        if isinstance(scaled_ingredient, Fraction):
            remainder = scaled_ingredient.numerator // scaled_ingredient.denominator

            if remainder:
                even_fraction = scaled_ingredient - remainder

                ingredient['quantity'] = '{} {}/{}{}'.format(
                    remainder,
                    even_fraction.numerator,
                    even_fraction.denominator,
                    str_suffix
                )
            else:
                ingredient['quantity'] = '{}/{}{}'.format(
                    scaled_ingredient.numerator,
                    scaled_ingredient.denominator,
                    str_suffix
                )
        elif scaled_ingredient % 1 == 0:
            ingredient['quantity'] = '{:d}{}'.format(int(scaled_ingredient), str_suffix)
        else:
            ingredient['quantity'] = '{:.2f}{}'.format(scaled_ingredient, str_suffix)

        ingredient['scaled'] = True
        return ingredient

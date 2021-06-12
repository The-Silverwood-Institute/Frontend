import re

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

quantity_parser = re.compile('^([0-9]+)( {0,1}[a-z]+){0,1}$', re.IGNORECASE)

def scale_ingredient(ingredient, factor):
    if ingredient['quantity'] is None:
        return ingredient
    else:
        match = quantity_parser.match(ingredient['quantity'])

        if not match:
            return ingredient

        quantity = int(match.group(1))
        suffix = match.group(2) if match.group(2) is not None else ''

        scaled_ingredient = quantity * factor

        if scaled_ingredient % 1 == 0:
            ingredient['quantity'] = '{:d}{}'.format(int(scaled_ingredient), suffix)
        else:
            ingredient['quantity'] = '{:.2f}{}'.format(scaled_ingredient, suffix)

        ingredient['scaled'] = True
        return ingredient

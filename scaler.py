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

    if scale > 50:
        return None

    return scale

def scale_ingredient(ingredient, factor):
    if ingredient['quantity'] is None:
        return ingredient
    else:
        try:
            quantity = int(ingredient['quantity'])
        except ValueError:
            return ingredient

        scaled_ingredient = quantity * factor

        if scaled_ingredient % 1 == 0:
            ingredient['quantity'] = '{:d}'.format(int(scaled_ingredient))
        else:
            ingredient['quantity'] = '{:.2f}'.format(scaled_ingredient)

        ingredient['scaled'] = True
        return ingredient

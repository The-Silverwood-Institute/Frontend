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

def format_suffix(suffix):
    return suffix if suffix is not None else ''

class SimpleQuantity:
    parser = re.compile('^([0-9]+)( {0,1}[a-z]+){0,1}$', re.IGNORECASE)

    @staticmethod
    def parse(raw_quantity):
        match = SimpleQuantity.parser.match(raw_quantity)

        if match:
            quantity    = int(match.group(1))
            suffix      = match.group(2)

            return SimpleQuantity(quantity, suffix)
        else:
            return None

    def __init__(self, quantity, suffix):
        self.quantity   = quantity
        self.suffix     = suffix

    def __mul__(self, by):
        return SimpleQuantity(self.quantity * by, self.suffix)

    def __str__(self):
        if self.quantity % 1 == 0:
            return '{:d}{}'.format(int(self.quantity), format_suffix(self.suffix))
        else:
            return '{:.2f}{}'.format(self.quantity, format_suffix(self.suffix))

class RangeQuantity:
    parser = re.compile('^([0-9]+)-([0-9]+)( {0,1}[a-z]+){0,1}$', re.IGNORECASE)

    @staticmethod
    def parse(raw_quantity):
        match = RangeQuantity.parser.match(raw_quantity)

        if match:
            lower_quantity  = int(match.group(1))
            upper_quantity  = int(match.group(2))
            suffix          = match.group(3)

            return RangeQuantity(lower_quantity, upper_quantity, suffix)
        else:
            return None

    def __init__(self, lower_quantity, upper_quantity, suffix):
        self.lower_quantity = lower_quantity
        self.upper_quantity = upper_quantity
        self.suffix         = suffix

    def __mul__(self, by):
        return RangeQuantity(
            self.lower_quantity * by,
            self.upper_quantity * by,
            self.suffix
        )

    def __str__(self):
        if self.lower_quantity % 1 == 0 and self.upper_quantity % 1 == 0:
            return '{:d}-{:d}{}'.format(
                int(self.lower_quantity),
                int(self.upper_quantity),
                format_suffix(self.suffix)
            )
        else:
            return '{:.2f}-{:.2f}{}'.format(
                self.lower_quantity,
                self.upper_quantity,
                format_suffix(self.suffix)
            )

class FractionQuantity:
    parser = re.compile('^([0-9]+/[0-9]+)( {0,1}[a-z]+){0,1}$', re.IGNORECASE)

    @staticmethod
    def parse(raw_quantity):
        match = FractionQuantity.parser.match(raw_quantity)

        if match:
            quantity    = Fraction(match.group(1))
            suffix      = match.group(2)

            return FractionQuantity(quantity, suffix)
        else:
            return None

    def __init__(self, quantity, suffix):
        self.quantity   = quantity
        self.suffix     = suffix

    def __mul__(self, by):
        return FractionQuantity(self.quantity * by, self.suffix)

    def __str__(self):
        remainder = self.quantity.numerator // self.quantity.denominator

        if remainder and self.quantity.numerator == self.quantity.denominator:
            return '{}{}'.format(
                remainder,
                format_suffix(self.suffix)
            )
        elif remainder:
            even_fraction = self.quantity - remainder

            return '{} {}/{}{}'.format(
                remainder,
                even_fraction.numerator,
                even_fraction.denominator,
                format_suffix(self.suffix)
            )
        else:
            return '{}/{}{}'.format(
                self.quantity.numerator,
                self.quantity.denominator,
                format_suffix(self.suffix)
            )

def scale_ingredient(ingredient, factor):
    if ingredient['quantity'] is None:
        return ingredient

    formats = [
        SimpleQuantity,
        RangeQuantity,
        FractionQuantity
    ]

    for format in formats:
        quantity = format.parse(ingredient['quantity'])

        if quantity:
            break

    if quantity is None:
        return ingredient

    scaled_quantity = quantity * factor

    ingredient['scaled']    = True
    ingredient['quantity']  = str(scaled_quantity)

    return ingredient

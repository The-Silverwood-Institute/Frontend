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


def format_number(value):
    if value % 1 == 0:
        return str(int(value))
    return '{:.2f}'.format(value)


def pluralize_unit(unit, count):
    if count == 1:
        return unit
    if unit.endswith('s'):
        return unit
    return unit + 's'


class SimpleQuantity:
    parser = re.compile(
        r'^([0-9]+(?:\.[0-9]+)?)( {0,1}[a-z]+){0,1}$',
        re.IGNORECASE
    )

    @staticmethod
    def parse(raw_quantity):
        match = SimpleQuantity.parser.match(raw_quantity)
        if not match:
            return None
        return SimpleQuantity(float(match.group(1)), match.group(2))

    def __init__(self, quantity, suffix):
        self.quantity = quantity
        self.suffix = suffix

    def __mul__(self, by):
        return SimpleQuantity(self.quantity * by, self.suffix)

    def __str__(self):
        return '{}{}'.format(format_number(self.quantity), format_suffix(self.suffix))


class RangeQuantity:
    parser = re.compile(
        r'^([0-9]+(?:\.[0-9]+)?)-([0-9]+(?:\.[0-9]+)?)( {0,1}[a-z]+){0,1}$',
        re.IGNORECASE
    )

    @staticmethod
    def parse(raw_quantity):
        match = RangeQuantity.parser.match(raw_quantity)
        if not match:
            return None
        return RangeQuantity(
            float(match.group(1)),
            float(match.group(2)),
            match.group(3)
        )

    def __init__(self, lower_quantity, upper_quantity, suffix):
        self.lower_quantity = lower_quantity
        self.upper_quantity = upper_quantity
        self.suffix = suffix

    def __mul__(self, by):
        return RangeQuantity(
            self.lower_quantity * by,
            self.upper_quantity * by,
            self.suffix
        )

    def __str__(self):
        return '{}-{}{}'.format(
            format_number(self.lower_quantity),
            format_number(self.upper_quantity),
            format_suffix(self.suffix)
        )


class FractionQuantity:
    parser = re.compile(
        r'^([0-9]+/[0-9]+)( {0,1}[a-z]+){0,1}$',
        re.IGNORECASE
    )

    @staticmethod
    def parse(raw_quantity):
        match = FractionQuantity.parser.match(raw_quantity)
        if not match:
            return None
        return FractionQuantity(Fraction(match.group(1)), match.group(2))

    def __init__(self, quantity, suffix):
        self.quantity = quantity
        self.suffix = suffix

    def __mul__(self, by):
        return FractionQuantity(Fraction(self.quantity * by), self.suffix)

    def __str__(self):
        remainder = self.quantity.numerator // self.quantity.denominator

        if self.quantity.denominator > 10:
            return '{:.2f}{}'.format(
                float(self.quantity),
                format_suffix(self.suffix)
            )
        elif remainder and self.quantity.numerator == self.quantity.denominator:
            return '{}{}'.format(remainder, format_suffix(self.suffix))
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


class MixedFractionQuantity:
    parser = re.compile(
        r'^([0-9]+)\s+([0-9]+/[0-9]+)( {0,1}[a-z]+){0,1}$',
        re.IGNORECASE
    )

    @staticmethod
    def parse(raw_quantity):
        match = MixedFractionQuantity.parser.match(raw_quantity)
        if not match:
            return None
        whole = int(match.group(1))
        fraction = Fraction(match.group(2))
        return MixedFractionQuantity(whole + fraction, match.group(3))

    def __init__(self, quantity, suffix):
        self.quantity = quantity
        self.suffix = suffix

    def __mul__(self, by):
        scaled = self.quantity * by
        if scaled % 1 == 0:
            return SimpleQuantity(scaled, self.suffix)
        return MixedFractionQuantity(scaled, self.suffix)

    def __str__(self):
        if isinstance(self.quantity, Fraction):
            return str(FractionQuantity(self.quantity, self.suffix))
        return str(SimpleQuantity(self.quantity, self.suffix))


class CompoundQuantity:
    parser = re.compile(
        r'^(?:(\d+)\s+)?(\d+(?:g|ml))\s+(\w+)$',
        re.IGNORECASE
    )

    @staticmethod
    def parse(raw_quantity):
        match = CompoundQuantity.parser.match(raw_quantity)
        if not match:
            return None
        if match.group(1):
            return CompoundQuantity(
                int(match.group(1)),
                match.group(2),
                match.group(3),
                explicit_count=True
            )
        return CompoundQuantity(1, match.group(2), match.group(3))

    def __init__(self, count, size, unit, explicit_count=False):
        self.count = count
        self.size = size
        self.unit = unit
        self.explicit_count = explicit_count

    def __mul__(self, by):
        return CompoundQuantity(
            self.count * by,
            self.size,
            self.unit,
            explicit_count=True
        )

    def __str__(self):
        unit = pluralize_unit(self.unit, self.count)
        if self.count == 1 and not self.explicit_count:
            return '{} {}'.format(self.size, unit)
        return '{} {} {}'.format(
            format_number(self.count),
            self.size,
            unit
        )


class ParentheticalQuantity:
    parser = re.compile(
        r'^(\d+)\s+(\w+)(?:,\s*approx\.\s*(\d+g)|\s+\((\d+g)\))$',
        re.IGNORECASE
    )

    @staticmethod
    def parse(raw_quantity):
        match = ParentheticalQuantity.parser.match(raw_quantity)
        if not match:
            return None
        size = match.group(3) or match.group(4)
        approx = match.group(3) is not None
        return ParentheticalQuantity(
            int(match.group(1)),
            match.group(2),
            size,
            approx
        )

    def __init__(self, count, unit, size, approx):
        self.count = count
        self.unit = unit
        self.size = size
        self.approx = approx

    def __mul__(self, by):
        size = self.size
        if self.approx:
            size_match = re.match(r'^(\d+(?:\.\d+)?)(g|ml)$', self.size, re.IGNORECASE)
            if size_match:
                size = '{}{}'.format(
                    format_number(float(size_match.group(1)) * by),
                    size_match.group(2)
                )
        return ParentheticalQuantity(
            self.count * by,
            self.unit,
            size,
            self.approx
        )

    def __str__(self):
        unit = pluralize_unit(self.unit, self.count)
        if self.approx:
            return '{} {}, approx {}'.format(
                format_number(self.count),
                unit,
                self.size
            )
        return '{} {} ({})'.format(
            format_number(self.count),
            unit,
            self.size
        )


class LengthQuantity:
    parser = re.compile(
        r'^(\d+(?:\.\d+)?)(\s*)cm(?:\s+(piece))?$',
        re.IGNORECASE
    )

    @staticmethod
    def parse(raw_quantity):
        match = LengthQuantity.parser.match(raw_quantity)
        if not match:
            return None
        return LengthQuantity(
            float(match.group(1)),
            match.group(2),
            match.group(3) is not None
        )

    def __init__(self, amount, spacing, has_piece):
        self.amount = amount
        self.spacing = spacing
        self.has_piece = has_piece

    def __mul__(self, by):
        return LengthQuantity(self.amount * by, self.spacing, self.has_piece)

    def __str__(self):
        amount = format_number(self.amount)
        if self.has_piece:
            piece = pluralize_unit('piece', self.amount)
            return '{}{}cm {}'.format(amount, self.spacing, piece)
        return '{}{}cm'.format(amount, self.spacing)


class DescriptiveQuantity:
    parser = re.compile(
        r'^(\d+(?:\.\d+)?)\s+(.+)$',
        re.IGNORECASE
    )
    non_plural_suffixes = {'minimum'}

    @staticmethod
    def parse(raw_quantity):
        match = DescriptiveQuantity.parser.match(raw_quantity)
        if not match:
            return None
        description = match.group(2)
        if len(description.split(' ')) < 2 and '-' not in description:
            return None
        return DescriptiveQuantity(float(match.group(1)), description)

    def __init__(self, count, description):
        self.count = count
        self.description = description

    def __mul__(self, by):
        return DescriptiveQuantity(self.count * by, self.description)

    def __str__(self):
        words = self.description.split(' ')
        if self.count != 1:
            if words[-1].lower() in DescriptiveQuantity.non_plural_suffixes:
                words[-2] = pluralize_unit(words[-2], self.count)
            else:
                words[-1] = pluralize_unit(words[-1], self.count)
        return '{} {}'.format(format_number(self.count), ' '.join(words))


class ApproximateQuantity:
    parsers = [
        re.compile(r'^~(\d+(?:\.\d+)?)(g|ml)$', re.IGNORECASE),
        re.compile(r'^(\d+(?:\.\d+)?)(g|ml)\s+approx$', re.IGNORECASE),
        re.compile(r'^up to (\d+(?:\.\d+)?)(g|ml)$', re.IGNORECASE),
    ]

    @staticmethod
    def parse(raw_quantity):
        match = ApproximateQuantity.parsers[0].match(raw_quantity)
        if match:
            return ApproximateQuantity(
                'tilde',
                float(match.group(1)),
                match.group(2)
            )

        match = ApproximateQuantity.parsers[1].match(raw_quantity)
        if match:
            return ApproximateQuantity(
                'suffix',
                float(match.group(1)),
                match.group(2)
            )

        match = ApproximateQuantity.parsers[2].match(raw_quantity)
        if match:
            return ApproximateQuantity(
                'upto',
                float(match.group(1)),
                match.group(2)
            )

        return None

    def __init__(self, style, amount, unit):
        self.style = style
        self.amount = amount
        self.unit = unit

    def __mul__(self, by):
        return ApproximateQuantity(self.style, self.amount * by, self.unit)

    def __str__(self):
        amount = format_number(self.amount)
        if self.style == 'tilde':
            return '~{}{}'.format(amount, self.unit)
        if self.style == 'suffix':
            return '{}{} approx'.format(amount, self.unit)
        return 'up to {}{}'.format(amount, self.unit)


QUANTITY_PARSERS = [
    ApproximateQuantity.parse,
    CompoundQuantity.parse,
    ParentheticalQuantity.parse,
    MixedFractionQuantity.parse,
    RangeQuantity.parse,
    FractionQuantity.parse,
    LengthQuantity.parse,
    DescriptiveQuantity.parse,
    SimpleQuantity.parse,
]


def parse_quantity(raw_quantity):
    for parser in QUANTITY_PARSERS:
        quantity = parser(raw_quantity)
        if quantity is not None:
            return quantity
    return None


def scale_ingredient(ingredient, factor):
    if ingredient['quantity'] is None:
        return ingredient

    quantity = parse_quantity(ingredient['quantity'])
    if quantity is None:
        return ingredient

    ingredient['scaled'] = True
    ingredient['quantity'] = str(quantity * factor)
    return ingredient


def normalize_unit(suffix):
    return (suffix or '').strip().lower()


def is_shopping_omitted_quantity(raw_quantity):
    if raw_quantity is None or raw_quantity == '':
        return True
    lowered = raw_quantity.lower().strip()
    return lowered.endswith('tsp') or lowered.endswith('tbsp')


def add_quantities(first, second):
    """Sum two parsed quantities when units are compatible, else None."""
    if isinstance(first, SimpleQuantity) and isinstance(second, SimpleQuantity):
        if normalize_unit(first.suffix) != normalize_unit(second.suffix):
            return None
        return SimpleQuantity(first.quantity + second.quantity, first.suffix)

    if isinstance(first, FractionQuantity) and isinstance(second, FractionQuantity):
        if normalize_unit(first.suffix) != normalize_unit(second.suffix):
            return None
        return FractionQuantity(first.quantity + second.quantity, first.suffix)

    if isinstance(first, MixedFractionQuantity) and isinstance(second, MixedFractionQuantity):
        if normalize_unit(first.suffix) != normalize_unit(second.suffix):
            return None
        return MixedFractionQuantity(first.quantity + second.quantity, first.suffix)

    summable = (SimpleQuantity, FractionQuantity, MixedFractionQuantity)
    if isinstance(first, summable) and isinstance(second, summable):
        if normalize_unit(first.suffix) != normalize_unit(second.suffix):
            return None
        total = float(first.quantity) + float(second.quantity)
        return SimpleQuantity(total, first.suffix)

    if isinstance(first, RangeQuantity) and isinstance(second, RangeQuantity):
        if normalize_unit(first.suffix) != normalize_unit(second.suffix):
            return None
        return RangeQuantity(
            first.lower_quantity + second.lower_quantity,
            first.upper_quantity + second.upper_quantity,
            first.suffix,
        )

    if isinstance(first, ApproximateQuantity) and isinstance(second, ApproximateQuantity):
        if first.style != second.style or first.unit.lower() != second.unit.lower():
            return None
        return ApproximateQuantity(first.style, first.amount + second.amount, first.unit)

    if isinstance(first, LengthQuantity) and isinstance(second, LengthQuantity):
        if first.has_piece != second.has_piece:
            return None
        return LengthQuantity(
            first.amount + second.amount,
            first.spacing,
            first.has_piece,
        )

    if isinstance(first, CompoundQuantity) and isinstance(second, CompoundQuantity):
        if first.size.lower() != second.size.lower() or first.unit.lower() != second.unit.lower():
            return None
        return CompoundQuantity(
            first.count + second.count,
            first.size,
            first.unit,
            explicit_count=True,
        )

    if isinstance(first, ParentheticalQuantity) and isinstance(second, ParentheticalQuantity):
        if (
            first.unit.lower() != second.unit.lower()
            or first.size.lower() != second.size.lower()
            or first.approx != second.approx
        ):
            return None
        return ParentheticalQuantity(
            first.count + second.count,
            first.unit,
            first.size,
            first.approx,
        )

    if isinstance(first, DescriptiveQuantity) and isinstance(second, DescriptiveQuantity):
        if first.description.lower() != second.description.lower():
            return None
        return DescriptiveQuantity(first.count + second.count, first.description)

    return None


def merge_quantity_strings(existing_raw, new_raw):
    """Merge two raw quantity strings. Returns (merged_raw, True) or (None, False)."""
    if is_shopping_omitted_quantity(existing_raw):
        if is_shopping_omitted_quantity(new_raw):
            return None, True
        return new_raw, True

    if is_shopping_omitted_quantity(new_raw):
        return existing_raw, True

    existing_parsed = parse_quantity(existing_raw)
    new_parsed = parse_quantity(new_raw)

    if existing_parsed is None or new_parsed is None:
        if existing_raw == new_raw:
            return existing_raw, True
        return None, False

    combined = add_quantities(existing_parsed, new_parsed)
    if combined is None:
        return None, False
    return str(combined), True


def format_ingredient_for_copy(name, raw_quantity):
    if is_shopping_omitted_quantity(raw_quantity):
        return name
    return '{} {}'.format(raw_quantity, name)


def ingredients_copy_text(ingredients_blocks):
    """Build clipboard text with duplicate ingredients merged across blocks."""
    merged = []

    for block in ingredients_blocks:
        for ingredient in block['ingredients']:
            name = ingredient['name']
            raw_quantity = ingredient.get('quantity')
            merge_target = None
            combined_quantity = None

            for item in merged:
                if item['name'].lower() != name.lower():
                    continue
                combined, compatible = merge_quantity_strings(
                    item['quantity'],
                    raw_quantity,
                )
                if compatible:
                    merge_target = item
                    combined_quantity = combined
                    break

            if merge_target is not None:
                merge_target['quantity'] = combined_quantity
            else:
                merged.append({'name': name, 'quantity': raw_quantity})

    return '\n'.join(
        format_ingredient_for_copy(item['name'], item['quantity'])
        for item in merged
    )

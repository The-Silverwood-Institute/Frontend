import scaler

class TestGetScaleFactor:
    @staticmethod
    def make_param(value):
        req_params = {
            'scale' : value
        }

        return req_params

    def test_return_nothing_if_no_param(self):
        assert scaler.get_scale_factor({}) == None

    def test_return_nothing_if_non_numeric(self):
        req_params = TestGetScaleFactor.make_param('lol')
        assert scaler.get_scale_factor(req_params) == None

    def test_return_number_if_numeric_scale(self):
        assert scaler.get_scale_factor(TestGetScaleFactor.make_param('2')) == 2
        assert scaler.get_scale_factor(TestGetScaleFactor.make_param('5')) == 5
        assert scaler.get_scale_factor(TestGetScaleFactor.make_param('20')) == 20

    def test_return_number_if_decimal_number_scale(self):
        assert scaler.get_scale_factor(TestGetScaleFactor.make_param('0.5')) == 0.5
        assert scaler.get_scale_factor(TestGetScaleFactor.make_param('.5')) == 0.5
        assert scaler.get_scale_factor(TestGetScaleFactor.make_param('1.5')) == 1.5

    def test_ignore_silly_scale(self):
        assert scaler.get_scale_factor(TestGetScaleFactor.make_param('1')) == None
        assert scaler.get_scale_factor(TestGetScaleFactor.make_param('0')) == None
        assert scaler.get_scale_factor(TestGetScaleFactor.make_param('1.0')) == None
        assert scaler.get_scale_factor(TestGetScaleFactor.make_param('0.0')) == None
        assert scaler.get_scale_factor(TestGetScaleFactor.make_param('-1')) == None
        assert scaler.get_scale_factor(TestGetScaleFactor.make_param('-1.0')) == None

    def test_ignore_large_scales(self):
        assert scaler.get_scale_factor(TestGetScaleFactor.make_param('50')) == 50
        assert scaler.get_scale_factor(TestGetScaleFactor.make_param('51')) == None
        assert scaler.get_scale_factor(TestGetScaleFactor.make_param('1000')) == None

class TestScaleIngredient:
    @staticmethod
    def make_ingredient(quantity):
        ingredient = {
            'name'     : 'Onion',
            'prep'     : 'chopped',
            'notes'    : None,
            'quantity' : quantity
        }

        return ingredient

    @staticmethod
    def make_scaled_ingredient(quantity):
        ingredient = TestScaleIngredient.make_ingredient(quantity)
        ingredient['scaled'] = True
        return ingredient

    def test_ignore_ingredients_with_no_quantity(self):
        ingredient = {'name': 'Onion', 'quantity': None}
        assert scaler.scale_ingredient(ingredient, 2) == {'name': 'Onion', 'quantity': None}

    def test_ignore_ingredients_with_unparseable_quantity(self):
        ingredient = {'name': 'Onion', 'quantity': 'About 3'}
        assert scaler.scale_ingredient(ingredient, 2) == {'name': 'Onion', 'quantity': 'About 3'}

    def test_scale_ingredient(self):
        ingredient = {'name': 'Onion', 'quantity': '2'}
        scaled_ingredient = scaler.scale_ingredient(ingredient, 2)
        assert scaled_ingredient['quantity'] == '4'
        assert scaled_ingredient['scaled'] == True

    def test_scale_ingredient_by_fraction(self):
        ingredient = {'name': 'Onion', 'quantity': '1'}
        scaled_ingredient = scaler.scale_ingredient(ingredient, 1.5)
        assert scaled_ingredient['quantity'] == '1.50'
        assert scaled_ingredient['scaled'] == True

    def test_scale_ingredient_with_suffix(self):
        ingredient        = TestScaleIngredient.make_ingredient('4g')
        scaled_ingredient = TestScaleIngredient.make_scaled_ingredient('8g')

        assert scaler.scale_ingredient(ingredient, 2.0) == scaled_ingredient

        ingredient        = TestScaleIngredient.make_ingredient('2 tbsp')
        scaled_ingredient = TestScaleIngredient.make_scaled_ingredient('4 tbsp')

        assert scaler.scale_ingredient(ingredient, 2.0) == scaled_ingredient

    def test_scale_ingredient_with_fraction(self):
        ingredient        = TestScaleIngredient.make_ingredient('1/4')
        scaled_ingredient = TestScaleIngredient.make_scaled_ingredient('1/2')

        assert scaler.scale_ingredient(ingredient, 2.0) == scaled_ingredient

    def test_scale_ingredient_with_uneven_fraction(self):
        ingredient        = TestScaleIngredient.make_ingredient('1/4')
        scaled_ingredient = TestScaleIngredient.make_scaled_ingredient('1 1/4')

        assert scaler.scale_ingredient(ingredient, 5.0) == scaled_ingredient

    def test_scale_fractional_ingredient_to_int(self):
        ingredient        = TestScaleIngredient.make_ingredient('1/2')
        scaled_ingredient = TestScaleIngredient.make_scaled_ingredient('1')

        assert scaler.scale_ingredient(ingredient, 2.0) == scaled_ingredient

    def test_scale_messy_fraction_to_decimal(self):
        ingredient        = TestScaleIngredient.make_ingredient('1/2')
        scaled_ingredient = TestScaleIngredient.make_scaled_ingredient('0.90')

        assert scaler.scale_ingredient(ingredient, 1.8) == scaled_ingredient

    def test_scale_ingredient_with_uneven_fraction_with_suffix(self):
        ingredient        = TestScaleIngredient.make_ingredient('1/4 tsp')
        scaled_ingredient = TestScaleIngredient.make_scaled_ingredient('1 1/4 tsp')

        assert scaler.scale_ingredient(ingredient, 5.0) == scaled_ingredient

    def test_scale_ingredient_with_range(self):
        ingredient        = TestScaleIngredient.make_ingredient('2-3')
        scaled_ingredient = TestScaleIngredient.make_scaled_ingredient('4-6')

        assert scaler.scale_ingredient(ingredient, 2.0) == scaled_ingredient

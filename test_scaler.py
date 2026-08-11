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

    def test_scale_decimal_quantity(self):
        ingredient        = TestScaleIngredient.make_ingredient('4.5 tsp')
        scaled_ingredient = TestScaleIngredient.make_scaled_ingredient('9 tsp')

        assert scaler.scale_ingredient(ingredient, 2.0) == scaled_ingredient

    def test_scale_decimal_quantity_without_space(self):
        ingredient        = TestScaleIngredient.make_ingredient('12.5g')
        scaled_ingredient = TestScaleIngredient.make_scaled_ingredient('25g')

        assert scaler.scale_ingredient(ingredient, 2.0) == scaled_ingredient

    def test_scale_mixed_fraction_quantity(self):
        ingredient        = TestScaleIngredient.make_ingredient('1 1/2 tsp')
        scaled_ingredient = TestScaleIngredient.make_scaled_ingredient('3 tsp')

        assert scaler.scale_ingredient(ingredient, 2.0) == scaled_ingredient

    def test_scale_compound_tin_quantity(self):
        ingredient        = TestScaleIngredient.make_ingredient('2 400g tins')
        scaled_ingredient = TestScaleIngredient.make_scaled_ingredient('4 400g tins')

        assert scaler.scale_ingredient(ingredient, 2.0) == scaled_ingredient

    def test_scale_single_compound_tin_quantity(self):
        ingredient        = TestScaleIngredient.make_ingredient('1 400g tin')
        scaled_ingredient = TestScaleIngredient.make_scaled_ingredient('2 400g tins')

        assert scaler.scale_ingredient(ingredient, 2.0) == scaled_ingredient

    def test_scale_implicit_compound_tin_quantity(self):
        ingredient        = TestScaleIngredient.make_ingredient('400g tin')
        scaled_ingredient = TestScaleIngredient.make_scaled_ingredient('2 400g tins')

        assert scaler.scale_ingredient(ingredient, 2.0) == scaled_ingredient

    def test_scale_compound_fillet_quantity(self):
        ingredient        = TestScaleIngredient.make_ingredient('2 110g fillets')
        scaled_ingredient = TestScaleIngredient.make_scaled_ingredient('4 110g fillets')

        assert scaler.scale_ingredient(ingredient, 2.0) == scaled_ingredient

    def test_scale_parenthetical_tin_quantity(self):
        ingredient        = TestScaleIngredient.make_ingredient('1 tin (400g)')
        scaled_ingredient = TestScaleIngredient.make_scaled_ingredient('2 tins (400g)')

        assert scaler.scale_ingredient(ingredient, 2.0) == scaled_ingredient

    def test_scale_parenthetical_block_quantity(self):
        ingredient        = TestScaleIngredient.make_ingredient('1 block (225g)')
        scaled_ingredient = TestScaleIngredient.make_scaled_ingredient('2 blocks (225g)')

        assert scaler.scale_ingredient(ingredient, 2.0) == scaled_ingredient

    def test_scale_approximate_block_quantity(self):
        ingredient        = TestScaleIngredient.make_ingredient('1 block, approx. 200g')
        scaled_ingredient = TestScaleIngredient.make_scaled_ingredient('2 blocks, approx 400g')

        assert scaler.scale_ingredient(ingredient, 2.0) == scaled_ingredient

    def test_scale_tilde_approximate_quantity(self):
        ingredient        = TestScaleIngredient.make_ingredient('~70g')
        scaled_ingredient = TestScaleIngredient.make_scaled_ingredient('~140g')

        assert scaler.scale_ingredient(ingredient, 2.0) == scaled_ingredient

    def test_scale_suffix_approximate_quantity(self):
        ingredient        = TestScaleIngredient.make_ingredient('25g approx')
        scaled_ingredient = TestScaleIngredient.make_scaled_ingredient('50g approx')

        assert scaler.scale_ingredient(ingredient, 2.0) == scaled_ingredient

    def test_scale_up_to_approximate_quantity(self):
        ingredient        = TestScaleIngredient.make_ingredient('up to 75g')
        scaled_ingredient = TestScaleIngredient.make_scaled_ingredient('up to 150g')

        assert scaler.scale_ingredient(ingredient, 2.0) == scaled_ingredient

    def test_scale_descriptive_quantities(self):
        cases = [
            ('1 large clove', '2 large cloves'),
            ('1 large tin', '2 large tins'),
            ('1 large bag minimum', '2 large bags minimum'),
            ('1 heaped tablespoon', '2 heaped tablespoons'),
            ('2 fork-fulls', '4 fork-fulls'),
        ]

        for quantity, expected in cases:
            ingredient = TestScaleIngredient.make_ingredient(quantity)
            scaled_ingredient = TestScaleIngredient.make_scaled_ingredient(expected)
            assert scaler.scale_ingredient(ingredient, 2.0) == scaled_ingredient

    def test_scale_length_quantities(self):
        cases = [
            ('1 cm piece', '2 cm pieces'),
            ('1cm piece', '2cm pieces'),
            ('2.5cm', '5cm'),
        ]

        for quantity, expected in cases:
            ingredient = TestScaleIngredient.make_ingredient(quantity)
            scaled_ingredient = TestScaleIngredient.make_scaled_ingredient(expected)
            assert scaler.scale_ingredient(ingredient, 2.0) == scaled_ingredient

    def test_ignore_vague_quantities(self):
        vague_quantities = [
            'pinch',
            'handful',
            'knob',
            'generous dash',
            '1 per person',
            'Several teaspoons',
        ]

        for quantity in vague_quantities:
            ingredient = TestScaleIngredient.make_ingredient(quantity)
            assert scaler.scale_ingredient(ingredient, 2.0) == ingredient


class TestIngredientsCopyText:
    def test_sums_matching_quantities_case_insensitively(self):
        blocks = [
            {'ingredients': [{'name': 'Butter', 'quantity': '50g'}]},
            {'ingredients': [{'name': 'butter', 'quantity': '150g'}]},
        ]
        assert scaler.ingredients_copy_text(blocks) == '200g Butter'

    def test_keeps_incompatible_units_separate(self):
        blocks = [{
            'ingredients': [
                {'name': 'Milk', 'quantity': '100ml'},
                {'name': 'Milk', 'quantity': '50g'},
            ],
        }]
        assert scaler.ingredients_copy_text(blocks) == '100ml Milk\n50g Milk'

    def test_omits_tsp_tbsp_and_missing_quantities(self):
        blocks = [{
            'ingredients': [
                {'name': 'Salt', 'quantity': '1tsp'},
                {'name': 'salt', 'quantity': '1/2tsp'},
                {'name': 'Pepper', 'quantity': None},
            ],
        }]
        assert scaler.ingredients_copy_text(blocks) == 'Salt\nPepper'

    def test_merges_omitted_quantity_into_concrete_quantity(self):
        blocks = [{
            'ingredients': [
                {'name': 'Butter', 'quantity': None},
                {'name': 'Butter', 'quantity': '50g'},
            ],
        }]
        assert scaler.ingredients_copy_text(blocks) == '50g Butter'

    def test_sums_fraction_quantities(self):
        blocks = [{
            'ingredients': [
                {'name': 'Flour', 'quantity': '1/2 cup'},
                {'name': 'Flour', 'quantity': '1/2 cup'},
            ],
        }]
        assert scaler.ingredients_copy_text(blocks) == '1 cup Flour'

    def test_preserves_order_of_first_occurrence(self):
        blocks = [{
            'ingredients': [
                {'name': 'Butter', 'quantity': '50g'},
                {'name': 'Sugar', 'quantity': '100g'},
                {'name': 'butter', 'quantity': '150g'},
            ],
        }]
        assert scaler.ingredients_copy_text(blocks) == '200g Butter\n100g Sugar'

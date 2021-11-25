import re
from custom.models.category import Category


def category_from_url(inputs):
    """Returns list of categories from parameter inputs"""
    name_filter = '('
    for input_name in inputs:
        input_name = input_name.lower()
        if input_name != 'population-density':
            input_name = input_name.replace('-', ' ')
        input_name = re.sub("[\(\[].*?[\)\]]", "", input_name)
        name_filter += input_name + '|'
    name_filter = name_filter[:-1] + ')'
    return Category.objects.filter(
        name_long__iregex=r'{}'.format(name_filter)
    )

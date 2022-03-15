import re
from custom.models.category import Category


def category_from_url(inputs):
    """Returns list of categories from parameter inputs"""
    categories = []
    for input_name in inputs:
        input_name = input_name.lower()
        domain = re.search(r'\((.*?)\)', input_name)
        if domain:
            domain = domain.group(1)
        weight = re.search(r'\[(.*?)\]', input_name)
        if weight:
            weight = weight.group(1)
        if input_name != 'population-density':
            input_name = input_name.replace('-', ' ')
        input_name = re.sub("[\(\[].*?[\)\]]", "", input_name)
        if Category.objects.filter(name_long__icontains=input_name):
            categories.append({
                'domain': domain,
                'weight': weight,
                'category': Category.objects.filter(
                    name_long__icontains=input_name
                ).first()
            })
    return categories

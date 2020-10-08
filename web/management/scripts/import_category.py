import csv
from apps.product.models import Category

with open('./web/management/scripts/templates/category.csv') as f:
    reader = csv.reader(f)
    for row in reader:
        _, created = Category.objects.get_or_create(
            typology_id=row[0],
            code=row[1],
            name=row[2],
            description=row[3],
            creator_id=1,
            last_modifier_id=1
        )
        # creates a tuple of the new object or
        # current object and a boolean of if it was created
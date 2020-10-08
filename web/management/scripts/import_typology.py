import csv
from apps.product.models import Typology

with open('./web/management/scripts/templates/typology.csv') as f:
    reader = csv.reader(f)
    for row in reader:
        _, created = Typology.objects.get_or_create(
            code=row[0],
            name=row[1],
            description=row[2],
            color=row[3],
            creator_id=1,
            last_modifier_id=1
        )
        # creates a tuple of the new object or
        # current object and a boolean of if it was created
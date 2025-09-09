from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_product'),
    ]

    operations = [
        migrations.DeleteModel(
            name='News',
        ),
    ]

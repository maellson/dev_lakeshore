# integrations/migrations/000X_remove_webhook.py
from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('integrations', '0001_initial'),  # Última migration
    ]

    operations = [
        migrations.DeleteModel(
            name='BrokermintWebhook',
        ),
    ]
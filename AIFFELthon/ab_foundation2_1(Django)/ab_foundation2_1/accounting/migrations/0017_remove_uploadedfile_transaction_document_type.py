# Generated by Django 4.1.13 on 2025-05-15 02:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("accounting", "0016_transactiondocument_anomaly_memo"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="uploadedfile",
            name="transaction_document_type",
        ),
    ]

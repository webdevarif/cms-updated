# Generated migration for ecommerce app

import django.contrib.postgres.indexes
import django.contrib.postgres.search
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ecommerce", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="search_vector",
            field=django.contrib.postgres.search.SearchVectorField(default=""),
        ),
        migrations.AddIndex(
            model_name="product",
            index_name="ecommerce_product_search_vector_idx",
            field=models.Field(
                name="search_vector",
                base_field=django.contrib.postgres.search.SearchVectorField(),
            ),
            index=django.contrib.postgres.indexes.GinIndex(
                fields=["search_vector"], name="ecommerce_product_search_vector_idx"
            ),
        ),
    ]

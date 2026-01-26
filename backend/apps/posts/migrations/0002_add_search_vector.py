# Generated migration for posts app

from django.db import migrations, models
import django.contrib.postgres.search
import django.contrib.postgres.indexes


class Migration(migrations.Migration):
    dependencies = [
        ('posts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='search_vector',
            field=django.contrib.postgres.search.SearchVectorField(default=''),
        ),
        migrations.AddIndex(
            model_name='post',
            index_name='posts_post_search_vector_idx',
            field=models.Field(
                name='search_vector',
                base_field=django.contrib.postgres.search.SearchVectorField(),
            ),
            index=django.contrib.postgres.indexes.GinIndex(
                fields=['search_vector'],
                name='posts_post_search_vector_idx'
            ),
        ),
    ]

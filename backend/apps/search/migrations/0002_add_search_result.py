# Generated migration for search app

from django.db import migrations, models
import django.contrib.postgres.indexes


class Migration(migrations.Migration):
    dependencies = [
        ('search', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SearchResult',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('query', models.CharField(max_length=255, db_index=True)),
                ('store', models.ForeignKey('stores.Store', on_delete=models.CASCADE, null=True, blank=True, related_name='cached_search_results')),
                ('content_type', models.CharField(max_length=50)),
                ('object_id', models.PositiveIntegerField()),
                ('title', models.CharField(max_length=255)),
                ('slug', models.SlugField(max_length=255)),
                ('excerpt', models.TextField(blank=True)),
                ('url', models.URLField(max_length=500)),
                ('score', models.FloatField(default=0.0)),
                ('metadata', models.JSONField(default=dict, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Search Result',
                'verbose_name_plural': 'Search Results',
                'indexes': [
                    models.Index(fields=['query', 'store']),
                    models.Index(fields=['content_type', 'object_id']),
                    models.Index(fields=['score']),
                ],
                'unique_together': [('query', 'store', 'content_type', 'object_id')],
                'ordering': ['-score', '-updated_at'],
            },
        ),
    ]

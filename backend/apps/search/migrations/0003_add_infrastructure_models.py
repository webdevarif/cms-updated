# Generated migration for search infrastructure models

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("search", "0002_add_search_result"),
        ("stores", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="SearchIndex",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=255)),
                ("index_name", models.CharField(db_index=True, max_length=255, unique=True)),
                (
                    "content_types",
                    models.JSONField(
                        default=list,
                        help_text="List of content types to index: ['Page', 'Post', 'Product']",
                    ),
                ),
                (
                    "fields",
                    models.JSONField(
                        default=dict, help_text="Field mappings and search configuration"
                    ),
                ),
                (
                    "facets",
                    models.JSONField(default=list, help_text="Facet configuration for filtering"),
                ),
                ("is_active", models.BooleanField(default=True)),
                ("last_reindexed_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "store",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="search_indexes",
                        to="stores.store",
                    ),
                ),
            ],
            options={
                "verbose_name": "Search Index",
                "verbose_name_plural": "Search Indices",
                "db_table": "search_index",
                "unique_together": {("store", "name")},
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="SearchQuery",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ("query", models.CharField(db_index=True, max_length=255)),
                (
                    "search_type",
                    models.CharField(
                        choices=[("content", "Content"), ("product", "Product"), ("all", "All")],
                        max_length=50,
                    ),
                ),
                ("results_count", models.PositiveIntegerField(default=0)),
                ("session_id", models.CharField(blank=True, max_length=100)),
                ("filters", models.JSONField(default=dict)),
                ("duration_ms", models.PositiveIntegerField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "store",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="search_queries",
                        to="stores.store",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="auth.user",
                    ),
                ),
            ],
            options={
                "verbose_name": "Search Query",
                "verbose_name_plural": "Search Queries",
                "db_table": "search_query",
                "indexes": [
                    models.Index(fields=["store", "query"]),
                    models.Index(fields=["created_at"]),
                    models.Index(fields=["search_type"]),
                ],
                "ordering": ["-created_at"],
            },
        ),
    ]

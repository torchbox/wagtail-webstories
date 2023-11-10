# Generated by Django 2.2.17 on 2021-03-11 17:37

import wagtail.blocks as wagtail_blocks
import wagtail.fields as wagtail_fields
from django.db import migrations

import wagtail_webstories.blocks


class Migration(migrations.Migration):
    dependencies = [
        ("tests", "0004_storypage_original_url"),
    ]

    operations = [
        migrations.AlterField(
            model_name="blogpage",
            name="body",
            field=wagtail_fields.StreamField(
                [
                    ("heading", wagtail_blocks.CharBlock()),
                    ("story_embed", wagtail_webstories.blocks.StoryEmbedBlock()),
                    ("story_link", wagtail_webstories.blocks.StoryChooserBlock()),
                    (
                        "external_story_embed",
                        wagtail_webstories.blocks.ExternalStoryEmbedBlock(),
                    ),
                    (
                        "external_story_link",
                        wagtail_webstories.blocks.ExternalStoryBlock(),
                    ),
                ],
                use_json_field=True,
            ),
        ),
    ]

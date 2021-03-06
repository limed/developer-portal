# Generated by Django 2.2.4 on 2019-08-14 16:00

from django.db import migrations
import wagtail.core.blocks
import wagtail.core.fields


class Migration(migrations.Migration):

    dependencies = [("externalcontent", "0020_auto_20190813_1503")]

    operations = [
        migrations.AlterField(
            model_name="externalvideo",
            name="speakers",
            field=wagtail.core.fields.StreamField(
                [
                    (
                        "speaker",
                        wagtail.core.blocks.PageChooserBlock(
                            page_type=["people.Person"]
                        ),
                    )
                ],
                blank=True,
                help_text="Optional list of people associated with or starring in the video",
                null=True,
            ),
        )
    ]

# Generated by Django 2.2.14 on 2020-07-06 12:26

from django.db import migrations, models
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0029_further_sponsored_events_changes'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='extra_content_panel',
            field=wagtail.core.fields.StreamField([('post', wagtail.core.blocks.PageChooserBlock(page_type=['articles.Article', 'externalcontent.ExternalArticle'])), ('external_page', wagtail.core.blocks.StructBlock([('url', wagtail.core.blocks.URLBlock()), ('title', wagtail.core.blocks.CharBlock()), ('description', wagtail.core.blocks.TextBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock(help_text='16:9 aspect-ratio image', label='16:9 image')), ('image_3_2', wagtail.images.blocks.ImageChooserBlock(help_text='3:2 aspect-ratio image - optiopnal but recommended', label='3:2 image', required=False))])), ('video', wagtail.core.blocks.PageChooserBlock(page_type=['videos.Video', 'externalcontent.ExternalVideo'])), ('topic', wagtail.core.blocks.PageChooserBlock(page_type=['topics.Topic']))], blank=True, help_text='Optional space for links to other pages/resources related to this Event, max. 4.', null=True, verbose_name='Links'),
        ),
        migrations.AddField(
            model_name='event',
            name='extra_content_panel_title',
            field=models.CharField(blank=True, default='Related items', max_length=140, verbose_name='Panel title'),
        ),
    ]

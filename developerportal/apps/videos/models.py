# pylint: disable=no-member
import datetime

from django.db.models import (
    CASCADE,
    SET_NULL,
    CharField,
    DateField,
    ForeignKey,
    TextField,
)

import readtime
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from taggit.models import TaggedItemBase
from wagtail.admin.edit_handlers import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    ObjectList,
    PageChooserPanel,
    StreamFieldPanel,
    TabbedInterface,
)
from wagtail.core.blocks import PageChooserBlock
from wagtail.core.fields import RichTextField, StreamBlock, StreamField
from wagtail.core.models import Orderable
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index

from ..common.blocks import ExternalLinkBlock
from ..common.constants import (
    DESCRIPTION_MAX_LENGTH,
    RICH_TEXT_FEATURES,
    RICH_TEXT_FEATURES_SIMPLE,
    VIDEO_TYPE,
)
from ..common.models import BasePage
from ..common.utils import get_combined_articles_and_videos


class VideosTag(TaggedItemBase):
    content_object = ParentalKey(
        "Videos", on_delete=CASCADE, related_name="tagged_items"
    )


class VideoTopic(Orderable):
    video = ParentalKey("Video", related_name="topics")
    topic = ForeignKey("topics.Topic", on_delete=CASCADE, related_name="+")

    panels = [PageChooserPanel("topic")]


class Videos(BasePage):
    # IMPORTANT: The Videos page has to exist in the CMS ( at /videos/) so that
    # it can be the parent page of actual Video pages eg, but it is not intended
    # to be shown in menus nor accessed directly, so it is only ever
    # in existence in draft form.

    parent_page_types = ["home.HomePage"]
    subpage_types = ["Video"]
    template = "videos.html"

    # Meta fields
    keywords = ClusterTaggableManager(through=VideosTag, blank=True)

    meta_panels = [
        MultiFieldPanel(
            [
                FieldPanel("seo_title"),
                FieldPanel("search_description"),
                ImageChooserPanel("social_image"),
                FieldPanel("keywords"),
            ],
            heading="SEO",
            help_text=(
                "Optional fields to override the default title and description "
                "for SEO purposes"
            ),
        )
    ]

    settings_panels = BasePage.settings_panels + [
        FieldPanel("slug"),
        FieldPanel("show_in_menus"),
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(BasePage.content_panels, heading="Content"),
            ObjectList(meta_panels, heading="Meta"),
            ObjectList(settings_panels, heading="Settings", classname="settings"),
        ]
    )

    class Meta:
        verbose_name_plural = "Videos"

    @classmethod
    def can_create_at(cls, parent):
        # Allow only one instance of this page type
        return super().can_create_at(parent) and not cls.objects.exists()

    @property
    def videos(self):
        return Video.published_objects.order_by("title")


class VideoTag(TaggedItemBase):
    content_object = ParentalKey(
        "Video", on_delete=CASCADE, related_name="tagged_items"
    )


class Video(BasePage):
    resource_type = "video"
    parent_page_types = ["Videos"]
    subpage_types = []
    template = "video.html"

    # Content fields
    description = RichTextField(
        blank=True,
        default="",
        features=RICH_TEXT_FEATURES_SIMPLE,
        help_text=(
            "Optional short text description, "
            f"max. {DESCRIPTION_MAX_LENGTH} characters"
        ),
        max_length=DESCRIPTION_MAX_LENGTH,
    )
    body = RichTextField(
        blank=True,
        default="",
        features=RICH_TEXT_FEATURES,
        help_text=(
            "Optional body content. Supports rich text, images, embed via URL, "
            "embed via HTML, and inline code snippets"
        ),
    )
    related_links = StreamField(
        StreamBlock([("link", ExternalLinkBlock())], required=False),
        null=True,
        blank=True,
        help_text="Optional links further reading",
        verbose_name="Related links",
    )
    types = CharField(max_length=14, choices=VIDEO_TYPE, default="conference")
    duration = CharField(
        max_length=30,
        blank=True,
        null=True,
        help_text=(
            "Optional video duration in MM:SS format e.g. “12:34”. Shown when the "
            "video is displayed as a card"
        ),
    )
    transcript = RichTextField(
        blank=True,
        default="",
        features=RICH_TEXT_FEATURES,
        help_text="Optional text transcript of the video, supports rich text",
    )
    video_url = StreamField(
        StreamBlock([("embed", EmbedBlock())], min_num=1, max_num=1, required=True),
        help_text=(
            "Embed URL for the video e.g. https://www.youtube.com/watch?v=kmk43_2dtn0"
        ),
    )
    speakers = StreamField(
        StreamBlock(
            [("speaker", PageChooserBlock(target_model="people.Person"))],
            required=False,
        ),
        blank=True,
        null=True,
        help_text="Optional list of people associated with or starring in the video",
    )

    # Card fields
    card_title = CharField("Title", max_length=140, blank=True, default="")
    card_description = TextField(
        "Description", max_length=DESCRIPTION_MAX_LENGTH, blank=True, default=""
    )
    card_image = ForeignKey(
        "mozimages.MozImage",
        null=True,
        blank=True,
        on_delete=SET_NULL,
        related_name="+",
        verbose_name="Image",
        help_text="An image in 16:9 aspect ratio",
    )
    card_image_3_2 = ForeignKey(
        "mozimages.MozImage",
        null=True,
        blank=True,
        on_delete=SET_NULL,
        related_name="+",
        verbose_name="Image",
        help_text="An image in 3:2 aspect ratio",
    )
    # Meta fields
    date = DateField("Upload date", default=datetime.date.today)
    keywords = ClusterTaggableManager(through=VideoTag, blank=True)

    # Content panels
    content_panels = BasePage.content_panels + [
        FieldPanel("description"),
        StreamFieldPanel("video_url"),
        FieldPanel("body"),
        StreamFieldPanel("related_links"),
        FieldPanel("transcript"),
    ]

    # Card panels
    card_panels = [
        FieldPanel("card_title"),
        FieldPanel("card_description"),
        MultiFieldPanel(
            [ImageChooserPanel("card_image")],
            heading="16:9 Image",
            help_text=(
                "Image used for representing this page as a Card. "
                "Should be 16:9 aspect ratio. "
                "If not specified a fallback will be used. "
                "This image is also shown when sharing this page via social "
                "media unless a social image is specified."
            ),
        ),
        MultiFieldPanel(
            [ImageChooserPanel("card_image_3_2")],
            heading="3:2 Image",
            help_text=(
                "Image used for representing this page as a Card. "
                "Should be 3:2 aspect ratio. "
                "If not specified a fallback will be used. "
            ),
        ),
    ]

    # Meta panels
    meta_panels = [
        FieldPanel("date"),
        StreamFieldPanel("speakers"),
        MultiFieldPanel(
            [InlinePanel("topics")],
            heading="Topics",
            help_text=(
                "These are the topic pages the video will appear on. The first topic "
                "in the list will be treated as the primary topic and will be shown "
                "in the page’s related content."
            ),
        ),
        FieldPanel("duration"),
        MultiFieldPanel(
            [FieldPanel("types")],
            heading="Type",
            help_text="Choose a video type to help people search for the video",
        ),
        MultiFieldPanel(
            [
                FieldPanel("seo_title"),
                FieldPanel("search_description"),
                ImageChooserPanel("social_image"),
                FieldPanel("keywords"),
            ],
            heading="SEO",
            help_text=(
                "Optional fields to override the default title and description "
                "for SEO purposes"
            ),
        ),
    ]

    settings_panels = BasePage.settings_panels + [FieldPanel("slug")]

    # Tabs
    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(card_panels, heading="Card"),
            ObjectList(meta_panels, heading="Meta"),
            ObjectList(settings_panels, heading="Settings", classname="settings"),
        ]
    )

    # Search config
    search_fields = BasePage.search_fields + [  # Inherit search_fields from Page
        # "title" is already specced in BasePage
        index.SearchField("description"),
        index.SearchField("body"),
        # Add FilterFields for things we may be filtering on (eg topics)
        index.FilterField("slug"),
    ]

    def get_absolute_url(self):
        # For the RSS feed
        return self.full_url

    @property
    def primary_topic(self):
        """Return the first (primary) topic specified for the video."""
        video_topic = self.topics.first()
        return video_topic.topic if video_topic else None

    @property
    def read_time(self):
        return str(readtime.of_html(str(self.body)))

    @property
    def related_resources(self):
        """Returns resources that are related to the current resource, i.e. live,
        public articles and videos which have the same topics."""
        topic_pks = [topic.topic.pk for topic in self.topics.all()]
        return get_combined_articles_and_videos(self, topics__topic__pk__in=topic_pks)

    def has_speaker(self, person):
        for speaker in self.speakers:  # pylint: disable=not-an-iterable
            if str(speaker.value) == str(person.title):
                return True
        return False

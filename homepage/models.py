import secrets
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from urllib.parse import urlparse

def generate_preview_token():
    return secrets.token_urlsafe(32)

def validate_storefront_url(value):
    if not value:
        return
    if value.startswith('/'):
        return
    parsed=urlparse(value)
    if parsed.scheme not in {'http','https'}:
        raise ValidationError('Use a relative /path or an http(s) URL.')

SECTION_TYPES=[
    ('hero','Hero / Slider'),('category_grid','Category Grid'),('product_rail','Product Rail'),
    ('editorial_banner','Editorial Banner'),('split_banner','Split Banner'),('video','Video'),
    ('story','Story'),('customer_love','Customer / Social Proof'),('newsletter','Newsletter'),
    ('custom_html','Custom HTML'),('spacer','Spacer'),
]
LAYOUTS=[('full','Full width'),('contained','Contained'),('two','2 columns'),('three','3 columns'),('four','4 columns'),('carousel','Carousel'),('masonry','Masonry')]
SOURCES=[('manual','Manual'),('selected_products','Selected products'),('category','Category'),('latest','Latest products'),('recommendations','Recommendations')]

class Homepage(models.Model):
    name=models.CharField(max_length=120, default="Ruff 'n' Tumble Homepage")
    code=models.SlugField(max_length=64, unique=True, default='home')
    active=models.BooleanField(default=True)
    preview_token=models.CharField(max_length=64, unique=True, default=generate_preview_token, editable=False)
    published_payload=models.JSONField(default=dict, blank=True)
    published_revision=models.PositiveIntegerField(default=0)
    published_at=models.DateTimeField(null=True, blank=True)
    published_by=models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='rnt_published_homepages')
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    def __str__(self): return self.name

class Section(models.Model):
    page=models.ForeignKey(Homepage, related_name='sections', on_delete=models.CASCADE)
    sequence=models.PositiveIntegerField(default=10, db_index=True)
    key=models.SlugField(max_length=80, blank=True)
    name=models.CharField(max_length=120, default='New Section')
    section_type=models.CharField(max_length=32, choices=SECTION_TYPES, default='editorial_banner')
    layout=models.CharField(max_length=20, choices=LAYOUTS, default='contained')
    enabled=models.BooleanField(default=True)
    hide_desktop=models.BooleanField(default=False)
    hide_mobile=models.BooleanField(default=False)
    starts_at=models.DateTimeField(null=True, blank=True)
    ends_at=models.DateTimeField(null=True, blank=True)

    eyebrow=models.CharField(max_length=160, blank=True)
    heading=models.CharField(max_length=220, blank=True)
    subheading=models.TextField(blank=True)
    body_html=models.TextField(blank=True)
    cta1_label=models.CharField(max_length=100, blank=True)
    cta1_url=models.CharField(max_length=500, blank=True, validators=[validate_storefront_url])
    cta2_label=models.CharField(max_length=100, blank=True)
    cta2_url=models.CharField(max_length=500, blank=True, validators=[validate_storefront_url])

    desktop_image=models.ImageField(upload_to='homepage/sections/%Y/%m/', blank=True, null=True)
    mobile_image=models.ImageField(upload_to='homepage/sections/%Y/%m/', blank=True, null=True)
    desktop_image_url=models.URLField(max_length=1000, blank=True, help_text='Optional existing CDN/DigitalOcean image URL')
    mobile_image_url=models.URLField(max_length=1000, blank=True)
    video_url=models.URLField(max_length=500, blank=True)

    source_type=models.CharField(max_length=32, choices=SOURCES, default='manual')
    category_key=models.CharField(max_length=180, blank=True, help_text='Existing storefront category slug, e.g. girls-dresses')
    product_refs=models.JSONField(default=list, blank=True, help_text='Existing storefront/Odoo product IDs or SKUs. The Next.js storefront resolves live price/stock.')
    product_limit=models.PositiveSmallIntegerField(default=8)

    background_color=models.CharField(max_length=32, blank=True)
    text_color=models.CharField(max_length=32, blank=True)
    min_height=models.CharField(max_length=32, blank=True)
    desktop_padding=models.CharField(max_length=64, blank=True)
    mobile_padding=models.CharField(max_length=64, blank=True)
    text_align=models.CharField(max_length=10, choices=[('left','Left'),('center','Center'),('right','Right')], default='center')
    settings=models.JSONField(default=dict, blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    class Meta:
        ordering=['sequence','id']
        indexes=[models.Index(fields=['page','sequence'])]
    def clean(self):
        if self.starts_at and self.ends_at and self.ends_at <= self.starts_at:
            raise ValidationError({'ends_at':'End time must be after start time.'})
        if self.product_limit < 1 or self.product_limit > 40:
            raise ValidationError({'product_limit':'Product limit must be between 1 and 40.'})
    def __str__(self): return f'{self.page.code}: {self.name}'

class SectionItem(models.Model):
    section=models.ForeignKey(Section, related_name='items', on_delete=models.CASCADE)
    sequence=models.PositiveIntegerField(default=10)
    enabled=models.BooleanField(default=True)
    key=models.SlugField(max_length=80, blank=True)
    eyebrow=models.CharField(max_length=160, blank=True)
    title=models.CharField(max_length=220, blank=True)
    subtitle=models.TextField(blank=True)
    button_label=models.CharField(max_length=100, blank=True)
    target_url=models.CharField(max_length=500, blank=True, validators=[validate_storefront_url])
    desktop_image=models.ImageField(upload_to='homepage/items/%Y/%m/', blank=True, null=True)
    mobile_image=models.ImageField(upload_to='homepage/items/%Y/%m/', blank=True, null=True)
    desktop_image_url=models.URLField(max_length=1000, blank=True)
    mobile_image_url=models.URLField(max_length=1000, blank=True)
    video_url=models.URLField(max_length=500, blank=True)
    product_ref=models.CharField(max_length=180, blank=True)
    settings=models.JSONField(default=dict, blank=True)
    class Meta: ordering=['sequence','id']
    def __str__(self): return self.title or self.key or f'Item {self.pk}'

class HomepageSnapshot(models.Model):
    page=models.ForeignKey(Homepage, related_name='snapshots', on_delete=models.CASCADE)
    revision=models.PositiveIntegerField()
    payload=models.JSONField()
    published_at=models.DateTimeField(default=timezone.now)
    published_by=models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    class Meta:
        ordering=['-revision']
        constraints=[models.UniqueConstraint(fields=['page','revision'], name='unique_homepage_revision')]
    def __str__(self): return f'{self.page.code} r{self.revision}'

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import homepage.models

class Migration(migrations.Migration):
    initial=True
    dependencies=[migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations=[
        migrations.CreateModel(name='Homepage',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
            ('name',models.CharField(default="Ruff 'n' Tumble Homepage",max_length=120)),
            ('code',models.SlugField(default='home',max_length=64,unique=True)),
            ('active',models.BooleanField(default=True)),
            ('preview_token',models.CharField(default=homepage.models.generate_preview_token,editable=False,max_length=64,unique=True)),
            ('published_payload',models.JSONField(blank=True,default=dict)),
            ('published_revision',models.PositiveIntegerField(default=0)),
            ('published_at',models.DateTimeField(blank=True,null=True)),
            ('created_at',models.DateTimeField(auto_now_add=True)),('updated_at',models.DateTimeField(auto_now=True)),
            ('published_by',models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.SET_NULL,related_name='rnt_published_homepages',to=settings.AUTH_USER_MODEL)),
        ]),
        migrations.CreateModel(name='Section',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
            ('sequence',models.PositiveIntegerField(db_index=True,default=10)),('key',models.SlugField(blank=True,max_length=80)),('name',models.CharField(default='New Section',max_length=120)),
            ('section_type',models.CharField(choices=[('hero','Hero / Slider'),('category_grid','Category Grid'),('product_rail','Product Rail'),('editorial_banner','Editorial Banner'),('split_banner','Split Banner'),('video','Video'),('story','Story'),('customer_love','Customer / Social Proof'),('newsletter','Newsletter'),('custom_html','Custom HTML'),('spacer','Spacer')],default='editorial_banner',max_length=32)),
            ('layout',models.CharField(choices=[('full','Full width'),('contained','Contained'),('two','2 columns'),('three','3 columns'),('four','4 columns'),('carousel','Carousel'),('masonry','Masonry')],default='contained',max_length=20)),
            ('enabled',models.BooleanField(default=True)),('hide_desktop',models.BooleanField(default=False)),('hide_mobile',models.BooleanField(default=False)),('starts_at',models.DateTimeField(blank=True,null=True)),('ends_at',models.DateTimeField(blank=True,null=True)),
            ('eyebrow',models.CharField(blank=True,max_length=160)),('heading',models.CharField(blank=True,max_length=220)),('subheading',models.TextField(blank=True)),('body_html',models.TextField(blank=True)),
            ('cta1_label',models.CharField(blank=True,max_length=100)),('cta1_url',models.CharField(blank=True,max_length=500,validators=[homepage.models.validate_storefront_url])),('cta2_label',models.CharField(blank=True,max_length=100)),('cta2_url',models.CharField(blank=True,max_length=500,validators=[homepage.models.validate_storefront_url])),
            ('desktop_image',models.ImageField(blank=True,null=True,upload_to='homepage/sections/%Y/%m/')),('mobile_image',models.ImageField(blank=True,null=True,upload_to='homepage/sections/%Y/%m/')),
            ('desktop_image_url',models.URLField(blank=True,help_text='Optional existing CDN/DigitalOcean image URL',max_length=1000)),('mobile_image_url',models.URLField(blank=True,max_length=1000)),('video_url',models.URLField(blank=True,max_length=500)),
            ('source_type',models.CharField(choices=[('manual','Manual'),('selected_products','Selected products'),('category','Category'),('latest','Latest products'),('recommendations','Recommendations')],default='manual',max_length=32)),
            ('category_key',models.CharField(blank=True,help_text='Existing storefront category slug, e.g. girls-dresses',max_length=180)),('product_refs',models.JSONField(blank=True,default=list,help_text='Existing storefront/Odoo product IDs or SKUs. The Next.js storefront resolves live price/stock.')),('product_limit',models.PositiveSmallIntegerField(default=8)),
            ('background_color',models.CharField(blank=True,max_length=32)),('text_color',models.CharField(blank=True,max_length=32)),('min_height',models.CharField(blank=True,max_length=32)),('desktop_padding',models.CharField(blank=True,max_length=64)),('mobile_padding',models.CharField(blank=True,max_length=64)),('text_align',models.CharField(choices=[('left','Left'),('center','Center'),('right','Right')],default='center',max_length=10)),('settings',models.JSONField(blank=True,default=dict)),
            ('created_at',models.DateTimeField(auto_now_add=True)),('updated_at',models.DateTimeField(auto_now=True)),
            ('page',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='sections',to='homepage.homepage')),
        ],options={'ordering':['sequence','id']}),
        migrations.CreateModel(name='SectionItem',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),('sequence',models.PositiveIntegerField(default=10)),('enabled',models.BooleanField(default=True)),('key',models.SlugField(blank=True,max_length=80)),
            ('eyebrow',models.CharField(blank=True,max_length=160)),('title',models.CharField(blank=True,max_length=220)),('subtitle',models.TextField(blank=True)),('button_label',models.CharField(blank=True,max_length=100)),('target_url',models.CharField(blank=True,max_length=500,validators=[homepage.models.validate_storefront_url])),
            ('desktop_image',models.ImageField(blank=True,null=True,upload_to='homepage/items/%Y/%m/')),('mobile_image',models.ImageField(blank=True,null=True,upload_to='homepage/items/%Y/%m/')),('desktop_image_url',models.URLField(blank=True,max_length=1000)),('mobile_image_url',models.URLField(blank=True,max_length=1000)),('video_url',models.URLField(blank=True,max_length=500)),('product_ref',models.CharField(blank=True,max_length=180)),('settings',models.JSONField(blank=True,default=dict)),
            ('section',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='items',to='homepage.section')),
        ],options={'ordering':['sequence','id']}),
        migrations.CreateModel(name='HomepageSnapshot',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),('revision',models.PositiveIntegerField()),('payload',models.JSONField()),('published_at',models.DateTimeField(default=django.utils.timezone.now)),
            ('page',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='snapshots',to='homepage.homepage')),('published_by',models.ForeignKey(null=True,on_delete=django.db.models.deletion.SET_NULL,to=settings.AUTH_USER_MODEL)),
        ],options={'ordering':['-revision']}),
        migrations.AddIndex(model_name='section',index=models.Index(fields=['page','sequence'],name='homepage_se_page_id_7fd2f7_idx')),
        migrations.AddConstraint(model_name='homepagesnapshot',constraint=models.UniqueConstraint(fields=('page','revision'),name='unique_homepage_revision')),
    ]

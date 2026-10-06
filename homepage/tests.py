from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from .models import Homepage, Section

class HomeBuilderTests(TestCase):
    def setUp(self):
        self.user=get_user_model().objects.create_superuser('admin','admin@example.com','testpass123')
        self.page=Homepage.objects.create(code='home',name='RNT Home')
        self.section=Section.objects.create(page=self.page,sequence=10,key='hero',name='Hero',section_type='hero',heading='Hello',enabled=True)

    def test_preview_returns_draft(self):
        r=self.client.get(reverse('rnt-homepage-preview',args=[self.page.preview_token]))
        self.assertEqual(r.status_code,200)
        self.assertEqual(r.json()['sections'][0]['content']['heading'],'Hello')

    def test_publish_then_public_api(self):
        self.client.login(username='admin',password='testpass123')
        r=self.client.post(reverse('rnt-publish',args=['home']),data='{}',content_type='application/json')
        self.assertEqual(r.status_code,200)
        public=self.client.get(reverse('rnt-homepage-api',args=['home']))
        self.assertEqual(public.status_code,200)
        self.assertEqual(public.json()['revision'],1)

    def test_hidden_section_not_public_after_publish(self):
        self.section.enabled=False
        self.section.save()
        self.client.login(username='admin',password='testpass123')
        self.client.post(reverse('rnt-publish',args=['home']),data='{}',content_type='application/json')
        public=self.client.get(reverse('rnt-homepage-api',args=['home']))
        self.assertEqual(public.json()['sections'],[])

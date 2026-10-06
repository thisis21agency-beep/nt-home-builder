from django.urls import path
from . import views
urlpatterns=[
    path('', views.storefront, name='rnt-storefront-preview'),
    path('api/v1/health/', views.health, name='rnt-health'),
    path('api/v1/homepage/<slug:code>/', views.homepage_api, name='rnt-homepage-api'),
    path('api/v1/homepage/preview/<str:token>/', views.homepage_preview_api, name='rnt-homepage-preview'),
    path('builder/<slug:code>/', views.builder, name='rnt-builder'),
    path('builder/<slug:code>/sections/add/', views.section_add, name='rnt-section-add'),
    path('builder/sections/<int:section_id>/update/', views.section_update, name='rnt-section-update'),
    path('builder/sections/<int:section_id>/move/', views.section_move, name='rnt-section-move'),
    path('builder/sections/<int:section_id>/upload-image/', views.section_upload_image, name='rnt-section-upload-image'),
    path('builder/sections/<int:section_id>/duplicate/', views.section_duplicate, name='rnt-section-duplicate'),
    path('builder/sections/<int:section_id>/delete/', views.section_delete, name='rnt-section-delete'),
    path('builder/<slug:code>/publish/', views.publish, name='rnt-publish'),
    path('builder/snapshots/<int:snapshot_id>/restore/', views.restore, name='rnt-restore'),
]

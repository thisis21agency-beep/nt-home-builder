from copy import deepcopy
from django.conf import settings
from django.utils import timezone


def media_url(field, request=None):
    if not field:
        return ''
    try:
        url = field.url
    except ValueError:
        return ''
    if settings.PUBLIC_MEDIA_BASE_URL:
        return settings.PUBLIC_MEDIA_BASE_URL + url
    if request:
        return request.build_absolute_uri(url)
    return url


def serialize_item(item, request=None):
    return {
        'id': item.id,
        'key': item.key or f'item-{item.id}',
        'eyebrow': item.eyebrow,
        'title': item.title,
        'subtitle': item.subtitle,
        'buttonLabel': item.button_label,
        'url': item.target_url,
        'desktopImage': media_url(item.desktop_image, request) or item.desktop_image_url,
        'mobileImage': media_url(item.mobile_image, request) or item.mobile_image_url,
        'videoUrl': item.video_url,
        'productRef': item.product_ref,
        'settings': item.settings or {},
    }


def serialize_section(section, request=None):
    return {
        'id': section.id,
        'key': section.key or f'section-{section.id}',
        'name': section.name,
        'type': section.section_type,
        'layout': section.layout,
        'enabled': section.enabled,
        'hideDesktop': section.hide_desktop,
        'hideMobile': section.hide_mobile,
        'schedule': {
            'startsAt': section.starts_at.isoformat() if section.starts_at else None,
            'endsAt': section.ends_at.isoformat() if section.ends_at else None,
        },
        'content': {
            'eyebrow': section.eyebrow,
            'heading': section.heading,
            'subheading': section.subheading,
            'bodyHtml': section.body_html,
            'cta1': {'label': section.cta1_label, 'url': section.cta1_url},
            'cta2': {'label': section.cta2_label, 'url': section.cta2_url},
        },
        'media': {
            'desktopImage': media_url(section.desktop_image, request) or section.desktop_image_url,
            'mobileImage': media_url(section.mobile_image, request) or section.mobile_image_url,
            'videoUrl': section.video_url,
        },
        'source': {
            'type': section.source_type,
            'categoryKey': section.category_key,
            'productRefs': section.product_refs or [],
            'limit': section.product_limit,
        },
        'style': {
            'backgroundColor': section.background_color,
            'textColor': section.text_color,
            'minHeight': section.min_height,
            'desktopPadding': section.desktop_padding,
            'mobilePadding': section.mobile_padding,
            'textAlign': section.text_align,
        },
        'items': [serialize_item(i, request) for i in section.items.all() if i.enabled],
        'settings': section.settings or {},
    }


def serialize_draft(page, request=None):
    return {
        'schemaVersion': 1,
        'page': {'code': page.code, 'name': page.name},
        'revision': page.published_revision + 1,
        'preview': True,
        'generatedAt': timezone.now().isoformat(),
        'sections': [serialize_section(s, request) for s in page.sections.prefetch_related('items').all()],
    }


def active_published_payload(payload):
    now = timezone.now()
    result = deepcopy(payload)
    visible = []
    for section in result.get('sections', []):
        if not section.get('enabled', True):
            continue
        schedule = section.get('schedule') or {}
        starts = schedule.get('startsAt')
        ends = schedule.get('endsAt')
        if starts:
            try:
                if timezone.datetime.fromisoformat(starts) > now:
                    continue
            except (TypeError, ValueError):
                pass
        if ends:
            try:
                if timezone.datetime.fromisoformat(ends) <= now:
                    continue
            except (TypeError, ValueError):
                pass
        visible.append(section)
    result['sections'] = visible
    result.pop('preview', None)
    return result

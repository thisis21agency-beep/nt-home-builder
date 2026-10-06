import json
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import permission_required
from django.db import transaction
from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from .models import Homepage, HomepageSnapshot, Section, SectionItem
from .services import active_published_payload, serialize_draft


def _json_body(request):
    try:
        return json.loads(request.body.decode('utf-8') or '{}')
    except json.JSONDecodeError:
        return {}


def _cors(response):
    response['Access-Control-Allow-Origin'] = settings.RNT_STOREFRONT_ORIGIN
    response['Vary'] = 'Origin'
    response['Cache-Control'] = 'public, max-age=60, stale-while-revalidate=300'
    return response


def _page(code='home'):
    return get_object_or_404(Homepage, code=code, active=True)


@require_GET
def storefront(request):
    page = get_object_or_404(Homepage, code='home', active=True)
    if page.published_payload:
        payload = active_published_payload(page.published_payload)
        mode = 'published'
    else:
        payload = serialize_draft(page, request)
        mode = 'draft'
    return render(request, 'homepage/storefront.html', {
        'page': page,
        'storefront_data': payload,
        'storefront_mode': mode,
    })

@require_GET
def homepage_api(request, code='home'):
    page = _page(code)
    if not page.published_payload:
        return _cors(JsonResponse({'error':'homepage_not_published'}, status=404))
    return _cors(JsonResponse(active_published_payload(page.published_payload)))

@require_GET
def homepage_preview_api(request, token):
    page = get_object_or_404(Homepage, preview_token=token, active=True)
    response = JsonResponse(serialize_draft(page, request))
    response['Cache-Control'] = 'no-store'
    response['Access-Control-Allow-Origin'] = settings.RNT_STOREFRONT_ORIGIN
    return response

@require_GET
def health(request):
    return JsonResponse({'status':'ok','service':'rnt-django-home-builder','time':timezone.now().isoformat()})

@staff_member_required
@permission_required('homepage.change_section', raise_exception=True)
def builder(request, code='home'):
    page = get_object_or_404(Homepage, code=code)
    return render(request, 'homepage/builder.html', {
        'page': page,
        'draft_data': serialize_draft(page, request),
        'section_types': Section._meta.get_field('section_type').choices,
        'layouts': Section._meta.get_field('layout').choices,
        'sources': Section._meta.get_field('source_type').choices,
    })

@require_POST
@staff_member_required
@permission_required('homepage.change_section', raise_exception=True)
def section_update(request, section_id):
    s = get_object_or_404(Section, pk=section_id)
    data = _json_body(request)
    fields = {
        'name':'name','key':'key','section_type':'section_type','layout':'layout','enabled':'enabled',
        'hide_desktop':'hideDesktop','hide_mobile':'hideMobile','eyebrow':'eyebrow','heading':'heading',
        'subheading':'subheading','body_html':'bodyHtml','cta1_label':'cta1Label','cta1_url':'cta1Url',
        'cta2_label':'cta2Label','cta2_url':'cta2Url','video_url':'videoUrl','desktop_image_url':'desktopImageUrl','mobile_image_url':'mobileImageUrl','source_type':'sourceType',
        'category_key':'categoryKey','product_limit':'productLimit','background_color':'backgroundColor',
        'text_color':'textColor','min_height':'minHeight','desktop_padding':'desktopPadding',
        'mobile_padding':'mobilePadding','text_align':'textAlign',
    }
    for attr, key in fields.items():
        if key in data:
            setattr(s, attr, data[key])
    from django.utils.dateparse import parse_datetime
    if 'startsAt' in data:
        s.starts_at = parse_datetime(data['startsAt']) if data['startsAt'] else None
    if 'endsAt' in data:
        s.ends_at = parse_datetime(data['endsAt']) if data['endsAt'] else None
    if 'productRefs' in data:
        refs = data['productRefs']
        if isinstance(refs, str):
            refs = [x.strip() for x in refs.split(',') if x.strip()]
        s.product_refs = refs if isinstance(refs, list) else []
    if 'settings' in data and isinstance(data['settings'], dict):
        s.settings = data['settings']
    if 'items' in data and isinstance(data['items'], list):
        keep_ids=[]
        for idx,row in enumerate(data['items'], start=1):
            if not isinstance(row, dict):
                continue
            item_id=row.get('id')
            item = s.items.filter(pk=item_id).first() if item_id else None
            if not item:
                item=SectionItem(section=s)
            item.sequence=idx*10
            item.enabled=bool(row.get('enabled', True))
            item.key=str(row.get('key') or '')[:80]
            item.eyebrow=str(row.get('eyebrow') or '')[:160]
            item.title=str(row.get('title') or '')[:220]
            item.subtitle=str(row.get('subtitle') or '')
            item.button_label=str(row.get('buttonLabel') or '')[:100]
            item.target_url=str(row.get('url') or '')[:500]
            item.desktop_image_url=str(row.get('desktopImageUrl') or '')[:1000]
            item.mobile_image_url=str(row.get('mobileImageUrl') or '')[:1000]
            item.video_url=str(row.get('videoUrl') or '')[:500]
            item.product_ref=str(row.get('productRef') or '')[:180]
            item.settings=row.get('settings') if isinstance(row.get('settings'), dict) else {}
            item.full_clean()
            item.save()
            keep_ids.append(item.id)
        s.items.exclude(id__in=keep_ids).delete()
    s.full_clean()
    s.save()
    return JsonResponse(serialize_draft(s.page, request))


@require_POST
@staff_member_required
@permission_required('homepage.change_section', raise_exception=True)
def section_upload_image(request, section_id):
    s = get_object_or_404(Section, pk=section_id)
    kind = request.POST.get('kind')
    upload = request.FILES.get('file')
    if kind not in {'desktop','mobile'} or not upload:
        return JsonResponse({'error':'kind_and_file_required'}, status=400)
    if kind == 'desktop':
        s.desktop_image = upload
        s.desktop_image_url = ''
    else:
        s.mobile_image = upload
        s.mobile_image_url = ''
    s.save()
    return JsonResponse(serialize_draft(s.page, request))

@require_POST
@staff_member_required
@permission_required('homepage.change_section', raise_exception=True)
def section_move(request, section_id):
    s = get_object_or_404(Section, pk=section_id)
    direction = _json_body(request).get('direction')
    ordered = list(s.page.sections.order_by('sequence','id'))
    idx = ordered.index(s)
    target = idx - 1 if direction == 'up' else idx + 1 if direction == 'down' else idx
    if 0 <= target < len(ordered) and target != idx:
        ordered[idx], ordered[target] = ordered[target], ordered[idx]
        with transaction.atomic():
            for i, row in enumerate(ordered, start=1):
                Section.objects.filter(pk=row.pk).update(sequence=i*10)
    return JsonResponse(serialize_draft(s.page, request))

@require_POST
@staff_member_required
@permission_required('homepage.add_section', raise_exception=True)
def section_add(request, code='home'):
    page = get_object_or_404(Homepage, code=code)
    last = page.sections.order_by('-sequence').first()
    s = Section.objects.create(
        page=page, sequence=(last.sequence + 10 if last else 10), key='new-section',
        name='New Homepage Section', heading='New Homepage Section', section_type='editorial_banner'
    )
    return JsonResponse({'sectionId':s.id,'draft':serialize_draft(page, request)})

@require_POST
@staff_member_required
@permission_required('homepage.add_section', raise_exception=True)
def section_duplicate(request, section_id):
    src = get_object_or_404(Section, pk=section_id)
    with transaction.atomic():
        src.pk = None
        src.sequence += 1
        src.name = f'{src.name} Copy'
        src.key = f'{src.key}-copy'[:80] if src.key else 'section-copy'
        src.save()
        clone = src
        # Re-sequence first, then item copying is handled from request's original id below.
        originals = SectionItem.objects.filter(section_id=section_id)
        for item in originals:
            item.pk = None
            item.section = clone
            item.save()
        ordered = list(clone.page.sections.order_by('sequence','id'))
        for i,row in enumerate(ordered,start=1):
            Section.objects.filter(pk=row.pk).update(sequence=i*10)
    return JsonResponse({'sectionId':clone.id,'draft':serialize_draft(clone.page, request)})

@require_POST
@staff_member_required
@permission_required('homepage.delete_section', raise_exception=True)
def section_delete(request, section_id):
    s = get_object_or_404(Section, pk=section_id)
    page = s.page
    s.delete()
    for i,row in enumerate(page.sections.order_by('sequence','id'),start=1):
        Section.objects.filter(pk=row.pk).update(sequence=i*10)
    return JsonResponse(serialize_draft(page, request))

@require_POST
@staff_member_required
@permission_required('homepage.change_homepage', raise_exception=True)
def publish(request, code='home'):
    page = get_object_or_404(Homepage, code=code)
    with transaction.atomic():
        revision = page.published_revision + 1
        payload = serialize_draft(page, request)
        payload['preview'] = False
        payload['revision'] = revision
        payload['generatedAt'] = timezone.now().isoformat()
        page.published_payload = payload
        page.published_revision = revision
        page.published_at = timezone.now()
        page.published_by = request.user
        page.save(update_fields=['published_payload','published_revision','published_at','published_by','updated_at'])
        HomepageSnapshot.objects.create(page=page, revision=revision, payload=payload, published_by=request.user)
    return JsonResponse({'ok':True,'revision':revision,'publishedAt':page.published_at.isoformat()})

@require_POST
@staff_member_required
@permission_required('homepage.change_homepage', raise_exception=True)
def restore(request, snapshot_id):
    snap = get_object_or_404(HomepageSnapshot, pk=snapshot_id)
    page = snap.page
    with transaction.atomic():
        revision = page.published_revision + 1
        payload = dict(snap.payload)
        payload['revision'] = revision
        payload['restoredFromRevision'] = snap.revision
        payload['generatedAt'] = timezone.now().isoformat()
        page.published_payload = payload
        page.published_revision = revision
        page.published_at = timezone.now()
        page.published_by = request.user
        page.save(update_fields=['published_payload','published_revision','published_at','published_by','updated_at'])
        HomepageSnapshot.objects.create(page=page, revision=revision, payload=payload, published_by=request.user)
    return JsonResponse({'ok':True,'revision':revision})

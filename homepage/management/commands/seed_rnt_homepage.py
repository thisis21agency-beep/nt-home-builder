from django.core.management.base import BaseCommand
from homepage.models import Homepage, Section, SectionItem

GIRL_IMG='https://lon1.digitaloceanspaces.com/rnt-website/banners/cmley41r801dbaiphnt8meeu5/1787311545703_jypb7v_DY8A9431_1.jpg'
BOY_IMG='https://lon1.digitaloceanspaces.com/rnt-website/banners/cmley41r801dbaiphnt8meeu5/1787311592596_qe3etw_DY8A9703.jpg'
BABY_IMG='https://lon1.digitaloceanspaces.com/rnt-website/banners/cmley41r801dbaiphnt8meeu5/1783000134320_u2wzim_baby_design_.jpg'

class Command(BaseCommand):
    help='Create the Ruff n Tumble homepage builder structure matching the current live homepage flow.'

    def handle(self,*args,**options):
        page,_=Homepage.objects.get_or_create(code='home', defaults={'name':"Ruff 'n' Tumble Homepage"})
        if page.sections.exists():
            self.stdout.write(self.style.WARNING('Homepage already has sections; nothing changed.'))
            return
        hero=Section.objects.create(page=page,sequence=10,key='hero',name='Hero',section_type='hero',layout='full',heading='New Season',cta1_label='Shop Girls',cta1_url='/category/girls',cta2_label='Shop Boys',cta2_url='/category/boys',desktop_image_url=GIRL_IMG,settings={'autoplay':True,'autoplayMs':5000})
        for seq,title,url,img in [(10,'Girls','/category/girls',GIRL_IMG),(20,'Boys','/category/boys',BOY_IMG),(30,'Baby','/category/babies',BABY_IMG)]:
            SectionItem.objects.create(section=hero,sequence=seq,title=title,button_label=f'Shop {title}',target_url=url,desktop_image_url=img)

        school=Section.objects.create(page=page,sequence=20,key='back-to-school',name='Back to School',section_type='category_grid',layout='four',heading='Explore our Back to School Collection')
        for seq,title,url in [
            (10,'Dresses','/category/girls-dresses'),(20,'Footwear','/category/footwear'),
            (30,'Matching Sets','/category/boys-matching-sets-sets'),(40,'Shirts','/category/boys-tops-shirts')]:
            SectionItem.objects.create(section=school,sequence=seq,title=title,button_label='Shop',target_url=url)

        departments=Section.objects.create(page=page,sequence=30,key='shop-departments',name='Shop Girls Boys Baby',section_type='category_grid',layout='three',heading='Shop by Department')
        for seq,title,url,img in [(10,'Shop Girls','/category/girls',GIRL_IMG),(20,'Shop Boys','/category/boys',BOY_IMG),(30,'Shop Baby Wears','/category/babies',BABY_IMG)]:
            SectionItem.objects.create(section=departments,sequence=seq,title=title,button_label='Shop',target_url=url,desktop_image_url=img)

        Section.objects.create(page=page,sequence=40,key='recommendations',name='Recommendations',section_type='product_rail',layout='carousel',heading='Recommendations for you',source_type='recommendations',product_limit=8)
        Section.objects.create(page=page,sequence=50,key='timotiwa',name='Timotiwa',section_type='editorial_banner',layout='full',heading='Timotiwa',cta1_label='Shop',cta1_url='/search?query=Timotiwa',desktop_image_url=GIRL_IMG)
        Section.objects.create(page=page,sequence=60,key='our-story',name='Our Story',section_type='story',layout='two',heading='Our Story',subheading='Let children be children.',body_html='<p>Premium children’s clothing designed for movement, comfort, confidence and real everyday childhood.</p>',cta1_label='Discover Our Story',cta1_url='/about-us',desktop_image_url=BOY_IMG)
        Section.objects.create(page=page,sequence=70,key='customer-love',name='Customer Love',section_type='customer_love',heading='Our Customers Love Us')
        Section.objects.create(page=page,sequence=80,key='newsletter',name='Mailing List',section_type='newsletter',heading='Join Our Mailing List',subheading='Be first to hear about new arrivals, offers and style updates.')
        self.stdout.write(self.style.SUCCESS('RNT homepage builder seeded. Open /builder/home/'))

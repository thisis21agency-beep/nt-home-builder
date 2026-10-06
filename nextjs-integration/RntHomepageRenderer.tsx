import Image from 'next/image';
import Link from 'next/link';
import type { ReactNode } from 'react';
import type { RntHomepage, RntSection } from './rnt-home';

export default function RntHomepageRenderer({payload, renderProductRail}:{
  payload:RntHomepage;
  renderProductRail:(section:RntSection)=>ReactNode;
}){
  return <main data-home-revision={payload.revision}>{payload.sections.map(section=>{
    if(section.type==='product_rail') return <section key={section.id}>{renderProductRail(section)}</section>;
    if(section.type==='hero') return <Hero key={section.id} section={section}/>;
    if(section.type==='category_grid') return <CategoryGrid key={section.id} section={section}/>;
    if(section.type==='editorial_banner'||section.type==='split_banner') return <Editorial key={section.id} section={section}/>;
    if(section.type==='story') return <Story key={section.id} section={section}/>;
    if(section.type==='newsletter') return <Newsletter key={section.id} section={section}/>;
    return null;
  })}</main>;
}
function Img({src,alt,className=''}:{src:string;alt:string;className?:string}){return src?<Image src={src} alt={alt} width={1600} height={1000} className={className}/>:null}
function Hero({section}:{section:RntSection}){const slide=section.items[0];return <section className="rnt-hero"><Img src={slide?.desktopImage||section.media.desktopImage} alt={slide?.title||section.content.heading}/><div><h1>{slide?.title||section.content.heading}</h1><p>{slide?.subtitle||section.content.subheading}</p>{(slide?.url||section.content.cta1.url)&&<Link href={slide?.url||section.content.cta1.url}>{slide?.buttonLabel||section.content.cta1.label}</Link>}</div></section>}
function CategoryGrid({section}:{section:RntSection}){return <section><h2>{section.content.heading}</h2><div className="rnt-category-grid">{section.items.map(i=><Link href={i.url||'#'} key={i.id}><Img src={i.desktopImage} alt={i.title}/><h3>{i.title}</h3></Link>)}</div></section>}
function Editorial({section}:{section:RntSection}){return <section className="rnt-editorial"><Img src={section.media.desktopImage} alt={section.content.heading}/><div><h2>{section.content.heading}</h2><p>{section.content.subheading}</p>{section.content.cta1.url&&<Link href={section.content.cta1.url}>{section.content.cta1.label}</Link>}</div></section>}
function Story({section}:{section:RntSection}){return <section className="rnt-story"><div><h2>{section.content.heading}</h2><p>{section.content.subheading}</p><div dangerouslySetInnerHTML={{__html:section.content.bodyHtml}}/></div><Img src={section.media.desktopImage} alt={section.content.heading}/></section>}
function Newsletter({section}:{section:RntSection}){return <section><h2>{section.content.heading}</h2><p>{section.content.subheading}</p>{/* Keep the CURRENT RNT/Brevo newsletter form here rather than creating a second subscriber system. */}</section>}

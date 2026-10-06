import { getRntHomepage } from './rnt-home';
import RntHomepageRenderer from './RntHomepageRenderer';
// Import the CURRENT RNT product component/service. Names below are examples only.
// import ProductCarousel from '@/components/ProductCarousel';

export default async function Home({searchParams}:{searchParams:Promise<{rnt_preview_token?:string}>}){
  const params=await searchParams;
  const payload=await getRntHomepage(params.rnt_preview_token);
  return <RntHomepageRenderer
    payload={payload}
    renderProductRail={(section)=>(
      <div>
        {/* Replace this block with the existing product carousel. */}
        <h2>{section.content.heading}</h2>
        <pre>{JSON.stringify(section.source,null,2)}</pre>
      </div>
    )}
  />;
}

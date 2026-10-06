export type RntItem = {
  id: number; key: string; eyebrow: string; title: string; subtitle: string;
  buttonLabel: string; url: string; desktopImage: string; mobileImage: string;
  videoUrl: string; productRef: string; settings: Record<string, unknown>;
};
export type RntSection = {
  id:number; key:string; name:string; type:string; layout:string; enabled:boolean;
  hideDesktop:boolean; hideMobile:boolean;
  content:{eyebrow:string;heading:string;subheading:string;bodyHtml:string;cta1:{label:string;url:string};cta2:{label:string;url:string}};
  media:{desktopImage:string;mobileImage:string;videoUrl:string};
  source:{type:string;categoryKey:string;productRefs:string[];limit:number};
  style:{backgroundColor:string;textColor:string;minHeight:string;desktopPadding:string;mobilePadding:string;textAlign:string};
  items:RntItem[]; settings:Record<string,unknown>;
};
export type RntHomepage = {schemaVersion:number;page:{code:string;name:string};revision:number;generatedAt:string;sections:RntSection[]};

const CMS = (process.env.RNT_HOME_CMS_URL || 'http://127.0.0.1:8000').replace(/\/$/,'');
export async function getRntHomepage(previewToken?:string):Promise<RntHomepage>{
  const url = previewToken ? `${CMS}/api/v1/homepage/preview/${encodeURIComponent(previewToken)}/` : `${CMS}/api/v1/homepage/home/`;
  const res = await fetch(url, previewToken ? {cache:'no-store'} : {next:{revalidate:60}});
  if(!res.ok) throw new Error(`RNT homepage CMS returned ${res.status}`);
  return res.json();
}

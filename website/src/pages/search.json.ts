import type { APIRoute } from 'astro';
import { book, chapterHref } from '../lib/book';
export const GET: APIRoute = () => {
 const docs=book.chapters.flatMap(c=>{
  const result=[{id:c.id,title:c.title,chapter:`Chapter ${c.number}`,number:String(c.number),url:chapterHref(c.slug),text:c.searchText}];
  const sections=c.sections.filter(s=>s.level===1);
  for(let i=0;i<sections.length;i++){
   const s=sections[i];const start=c.html.indexOf(`id="${s.anchor}"`);const end=i+1<sections.length?c.html.indexOf(`id="${sections[i+1].anchor}"`):c.html.length;
   const html=start>=0?c.html.slice(c.html.lastIndexOf('<',start),end>start?c.html.lastIndexOf('<',end):undefined):'';
   const text=html.replace(/<[^>]+>/g,' ').replace(/&lt;/g,'<').replace(/&gt;/g,'>').replace(/&quot;/g,'"').replace(/&#(?:39|x27);/gi,"'").replace(/&amp;/g,'&').replace(/\s+/g,' ').trim();
   result.push({id:s.id,title:s.title,chapter:`Chapter ${c.number}`,number:s.number,url:chapterHref(c.slug)+`#${s.anchor}`,text});
  }
  return result;
 });
 return new Response(JSON.stringify(docs),{headers:{'Content-Type':'application/json; charset=utf-8'}});
};

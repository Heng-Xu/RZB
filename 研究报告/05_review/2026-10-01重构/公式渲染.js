const fs=require('fs');
const {mathjax}=require('/tmp/xuzhou_math/node_modules/mathjax-full/js/mathjax.js');
const {TeX}=require('/tmp/xuzhou_math/node_modules/mathjax-full/js/input/tex.js');
const {SVG}=require('/tmp/xuzhou_math/node_modules/mathjax-full/js/output/svg.js');
const {liteAdaptor}=require('/tmp/xuzhou_math/node_modules/mathjax-full/js/adaptors/liteAdaptor.js');
const {RegisterHTMLHandler}=require('/tmp/xuzhou_math/node_modules/mathjax-full/js/handlers/html.js');
const {AllPackages}=require('/tmp/xuzhou_math/node_modules/mathjax-full/js/input/tex/AllPackages.js');
const adapter=liteAdaptor();RegisterHTMLHandler(adapter);
const doc=mathjax.document('',{InputJax:new TeX({packages:AllPackages}),OutputJax:new SVG({fontCache:'none'})});
const data=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
for (const item of data){
 const node=doc.convert(item.tex,{display:true,em:16,ex:8,containerWidth:750});
 const svg=adapter.firstChild(node);const str=adapter.outerHTML(svg);
 if(str.includes('data-mjx-error')) throw new Error(item.number+':'+str);
 fs.writeFileSync(item.svg,str);
}

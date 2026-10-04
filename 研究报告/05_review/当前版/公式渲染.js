const fs=require('fs');
const path=require('path');
let mathjaxRoot;
try { mathjaxRoot=path.dirname(require.resolve('mathjax-full/package.json')); }
catch (error) { mathjaxRoot=process.env.XUZHOU_MATHJAX_ROOT || '/tmp/xuzhou_math/node_modules/mathjax-full'; }
const mj=(file)=>require(path.join(mathjaxRoot,file));
const {mathjax}=mj('js/mathjax.js');
const {TeX}=mj('js/input/tex.js');
const {SVG}=mj('js/output/svg.js');
const {liteAdaptor}=mj('js/adaptors/liteAdaptor.js');
const {RegisterHTMLHandler}=mj('js/handlers/html.js');
const {AllPackages}=mj('js/input/tex/AllPackages.js');
const adapter=liteAdaptor();RegisterHTMLHandler(adapter);
const doc=mathjax.document('',{InputJax:new TeX({packages:AllPackages}),OutputJax:new SVG({fontCache:'none'})});
const data=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
for (const item of data){
 const node=doc.convert(item.tex,{display:true,em:16,ex:8,containerWidth:750});
 const svg=adapter.firstChild(node);const str=adapter.outerHTML(svg);
 if(str.includes('data-mjx-error')) throw new Error(item.number+':'+str);
 fs.writeFileSync(item.svg,str);
}

const $=id=>document.getElementById(id), host=$('viewport');
const scene=new THREE.Scene();scene.background=new THREE.Color('#edf1f3');
const camera=new THREE.PerspectiveCamera(38,1,.05,5000);camera.up.set(0,0,1);
const renderer=new THREE.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});
renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.outputEncoding=THREE.sRGBEncoding;host.prepend(renderer.domElement);
scene.add(new THREE.HemisphereLight(0xffffff,0x75818b,1.05));
for(const [p,intensity] of [[[100,400,280],.9],[[-160,760,90],.45]]){const l=new THREE.DirectionalLight(0xffffff,intensity);l.position.set(...p);scene.add(l);}
const controls=new THREE.OrbitControls(camera,renderer.domElement);controls.enableDamping=true;
const objects=[],angles=[0,0,0,0],my=[515,565,615,678];let playing=false,ready=false;
const loader=new THREE.STLLoader();
for(let k=0;k<4;k++){
 const d=document.createElement('div');d.className='angle';d.innerHTML=`<label>Мотор ${k}<input aria-label="Угол мотора ${k}" type="number" min="0" max="360" value="0" id="n${k}"></label><input aria-label="Ползунок мотора ${k}" id="a${k}" type="range" min="0" max="360" value="0">`;$('angles').append(d);
 for(const prefix of ['a','n'])$(prefix+k).addEventListener('input',e=>{angles[k]=Math.max(0,Math.min(360,Number(e.target.value)||0));$('a'+k).value=$('n'+k).value=angles[k];pose();});
}
function visibleItem(o){return $('view').value==='guide' ? /^guide_0$|^(bolt|washer|nut)_0_/.test(o.name) : ($('base').checked||!['D1','D2'].includes(o.name));}
function pose(){
 const e=Number($('explode').value);$('explodeOut').textContent=e+' мм';
 for(const o of objects){o.mesh.visible=visibleItem(o);o.mesh.position.set(0,0,0);o.mesh.rotation.z=0;
  if(o.group==='crank'){o.mesh.position.set(0,my[o.k],0);o.mesh.rotation.z=angles[o.k]*Math.PI/180;}
  if(o.group==='tail')o.mesh.position.y=4.8*Math.sin(angles[o.k]*Math.PI/180);
  if(o.group==='guide')o.mesh.position.z=e;
  if(o.group==='hardware')o.mesh.position.z=o.name.startsWith('nut')?e+e*.3:-e*.6;
  if(o.group==='tail'&&$('view').value==='assembly')o.mesh.position.z=e*(1.4+o.k*.25);
 }
}
function frame(top=false){
 const bounds=new THREE.Box3();for(const o of objects)if(o.mesh.visible)bounds.expandByObject(o.mesh);
 if(bounds.isEmpty())return;const center=bounds.getCenter(new THREE.Vector3()),r=bounds.getSize(new THREE.Vector3()).length()/2;
 const dist=r/Math.sin(camera.fov*Math.PI/360)*Math.max(1,1/camera.aspect)*1.1;
 controls.target.copy(center);camera.position.copy(center).add((top?new THREE.Vector3(0,-.001,1):new THREE.Vector3(1,-1.45,1.25)).normalize().multiplyScalar(dist));camera.lookAt(center);controls.update();
}
new ResizeObserver(()=>{const w=host.clientWidth,h=host.clientHeight;renderer.setSize(w,h);camera.aspect=w/h;camera.updateProjectionMatrix();if(ready)frame();}).observe(host);
$('view').onchange=()=>{pose();frame();};$('base').onchange=pose;$('explode').oninput=pose;$('home').onclick=()=>frame();$('top').onclick=()=>frame(true);
$('play').onclick=()=>{playing=!playing;$('play').innerHTML=`<i data-lucide="${playing?'pause':'play'}"></i>`;lucide.createIcons();};
async function init(){
 const response=await fetch('scene.json');if(!response.ok)throw Error('scene.json '+response.status);const data=await response.json();
 for(const o of data){const geo=await loader.loadAsync('meshes/'+o.name+'.stl');
  if(o.group==='crank')geo.translate(0,-my[o.k],0);
  const mesh=new THREE.Mesh(geo,new THREE.MeshStandardMaterial({color:o.color,roughness:.62,metalness:o.group==='hardware'?.5:.05}));scene.add(mesh);objects.push({...o,mesh});
 }ready=true;pose();frame();$('status').textContent='A3 · CAD, мм';window.astra={objects,angles,pose,frame,renderer,scene,camera};
}
let last=performance.now();function loop(now){requestAnimationFrame(loop);const dt=Math.min((now-last)/1000,.05);last=now;
 if(playing&&ready){for(let k=0;k<4;k++){angles[k]=(angles[k]+dt*35)%360;$('a'+k).value=$('n'+k).value=Math.round(angles[k]);}pose();}
 controls.update();renderer.render(scene,camera);
}lucide.createIcons();requestAnimationFrame(loop);init().catch(e=>{$('status').textContent='Ошибка загрузки: '+e.message;console.error(e);});

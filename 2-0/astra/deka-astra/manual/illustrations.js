const stage=document.getElementById('stage'),W=1280,H=672;
const scene=new THREE.Scene();scene.background=new THREE.Color('#f3f5f6');
const camera=new THREE.OrthographicCamera(-160,160,84,-84,.1,2500);camera.up.set(0,0,1);
const renderer=new THREE.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});renderer.setSize(W,H);renderer.setPixelRatio(1);renderer.outputEncoding=THREE.sRGBEncoding;stage.prepend(renderer.domElement);
scene.add(new THREE.HemisphereLight(0xffffff,0x7a8991,.8));
for(const [pos,power] of [[[150,300,450],.7],[[-180,700,140],.35]]){const l=new THREE.DirectionalLight(0xffffff,power);l.position.set(...pos);scene.add(l);}
const loader=new THREE.STLLoader(),parts={},extra=[];
function mesh(geometry,color){const m=new THREE.Mesh(geometry,new THREE.MeshStandardMaterial({color,roughness:.72,metalness:.03}));scene.add(m);return m;}
async function load(){
 const data=await(await fetch('../viewer/scene.json')).json();
 for(const item of data){const g=await loader.loadAsync('../viewer/meshes/'+item.name+'.stl');parts[item.name]=mesh(g,item.color);}
 for(let i=0;i<4;i++){parts['plate_'+i]=mesh(await loader.loadAsync('plate_'+i+'.stl'),i?'#42a67a':'#bec9d1');parts['id_'+i]=mesh(await loader.loadAsync('crank_id_'+i+'.stl'),'#3589c9');}
 for(const n of ['lap_ext','lap_tail'])parts[n]=mesh(await loader.loadAsync(n+'.stl'),n==='lap_ext'?'#42a67a':'#ed9947');
 for(const n of ['mount_floor','motor_floor','joint_d1','joint_d2'])parts[n]=mesh(await loader.loadAsync(n+'.stl'),'#bec9d1');
 window.manual={draw};draw(0);window.manualReady=true;
}
function show(names){for(const n of names)parts[n].visible=true;}
function move(name,x=0,y=0,z=0){parts[name].position.set(x,y,z);}
function arrow(from,to,color='#dc513f'){
 const a=new THREE.Vector3(...from),b=new THREE.Vector3(...to),d=b.clone().sub(a),len=d.length();
 const helper=new THREE.ArrowHelper(d.normalize(),a,len,color,Math.min(4,len*.3),Math.min(2,len*.16));scene.add(helper);extra.push(helper);
}
function bolt(x,y,z,len=4){
 const g=new THREE.Group();
 for(const [r,h,offset] of [[1.5,len,len/2],[2.75,2,-1]]){const m=new THREE.Mesh(new THREE.CylinderGeometry(r,r,h,24),new THREE.MeshStandardMaterial({color:'#586976'}));m.rotation.x=Math.PI/2;m.position.z=offset;g.add(m);}
 g.position.set(x,y,z);scene.add(g);extra.push(g);
}
function highlightWindow(){
 const pts=[[5.6,536.8,8.25],[14.4,536.8,8.25],[14.4,536.8,10.35],[5.6,536.8,10.35],[5.6,536.8,8.25]].map(p=>new THREE.Vector3(...p));
 const l=new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts),new THREE.LineBasicMaterial({color:'#c8402e'}));scene.add(l);extra.push(l);
}
function label(text,detail,point,x,y){return {text,detail,point,x,y};}
const all=['D1','D2','guide_0','guide_1','guide_2','motor_0','motor_1','motor_2','motor_3','crank_0','crank_1','crank_2','crank_3','tail_0','tail_1','tail_2','tail_3','spacer_0'];
function draw(step){
 for(const m of Object.values(parts)){m.visible=false;m.position.set(0,0,0);m.rotation.set(0,0,0);}
 for(const o of extra){scene.remove(o);}extra.length=0;
 let title='',sub='',note='',labels=[],center=[0,610,0],dir=[1,-1.3,1.25],height=270;
 switch(step){
 case 0:
  title='Напечатай только новые детали';sub='Файл 01_A2_D1_and_3_guides.3mf · 4 отдельных объекта';
  show(['plate_0','plate_1','plate_2','plate_3']);center=[48,89,8];height=225;dir=[.7,-1,1.8];
  labels=[label('Д1 — 1 штука','Новое основание A2',[28,95,3],42,55),label('Опоры — 3 штуки','Цельные, без болтов',[82,48,3],1010,380)];note='3MF содержит геометрию. Профиль принтера и пластика выбери свой, затем проверь нарезку.';break;
 case 1:
  title='Подготовь Д1 и Д2';sub='Д1 — к грифу; Д2 — дальняя часть деки';
  show(['D1','D2']);move('D2',0,20,0);center=[0,645,0];height=285;
  labels=[label('Д1, ближе к грифу','Три места под моторы',[0,550,3],32,450),label('Д2, дальше от грифа','Одно место под мотор',[0,740,3],1010,40)];note='Д2 v3 можно оставить уже напечатанный. Старый Д1 с длинными пазами для A2 не подходит.';break;
 case 2:
  title='Соедини две части основания';sub='Д2 опускается на тонкую полку Д1';
  sub='Крупный план стыка; борта скрыты для наглядности';
  show(['joint_d1','joint_d2']);move('joint_d2',0,0,16);center=[0,649,1];height=95;dir=[.4,-1,.7];
  for(const x of [-21,-9,21]){bolt(x,649,-22);arrow([x,649,-17],[x,649,0]);}
  arrow([0,660,25],[0,660,5]);
  labels=[label('Три М3×4 снизу','Два крайних и левое среднее',[-9,649,-23],30,450),label('Это отверстие пустое','У лент, X = +5',[5,649,17.5],1000,85)];note='Не ставь четвёртый винт: его конец окажется возле прохода лент.';break;
 case 3:
  title='Мотор 0 ставится через проставку';sub='Ближайший мотор к грифу · вид узла в разнесении';
  sub='Ближайший мотор к грифу · борта основания скрыты';
  show(['motor_floor','motor_0','spacer_0']);move('motor_0',0,0,-19);move('spacer_0',0,0,-8);center=[0,514,-17];height=92;dir=[1,-1.4,.7];
  arrow([0,515,-14],[0,515,-3]);
  labels=[label('Проставка — 4 мм','Между мотором 0 и Д1',[8,515,-10],1000,90),label('Мотор 0 снизу','Выступ и шестерня вверх',[0,515,-34],30,390)];note='Два винта через основание и проставку в уши мотора. Примерь длину, не упирай винт в дно резьбы.';break;
 case 4:
  title='Установи остальные три мотора';sub='Моторы 1, 2, 3 — без проставки';
  show(['D1','D2','motor_0','motor_1','motor_2','motor_3','spacer_0']);center=[0,611,-5];height=260;dir=[1,-1.2,.9];
  labels=[label('0 — с проставкой','У переднего края',[12,508,-21],30,465),label('1, 2, 3 — без неё','Плотно к дну основания',[12,608,-16],1005,120)];note='Каждый мотор должен стоять ровно и не качаться. Провода отведи от движущихся деталей.';break;
 case 5:
  title='Разложи кривошипы по номерам';sub='Палец на диске всегда направлен вверх';
  show(['id_0','id_1','id_2','id_3']);center=[49,8,6];height=83;dir=[.1,-1,.45];
  labels=[label('0 и 1 — низкие','Ориентируйся по имени файла',[8,8,1],35,425),label('2 и 3 — высокие','Не меняй этажи местами',[64,8,9],1000,45)];
  for(let k=0;k<4;k++)labels.push(label(String(k),'',[k*28+8.3,8.3,k?6:2],260+k*185,540));
  note='Слева направо: crank0, crank1, crank2, crank3. Нумерация файлов важнее внешнего сходства.';break;
 case 6:
  title='Надень кривошипы на моторы';sub='Показан мотор 0; повтори для остальных этажей';
  show(['D1','motor_0','spacer_0','crank_0']);move('crank_0',0,0,14);center=[0,515,4];height=83;dir=[1,-1.4,1.6];arrow([0,515,13],[0,515,3]);
  labels=[label('Палец вверх','В начале — в сторону лент',[4.8,515,18.45],1000,100),label('На шестерню','Не забивать и не давить на вал',[0,515,2.5],30,440)];note='Кривошип не должен свободно проворачиваться на шестерне. Если посадка плохая — здесь остановись.';break;
 case 7:
  title='Продень узкий конец ленты';sub='Отдельно от основания · пример: лента 1 и опора А';
  show(['guide_0','tail_1']);move('tail_1',0,80,0);center=[4,573,10];height=95;dir=[1,-1.5,1.2];
  arrow([10,566,8.9],[10,532,8.9]);highlightWindow();
  labels=[label('Лента 1: второе окно','Считай снизу: 0, 1, 2, 3',[10,537,9.3],30,100),label('Узкий конец первым','Не широкая рамка',[10,560,9],1000,430)];note='Ленты пока не соединяй с продолжениями грифа. Широкая рамка через закрытое окно не проходит.';break;
 case 8:
  title='Собери ленты с тремя опорами';sub='Опоры А, Б, В от грифа; все окна своих этажей';
  show(['guide_0','guide_1','guide_2','tail_1','tail_2','tail_3']);center=[4,580,10];height=200;
  labels=[label('А — ближе к грифу','Ленты 1, 2, 3',[0,540,15],30,405),label('Б — средняя','Ленты 2, 3',[0,590,15],1000,340),label('В — дальняя','Только лента 3',[0,634,20],1000,45)];note='Лента 0 до опор не доходит. Пустые нижние окна — это нормально.';break;
 case 9:
  title='Опусти комплект в основание';sub='Три опоры с лентами — вниз; рамки попадают на пальцы';
  show(all);center=[0,602,12];height=265;
  for(const n of ['guide_0','guide_1','guide_2','tail_1','tail_2','tail_3'])move(n,0,0,18);
  for(const y of [540,590,634])arrow([-4,y,19],[-4,y,3]);
  labels=[label('Опоры в круглые отверстия','Поддерживай ленты руками',[-4,540,5],30,445),label('Рамки — на пальцы','У каждой свой мотор',[4.8,615,15],1000,80)];note='Ленту 0 положи отдельно на палец мотора 0. Не сгибай ленты для попадания в опоры.';break;
 case 10:
  title='Посади обе ножки до упора';sub='Без болтов, гаек и клея · показана опора А';
  sub='Опора А; борта основания скрыты. Крепёж не нужен';
  show(['mount_floor','guide_0']);move('guide_0',0,0,8);center=[5,540,12];height=66;dir=[1,-1.5,1.9];
  for(const x of [-4,18])arrow([x,540,7],[x,540,1]);
  labels=[label('Нажимай над ножками','Равномерно, без молотка',[-4,540,27],30,70),label('Ø5,7 → Ø6,0','Как у прежнего удачного варианта',[18,540,3],1000,430)];note='Плечики опоры должны сесть на дно. Если качается или вынимается от хода ленты — остановись.';break;
 case 11:
  title='Соедини хвосты с лентами грифа';sub='Крупный план стыка этажа 1; повтори для каждого этажа';
  show(['lap_ext','lap_tail']);move('lap_tail',0,0,5);center=[10,489,10];height=43;dir=[1,-1.6,.9];
  arrow([10,486.5,13],[10,486.5,9]);
  labels=[label('Лента из грифа','На рисунке зелёная',[10,476,9],30,400),label('Хвост из деки','Накрой штырёк отверстием',[10,486.5,14],1000,60)];note='Высокий штырёк входит в отверстие верхнего язычка. Соединение должно лечь без ступеньки и перекоса.';break;
 case 12:
  title='Проверь каждый привод руками';sub='Сначала без питания · четыре независимые проверки';
  show(all);center=[0,610,0];height=265;
  arrow([10,469,21],[10,482,21]);arrow([10,491,21],[10,482,21]);
  labels=[label('Крути по одному','Без заеданий на полном обороте',[4.8,565,9],1000,105),label('Ход хвоста ≈ 9,6 мм','Соседние ленты неподвижны',[10,480,10],30,450)];note='Опоры не выходят из отверстий, соединения не расходятся. Моторный прогон — только после этой проверки.';break;
 }
 document.getElementById('number').textContent=String(step).padStart(2,'0');document.getElementById('title').textContent=title;document.getElementById('subtitle').textContent=sub;document.getElementById('footer').textContent=note;
 camera.left=-height*W/H/2;camera.right=height*W/H/2;camera.top=height/2;camera.bottom=-height/2;camera.updateProjectionMatrix();
 const c=new THREE.Vector3(...center);camera.position.copy(c).add(new THREE.Vector3(...dir).normalize().multiplyScalar(700));camera.lookAt(c);camera.updateMatrixWorld();
 renderer.render(scene,camera);stage.querySelectorAll('.label').forEach(e=>e.remove());
 const svg=document.getElementById('overlay');svg.innerHTML='<defs><marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#dc513f"/></marker></defs>';
 for(const a of labels){
  const el=document.createElement('div');el.className='label';el.style.left=a.x+'px';el.style.top=a.y+'px';if(a.detail==='')el.style.width='52px';
  const strong=document.createElement('strong');strong.textContent=a.text;el.append(strong);const small=document.createElement('small');small.textContent=a.detail;el.append(small);stage.append(el);
  const p=new THREE.Vector3(...a.point).project(camera),tx=(p.x+1)*W/2,ty=(1-p.y)*H/2;
  const sx=Math.max(a.x,Math.min(tx,a.x+el.offsetWidth)),sy=Math.max(a.y,Math.min(ty,a.y+el.offsetHeight));
  const line=document.createElementNS('http://www.w3.org/2000/svg','line');Object.entries({x1:sx,y1:sy,x2:tx,y2:ty,stroke:'#dc513f','stroke-width':2.5,'marker-end':'url(#arrow)'}).forEach(([k,v])=>line.setAttribute(k,v));svg.append(line);
 }
}
load().catch(e=>{document.getElementById('title').textContent=e.message;console.error(e);});

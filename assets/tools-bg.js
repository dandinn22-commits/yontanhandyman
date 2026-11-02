/* Tool background: spaced cut-outs on both sides of the content, placed only where they don't touch text or buttons, with a calm parallax */
(function(){
  var layer=document.getElementById('tools-bg'); if(!layer) return;
  var page=layer.parentNode;
  var SPR=[{k:'kit',src:'/img/art/kit.webp',w:582,h:414,rot:3},{k:'screwdriver',src:'/img/art/screwdriver.webp',w:365,h:92,rot:14},{k:'drill',src:'/img/art/drill.webp',w:308,h:305,rot:4}];
  var reduce=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;
  var items=[], timer;
  function rng(seed){return function(){seed|=0;seed=seed+0x6D2B79F5|0;var t=Math.imul(seed^seed>>>15,1|seed);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};}
  function obstacles(base,padX,padY){
    var out=[];
    function add(r){ if(r.width<2||r.height<2) return; out.push({l:r.left-base.left-padX,t:r.top-base.top-padY,r:r.right-base.left+padX,b:r.bottom-base.top+padY}); }
    page.querySelectorAll('h1,h2,h3,p,dt,dd,caption,summary,.eyebrow,.foot-in>div').forEach(function(el){
      if(el.closest('.ticket,.svc,.panel,.faq details,.steps li,.facts,.table-wrap')) return;
      var rg=document.createRange(); rg.selectNodeContents(el); Array.prototype.forEach.call(rg.getClientRects(),add);
    });
    page.querySelectorAll('.top,.ticket,.svc,.table-wrap,.steps li,.facts,.areas li,.faq details,.chips li,.btn,.panel,.a11y,.skip').forEach(function(el){add(el.getBoundingClientRect());});
    return out;
  }
  function hit(a,list){for(var i=0;i<list.length;i++){var o=list[i];if(a.l<o.r&&a.r>o.l&&a.t<o.b&&a.b>o.t)return true;}return false;}
  function layout(){
    layer.innerHTML=''; items=[];
    var vw=page.clientWidth, mob=vw<700, base=page.getBoundingClientRect(), H=page.scrollHeight;
    layer.style.height=H+'px';
    var amp=reduce?0:(mob?12:36), widths=mob?{kit:150,screwdriver:130,drill:84}:{kit:290,screwdriver:210,drill:160};
    var obs=obstacles(base,mob?12:24,(mob?16:20)+amp), placed=[];
    var rand=rng(20261102), step=mob?440:560, start=(mob?90:110), side=0, n=0;
    for(var y=start; y<H-120; y+=step*(0.85+rand()*0.3)){
      var spr=SPR[n%3]; n++;
      var flip=rand()<0.5, rot=(rand()*2-1)*spr.rot, ok=null;
      [1,0.78,0.6].some(function(sc){
        var w=Math.round(widths[spr.k]*sc), h=Math.round(w*spr.h/spr.w), edge=mob?6:Math.max(12,vw*0.025);
        var xs=[]; for(var f=0;f<=1.0001;f+=mob?0.25:0.12){ var x=edge+f*(vw*0.5-w-edge); xs.push(side?vw-x-w:x); }
        for(var dy=0; dy<=step*0.55; dy+=16){
          for(var sgn=-1;sgn<=1;sgn+=2){
            var top=y+sgn*dy-h/2; if(top<40||top+h>H-40) continue;
            for(var i=0;i<xs.length;i++){
              var box={l:xs[i],t:top,r:xs[i]+w,b:top+h}, gap=mob?40:90;
              if(hit(box,obs)) continue;
              if(hit(mob?{l:-1e5,t:box.t-gap*2.5,r:1e5,b:box.b+gap*2.5}:{l:box.l-gap,t:box.t-gap*2,r:box.r+gap,b:box.b+gap*2},placed)) continue;
              ok={x:xs[i],top:top,w:w,h:h}; return true;
            }
          }
        }
        return false;
      });
      side=1-side;
      if(!ok) continue;
      placed.push({l:ok.x,t:ok.top,r:ok.x+ok.w,b:ok.top+ok.h});
      var img=new Image(); img.src=spr.src; img.alt=''; img.decoding='async'; img.className='tool';
      img.style.cssText='left:'+ok.x+'px;top:'+ok.top+'px;width:'+ok.w+'px;';
      layer.appendChild(img);
      items.push({el:img,h:ok.h,cy:ok.top+ok.h/2,k:0.05+rand()*0.07,amp:amp,tf:'rotate('+rot.toFixed(1)+'deg)'+(flip?' scaleX(-1)':'')});
    }
    paint();
  }
  var ticking=false;
  function paint(){
    ticking=false;
    var mid=window.scrollY+window.innerHeight/2, pageTop=page.getBoundingClientRect().top, off=pageTop+window.scrollY;
    items.forEach(function(it){
      var dy=it.amp?Math.max(-it.amp,Math.min(it.amp,(mid-off-it.cy)*-it.k)):0;
      it.el.style.transform='translate3d(0,'+dy.toFixed(1)+'px,0) '+it.tf;
    });
  }
  window.addEventListener('scroll',function(){ if(!ticking&&!reduce){ticking=true;requestAnimationFrame(paint);} },{passive:true});
  function later(){clearTimeout(timer);timer=setTimeout(layout,150);}
  window.addEventListener('resize',later);
  document.addEventListener('toggle',later,true);
  if(document.fonts&&document.fonts.ready) document.fonts.ready.then(later);
  window.addEventListener('load',later);
  layout();
})();

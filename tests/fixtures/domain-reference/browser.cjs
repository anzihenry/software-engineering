const {chromium} = require('playwright');
const fs = require('node:fs');
const path = require('node:path');
const output = process.argv[2];
if (!output) throw new Error('output directory required');
fs.mkdirSync(output, {recursive:true});
(async () => {
 const browser = await chromium.launch({executablePath:process.env.REFERENCE_CHROMIUM,headless:true,args:['--no-proxy-server']});
 try {
 const page = await browser.newPage({viewport:{width:1024,height:768}});
 const observations = {layout_shifts:[],resource_entries:[],browser:browser.version(),executed_at:new Date().toISOString(),playwright:require('playwright/package.json').version,viewport:{width:1024,height:768},responses:[],console:[],states:[],loading:[],navigation_samples_ms:[],keyboard_states:[]};
 page.on('request',r=>{if(r.url().includes('/api/')) (observations.requests??=[]).push({url:r.url(),method:r.method(),headers:r.headers()});});
 page.on('console',m=>observations.console.push({type:m.type(),text:m.text()}));
 page.on('response',async r=>{if(r.url().includes('/api/'))observations.responses.push({url:r.url(),status:r.status(),body:await r.text()});});
 for(let i=0;i<5;i++){
  await page.goto('http://127.0.0.1:8765');
  observations.navigation_samples_ms.push(await page.evaluate(()=>performance.getEntriesByType('navigation')[0].duration));
 }
 await page.evaluate(()=>{window.referenceShifts=[];new PerformanceObserver(list=>window.referenceShifts.push(...list.getEntries().map(e=>({value:e.value,hadRecentInput:e.hadRecentInput})))).observe({type:'layout-shift',buffered:true});});
 for (const mode of ['normal','fault','normal','expired','empty']) {
  await page.getByRole('radio',{name:{normal:'Normal',fault:'Service failure',expired:'Expired session',empty:'Empty'}[mode],exact:true}).check();
  await page.getByRole('button',{name:'Load item'}).click();
  observations.loading.push(await page.getByRole('status').innerText());
  await page.waitForFunction(()=>!document.querySelector('#load').disabled);
  observations.states.push({mode,text:await page.getByRole('status').innerText()});
 }
 const keyboardPage = await browser.newPage();
 await keyboardPage.goto('http://127.0.0.1:8765');
 await keyboardPage.keyboard.press('Tab');
 const selectFocus = await keyboardPage.evaluate(()=>document.activeElement.id);
 await keyboardPage.keyboard.press('Tab');
 const focus = await keyboardPage.evaluate(()=>document.activeElement.id);
 await keyboardPage.keyboard.press('Enter');
 await keyboardPage.waitForFunction(()=>!document.querySelector('#load').disabled);
 observations.keyboard={selectFocus,focus,result:await keyboardPage.getByRole('status').innerText()};
 // Select via actual keyboard in a fresh page; do not set DOM state.
 await keyboardPage.keyboard.press('Shift+Tab');
 await keyboardPage.keyboard.press('ArrowDown');
 await keyboardPage.keyboard.press('Tab');
 await keyboardPage.keyboard.press('Enter');
 await keyboardPage.waitForFunction(()=>!document.querySelector('#load').disabled);
 observations.keyboard_states.push({scenario:await keyboardPage.locator('input[name=scenario]:checked').inputValue(),text:await keyboardPage.getByRole('status').innerText(),focus:await keyboardPage.evaluate(()=>document.activeElement.id)});
 await keyboardPage.keyboard.press('Shift+Tab');
 await keyboardPage.keyboard.press('ArrowUp');
 await keyboardPage.keyboard.press('Tab');
 await keyboardPage.keyboard.press('Enter');
 await keyboardPage.waitForFunction(()=>!document.querySelector('#load').disabled);
 observations.keyboard_states.push({scenario:await keyboardPage.locator('input[name=scenario]:checked').inputValue(),text:await keyboardPage.getByRole('status').innerText(),focus:await keyboardPage.evaluate(()=>document.activeElement.id)});
 observations.focus_colors=await keyboardPage.evaluate(()=>({outline:getComputedStyle(document.querySelector('#load')).outlineColor,background:getComputedStyle(document.body).backgroundColor}));
 await keyboardPage.screenshot({path:path.join(output,'keyboard-focus.png')});
 await keyboardPage.close();
 await page.getByRole('radio',{name:'Normal',exact:true}).check();
 await page.getByRole('button',{name:'Load item'}).click();
 await page.waitForFunction(()=>!document.querySelector('#load').disabled);
 observations.performance=await page.evaluate(()=>({navigation_ms:performance.getEntriesByType('navigation')[0].duration,userAgent:navigator.userAgent}));
 observations.accessibility=(await (await page.context().newCDPSession(page)).send('Accessibility.getFullAXTree')).nodes;
 await page.screenshot({path:path.join(output,'browser.png'),fullPage:true});
 observations.layout_shifts=await page.evaluate(()=>window.referenceShifts);
 observations.resource_entries=await page.evaluate(()=>performance.getEntriesByType('resource').map(e=>({name:e.name,transferSize:e.transferSize,duration:e.duration})));
 observations.colors=await page.evaluate(()=>({foreground:getComputedStyle(document.body).color,background:getComputedStyle(document.body).backgroundColor}));
 await page.setViewportSize({width:375,height:667});
 await page.screenshot({path:path.join(output,'browser-narrow.png'),fullPage:true});
 await page.getByRole('radio',{name:'Service failure',exact:true}).check();
 await page.getByRole('button',{name:'Load item'}).click();
 await page.waitForFunction(()=>!document.querySelector('#load').disabled);
 await page.evaluate(()=>document.body.style.fontSize='36px');
 observations.reflow={method:'actual browser rendering at 375px with body text doubled 18px->36px; controlled text scaling, no desktop zoom claim',text:await page.getByRole('status').innerText(),dimensions:await page.evaluate(()=>({viewport:document.documentElement.clientWidth,scroll:document.documentElement.scrollWidth,font:getComputedStyle(document.body).fontSize}))};
 await page.screenshot({path:path.join(output,'browser-reflow-error.png'),fullPage:true});
 fs.writeFileSync(path.join(output,'browser.json'),JSON.stringify(observations,null,2));
 } finally {
  await browser.close();
 }
})().catch(error => {
 console.error(error);
 process.exitCode = 1;
});

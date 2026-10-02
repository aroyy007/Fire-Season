const {chromium}=require('playwright');
const fs=require('fs');
const path=require('path');
const {pathToFileURL}=require('url');
const root=path.dirname(__dirname);
const qa=name=>path.join(root,'output','qa',name);
(async()=>{
 // Uses Playwright's Chromium (`npx playwright install chromium`); set CHROME_PATH to use an installed Chrome instead.
 const browser=await chromium.launch({headless:true,executablePath:process.env.CHROME_PATH||undefined});
 const page=await browser.newPage({viewport:{width:1440,height:1000}});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 const url=pathToFileURL(path.join(root,'research-report.html')).href;
 await page.goto(url);
 await page.screenshot({path:qa('report-desktop.png')});
 await page.locator('#search').fill('calibration');
 const search_visible_chapters=await page.locator('.chapter:visible').count();
 await page.locator('nav a[href="#prd"]').click();
 const reset_chapters=await page.locator('.chapter:visible').count();
 await page.setViewportSize({width:390,height:844});
 await page.goto(url);
 await page.screenshot({path:qa('report-mobile.png')});
 const mobile_overflow=await page.evaluate(()=>document.documentElement.scrollWidth>window.innerWidth);
 const result={errors,search_visible_chapters,reset_chapters,mobile_overflow};
 fs.writeFileSync(qa('browser-check.json'),JSON.stringify(result,null,2));console.log(result);
 await browser.close();
 if(errors.length||mobile_overflow||reset_chapters!==11)process.exit(1);
})().catch(e=>{console.error(e.message);process.exit(1)});

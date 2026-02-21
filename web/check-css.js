const puppeteer = require('puppeteer');
(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  await page.goto('http://localhost:4321/p/tnews365');
  const styles = await page.evaluate(() => {
    const header = document.querySelector('.detail-header');
    const info = document.querySelector('.header-info');
    const title = document.querySelector('.detail-title');
    return {
      headerW: header?.getBoundingClientRect().width,
      infoW: info?.getBoundingClientRect().width,
      titleW: title?.getBoundingClientRect().width,
      headerFlex: window.getComputedStyle(header).display,
      infoFlex: window.getComputedStyle(info).flex,
      infoMinWidth: window.getComputedStyle(info).minWidth,
      parentW: header?.parentElement.getBoundingClientRect().width
    };
  });
  console.log(JSON.stringify(styles, null, 2));
  await browser.close();
})();

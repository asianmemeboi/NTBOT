from pyppeteer.launcher import launch
import asyncio
import random, json, cloudscraper, jsonpickle, asyncio
with open('scrapers.json') as f:
    data = json.load(f)
scraper = jsonpickle.decode(random.choice(data['scrapers']))
async def get_cookies(username, password):
    args = [
        "--timeout 5",
				'--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-infobars',
        '--window-position=0,0',
        '--ignore-certifcate-errors',
        '--ignore-certifcate-errors-spki-list',
        f'--user-agent="{scraper.headers["User-Agent"]}"'
        ]
    browser = await launch(headless=False, ignoreHTTPSErrors=True, args=args, handleSIGTERM=False, handleSIGINT=False, handleSIGHUP=False)
    pages = await browser.pages()
    page = pages[0]
    await page.setUserAgent(scraper.headers['User-Agent'])
    await page.goto('https://www.nitrotype.com/login')
    '''with open('persist.json') as f:
        data = f.read()'''
    #print(await page.evaluate("() => {localStorage.setItem('persist:nt', %s);}" % (data)))
    with open('preload.js') as f:
        js = f.read()
    await page.evaluateOnNewDocument(js)
    await page.type('#username', username)
    await page.type('#password', password)
    await asyncio.wait([
        page.click('.btn--primary'),
        page.waitForNavigation({'waitUntil': 'domcontentloaded'}),
    ])
    return (await page.cookies())

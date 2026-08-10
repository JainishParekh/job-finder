import os
import asyncio
import hashlib
from dotenv import load_dotenv
from supabase import create_client, Client
from playwright.async_api import async_playwright

# Load environment variables from the root .env file
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing Supabase credentials. Check your root .env file.")

# Initialize Supabase Client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

async def handle_cookie_consent(page):
    """
    Dismisses XING cookie banners if they pop up.
    """
    try:
        # Common cookie accept selectors used on XING
        accept_button = page.locator("button#uc-btn-accept-banner, button[data-testid='uc-accept-all-button']")
        if await accept_button.is_visible(timeout=3000):
            await accept_button.click()
            print("🍪 Clicked cookie consent button.")
    except Exception:
        pass  # Cookie banner didn't appear, continue normally

async def run_scraper():
    print("🚀 Starting XING Scraper...")
    
    # Target XING Search URL for Werkstudent Machine Learning jobs (Last 24 Hours)
    target_url = "https://www.xing.com/jobs/search/ki?id=11b7b0838b0065cf251ae96c99bda6ac&keywords=workstudent%20machine%20learning&sincePeriod=LAST_24_HOURS"

    async with async_playwright() as p:
        # Launch Chromium with low-RAM options
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--disable-gpu",
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--single-process"
            ]
        )
        
        # Spoof standard browser context
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        
        page = await context.new_page()

        # Block images and fonts to preserve RAM and bandwidth
        await page.route("**/*.{png,jpg,jpeg,gif,svg,woff,woff2}", lambda route: route.abort())
        
        print(f"Navigating to XING search feed: {target_url}")
        try:
            await page.goto(target_url, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(3000)  # Wait for dynamic JS rendering
            await handle_cookie_consent(page)
            
            # --- 1. EXTRACT JOB LINKS FROM <ol> -> <li> -> <article> -> <a> ---
            job_links = await page.evaluate('''() => {
                // Target <ol> results list -> <li> -> <article> -> <a>
                const articleAnchors = Array.from(document.querySelectorAll('ol li article a'));
                
                // Fallback selector in case class names vary
                const fallbackAnchors = Array.from(document.querySelectorAll('main#content ol li a'));
                
                const combined = [...articleAnchors, ...fallbackAnchors];
                
                // Extract clean absolute hrefs and filter duplicates
                const links = combined
                    .map(a => a.href)
                    .filter(href => href && href.includes('/jobs/'))
                    .filter((value, index, self) => self.indexOf(value) === index);
                    
                return links;
            }''')
            
            print(f"📋 Found {len(job_links)} potential job links on the feed.")
            
            # --- 2. PROCESS EACH JOB (Limit to 5 for initial testing) ---
            for raw_url in job_links[:5]:
                # Clean URL (remove tracking parameters)
                clean_url = raw_url.split('?')[0]
                
                # Extract a stable unique ID from the end of the URL
                url_slug = clean_url.rstrip('/').split('/')[-1]
                external_id = f"xing_{url_slug}"
                
                # Check Supabase: Has this job already been scraped?
                existing = supabase.table("jobs").select("id").eq("external_job_id", external_id).execute()
                
                if len(existing.data) > 0:
                    print(f"⏭️  Skipping {external_id} - Already in database.")
                    continue
                    
                print(f"🔍 Scraping new XING job: {external_id}")
                
                job_page = await context.new_page()
                await job_page.route("**/*.{png,jpg,jpeg,gif,svg,woff,woff2}", lambda route: route.abort())
                
                try:
                    await job_page.goto(clean_url, wait_until="domcontentloaded", timeout=30000)
                    await job_page.wait_for_timeout(2000)
                    await handle_cookie_consent(job_page)
                    
                    # Extract page title
                    title = await job_page.title()
                    
                    # Extract text content specifically from <main id="content">
                    raw_description = await job_page.evaluate('''() => {
                        const mainContent = document.querySelector('main#content');
                        return mainContent ? mainContent.innerText : document.body.innerText;
                    }''')
                    
                    # --- 3. SAVE RAW DATA TO SUPABASE ---
                    job_data = {
                        "external_job_id": external_id,
                        "platform": "xing",
                        "title": title.strip(),
                        "company": "Pending LLM Extraction",  # LLM will extract exact company name in RAG step
                        "location": "Pending LLM Extraction",
                        "url": clean_url,
                        "raw_description": raw_description[:15000]  # Safe token ceiling for LLM
                    }
                    
                    # Insert into 'jobs' table
                    inserted_job = supabase.table("jobs").insert(job_data).execute()
                    job_uuid = inserted_job.data[0]['id']
                    
                    # Initialize tracking row in 'applications' table
                    app_data = {
                        "job_id": job_uuid,
                        "status": "DISCOVERED"
                    }
                    supabase.table("applications").insert(app_data).execute()
                    
                    print(f"✅ Successfully saved: {title[:50]}...")
                    
                except Exception as e:
                    print(f"❌ Failed to scrape individual job page {clean_url}: {e}")
                finally:
                    await job_page.close()
                    # Delay to prevent rate limiting
                    await asyncio.sleep(2)
                    
        except Exception as e:
            print(f"❌ Main XING search feed failed: {e}")
        finally:
            await browser.close()
            print("🏁 XING scraping session finished.")

if __name__ == "__main__":
    asyncio.run(run_scraper())
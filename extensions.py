from fasthtml.common import A, Grid, Container
from fastcore.xml import *
from datetime import datetime

def A2(*c, **kwargs)->FT:
    '''
    simple wrapper to add some default tailwind classes for our links
    '''
    if 'cls' not in kwargs:
        kwargs['cls'] = " hover:text-blue-400 text-blue-600"
    elif 'cls' in kwargs and not any(cls.startswith('text-') for cls in kwargs['cls'].split()):
        kwargs['cls'] += " hover:text-blue-400 text-blue-600"
    return A(*c, **kwargs)


def display_time(timestr):
    now = datetime.now()
    if timestr:
        try:
            created_date = datetime.strptime(timestr, "%Y-%m-%d %H:%M:%S")
            if created_date.date() >= now.date():
                created_at_str = created_date.strftime("%-I:%M %p")
            else:
                created_at_str = created_date.strftime("%Y-%m-%d")
        except ValueError:
            # Fallback in case the format is different
            created_at_str = timestr
    else:
        created_at_str = 'N/A'
    return created_at_str

    
def page_header(_title, auth, *args): 
  title = _title # title = f"{_title} - {auth['username'] if auth else ''}"

  AHeaderClass = "border-l-2 font-light px-8 inline-flex border-black items-center hover:text-blue-500 text-blue-700"
  top = Div(
          Div(
            Div(
                A2("AINews", href="/", cls="text-[10rem] font-black block -mb-24"),
                # H1(title),
                cls=""
            ),
            cls="flex justify-between w-[640px] m-auto"
          ),
          Div(
            A('home', href='/', cls=AHeaderClass), 
            A('submit', href='/submit', cls=AHeaderClass), 
            A(auth['username'], href='/profile', cls=AHeaderClass) if auth else A2('login', href='/login'),
            cls="flex justify-between h-16 pr-8"
          ),
          cls="flex justify-between bg-[#fff200] mb-16"
        )
  return Title("[AINews] " + title), top, Container(*args)


def scrape_site(url: str):
 # Check if source_url exists
  if url:
      import requests
      import json

      # Send request to scraper
      scraper_url = f"https://scraper.smol.ai/?url={url}&maxChars=-1"
      response = requests.get(scraper_url)
      
      if response.status_code == 200:
          scraped_data = json.loads(response.text)
          
          # Parse the scraped data
          text_content = scraped_data.get("textContent", "")
          meta_object = scraped_data.get("metaObject", {})
          return (scraped_data, text_content, meta_object)
      else:
          scraped_data = None # P("Failed to fetch scraped content.", cls="text-sm text-red-500 mt-4")
  else:
      scraped_data = None

  return scraped_data


__all__ = ['A2', 'display_time', 'page_header', 'scrape_site']


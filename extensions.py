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
            # Try parsing with both formats
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f"): # when submitted from ui it is 2024-08-07T14:56:48.326337, when seeded it is 2024-08-07 14:56:48.326337
                try:
                    created_date = datetime.strptime(timestr, fmt)
                    break
                except ValueError:
                    continue
            else:
                # If no format matches, use the original string
                raise ValueError

            if created_date.date() >= now.date():
                created_at_str = created_date.strftime("%-I:%M %p")
            else:
                created_at_str = created_date.strftime("%Y-%m-%d")
        except ValueError:
            # Fallback in case neither format matches
            created_at_str = timestr
    else:
        created_at_str = 'N/A'
    return created_at_str

def display_submission_url(submission_state, url, type, title, timestr, owner, state):
    created_at = display_time(timestr)
    from urllib.parse import urlparse
    try:
        parsed_url = urlparse(url)
        prefix_type = f"{type.capitalize()}: " if type != "" else ""
        if parsed_url.netloc.startswith('www.'):
            parsed_url = parsed_url._replace(netloc=parsed_url.netloc[4:])
        show = Div(
                  Span(A2(f"Submission State: {submission_state} {prefix_type}{title}", href=url, target="_blank")), 
                  Span(f"{created_at} by {owner} {state})", cls="text-xs text-gray-400"), 
                  cls="flex flex-col"
              ) if parsed_url.netloc == '' else Div(
                  Span(A2(f"Submission State: {submission_state} {prefix_type}{title}", href=url, target="_blank")), 
                  Span(f"({parsed_url.netloc}, {created_at} by {owner} {state})", cls="text-xs text-gray-400"), 
                  cls="flex flex-col"
              )
    except ValueError:
        show = Span(title) if url is None else Span(A2(title, href=url), 'NA')
    return show
    
    
def page_header(_title, auth, *args, wide=False): 
  title = _title # title = f"{_title} - {auth['username'] if auth else ''}"

  AHeaderClass = "border-l-2 font-bold px-8 inline-flex border-black items-center hover:text-blue-500 text-blue-700"

  header_links = []
  header_links.append(A('home', href='/', cls=AHeaderClass))
  header_links.append(A('submit', href='/submit', cls=AHeaderClass))
  header_links.append(A('all', href='/all', cls=AHeaderClass))
  header_links.append(A('feedback', href='/feedback', cls=AHeaderClass))
  if (auth is not None) and (auth.get("roles") is not None) and (auth["roles"].get("role") == "admin"):
      header_links.append(A('admin', href='/admin', cls=AHeaderClass)),
  header_links.append(A(auth['username'], href='/profile', cls=AHeaderClass) if auth else A2('login', href='/login', cls=AHeaderClass))


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
            *header_links,
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


__all__ = ['A2', 'display_time', 'page_header', 'display_submission_url', 'scrape_site']

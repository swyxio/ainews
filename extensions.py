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

def display_url(url, title, timestr, owner):
    created_at = display_time(timestr)
    from urllib.parse import urlparse
    try:
        parsed_url = urlparse(url)
        if parsed_url.netloc.startswith('www.'):
            parsed_url = parsed_url._replace(netloc=parsed_url.netloc[4:])
        show = Div(Span(title), 
                   Span(f"{created_at} by {owner}", cls="text-xs text-gray-400")
              ) if parsed_url.netloc == '' else Div(
                  Span(A2(title, href=url, target="_blank")), 
                  Span(f"({parsed_url.netloc}, {created_at} by {owner})", cls="text-xs text-gray-400"), 
                  cls="flex flex-col"
              )
    except ValueError:
        show = Span(title) if url is None else Span(A2(title, href=url), 'NA')
    return show
    
def page_header(_title, auth, *args): 
  title = _title # title = f"{_title} - {auth['username'] if auth else ''}"

  AHeaderClass = "border-l-2 font-light px-8 inline-flex border-black items-center hover:text-blue-500 text-blue-700"
  top = Div(
          Div(
            Div(
                Span("AINews", cls="text-[10rem] font-black block -mb-24"),
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


__all__ = ['A2', 'display_time', 'display_url', 'page_header']


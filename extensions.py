from fasthtml.common import A, Grid, Container
from fastcore.xml import *
from datetime import datetime

def A2(*c, **kwargs)->FT:
    '''
    simple wrapper to add some default tailwind classes for our links
    '''
    if 'cls' not in kwargs:
        kwargs['cls'] = " hover:text-blue-200 text-blue-400"
    elif 'cls' in kwargs and not any(cls.startswith('text-') for cls in kwargs['cls'].split()):
        kwargs['cls'] += " hover:text-blue-200 text-blue-400"
    return A(*c, **kwargs)


def display_time(timestr):
    now = datetime.now()
    if timestr:
        try:
            created_date = datetime.strptime(timestr, "%Y-%m-%dT%H:%M:%S.%f")
            if created_date.date() == now.date():
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
        show = (Span(title), Span(f"{created_at} by {owner}", cls="text-xs text-gray-400")) if parsed_url.netloc == '' else (Span(A2(title, href=url)), Span(f"({parsed_url.netloc}, {created_at} by {owner})", cls="text-xs text-gray-400"))
    except ValueError:
        show = Span(title) if url is None else Span(A2(title, href=url), 'NA')
    return show
    
def page_header(_title, auth, *args): 
  title = f"{_title} - Welcome {auth['username'] if auth else ''}"
  top = Grid(H1(title), 
              Div(
                  A2('submit', href='/submit'), 
                  '|',
                  A2(auth['username'], href='/profile') if auth else A2('login', href='/login') , 
                  style='text-align: right'))
  return Title(title), Container(top, *args)


__all__ = ['A2', 'display_time', 'display_url', 'page_header']


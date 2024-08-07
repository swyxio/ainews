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

def display_url(url, type, title, timestr, owner, state):
    created_at = display_time(timestr)
    from urllib.parse import urlparse
    try:
        parsed_url = urlparse(url)
        prefix_type = f"{type.capitalize()}: " if type != "" else ""
        if parsed_url.netloc.startswith('www.'):
            parsed_url = parsed_url._replace(netloc=parsed_url.netloc[4:])
        show = Div(
                  Span(A2(f"{prefix_type}{title}", href=url, target="_blank")), 
                  Span(f"({created_at} by {owner} {state})", cls="text-xs text-gray-400"), 
                  cls="flex flex-col"
              ) if parsed_url.netloc == '' else Div(
                  Span(A2(f"{prefix_type}{title}", href=url, target="_blank")), 
                  Span(f"({parsed_url.netloc}, {created_at} by {owner} {state})", cls="text-xs text-gray-400"), 
                  cls="flex flex-col"
              )
    except ValueError:
        show = Span(title) if url is None else Span(A2(title, href=url), 'NA')
    return show

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
    
def page_header(_title, auth, *args): 
  title = f"{_title} - {auth['username'] if auth else ''}"
  top = Grid(H1(title), 
              Div(
                  A2('home', href='/'), 
                  '|',
                  A2('submissions', href='/submissions'), 
                  '|',
                  A2('submit', href='/submit'), 
                  '|',
                  A2(auth['username'], href='/profile') if auth else A2('login', href='/login') , 
                  style='text-align: right'))
  return Title(title), Container(top, *args)


__all__ = ['A2', 'display_time', 'display_url', 'display_submission_url', 'page_header']


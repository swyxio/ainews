
from fasthtml.common import * # type: ignore
from extensions import A2, display_time, page_header, scrape_site
from datetime import datetime
from uuid import uuid4
from hmac import compare_digest
from db_config import setup_db  # Add this import
from admin import setup_admin_routes

# Remove the DB Setup Code block and replace it with:
db, (
        Comment, Tag, TagGroup, TagGroupAssociation, Source, Submission, Feedback, User, Topic, TopicSource, TopicTag, Bookmark, Friend, TopicVote, CommentVote,
        comment, tag, tagGroup, tagGroupAssociation, source, submission, user, topic, topicSource, topicTag, bookmark, friend, topicVote, commentVote, feedback
    ) = setup_db()

# Any Starlette response class can be returned by a FastHTML route handler.
# In that case, FastHTML won't change it at all.
# Status code 303 is a redirect that can change POST to GET, so it's appropriate for a login page.
login_redir = RedirectResponse('/login', status_code=303)

# The `before` function is a *Beforeware* function. These are functions that run before a route handler is called.
def before(req, sess):
    # This sets the `auth` attribute in the request scope, and gets it from the session.
    # The session is a Starlette session, which is a dict-like object which is cryptographically signed,
    # so it can't be tampered with.

    # The `auth` key in the scope is automatically provided to any handler which requests it, and can not
    # be injected by the user using query params, cookies, etc, so it should be secure to use.
    # print('sessget', sess.get('auth', None))
    # print('reqsget', req.scope)
    auth = req.scope['auth'] = sess.get('auth', None)
    # If the session key is not there, it redirects to the login page.
    private_routes = ['/profile', '/submit']
    post_allow_routes = ['/feedbackLink']
    print('cookie_req_auth', auth)

    if auth is not None:
        user_id = auth.get('user_id', None)
        if user_id is not None:
            # Query for username from auth. todo: refactor to put in beforeware
            try:
                print('user_id', auth['user_id'])
                auth = next(db.query("SELECT * FROM user WHERE user_id = ?", [user_id]), None)
                if auth is not None:
                    roles = next(db.query("SELECT * FROM user_roles WHERE user_id = ?", [user_id]), None)
                    if roles is not None:
                        auth['roles'] = roles
                    else:
                        auth['roles'] = None

            except Exception as e:
                auth = None
    
    print('auth_post_before', auth)
    print('req.method', req.method)
    print('req.url.path', req.url.path)
    if not auth and (req.url.path in private_routes): return login_redir
    if not auth and ((req.method != 'GET') and (req.url.path not in post_allow_routes)): return login_redir
    # # `xtra` is part of the MiniDataAPI spec. It adds a filter to queries and DDL statements,
    # # to ensure that the user can only see/edit their own todos.
    # swyx: commented out because want to see global posts
    # posts.xtra(name=auth)

markdown_js = """
import { marked } from "https://cdn.jsdelivr.net/npm/marked/lib/marked.esm.js";
import { proc_htmx} from "https://cdn.jsdelivr.net/gh/answerdotai/fasthtml-js/fasthtml.js";
proc_htmx('.markdown', e => e.innerHTML = marked.parse(e.textContent));
"""

# To create a Beforeware object, we pass the function itself, and optionally a list of regexes to skip.
bware = Beforeware(before, skip=[r'/favicon\.ico', r'/static/.*', r'.*\.css', '/login'])
# The `FastHTML` class is a subclass of `Starlette`, so you can use any parameters that `Starlette` accepts.
# In addition, you can add your Beforeware here, and any headers you want included in HTML responses.
# FastHTML includes the "HTMX" and "Surreal" libraries in headers, unless you pass `default_hdrs=False`.
app, rt = fast_app(
              #  live=os.getenv('DEV') == 'true', # https://docs.fastht.ml/ref/live_reload.html
               before=bware,
               debug=True,
               # PicoCSS is a particularly simple CSS framework, with some basic integration built in to FastHTML.
               # `picolink` is pre-defined with the header for the PicoCSS stylesheet.
               # You can use any CSS framework you want, or none at all.
               pico=False,
               hdrs=(
                     MarkdownJS(),
                  #  picolink,
                     Link(rel='preconnect', href='https://rsms.me/'),
                     Script(src="https://unpkg.com/x-frame-bypass", type="module"),
                     Script(src="https://cdn.tailwindcss.com"), # SWYX TODO: proper deployment of tailwind
                     Link(rel='stylesheet', href='https://rsms.me/inter/inter.css', type='text/css'),
                    #  #  https://picocss.com/docs/conditional
                    #  Link(rel='stylesheet', href='https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.conditional.min.css', type='text/css'),
                     # `Style` is an `FT` object, which are 3-element lists consisting of:
                     # (tag_name, children_list, attrs_dict).
                     # FastHTML composes them from trees and auto-converts them to HTML when needed.
                     # You can also use plain HTML strings in handlers and headers,
                     # which will be auto-escaped, unless you use `NotStr(...string...)`.
                     Style("""
                           :root {
                            font-size: 8pt;
                            font-family: Inter, Verdana, Geneva, sans-serif;
                            font-feature-settings: 'liga' 1, 'calt' 1; /* fix for Chrome */
                           }
                            @supports (font-variation-settings: normal) {
                              :root { font-family: InterVariable, sans-serif; }
                            }
                           .container {
                            margin: 0 auto;
                           }
  .unreset a {
    color: #1d4ed8;
    text-decoration: underline;
  }
  .unreset p {
    margin-top: 1rem;
    margin-bottom: 1rem;
  }

  .unreset blockquote,
  figure {
    margin-top: 1rem;
    margin-bottom: 1rem;
    margin-left: 2.5rem;
    margin-right: 2.5rem;
  }

  .unreset hr {
    border-width: 1px;
  }

  .unreset h1 {
    font-size: 2.25rem;
    font-weight: bold;
    margin-top: 0.5rem;
    margin-bottom: 0.5rem;
  }

  .unreset h2 {
    font-size: 1.5rem;
    font-weight: bold;
    margin-top: 0.75rem;
    margin-bottom: 0.75rem;
  }

  .unreset h3 {
    font-size: 1.125rem;
    font-weight: bold;
    margin-top: 1rem;
    margin-bottom: 1rem;
  }

  .unreset h4 {
    font-size: 1rem;
    font-weight: bold;
    margin-top: 1.25rem;
    margin-bottom: 1.25rem;
  }

  .unreset h5 {
    font-size: 0.875rem;
    font-weight: bold;
    margin-top: 1.5rem;
    margin-bottom: 1.5rem;
  }

  .unreset h6 {
    font-size: 0.75rem;
    font-weight: bold;
    margin-top: 2.5rem;
    margin-bottom: 2.5rem;
  }

  .unreset ul,
  menu {
    list-style-type: disc;
    margin-top: 0.25rem;
    margin-bottom: 0.25rem;
    padding-left: 2.5rem;
  }

  .unreset ol {
    list-style-type: decimal;
    margin-top: 1rem;
    margin-bottom: 1rem;
    padding-left: 2.5rem;
  }

  .unreset ul,
  ol {
    .unreset ul {
      list-style-type: circle;
    }

    .unreset ul,
    ol {
      .unreset ul {
        list-style-type: square;
      }
    }
  }

  .unreset dd {
    padding-left: 2.5rem;
  }

  .unreset dl {
    margin-top: 1rem;
    margin-bottom: 1rem;
  }

  .unreset ul,
  ol,
  menu,
  dl {
    ul,
    ol,
    menu,
    .unreset dl {
      margin: 0;
    }
  }

  b, strong {
    font-weight: bold;
  }

  .unreset pre {
    margin-top: 1rem;
    margin-bottom: 1rem;
  }
}
                           """),
                     # Have a look at fasthtml/js.py to see how these Javascript libraries are added to FastHTML.
                     # They are only 5-10 lines of code each, and you can add your own too.
                    #  SortableJS('.sortable'), # commented out bc not needed
                     # MarkdownJS is actually provided as part of FastHTML, but we've included the js code here
                     # so that you can see how it works.
                     Script(markdown_js, type='module'))
                )
# # We add `rt` as a shortcut for `app.route`, which is what we'll use to decorate our route handlers.
# # When using `app.route` (or this shortcut), the only required argument is the path.
# # The name of the decorated function (eg `get`, `post`, etc) is used as the HTTP verb for the handler.
# swyx: no longer needed since we switched from `FastHTMLWithLiveReload` to `fast_app`

# For instance, this function handles GET requests to the `/login` path.
@app.get("/login")
def loginroute(auth):
    # This creates a form with two input fields, and a submit button.
    # All of these components are `FT` objects. All HTML tags are provided in this form by FastHTML.
    # If you want other custom tags (e.g. `MyTag`), they can be auto-generated by e.g
    # `from fasthtml.components import MyTag`.
    # Alternatively, manually call e.g `ft(tag_name, *children, **attrs)`.
    modal = Div('You are already logged in as ' + auth['username'], cls="text-center text-lg font-semibold mb-4") if auth else None

    frm = Form(
        Div(
            Input(id='username', placeholder='Your @username here. Can change later', cls="w-full p-3 mb-4 border rounded"),
            Input(id='password', type='password', placeholder='Password', cls="w-full p-3 mb-4 border rounded"),
            Button('Login / Signup', cls="w-full bg-blue-500 hover:bg-blue-600 text-white font-bold py-3 px-4 rounded"),
            cls="space-y-4"
        ),
        action='/login', method='post',
        cls="mt-[15rem] max-w-md mx-auto bg-white p-8 border rounded-lg shadow-md")
    # If a user visits the URL directly, FastHTML auto-generates a full HTML page.
    # However, if the URL is accessed by HTMX, then one HTML partial is created for each element of the tuple.
    # To avoid this auto-generation of a full page, return a `HTML` object, or a Starlette `Response`.
    # `Titled` returns a tuple of a `Title` with the first arg and a `Container` with the rest.
    # See the comments for `Title` later for details.
    return page_header("Login", modal, frm)

# Handlers are passed whatever information they "request" in the URL, as keyword arguments.
# Dataclasses, dicts, namedtuples, TypedDicts, and custom classes are automatically instantiated
# from form data.
# In this case, the `Login` class is a dataclass, so the handler will be passed `username` and `password`.
@dataclass
class Login: username:str; password:str

# This handler is called when a POST request is made to the `/login` path.
# The `login` argument is an instance of the `Login` class, which has been auto-instantiated from the form data.
# There are a number of special parameter names, which will be passed useful information about the request:
# `session`: the Starlette session; `request`: the Starlette request; `auth`: the value of `scope['auth']`,
# `htmx`: the HTMX headers, if any; `app`: the FastHTML app object.
# You can also pass any string prefix of `request` or `session`.
@app.post("/login")
def loginEndpoint(login:Login, sess):
    if not login.username or not login.password: return login_redir
    try:
        u = next(db.query("select * from user where username = ?", [login.username]), None)
    except StopIteration:
        # import bcrypt
        if u is not None:
            u = user.insert({
                "user_id": uuid4(),
                "username" : login.username,
                "password" : login.password,
                "markdown_bio": f"Default bio for {login.username}"
            })

    if u is not None:
        roles_query = db.query("SELECT * FROM user_roles WHERE user_id = ?", [u['user_id']])
        roles = next(roles_query, None)
        if roles is not None:
            u['roles'] = roles
        else:
            u['roles'] = None


    u = dict2obj(u)

        # return RedirectResponse('/signup', status_code=303)  # Or handle as appropriate

    print(f"User object type: {type(u)}")
    print(f"User object contents: {u}")

    try:
        print(f"Password is attribute:{u.password}")
        stored_password = u.password
    except:
        print(f"Password is dict:{u['password']}")
        stored_password = u['password']

    if not compare_digest(stored_password, login.password):
        print('comapre ' + stored_password + ' and ' + login.password)
        return login_redir

    # Determine how to access the user_id field
    user_id = u.user_id

    print('logging you in ' + user_id)
    sess['auth'] = obj2dict(u)
    print('sess', sess)
    return RedirectResponse('/', status_code=303)

# Instead of using `app.route` (or the `rt` shortcut), you can also use `app.get`, `app.post`, etc.
# In this case, the function name is not used to determine the HTTP verb.
@app.get("/profile")
def profile(auth):
    # Check if user is authenticated
    if not auth:
        return RedirectResponse('/login', status_code=303)

    # Create a list of user fields
    user_fields = [
        Div(
            Span(f"user_id: ", cls="font-bold"), Span(str(auth['user_id'])),
            cls="mb-2"
        ),
        Div(
            Span(f"created_at: ", cls="font-bold"), Span(str(auth['created_at'])),
            cls="mb-2"
        ),
        Div(
            Span(f"username: ", cls="font-bold"), Input(name="username", value=str(auth['username'])),
            cls="mb-2"
        ),
        # Div(
        #     Span(f"password: ", cls="font-bold"), Input(name="password", type="password", placeholder="new password"),
        #     cls="mb-2"
        # ),
        Div(
            Span(f"email: ", cls="font-bold"), Input(name="email", type="email", value=str(auth['email'])),
            cls="mb-2"
        ),
        Div(
            Span(f"markdown_bio: ", cls="font-bold"),
            Textarea(str(auth['markdown_bio']), id="markdown_bio", name="markdown_bio", rows=5, cls="w-full p-2 border rounded"),
            cls="mb-2"
        ),
    ]
    # Add a logout button to the profile content
    logout_button = Form(
        Button("Update Profile (currently doesnt work yet)", type="submit", cls="mt-4 text-white font-bold py-2 px-4 rounded"),
        Button("Logout", hx_post="/logout", hx_target="body", cls="mt-4 bg-red-500 hover:bg-red-600 text-white font-bold py-2 px-4 rounded"),
        action="/updateProfile",
        method="post",
        cls="mt-4"
    )
    # Wrap user fields in a container
    profile_content = Div(
        H2("User Profile", cls="text-2xl mb-4"),
        *user_fields,
        logout_button,
        cls="p-4 rounded-lg"
    )

    return page_header(
        "User Profile",
        auth,
        profile_content
    )

# Instead of using `app.route` (or the `rt` shortcut), you can also use `app.get`, `app.post`, etc.
# In this case, the function name is not used to determine the HTTP verb.
@app.post("/logout")
def logout(sess):
    del sess['auth']
    return login_redir
@app.get("/logout")
def logout(sess):
    del sess['auth']
    return login_redir

# FastHTML uses Starlette's path syntax, and adds a `static` type which matches standard static file extensions.
# You can define your own regex path specifiers -- for instance this is how `static` is defined in FastHTML
# `reg_re_param("static", "ico|gif|jpg|jpeg|webm|css|js|woff|png|svg|mp4|webp|ttf|otf|eot|woff2|txt|xml|html")`
# In this app, we only actually have one static file, which is `favicon.ico`. But it would also be needed if
# we were referencing images, CSS/JS files, etc.
# Note, this function is unnecessary, as the `fast_app()` call already includes this functionality.
# However, it's included here to show how you can define your own static file handler.
@rt("/{fname:path}.{ext:static}")
async def get(fname:str, ext:str): return FileResponse(f'/static/{fname}.{ext}')
# swyx note - this doesnt quite work yet - http://0.0.0.0:5001/favicon.ico returns 404 - we will fix later


# deopted from __ft__ in https://github.com/swyxio/ainews/pull/3/files
def renderTopic(self):
    # rank = Span(A2(str(self["rank"] or 0), href=f'/p/{self["topic_id"]}'))


    def display_topic_url(url, type, title, timestr, owner, state):
      created_at = display_time(timestr)
      from urllib.parse import urlparse
      try:
          parsed_url = urlparse(url)
          if parsed_url.netloc.startswith('www.'):
              parsed_url = parsed_url._replace(netloc=parsed_url.netloc[4:])
          parsed_domain = parsed_url.netloc
          show = Div(
                    # Div(
                    #     Img(src=meta_object.get('image', ''),
                    #         alt="Article image",
                    #         cls="w-16 h-16 object-cover mr-2 float-left"
                    #     ) if scraped_data and meta_object.get('image') else None,
                    #     cls="flex-shrink-0"
                    # ),
                    Div(Span(type, cls="bg-blue-100 p-1 border border-blue-800 rounded"), Span(parsed_domain, cls="italic text-thin"), cls="mb-2"),
                    Span(A2(title, href=f'/p/{self["topic_id"]}', cls="font-bold text-2xl")),
                    Span(f"({created_at} by {owner})", cls="text-xs text-white group-hover:text-gray-600"),
                    cls="flex flex-col"
                )
      except ValueError:
          show = Span(title) if url is None else Span(A2(title, href=url), 'NA')
      return show

    # cts = Div(Div(rank, cls="w-12 text-right"), Div(show, Hidden(id="id", value=self['topic_id'])), cls="flex gap-4")

    cts = Div(
        # Div(
        #     Span(A2(str(self["rank"] or 0), href=f'/p/{self["topic_id"]}')),
        #     cls="w-12 text-right"
        # ),
        show,
        Div(
            display_topic_url(self["source_url"], self["type"],self["source_title"], self["created_at"], self["username"], self["state"]),
            Hidden(id="id", value=self['topic_id']),
        ),
        cls="flex gap-4 group"
        )
    # Any FT object can take a list of children as positional args, and a dict of attrs as keyword args.
    return Li(Form(cts), id=f'post-{self["topic_id"]}', cls='list-none')
def renderSubmission(self):
    def display_submission_url(submission_state, url, type, title, timestr, owner, state):
        created_at = display_time(timestr)
        from urllib.parse import urlparse
        try:
            parsed_url = urlparse(url)
            prefix_type = f"{type.capitalize()}: " if type != "" else ""
            if parsed_url.netloc.startswith('www.'):
                parsed_url = parsed_url._replace(netloc=parsed_url.netloc[4:])
            parsed_domain = parsed_url if isinstance(parsed_url, str) else parsed_url.netloc if parsed_url.netloc else 'N/A'
            show = Div(
                      Span(
                        Span(
                            Button("⬆️", hx_post=f"/vote_topic/{self['topic_id']}?vote_type=1", hx_target=f"#score-{self['topic_id']}", hx_swap="outerHTML"),
                            Span(self["vote_score"] if self["vote_score"] else 0, id=f"score-{self['topic_id']}", cls="w-2"),
                            Button("⬇️", hx_post=f"/vote_topic/{self['topic_id']}?vote_type=-1", hx_target=f"#score-{self['topic_id']}", hx_swap="outerHTML"),
                            cls="inline-flex items-center space-x-2"
                        ),
                        Span(
                            self["submission_state"],
                            cls="bg-gray-100 text-gray-800 px-2 py-1 rounded-md border border-gray-300 text-sm mr-2 mb-2"
                        ),
                        A2(f"{prefix_type}{title}", href=url, target="_blank")
                      ),
                      Span(f"({parsed_url.netloc}, {created_at} by {owner} {state})", cls="text-xs text-gray-400"),
                      cls="flex flex-col mb-2"
                  )
        except ValueError:
            show = Span(title) if url is None else Span(A2(title, href=url), 'NA')
        return show

    show = display_submission_url(self["submission_state"], self["source_url"], self["type"],self["source_title"], self["created_at"], self["username"], self["state"])
    # isRead = '✅ ' if self["read"] else '🔲 '

    # (scraped_data, text_content, meta_object) = scrape_site(self["source_url"])
#

    cts = Div(
        # Div(
        #     Span(A2(str(self["rank"] or 0), href=f'/p/{self["topic_id"]}')),
        #     cls="w-12 text-right"
        # ),
        show,
        )
    # Any FT object can take a list of children as positional args, and a dict of attrs as keyword args.
    return Li(Form(cts), id=f'post-{self["topic_id"]}', cls='list-none')


@app.post("/vote_topic/{topic_id}")
async def vote_topic(auth, topic_id: str, vote_type: int):
    if not auth:
        raise HTTPException(status_code=401, detail="Authentication required")

    user_id = auth['user_id']
    # Check if the user's OWN aggregate vote would exceed +5 or -5
    current_vote_sum = db.q(f"""
        SELECT SUM(CASE WHEN vote_type = 1 THEN 1 WHEN vote_type = -1 THEN -1 ELSE 0 END) as vote_sum
        FROM {topicVote}
        WHERE topic_id = ? AND user_id = ?
    """, [topic_id, user_id])

    current_sum = current_vote_sum[0]['vote_sum'] or 0
    new_sum = current_sum + vote_type
    print('new_sum', new_sum)
    if new_sum > 5 or new_sum < -5:
        raise HTTPException(status_code=400, detail="Your vote would exceed the allowed range of +5 to -5 for this topic")

    # Insert the new vote
    topicVote.insert({
        'topic_id': topic_id,
        'user_id': user_id,
        'vote_type': vote_type,  # Use the vote_type from the query parameter
        'created_at': datetime.now().isoformat()
    })

    # Calculate and return the new score ACROSS ALL PEOPLE
    new_score = db.q(f"""
        SELECT SUM(CASE WHEN vote_type = 1 THEN 1 WHEN vote_type = -1 THEN -1 ELSE 0 END) as vote_score
        FROM {topicVote}
        WHERE topic_id = ?
    """, [topic_id])

    # return {"new_score": new_score[0]['vote_score']}
    return Span(new_score[0]['vote_score'], id=f"score-{topic_id}", cls="w-2")


# This is the handler for the main todo list application.
# By including the `auth` parameter, it gets passed the current username, for displaying in the title.
# @rt("/")
# def get(auth):
@app.get("/")
def home(auth):
    # We don't normally need separate "screens" for adding or editing data. Here for instance,
    # we're using an `hx-post` to add a new todo, which is added to the start of the list (using 'afterbegin').
    # new_inp = Input(id="new-title", name="title", placeholder="New Post")
    # new_url = Input(id="new-url", name="url", placeholder="Post URL (optional)")
    # add = Form(Group(new_inp, new_url, Button("Submit New Post")),
    #            hx_post="/", target_id='posts-list', hx_swap="afterbegin")
    # In the MiniDataAPI spec, treating a table as a callable (i.e with `todos(...)` here) queries the table.
    # Because we called `xtra` in our Beforeware, this queries the todos for the current user only.
    # We can include the todo objects directly as children of the `Form`, because the `Todo` class has `__ft__` defined.
    # This is automatically called by FastHTML to convert the `Todo` objects into `FT` objects when needed.
    # The reason we put the todo list inside a form is so that we can use the 'sortable' js library to reorder them.
    # That library calls the js `end` event when dragging is complete, so our trigger here causes our `/upvote`
    # handler to be called.


    # data = str(db.q(f"SELECT * FROM {post}"))

    # output = Div(data)
    # frm = Form(*posts(order_by='rank'),
    #            id='posts-list', cls='sortable', hx_post="/upvote", hx_trigger="end")

    # for access on / page
    topicsview = f"""select {topic}.*,
    url as source_url, {source}.title as source_title, {source}.description as source_description,
    username
    from {topic} join {source} on {topic}.primary_source_id = {source}.source_id
    join {user} on {topic}.user_id={user}.user_id
    where {topic}.state = 'top' limit 11
    """
    db.create_view("TopicsView", topicsview, replace=True)

    # tps = db.q(f"select * from {topic}")
    # print('tps')
    # print('tps')
    # import json
    # print(json.dumps(tps, indent=2))
    # print('tps')
    # print('tps')

    topicsViewLimit = db.q(f"select * from {db.v.TopicsView}")
    # print('topicsViewLimit')
    # print('topicsViewLimit')
    # import json
    # print(json.dumps(topicsViewLimit, indent=2))
    # print('topicsViewLimit')
    # print('topicsViewLimit')

    frm = Ul(*[renderTopic(x) for x in topicsViewLimit[0:]],
             cls= "grid grid-cols-2 gap-4 max-w-[640px] mx-auto " +
                 " ".join(map(lambda x: f"[&>*:first-child]:{x}", "col-span-2 flex justify-center text-4xl borderb-b-2".split()
                 ))

             )
            #  cls="flex flex-col justify-center items-start gap-4 max-w-[640px] m-auto"
              #  id='posts-list', cls='sortable', hx_post="/upvote", hx_trigger="end")
    # We create an empty 'current-post' Div at the bottom of our page, as a target for the details and editing views.
    card = Card(frm, header=Div(
        # SWYX todo: convert to buttons as filters in future?
        Span('Ask', cls="text-blue-900 mr-2"),
        Span('Show', cls="text-blue-900 mr-2"),
        Span('and', cls="mr-2"),
        Span('Tell', cls="text-blue-900 mr-2"),
        "everything in AI",
        Span(" (", A2("why?", href="/blog/why-private"), Span(")")),
        cls="font-medium text-2xl flex mb-16"
    ), footer=Div(id='current-post'))
    # PicoCSS uses `<Main class='container'>` page content; `Container` is a tiny function that generates that.
    # A handler can return either a single `FT` object or string, or a tuple of them.
    # In the case of a tuple, the stringified objects are concatenated and returned to the browser.
    # The `Title` tag has a special purpose: it sets the title of the page.

    return page_header("AI News Home",auth, card)



@app.get("/all")
def allSubmissions(auth, by_votes: str = None):
    # We don't normally need separate "screens" for adding or editing data. Here for instance,
    # we're using an `hx-post` to add a new todo, which is added to the start of the list (using 'afterbegin').
    # new_inp = Input(id="new-title", name="title", placeholder="New Post")
    # new_url = Input(id="new-url", name="url", placeholder="Post URL (optional)")
    # add = Form(Group(new_inp, new_url, Button("Submit New Post")),
    #            hx_post="/", target_id='posts-list', hx_swap="afterbegin")
    # In the MiniDataAPI spec, treating a table as a callable (i.e with `todos(...)` here) queries the table.
    # Because we called `xtra` in our Beforeware, this queries the todos for the current user only.
    # We can include the todo objects directly as children of the `Form`, because the `Todo` class has `__ft__` defined.
    # This is automatically called by FastHTML to convert the `Todo` objects into `FT` objects when needed.
    # The reason we put the todo list inside a form is so that we can use the 'sortable' js library to reorder them.
    # That library calls the js `end` event when dragging is complete, so our trigger here causes our `/upvote`
    # handler to be called.


    # data = str(db.q(f"SELECT * FROM {post}"))

    # output = Div(data)
    # frm = Form(*posts(order_by='rank'),
    #            id='posts-list', cls='sortable', hx_post="/upvote", hx_trigger="end")

    # for access on / page
    submissionsview = f"""select {topic}.*,
    url as source_url, {source}.title as source_title, {source}.description as source_description, {submission}.state as submission_state,
    username
    from {topic} join {source} on {topic}.primary_source_id = {source}.source_id join {submission} on {submission}.source_id={source}.source_id
    join {user} on {topic}.user_id={user}.user_id
    order by {topic}.created_at desc
    """
    db.create_view("SubmissionsView", submissionsview, replace=True)

    # tps = db.q(f"select * from {topic}")
    # print('tps')
    # print('tps')
    # import json
    # print(json.dumps(tps, indent=2))
    # print('tps')
    # print('tps')

    submissionsViewLimit = db.q(f"select * from {db.v.SubmissionsView} limit 50")

    # Query to get vote scores for each topic
    vote_scores = db.q(f"""
        SELECT topic_id, SUM(CASE WHEN vote_type = 1 THEN 1 WHEN vote_type = -1 THEN -1 ELSE 0 END) as vote_score
        FROM {topicVote}
        WHERE topic_id IN ({','.join(['?'] * len(submissionsViewLimit))})
        GROUP BY topic_id
    """, [_submission['topic_id'] for _submission in submissionsViewLimit])

    # Convert vote_scores to a dictionary for easy lookup
    vote_score_dict = {score['topic_id']: score['vote_score'] for score in vote_scores}
    print('vote_score_dict', vote_score_dict)

    # Add vote_score to each submission in submissionsViewLimit
    for _submission in submissionsViewLimit:
        _submission['vote_score'] = vote_score_dict.get(_submission['topic_id'], 0)

    sort_by = 'By Date'
    target = '/all?by_votes=true'
    if by_votes == 'true':
        sort_by = 'By Votes'
        target = '/all'
        # Sort submissionsViewLimit by vote_score in descending order
        submissionsViewLimit = sorted(submissionsViewLimit, key=lambda x: x['vote_score'], reverse=True)

    frm = Ul(*[renderSubmission(x) for x in submissionsViewLimit])
              #  id='posts-list', cls='sortable', hx_post="/upvote", hx_trigger="end")
    # We create an empty 'current-post' Div at the bottom of our page, as a target for the details and editing views.

    header_div = Div(Span(f'Recent Submissions ', A(sort_by, href=target, cls="text-blue-600 hover:underline"), ' (you can personally up/downvote max of +/- 5 votes)'))
    card = Card(frm, header=header_div, footer=Div(id='current-post'))
    # PicoCSS uses `<Main class='container'>` page content; `Container` is a tiny function that generates that.
    # A handler can return either a single `FT` object or string, or a tuple of them.
    # In the case of a tuple, the stringified objects are concatenated and returned to the browser.
    # The `Title` tag has a special purpose: it sets the title of the page.

    return page_header("AI News Submissions",auth, card)

# swyx: submit page
@app.get("/submit")
def get(auth):
    new_type = Select(
        Option("Ask", value="ask", selected=True),
        Option("Show", value="show"),
        Option("Tell", value="tell"),
        cls="w-full p-2 mb-4 border rounded shadow-sm",
        id="_verb"
    )

    new_inp = Input(id="new-title", name="title", placeholder="Item Title", cls="w-full p-2 mb-4 border rounded shadow-sm")
    new_url = Input(id="new-url", name="url", placeholder="Item URL (optional)", cls="w-full p-2 mb-4 border rounded shadow-sm")
    new_verb = Input(id="verb", name="verb", placeholder="Submission Verb", cls="w-full p-2 mb-4 border rounded shadow-sm")
    description = Textarea(id="description", name="description", placeholder="Description (Markdown supported)",
                           rows="5",
                          #  hx_post="/preview",
                           hx_trigger="keyup changed delay:500ms",
                           hx_target="#live-preview",
                           cls="w-full p-2 mb-4 border rounded shadow-sm h-32")

    add = Form(
        Div(
            new_type,
            new_inp,
            new_url,
            description,
            Div(
                id="live-preview",
                cls="mt-4 p-4 border rounded shadow-sm marked",
            ),
            Button("Submit New Link or Story", cls="w-full bg-blue-500 hover:bg-blue-600 text-white font-bold py-3 px-4 rounded shadow"),
            cls="space-y-4"
        ),
        action="/submitLink",
        method='post',
        cls="max-w-2xl mx-auto bg-white p-8 rounded-lg shadow-md"
    )

    card = Card(
        add,
        header=Div(
            'Submit New Item for Consideration',
            P(
                Ul(
                    Li("Ask: For questions or seeking advice from the community"),
                    Li("Show: To showcase your projects, products, or achievements"),
                    Li("Tell: To share interesting information or stories"),
                    cls="list-disc pl-5 text-sm text-gray-600 mb-4 flex flex-col max-w-[300px] mx-auto text-left"
                ),
               Span("AIN is manually curated. These submissions and votes only go to the /all page and we update /all ~once a day.",
                    cls="text-sm"),
                cls="mt-2"
            ),
            id='header', cls="text-2xl font-bold mb-6 text-center"),
        footer=Div(id='current-post'),
        cls="bg-gray-100 p-8 rounded-lg shadow-lg"
    )

    return page_header("Submit AI News", auth, card)


@app.post("/submitLink")
async def submitLink(auth, title:str, url:str, description:str, _verb:str):
    print('title', title)
    print('url', url)
    print('description', description)
    print('verb', _verb)

    sourceDC = None
    source_id = None
    if url is not None:
        sourceDC = Source(title=title, url=url, description=description, source_type='article', user_id=auth['user_id'])
        source_id = uuid4()
        sourceDC.source_id = source_id
        sourceDC.created_at = datetime.now().isoformat()

    submissionDC = Submission(
        source_id=source_id if sourceDC else None,
        user_id=auth['user_id'],
        type=_verb,
        title=title,
        description=description,
        state="submission"
    )
    submissionDC.submission_id = uuid4()
    submissionDC.created_at = datetime.now().isoformat()

    topicDC = Topic(
        topic_id=uuid4(),
        title=title,
        type=_verb,
        state="submission",
        user_id=auth['user_id'],
        submission_id=submissionDC.submission_id,
        primary_source_id=source_id if sourceDC else None,
        description=description,
        created_at=datetime.now().isoformat()
    )

    try:
        if source:
            source.insert(sourceDC)
        submission.insert(submissionDC)
        topic.insert(topicDC)
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return RedirectResponse('/all', status_code=303)

    return RedirectResponse('/all', status_code=303)
    
    # _source.created_at = datetime.now().isoformat()
    # _source.source_id = uuid4()
    # _source.source_type = 'article'
    # print('_source', _source)
    # try:
    #   _source = source.insert(_source)
    # except Exception as e:
    #     # SWYX TODO: if its a sqlite3.IntegrityError then its a double post
    #     # we dont know how to return a nice error here
    #     print(f"Error occurred: {str(e)}")
    #     return RedirectResponse('/all', status_code=303)

    # # For Now Lets Use the Same Submission States as Topic States
    # # valid_topic_states = ["submission", "top", "archived", "hidden"]
    # submission.insert({
    #     "source_id": _source.source_id,
    #     "user_id": auth['user_id'],
    #     "type": _verb,
    #     "state": "submission"
    # })

    # import random
    # result = topic.insert({
    #     "topic_id": uuid4(),
    #     "title": _source.title,
    #     "type": _verb,
    #     "state": "submission",
    #     "user_id": auth['user_id'],
    #     "primary_source_id": _source.source_id,
    #     "description": _source.description,
    #     "rank": random.randint(0, 500), # # just for demo purposes, comment out in future
    #     "created_at": _source.created_at
    # })
    # print('result', result)

    # return allSubmissions(auth)

@app.post("/feedbackLink")
async def feedbackLink(auth, _feedback:Feedback):
    _feedback.created_at = datetime.now().isoformat()
    _feedback.feedback_id = uuid4()
    print('_feedback', _feedback)
    try:
      _feedback = feedback.insert(_feedback)
    except Exception as e:
        # SWYX TODO: if its a sqlite3.IntegrityError then its a double post
        # we dont know how to return a nice error here
        print(f"Error occurred: {str(e)}")
        return RedirectResponse('/all', status_code=303)
    return feedbackThanks(auth)

@app.get("/feedbackThanks")
def feedbackThanks(auth):
    card = Card(
        header=Div(
            'Thank you for your feedback!',
            id='header', cls="text-2xl font-bold mb-6 text-center"),
        footer=Div(id='current-post'),
        cls="bg-gray-100 p-8 rounded-lg shadow-lg"
    )

    return page_header("AI News Feedback", auth, card)

@app.get("/feedback")
def get(auth):
    new_type = Select(
        Option("Feature", value="Feature", selected=True),
        Option("Bug", value="Bug"),
        Option("General", value="General"),
        cls="w-full p-2 mb-4 border rounded shadow-sm",
        id="type"
    )

    new_title = Input(id="new-title", name="title", placeholder="Title", cls="w-full p-2 mb-4 border rounded shadow-sm")
    new_email = Input(id="new-email", name="email", placeholder="Email", cls="w-full p-2 mb-4 border rounded shadow-sm")
    description = Textarea(id="description", name="description", placeholder="Description (Markdown supported)",
                           rows="5",
                          #  hx_post="/preview",
                           hx_trigger="keyup changed delay:500ms",
                           hx_target="#live-preview",
                           cls="w-full p-2 mb-4 border rounded shadow-sm h-32")

    add = Form(
        Div(
            new_type,
            new_title,
            new_email,
            description,
            Div(
                id="live-preview",
                cls="mt-4 p-4 border rounded shadow-sm markdown",
            ),
            Button("Submit Feedback", cls="w-full bg-blue-500 hover:bg-blue-600 text-white font-bold py-3 px-4 rounded shadow"),
            cls="space-y-4"
        ),
        action="/feedbackLink",
        method='post',
        cls="max-w-2xl mx-auto bg-white p-8 rounded-lg shadow-md"
    )

    card = Card(
        add,
        header=Div(
            'Submit Feedback for Consideration',
            id='header', cls="text-2xl font-bold mb-6 text-center"),
        footer=Div(id='current-post'),
        cls="bg-gray-100 p-8 rounded-lg shadow-lg"
    )

    return page_header("AI News Feedback", auth, card)

# # This is the handler for the reordering of todos.
# # It's a POST request, which is used by the 'sortable' js library.
# # Because the todo list form created earlier included hidden inputs with the todo IDs,
# # they are passed as form data. By using a parameter called (e.g) "id", FastHTML will try to find
# # something suitable in the request with this name. In order, it searches as follows:
# # path; query; cookies; headers; session keys; form data.
# # Although all these are provided in the request as strings, FastHTML will use your parameter's type
# # annotation to try to cast the value to the requested type.
# # In the case of form data, there can be multiple values with the same key. So in this case,
# # the parameter is a list of ints.
# @rt("/upvote")
# def post(id:list[int]):
#     for i,id_ in enumerate(id): posts.update({'rank':i}, id_)
#     # HTMX by default replaces the inner HTML of the calling element, which in this case is the todo list form.
#     # Therefore, we return the list of posts, now in the correct order, which will be auto-converted to FT for us.
#     # In this case, it's not strictly necessary, because sortable.js has already reorder the DOM elements.
#     # However, by returning the updated data, we can be assured that there aren't sync issues between the DOM
#     # and the server.
#     return tuple(posts(order_by='points'))

# Refactoring components in FastHTML is as simple as creating Python functions.
# `clr_details` creates a div to clear the details of the current Todo.
def clr_details(): return Div(hx_swap_oob='innerHTML', id='current-post')

# SWYX: possible duplicate, commented out
# # The `clr_details` function creates a Div with specific HTMX attributes.
# # `hx_swap_oob='innerHTML'` tells HTMX to swap the inner HTML of the target element out-of-band,
# # meaning it will update this element regardless of where the HTMX request originated from.
# def clr_details(): return Div(hx_swap_oob='innerHTML', id='current-post')

# # SWYX: this route isnt tested yet lol do we even want to let them delete
# # This route handler uses a path parameter `{id}` which is automatically parsed and passed as an int.
# @app.delete("/topic/{id}")
# def deleteTopic(id:int):
#     # The `delete` method is part of the MiniDataAPI spec, removing the item with the given primary key.
#     topic.delete(id)
#     # Returning `clr_details()` ensures the details view is cleared after deletion,
#     # leveraging HTMX's out-of-band swap feature.
#     # Note that we are not returning *any* FT component that doesn't have an "OOB" swap, so the target element
#     # inner HTML is simply deleted. That's why the deleted todo is removed from the list.
#     return clr_details()


@app.get("/p/{id}")
async def seeTopic(auth, id:str):

    # Query the topic table by topic_id, joining with the source table
    topic_query = f"""
    SELECT t.*, s.url as source_url, s.title as source_title, s.description as source_description
    FROM {topic} t
    JOIN {source} s ON t.primary_source_id = s.source_id
    WHERE t.topic_id = ?
    """

    try:
        topic_data = next(db.query(topic_query, [id]))
    except StopIteration:
        raise HTTPException(status_code=404, detail="Topic not found") # SWYX TODO: handle this properly

    # Query the topic_source table for all matches of the topic_id, and then join the source table
    sources_query = f"""
    SELECT s.*
    FROM {topicSource} ts
    JOIN {source} s ON ts.source_id = s.source_id
    LEFT JOIN {topic} t ON ts.topic_id = t.topic_id
    WHERE ts.topic_id = ? AND s.source_id != t.primary_source_id
    """

    additional_sources = list(db.query(sources_query, [id]))

    # Add the additional sources to the topic_data
    topic_data['additional_sources'] = additional_sources


    # Create a dictionary with the topic data
    topic_details = {
        "topic_id": topic_data["topic_id"],
        "title": topic_data["title"],
        "description": topic_data["description"],
        "user_id": topic_data["user_id"],
        "source_url": topic_data["source_url"],
        "source_title": topic_data["source_title"],
        "source_description": topic_data["source_description"],
        "created_at": topic_data["created_at"]
    }

    (scraped_data, text_content, meta_object) = scrape_site(topic_details['source_url'])
    scraped_content = None
    if scraped_data:
      # Create HTML elements to display the scraped info
      scraped_content = Div(
          P(f"Title: {meta_object.get('title', 'N/A')}", cls="text-sm"),
          P(f"Description: {meta_object.get('description', 'N/A')}", cls="text-sm"),
          Img(src=meta_object.get('image', ''), alt="Article image", cls="mt-2 max-w-full h-auto") if meta_object.get('image') else None,
          (H3("Article Peek:", cls="text-lg font-semibold mt-4 mb-2"),
          P(text_content[:500] + "..." if len(text_content) > 500 else text_content, cls="text-sm mb-3")) if text_content else None,
          H4("Meta Information:", cls="text-md font-semibold mt-3 mb-2"),
          cls="mt-4 p-3 bg-gray-100 rounded-md"
      )

    # Create the HTML content for displaying the topic details
    topic_content = Div(
        H2(topic_details["title"], cls="text-xl font-bold mb-2"),
        Div(
            P(f"Source: ", A(topic_details["source_title"], href=topic_details["source_url"], target="_blank"), cls="text-sm"),
            P(f"Created: {topic_details['created_at']}", cls="text-xs"),
            cls="flex justify-between items-center mb-2"
        ),
        # if source_url is present, display in an iframe component
        Div(
            scraped_content, # Iframe(src=topic_details["source_url"], width="100%", height="400", cls="mb-4", **{"is": "x-frame-bypass", "referrerpolicy": "no-referrer", "sandbox": "allow-scripts allow-same-origin"}),
            cls="mb-4"
        ) if topic_details["source_url"] else None,
        P(topic_details['description'], cls="text-sm mb-3"),
        *([
            H3("Additional Sources:", cls="text-lg font-semibold mb-2"),
            Ul(*[
                Li(
                    A(source['title'], href=source['url'], target="_blank", cls="text-blue-600 hover:underline"),
                    cls="text-sm mb-1"
                ) for source in topic_data['additional_sources']
            ], cls="list-disc pl-5 mb-3")
        ] if topic_data['additional_sources'] else []),
        cls="p-3 rounded-md shadow-sm border border-gray-200 max-w-2xl mx-auto mb-8"
    )

    # The `hx_put` attribute tells HTMX to send a PUT request when the form is submitted.
    # `target_id` specifies which element will be updated with the server's response.

    # res = Form(
    #     Div(
    #         Label("Title:", For="title"),
    #         Input(id="title", cls="w-full mb-4"),
    #         cls="mb-4"
    #     ),
    #     Div(
    #         Label("URL:", For="url"),
    #         Input(id="url", cls="w-full mb-4"),
    #         cls="mb-4"
    #     ),
    #     Div(
    #         Label("Owner:", For="owner"),
    #         Input(id="owner", cls="w-full mb-4"),
    #         cls="mb-4"
    #     ),
    #     Hidden(id="created_at"),
    #     Div(
    #         Label("Rank:", For="rank"),
    #         Input(id="rank", cls="w-full mb-4"),
    #         cls="mb-4"
    #     ),
    #     Div(
    #         Checkbox(id="read", label='Read'),
    #         cls="mb-4"
    #     ),
    #     Div(
    #         Label("Details:", For="details"),
    #         Textarea(id="details", name="details", rows=10, cls="w-full mb-4"),
    #         cls="mb-4"
    #     ),
    #     Button("Save", cls="mt-4"),
    #     Hidden(id="id"),
    #     hx_put="/", target_id=f'post-{id}', id="edit",
    #     cls="flex flex-col"
    # )
    # `fill_form` populates the form with existing todo data, and returns the result.
    # Indexing into a table (`todos`) queries by primary key, which is `id` here. It also includes
    # `xtra`, so this will only return the id if it belongs to the current user.


    # swyx TODO: using @htmx , when user clicks on content, render comment_form which when clicked creates a new comment with the right parent . refactor comment_form to be flexible as needed, to render once at the top and also optionally in context when clicked on a comment.  apply the create_comment_form function as appropriate

    # Comment submission form
    comment_form = Form(
        Textarea(id="content", name="content", placeholder="Add a comment...", rows=3, cls="w-full p-2 border rounded mb-2"),
        Button("Submit Comment", cls="bg-blue-500 text-white px-4 py-2 rounded"),
        Hidden(name="topic_id", value=id),
        Hidden(name="user_id", value=auth['user_id']),
        hx_post="/submit_comment",
        hx_target="#comments-title",
        hx_swap="afterend",
        cls="mb-8"
    )

    # Query comments for the current topic, joining with the user table to get the username
    comments = db.q(f"""
        SELECT c.*, u.username
        FROM {comment} c
        JOIN {user} u ON c.user_id = u.user_id
        WHERE c.topic_id = ?
        ORDER BY c.created_at DESC
    """, [id])
    # Function to recursively render comments
    def render_comments(parent_id=None, depth=0, rendered_comments=None):
        if rendered_comments is None:
            rendered_comments = set()
        if depth > 5:
            return []
        rendered = []
        for c in comments:
            if (parent_id is None and c['parent_id'] is None) or (c['parent_id'] == parent_id):
                if c['comment_id'] not in rendered_comments:
                    rendered_comments.add(c['comment_id'])
                    child_comments = render_comments(c['comment_id'], depth + 1, rendered_comments)
                    if child_comments:
                        comment_content = Details(
                            Summary(f"@{c['username']} at {display_time(c['created_at'])}", cls="text-sm text-gray-500 mb-1"),
                            Div(c['content'], cls="text-md text-gray-800 mb-2"),
                            *child_comments,
                            cls=f"pl-{depth*4} mb-4",
                            open=True  # This sets the details to be default expanded
                        )
                    else:
                        comment_content = Div(
                            Div(f"@{c['username']} at {display_time(c['created_at'])}", cls="text-sm text-gray-500 mb-1"),
                            Div(c['content'], cls="text-md text-gray-800 mb-2"),
                            cls=f"pl-{depth*4} mb-4"
                        )
                    rendered.append(comment_content)
        return rendered

    # Render all comments
    comments_section = Div(
        H3("Comments", cls="text-xl font-bold mb-4", id="comments-title"),
        *render_comments(),
        cls="mt-8"
    )


    # Wrap comments in a container for HTMX targeting
    comments_container = Div(
        comment_form,
        Div(id="comments-container", *comments_section.children),
        cls="max-w-2xl mx-auto"
    )

    topic_content = Div(topic_content, comments_container)


    return page_header(
        "Topic Details",
        auth,
        topic_content,
        # fill_form(res, topic[id])
    )

@app.post("/submit_comment")
async def submit_comment(auth, _comment: Comment):
    # Ensure the user is authenticated
    if not auth:
        return RedirectResponse('/login', status_code=303)

    # Set the user_id from the authenticated user
    _comment.user_id = auth['user_id']
    _comment.comment_id = uuid4()
    _comment.parent_id = None
    # Set the created_at timestamp
    _comment.created_at = datetime.now().isoformat()

    # Insert the comment into the database
    new_comment = comment.insert(_comment)

    # Fetch the username for the newly created comment
    user_data = next(db.query("SELECT username FROM user WHERE user_id = ?", [new_comment.user_id]))

    # Render the new comment
    new_comment_html = Div(
        Div(f"@{user_data['username']} on {display_time(new_comment.created_at)}", cls="text-sm text-gray-500 mb-1"),
        Div(new_comment.content, cls="mb-2"),
        # Span(f"Comment ID: {new_comment.comment_id}", cls="text-xs text-gray-500 mr-2"),
        # Span(f"Parent ID: {new_comment.parent_id or 'None'}", cls="text-xs text-gray-500"),
        cls="pl-0 mb-4"
    )

    # Return the rendered HTML for the new comment
    return new_comment_html


@app.put("/updateTopic")
async def updateTopic(topic: Topic):
    # `upsert` and `update` are both part of the MiniDataAPI spec, updating or inserting an item.
    # Note that the updated/inserted todo is returned. By returning the updated todo, we can update the list directly.
    # Because we return a tuple with `clr_details()`, the details view is also cleared.
    return topics.upsert(topic), clr_details()


@app.get("/topics/{id}")
async def get(id:int):
    _topic = topic[id]
    # `hx_swap` determines how the update should occur. We use "outerHTML" to replace the entire todo `Li` element.
    btn = Button('delete', hx_delete=f'/topics/{_topic.id}',
                 target_id=f'topic-{_topic.id}', hx_swap="outerHTML")
    # The "markdown" class is used here because that's the CSS selector we used in the JS earlier.
    # Therefore this will trigger the JS to parse the markdown in the details field.
    # Because `class` is a reserved keyword in Python, we use `cls` instead, which FastHTML auto-converts.
    return Div(H2(_topic.title), Div(_topic.details, cls="markdown"), btn)

@app.get("/tables")
async def get_tables():
    return {"tables": list(db.t)}

# Function to read and parse markdown files
def parse_markdown_file(file_path):
  import yaml
  with open(file_path, 'r') as file:
      content = file.read()
      # Split the file into frontmatter and markdown content
      parts = content.split('---', 2)
      if len(parts) == 3:
          frontmatter = yaml.safe_load(parts[1])
          md_content = parts[2]
      else:
          frontmatter = {}
          md_content = content
  # Add date to frontmatter if not present
  if 'date' not in frontmatter:
      from datetime import datetime
      import os
      file_mtime = os.path.getmtime(file_path)
      frontmatter['date'] = datetime.fromtimestamp(file_mtime).strftime('%Y-%m-%d %H:%M:%S')

  return frontmatter, md_content

@app.get("/blog/")
async def blog_list(auth):
  import os
  blog_posts = []
  content_dir = './content'
  for filename in os.listdir(content_dir):
      if filename.endswith('.md'):
          file_path = os.path.join(content_dir, filename)
          frontmatter, _ = parse_markdown_file(file_path)
          slug = os.path.splitext(filename)[0]
          blog_posts.append({
              'title': frontmatter.get('title', 'Untitled'),
              'date': frontmatter.get('date', 'No date'),
              'slug': slug
          })

  # Sort blog posts by date, newest first
  blog_posts.sort(key=lambda x: x['date'], reverse=True)

  # Render the blog list
  blog_list_html = Div(
      H1("Blog Posts", cls="text-4xl font-bold mb-8 text-center"),
      Ul(*[
          Li(
              Div(
                  A2(post['title'], href=f"/blog/{post['slug']}", cls="text-xl font-semibold hover:text-blue-600 transition-colors duration-300"),
                  Span(f"{post['date']}", cls="block text-sm text-gray-500 mt-1"),
                  cls="mb-6 pb-4 border-b border-gray-200 last:border-b-0"
              )
          )
          for post in blog_posts
      ], cls="space-y-4"),
      cls="container mx-auto px-4 py-8 max-w-2xl"
  )

  return page_header("Blog", auth, blog_list_html)

@app.get("/blog/{slug}")
async def blog_post(auth, slug: str):
  # import markdown
  content_dir = './content'
  file_path = os.path.join(content_dir, f"{slug}.md")

  if not os.path.exists(file_path):
      blog_list_html = await blog_list(auth)
      return page_header("Blog Post Not Found", auth,
          Div(
              H1("Blog Post Not Found", cls="text-3xl font-bold mb-8 text-red-600"),
              P("The requested blog post could not be found. Here's a list of available posts:", cls="mb-8"),
              blog_list_html,
              cls="container mx-auto px-4 py-8"
          )
      )
  frontmatter, md_content = parse_markdown_file(file_path)
  # Render the blog post
  blog_post_html = Div(
      Div(
          H1(frontmatter.get('title', 'Untitled'), cls="text-4xl font-bold mb-4 text-gray-800"),
          Div(frontmatter.get('date', 'No date'), cls="text-sm text-gray-600 mb-8"),
          cls="border-b border-gray-200 pb-8 mb-8"
      ),
      Div(md_content,  **{"data-theme":"light"}, cls="prose prose-lg max-w-none mb-12 text-gray-700 marked unreset"),
      A2("← Back to Blog List", href="/blog/", cls="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition duration-300 ease-in-out"),
      cls="container mx-auto px-4 py-12 max-w-3xl"
  )

  return page_header(frontmatter.get('title', 'Blog Post'), auth, blog_post_html)



@app.get("/seed")
async def seed():
    user

@app.get("/schema/{table_name}")
async def get_schema(table_name: str):
    if table_name not in db.t:
        raise HTTPException(status_code=404, detail="Table not found")
    return {"schema": db.t[table_name].schema}

setup_admin_routes(app)

serve()

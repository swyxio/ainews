
from fasthtml.common import *
from extensions import A2, display_time, display_url, page_header
from datetime import datetime
from uuid import uuid4
from hmac import compare_digest
from db import setup_database
import sqlite_utils

import os

# Create /data folder if it doesn't exist
os.makedirs('./data', exist_ok=True)
db = sqlite_utils.Database("./data/ainews.db") #only for live reload, and this causes some weirdness with users if ur still have a session with a new user but the db is reset and reseeded
setup_database(db)

if db["user"].count == 0:
    import seed
    seed.seed_objects(db)
db.close()


db = database('./data/ainews.db')

comment, tag, tagGroup, tagGroupAssociation, source, submission = db.t.comment, db.t.tag, db.t.tag_group, db.t.tag_groupAssociation, db.t.source, db.t.submission
user, topic, topicSource, topicTag, bookmark, friend, topicVote, commentVote = db.t.user, db.t.topic, db.t.topic_source, db.t.topic_tag, db.t.bookmark, db.t.friend, db.t.topic_vote, db.t.commentVote

Comment, Tag, TagGroup, TagGroupAssociation, Source, Submission = comment.dataclass(), tag.dataclass(), tagGroup.dataclass(), tagGroupAssociation.dataclass(), source.dataclass(), submission.dataclass()
User, Topic, TopicSource, TopicTag, Bookmark, Friend, TopicVote, CommentVote  = user.dataclass(), topic.dataclass(), topicSource.dataclass(), topicTag.dataclass(), bookmark.dataclass(), friend.dataclass(), topicVote.dataclass(), commentVote.dataclass()



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
    privateroutes = ['/profile', '/submit']
    print('auth1', auth)
    # Query for username from auth. todo: refactor to put in beforeware
    try:
        print('user_id', auth['user_id'])
        auth = next(db.query("SELECT * FROM user WHERE user_id = ?", [auth['user_id']]))
    except:
        auth = None
    print('auth2', auth)
    print('req.method', req.method)
    print('req.url.path', req.url.path)
    if not auth and (req.method != 'GET' or req.url.path in privateroutes): return login_redir
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
               # PicoCSS is a particularly simple CSS framework, with some basic integration built in to FastHTML.
               # `picolink` is pre-defined with the header for the PicoCSS stylesheet.
               # You can use any CSS framework you want, or none at all.
               hdrs=(picolink,
                     Script(src="https://cdn.tailwindcss.com"), # SWYX TODO: proper deployment of tailwind
                     # `Style` is an `FT` object, which are 3-element lists consisting of:
                     # (tag_name, children_list, attrs_dict).
                     # FastHTML composes them from trees and auto-converts them to HTML when needed.
                     # You can also use plain HTML strings in handlers and headers,
                     # which will be auto-escaped, unless you use `NotStr(...string...)`.
                     Style(':root { --pico-font-size: 60%; }'),
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
    modal = Div('You are already logged in as ' + auth.username) if auth else None

    frm = Form(
        # Tags with a `name` attr will have `name` auto-set to the same as `id` if not provided
        Input(id='username', placeholder='your @username here. can change later'),
        Input(id='password', type='password', placeholder='Password'),
        Button('login'),
        action='/login', method='post')
    # If a user visits the URL directly, FastHTML auto-generates a full HTML page.
    # However, if the URL is accessed by HTMX, then one HTML partial is created for each element of the tuple.
    # To avoid this auto-generation of a full page, return a `HTML` object, or a Starlette `Response`.
    # `Titled` returns a tuple of a `Title` with the first arg and a `Container` with the rest.
    # See the comments for `Title` later for details.
    return Titled("Login", modal, frm)

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
        u = next(db.query(
            "select * from user where username = ?",
            [login.username]
        ))
    except StopIteration:
        # Handle case when user is not found: create new user
        
        # import bcrypt
        u = user.insert({
            "user_id": uuid4(),
            "username" : login.username,
            "password" : login.password,
            "markdown_bio": f"Default bio for {login.username}"
          })
        # return RedirectResponse('/signup', status_code=303)  # Or handle as appropriate

    print(f"User object type: {type(u)}")
    print(f"User object contents: {u}")

    stored_password = u.password

    if not compare_digest(stored_password, login.password):
        print('comapre ' + stored_password + ' and ' + login.password)
        return login_redir

    # Determine how to access the user_id field
    user_id = u.user_id

    print('logging you in ' + user_id)
    sess['auth'] = u.__dict__
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
    show = display_url(self["source_url"], self["source_title"], self["created_at"], self["username"])
    # isRead = '✅ ' if self["read"] else '🔲 '
    rank = Span(A2(str(self["rank"] or 0), href=f'/p/{self["topic_id"]}'))


    cts = Div(Div(rank, cls="w-12 text-right"), Div(show, Hidden(id="id", value=self['topic_id'])), cls="flex gap-4")
    # Any FT object can take a list of children as positional args, and a dict of attrs as keyword args.
    return Li(Form(cts), id=f'post-{self["topic_id"]}', cls='list-none')


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
    """
    db.create_view("TopicsView", topicsview, replace=True)

    # tps = db.q(f"select * from {topic}")
    # print('tps')
    # print('tps')
    # import json
    # print(json.dumps(tps, indent=2))
    # print('tps')
    # print('tps')

    topicsViewLimit = db.q(f"select * from {db.v.TopicsView} limit 20")
    # print('topicsViewLimit')
    # print('topicsViewLimit')
    # import json
    # print(json.dumps(topicsViewLimit, indent=2))
    # print('topicsViewLimit')
    # print('topicsViewLimit')


    frm = Ul(*[renderTopic(x) for x in topicsViewLimit])
              #  id='posts-list', cls='sortable', hx_post="/upvote", hx_trigger="end")
    # We create an empty 'current-post' Div at the bottom of our page, as a target for the details and editing views.
    card = Card(frm, header=Div('read em and weep'), footer=Div(id='current-post'))
    # PicoCSS uses `<Main class='container'>` page content; `Container` is a tiny function that generates that.
    # A handler can return either a single `FT` object or string, or a tuple of them.
    # In the case of a tuple, the stringified objects are concatenated and returned to the browser.
    # The `Title` tag has a special purpose: it sets the title of the page.

    return page_header("AI News Home", auth, card)

# swyx: submit page
@app.get("/submit")
def get(auth):
    # We don't normally need separate "screens" for adding or editing data. Here for instance,
    # we're using an `hx-post` to add a new todo, which is added to the start of the list (using 'afterbegin').
    new_inp = Input(id="new-title", name="title", placeholder="Link Title")
    new_url = Input(id="new-url", name="url", placeholder="Link URL")
    description = Textarea(id="description", name="description", placeholder="Link Description (optional - Markdown supported)", cls="w-full p-4")
    add = Form(Group(new_inp, new_url,
                    #  Div( owner, created_at,  cls="flex justify-between"),
                     description,
                     Button("Submit New Link or Story", cls="mt-4 p-8 hover:bg-green-700"), cls="flex-col gap-4"),
               action="/submitLink", method='post')
    # We create an empty 'current-post' Div at the bottom of our page, as a target for the details and editing views.
    card = Card(add, header=Div( 'Submit', id='header'), footer=Div(id='current-post'))
    # PicoCSS uses `<Main class='container'>` page content; `Container` is a tiny function that generates that.
    # A handler can return either a single `FT` object or string, or a tuple of them.
    # In the case of a tuple, the stringified objects are concatenated and returned to the browser.
    # The `Title` tag has a special purpose: it sets the title of the page.
    
    # Query for username from auth. todo: refactor to put in beforeware
    return page_header("Submit AI News", auth, card)


@app.post("/submitLink")
async def submitLink(auth, _source:Source):
    # # `hx_swap_oob='true'` tells HTMX to perform an out-of-band swap, updating this element wherever it appears.
    # # This is used to clear the input field after adding the new todo.
    # new_inp =  Input(id="new-title", name="title", placeholder="New Todo", hx_swap_oob='true')
    # new_url = Input(id="new-url", name="url", placeholder="Post URL (optional)", hx_swap_oob='true')
    # dummy = Input(id="new-dummy", name="dummy", placeholder="Dummy")
    # # `insert` returns the inserted todo, which is appended to the start of the list, because we used
    # # `hx_swap='afterbegin'` when creating the todo list form.
    _source.created_at = datetime.now().isoformat()
    _source.source_id = uuid4()
    _source.source_type = 'article'
    print('_source', _source)
    try:
      _source = source.insert(_source)
    except:
        # SWYX TODO: if its a sqlite3.IntegrityError then its a double post
        # we dont know how to return a nice error here
        return RedirectResponse('/', status_code=303)
        

    submission.insert({
        "source_id": _source.source_id,
        "user_id": auth['user_id']
    })

    import random
    topic.insert({
        "topic_id": uuid4(),
        "title": _source.title,
        "user_id": auth['user_id'],
        "primary_source_id": _source.source_id,
        "description": _source.description,
        "rank": random.randint(0, 500), # # just for demo purposes, comment out in future
        "created_at": _source.created_at
    })
    
    return home(auth)

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

    # Create the HTML content for displaying the topic details
    topic_content = Div(
        H2(topic_details["title"], cls="text-xl font-bold mb-2"),
        Div(
            P(f"Source: ", A(topic_details["source_title"], href=topic_details["source_url"], target="_blank"), cls="text-sm"),
            P(f"Created: {topic_details['created_at']}", cls="text-xs"),
            cls="flex justify-between items-center mb-2"
        ),
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
                            Div(c['content'], cls="text-md text-gray-200 mb-2"),
                            *child_comments,
                            cls=f"pl-{depth*4} mb-4",
                            open=True  # This sets the details to be default expanded
                        )
                    else:
                        comment_content = Div(
                            Div(f"@{c['username']} at {display_time(c['created_at'])}", cls="text-sm text-gray-500 mb-1"),
                            Div(c['content'], cls="text-md text-gray-200 mb-2"),
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

@app.get("/seed")
async def seed():
    user

@app.get("/schema/{table_name}")
async def get_schema(table_name: str):
    if table_name not in db.t:
        raise HTTPException(status_code=404, detail="Table not found")
    return {"schema": db.t[table_name].schema}    

serve()
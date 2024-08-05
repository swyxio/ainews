
from fasthtml.common import *
from extensions import A2, display_time, display_url
from datetime import datetime

from hmac import compare_digest
from db import setup_database
import sqlite_utils

import os

# Create /data folder if it doesn't exist
os.makedirs('./data', exist_ok=True)
db = sqlite_utils.Database("./data/ainews.db", recreate=True)
setup_database(db)

import seed
seed.seed_objects(db)
db.close()


db = database('./data/ainews.db')

comment, tag, tagGroup, tagGroupAssociation, source, submission = db.t.comment, db.t.tag, db.t.tagGroup, db.t.tagGroupAssociation, db.t.source, db.t.submission
user, post, postSource, postTag, bookmark, friend, postVote, commentVote = db.t.user, db.t.post, db.t.postSource, db.t.postTag, db.t.bookmark, db.t.friend, db.t.postVote, db.t.commentVote

Comment, Tag, TagGroup, TagGroupAssociation, Source, Submission = comment.dataclass(), tag.dataclass(), tagGroup.dataclass(), tagGroupAssociation.dataclass(), source.dataclass(), submission.dataclass()
User, Post, PostSource, PostTag, Bookmark, Friend, PostVote, CommentVote  = user.dataclass(), post.dataclass(), postSource.dataclass(), postTag.dataclass(), bookmark.dataclass(), friend.dataclass(), postVote.dataclass(), commentVote.dataclass()



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
    privateroutes = ['/profile']
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
                     Style(':root { --pico-font-size: 100%; }'),
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
# rt = app.route
# swyx: no longer needed since we switched from `FastHTMLWithLiveReload` to `fast_app`

# For instance, this function handles GET requests to the `/login` path.
@app.get("/login")
def loginroute():
    # This creates a form with two input fields, and a submit button.
    # All of these components are `FT` objects. All HTML tags are provided in this form by FastHTML.
    # If you want other custom tags (e.g. `MyTag`), they can be auto-generated by e.g
    # `from fasthtml.components import MyTag`.
    # Alternatively, manually call e.g `ft(tag_name, *children, **attrs)`.
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
    return Titled("Login", frm)

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
        import uuid
        # import bcrypt
        u = user.insert({
            "user_id": uuid.uuid4(),
            "username" : login.username,
            "password" : login.password.encode("utf-8"),
            "markdown_bio": f"Default bio for {login.username}"
          })
        # return RedirectResponse('/signup', status_code=303)  # Or handle as appropriate

    print(f"User object type: {type(u)}")
    print(f"User object contents: {u}")

    stored_password = u.password

    if not compare_digest(stored_password.decode("utf-8"), login.password):
        print('comapre ' + stored_password.decode("utf-8") + ' and ' + login.password)
        return login_redir

    # Determine how to access the user_id field
    user_id = u.user_id

    print('logging you in ' + user_id)
    sess['auth'] = user_id
    print('sess', sess)
    return RedirectResponse('/', status_code=303)

# Instead of using `app.route` (or the `rt` shortcut), you can also use `app.get`, `app.post`, etc.
# In this case, the function name is not used to determine the HTTP verb.
@app.get("/profile")
def profile(auth):
    # Check if user is authenticated
    if not auth:
        return RedirectResponse('/login', status_code=303)
    
    # Fetch user data
    _user = next(db.query(
              "select * from user where user_id = :user_id",
              {"user_id": auth}
          ))
    
    # Create a list of user fields
    user_fields = [
        Div(
            Span(f"{field}: ", cls="font-bold"),
            Span(str(getattr(_user, field))),
            cls="mb-2"
        )
        for field in _user.__dataclass_fields__
        if field != 'password'  # Exclude password field for security
    ]
    # Add a logout button to the profile content
    logout_button = Form(
        Button("Logout", type="submit", cls="mt-4 bg-red-500 hover:bg-red-600 text-white font-bold py-2 px-4 rounded"),
        action="/logout",
        method="post",
        cls="mt-4"
    )
    # Wrap user fields in a container
    profile_content = Div(
        H2("User Profile", cls="text-2xl mb-4"),
        *user_fields,
        logout_button,
        cls="p-4 bg-gray-100 rounded-lg"
    )
    
    return profile_content

# Instead of using `app.route` (or the `rt` shortcut), you can also use `app.get`, `app.post`, etc.
# In this case, the function name is not used to determine the HTTP verb.
@app.post("/logout")
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
def renderPost(self):
    show = display_url(self["source_url"], self["source_title"], self["created_at"], self["username"])
    comments = AX('comments',     f'/p/{self["post_id"]}' , 'current-post', cls="hover:text-blue-200 text-blue-400")
    # isRead = '✅ ' if self["read"] else '🔲 '
    rank = Span(str(self["rank"] or 0))

    # show = display_url(self.primary_source_id, self.source_title, self.created_at, self.user_id)
    # comments = AX('comments',     f'/p/{self.post_id}' , 'current-post', cls="hover:text-blue-200 text-blue-400")
    # # isRead = '✅ ' if self.read else '🔲 '
    # rank = Span(str(self.rank or 0))
    # FastHTML provides some shortcuts. For instance, `Hidden` is defined as simply:
    # `return Input(type="hidden", value=value, **kwargs)`
    cts = Div(Div(rank, cls="w-24 text-right"), Div(show, ' | ', comments, Hidden(id="id", value=self['post_id'])), cls="flex gap-4")
    # Any FT object can take a list of children as positional args, and a dict of attrs as keyword args.
    return Li(Form(cts), id=f'post-{self['post_id']}', cls='list-none')


# This is the handler for the main todo list application.
# By including the `auth` parameter, it gets passed the current username, for displaying in the title.
# @rt("/")
# def get(auth):
@app.get("/")
def home(auth):
    # Query for username from auth
    try:
        u = next(db.query("SELECT * FROM user WHERE user_id = ?", [auth]))
    except:
        auth = None
    title = f"AI News - Welcome {u['username'] if auth else ''}"
    top = Grid(H1(title), 
               Div(
                   A2('submit', href='/submit'), 
                   '|',
                   A2(u['username'], href='/profile') if auth else A2('login', href='/login') , 
                   style='text-align: right'))
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
    postsview = f"""select {post}.*, 
    url as source_url, {source}.title as source_title, {source}.description as source_description,
    username
    from {post} join {source} on {post}.primary_source_id = {source}.source_id
    join {user} on {post}.user_id={user}.user_id
    """
    db.create_view("PostsView", postsview, replace=True)

    postsViewLimit = db.q(f"select * from {db.v.PostsView} limit 10")
    # print('acca_dacca')
    # print('acca_dacca')
    # import json
    # print(json.dumps(postsViewLimit, indent=2))
    # print('acca_dacca')
    # print('acca_dacca')


    frm = Ul(*[renderPost(x) for x in postsViewLimit])
              #  id='posts-list', cls='sortable', hx_post="/upvote", hx_trigger="end")
    # We create an empty 'current-post' Div at the bottom of our page, as a target for the details and editing views.
    card = Card(frm, header=Div('read em and weep'), footer=Div(id='current-post'))
    # PicoCSS uses `<Main class='container'>` page content; `Container` is a tiny function that generates that.
    # A handler can return either a single `FT` object or string, or a tuple of them.
    # In the case of a tuple, the stringified objects are concatenated and returned to the browser.
    # The `Title` tag has a special purpose: it sets the title of the page.
    return Title(title), Container(top, card) # output, card)

# swyx: submit page
@app.get("/submit")
def get(auth):
    title = f"Submit AI News - by {auth}"
    top = Grid(H1(title), Div(A2(auth, href='/profile'), style='text-align: right'))
    # We don't normally need separate "screens" for adding or editing data. Here for instance,
    # we're using an `hx-post` to add a new todo, which is added to the start of the list (using 'afterbegin').
    new_inp = Input(id="new-title", name="title", placeholder="Post Title")
    new_url = Input(id="new-url", name="url", placeholder="Post URL (optional)")
    # owner = Div("Submitter: ", Input(id="owner", name="owner", value=auth, disabled = True, cls="w-full"), cls="flex gap-4 items-center")
    # created_at = Div("At: ", Input(id="created_at", name="created_at", value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), disabled=True, cls="w-full"), cls="flex gap-4 items-center")
    details = Textarea(id="details", name="details", placeholder="Post Comments (optional - Markdown supported)", cls="w-full p-4")
    rank = Hidden(id="rank", name="rank", value="0")
    add = Form(Group(new_inp, new_url,
                     rank,
                    #  Div( owner, created_at,  cls="flex justify-between"),
                     details,
                     Button("Submit New Post", cls="mt-4 p-8 hover:bg-green-700"), cls="flex-col gap-4"),
               action="/", method='post')
    # We create an empty 'current-post' Div at the bottom of our page, as a target for the details and editing views.
    card = Card(add, header=Div( 'Submit', id='header'), footer=Div(id='current-post'))
    # PicoCSS uses `<Main class='container'>` page content; `Container` is a tiny function that generates that.
    # A handler can return either a single `FT` object or string, or a tuple of them.
    # In the case of a tuple, the stringified objects are concatenated and returned to the browser.
    # The `Title` tag has a special purpose: it sets the title of the page.
    return Title(title), Container(top, card)

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

# This route handler uses a path parameter `{id}` which is automatically parsed and passed as an int.
@app.delete("/login/{id}")
def deletePost(id:int):
    # The `delete` method is part of the MiniDataAPI spec, removing the item with the given primary key.
    posts.delete(id)
    # Returning `clr_details()` ensures the details view is cleared after deletion,
    # leveraging HTMX's out-of-band swap feature.
    # Note that we are not returning *any* FT component that doesn't have an "OOB" swap, so the target element
    # inner HTML is simply deleted. That's why the deleted todo is removed from the list.
    return clr_details()

@app.get("/edit/{id}")
async def seePost(id:int):
    # The `hx_put` attribute tells HTMX to send a PUT request when the form is submitted.
    # `target_id` specifies which element will be updated with the server's response.
    res = Form(Group(Input(id="title"), Input(id="url"),  Input(id="owner"),  Hidden(id="created_at"),  Input(id="rank"), Button("Save")),
        Hidden(id="id"), Checkbox(id="read", label='Read'),
        Textarea(id="details", name="details", rows=10),
        hx_put="/", target_id=f'post-{id}', id="edit")
    # `fill_form` populates the form with existing todo data, and returns the result.
    # Indexing into a table (`todos`) queries by primary key, which is `id` here. It also includes
    # `xtra`, so this will only return the id if it belongs to the current user.
    return fill_form(res, posts[id])

@app.put("/updatePost")
async def updatePost(post: Post):
    # `upsert` and `update` are both part of the MiniDataAPI spec, updating or inserting an item.
    # Note that the updated/inserted todo is returned. By returning the updated todo, we can update the list directly.
    # Because we return a tuple with `clr_details()`, the details view is also cleared.
    return posts.upsert(post), clr_details()

@app.post("/addPost")
async def addPost(auth, _post:Post):
    # # `hx_swap_oob='true'` tells HTMX to perform an out-of-band swap, updating this element wherever it appears.
    # # This is used to clear the input field after adding the new todo.
    # new_inp =  Input(id="new-title", name="title", placeholder="New Todo", hx_swap_oob='true')
    # new_url = Input(id="new-url", name="url", placeholder="Post URL (optional)", hx_swap_oob='true')
    # dummy = Input(id="new-dummy", name="dummy", placeholder="Dummy")
    # # `insert` returns the inserted todo, which is appended to the start of the list, because we used
    # # `hx_swap='afterbegin'` when creating the todo list form.
    _post.created_at = datetime.now().isoformat()
    _post.owner = auth

    # just for demo purposes, comment out in future
    import random
    _post.rank = random.randint(0, 500)

    posts.insert(_post)
    return home(auth)

@app.get("/posts/{id}")
async def get(id:int):
    post = posts[id]
    # `hx_swap` determines how the update should occur. We use "outerHTML" to replace the entire todo `Li` element.
    btn = Button('delete', hx_delete=f'/posts/{post.id}',
                 target_id=f'post-{post.id}', hx_swap="outerHTML")
    # The "markdown" class is used here because that's the CSS selector we used in the JS earlier.
    # Therefore this will trigger the JS to parse the markdown in the details field.
    # Because `class` is a reserved keyword in Python, we use `cls` instead, which FastHTML auto-converts.
    return Div(H2(post.title), Div(post.details, cls="markdown"), btn)

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
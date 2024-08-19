from fasthtml.common import *
from extensions import A2, display_time, page_header, scrape_site
from db_config import *  # Import all database-related entities and functions

db, (
    Comment, Tag, TagGroup, TagGroupAssociation, Source, Submission, Feedback, User, Topic, TopicSource, TopicTag, Bookmark, Friend, TopicVote, CommentVote,
    comment, tag, tagGroup, tagGroupAssociation, source, submission, user, topic, topicSource, topicTag, bookmark, friend, topicVote, commentVote, feedback
) = setup_db()

def setup_admin_routes(app):
    @app.get("/admin")
    def admin_home(auth):
        header_div = Div("Admin Home")

        # Admin home page logic
        admin_index_content = Div(
            P(
                Ul(*[
                    Li(
                        A("/submissions", href="/admin/submissions", target="_blank", cls="text-blue-600 hover:underline"),
                        cls="text-sm mb-1"
                    ),
                    Li(
                        A("/topics", href="/admin/topics", target="_blank", cls="text-blue-600 hover:underline"),
                        cls="text-sm mb-1"
                    ),
                                        Li(
                        A("/suggestions", href="/admin/suggestions", target="_blank", cls="text-blue-600 hover:underline"),
                        cls="text-sm mb-1"
                    ),
                    Li(
                        A("/users", href="/admin/users", target="_blank", cls="text-blue-600 hover:underline"),
                        cls="text-sm mb-1"
                    )                   
                ], cls="list-disc pl-5 mb-3")
            , cls="")
        )

        card = Card(admin_index_content, header=header_div)

        return page_header("Admin Home", auth, card)

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
                                Span(self["vote_score"] if self["vote_score"] else 0, id=f"score-{self['topic_id']}", cls="w-2"),
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

    @app.get("/admin/submissions")
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


        @app.get("/admin/users")
        def admin_users(auth):
            # User management logic
            return page_header("User Management", auth, Div("User List"))
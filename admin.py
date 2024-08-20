from fasthtml.common import *
from extensions import A2, display_time, page_header, scrape_site, Modal
from db_config import *  # Import all database-related entities and functions
import asyncio

db, (
    Comment, Tag, TagGroup, TagGroupAssociation, Source, Submission, Feedback, User, Topic, TopicSource, TopicTag, Bookmark, Friend, TopicVote, CommentVote,
    comment, tag, tagGroup, tagGroupAssociation, source, submission, user, topic, topicSource, topicTag, bookmark, friend, topicVote, commentVote, feedback
) = setup_db()

valid_topic_states = ["submission", "top", "archived", "hidden"]



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
        
        def display_submission_url(url, type, title, timestr, owner, submission_state):
            created_at = display_time(timestr)
            from urllib.parse import urlparse
            try:
                parsed_url = urlparse(url)
                prefix_type = f"{type.capitalize()}: " if type != "" else ""
                if parsed_url.netloc.startswith('www.'):
                    parsed_url = parsed_url._replace(netloc=parsed_url.netloc[4:])
                parsed_domain = parsed_url if isinstance(parsed_url, str) else parsed_url.netloc if parsed_url.netloc else 'N/A'
                admin_links = [
                    A2(f"[{s.capitalize()}]", 
                       href=f"/admin/change_state/{self['topic_id']}/{s}", 
                       hx_post=f"/admin/change_state/{self['topic_id']}/{s}",
                       hx_target=f"#post-{self['topic_id']}",
                       hx_swap="outerHTML",
                       cls="text-red-600 hover:underline")
                    for s in valid_topic_states if s != submission_state
                ]
                delete_link = A2(f"[Delete]", 
                                 href=f"#",
                                 hx_get=f"/admin/confirm_delete/{self['topic_id']}",
                                 hx_target="#delete-modal-container",
                                 cls="text-red-600 hover:underline")

                show = Div(
                        Div(
                            Div(
                                Span(self["vote_score"] if self["vote_score"] else 0, id=f"score-{self['topic_id']}", cls="w-8 text-right inline-block"),
                                cls="inline-block mr-4 w-8 fixed-width"),
                            Div(
                                Span(
                                    self["submission_state"],
                                    cls="bg-green-100 text-green-800 px-2 py-1 rounded-md border border-green-300 text-sm mr-2 mb-2 inline-block w-24 text-center"
                                )
                                , cls="inline-block mr-4"),
                            Div(
                                A2(f"Topic Title: {prefix_type}{self['title']}", href=url, target="_blank", cls="font-bold block"),
                                A2(f"Submission Title: {prefix_type}{self['submission_title']}", href=url, target="_blank", cls="font-bold block"),
                                cls="inline-block mr-4"
                            ),
                            Div(
                                Span(*admin_links),
                                Br(),
                                Span(delete_link),
                                cls="inline-block font-bold"),
                            cls="flex items-start p-2"
                        )                         
                    )
                # show = Div(
                #     Div(
                #         Span(
                #             Span(str(self["vote_score"] if self["vote_score"] is not None else 0), id=f"score-{self['topic_id']}", cls="w-2"),
                #             cls="inline-flex items-center space-x-2"
                #         ),
                #         Span(
                #             submission_state.capitalize(),
                #             cls="bg-gray-100 text-gray-800 px-2 py-1 rounded-md border border-gray-300 text-sm mr-2 mb-2"
                #         ),
                #         Span(
                #             A2(f"Topic Title: {prefix_type}{self['title']}", href=url, target="_blank", cls="font-bold"),
                #             A2(f"Submission Title: {prefix_type}{self['submission_title']}", href=url, target="_blank", cls="font-bold"),
                #             cls="flex flex-col"
                #         ),
                #         Span(
                #             *admin_links,
                #             cls="text-sm text-gray-600 ml-2"
                #         )
                #     ), 
                #     Span(f"({parsed_url.netloc}, {created_at} by {owner} {submission_state})", cls="text-xs text-gray-400"), 
                #     cls="flex flex-col mb-2"
                # )
            except ValueError:
                show = Span(title) if url is None else Span(A2(title, href=url), 'NA')
            return show
            
        show = display_submission_url(self["source_url"], self["type"], self["source_title"], self["created_at"], self["username"], self["state"])

        cts = Div(
            show,
            Div(id="delete-modal-container")  # Container for the delete confirmation modal
        )
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
        url as source_url, {source}.title as source_title, {source}.description as source_description, {submission}.state as submission_state, {submission}.title as submission_title,
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

        frm = Ul(*[renderSubmission(x) for x in submissionsViewLimit], cls="divide-y divide-gray-300")
        for index, li in enumerate(frm.children):
            li.attrs['class'] = f"{'bg-gray-200' if index % 2 == 0 else 'bg-white'}"
                #  id='posts-list', cls='sortable', hx_post="/upvote", hx_trigger="end")
        # We create an empty 'current-post' Div at the bottom of our page, as a target for the details and editing views.
        
        header_div = Div(Span(f'Recent Submissions ', A(sort_by, href=target, cls="text-blue-600 hover:underline"), ' (you can personally up/downvote max of +/- 5 votes)'))
        card = Card(frm, header=header_div, footer=Div(id='current-post'))
        # PicoCSS uses `<Main class='container'>` page content; `Container` is a tiny function that generates that.
        # A handler can return either a single `FT` object or string, or a tuple of them.
        # In the case of a tuple, the stringified objects are concatenated and returned to the browser.
        # The `Title` tag has a special purpose: it sets the title of the page.

        return page_header("AI News Submissions",auth, card, wide=True)


        @app.get("/admin/users")
        def admin_users(auth):
            # User management logic
            return page_header("User Management", auth, Div("User List"))

    @app.post("/admin/change_state/{topic_id}/{new_state}")
    def change_submission_state(topic_id: str, new_state: str, auth):
        if new_state not in valid_topic_states:
                return "Invalid state", 400

        statements = f"""
            UPDATE {topic} SET state = "{new_state}" WHERE topic_id = "{topic_id}";
            UPDATE {submission} SET state = "{new_state}" WHERE submission_id = 
            (SELECT submission_id FROM {topic} WHERE topic_id = "{topic_id}");
        """
        print('statements', statements)

        db.executescript(statements)
        
        # Fetch the updated submission data
        submission_sql = f"""select {topic}.*, 
        url as source_url, {source}.title as source_title, {source}.description as source_description, {submission}.state as submission_state, {submission}.title as submission_title, username
        from {topic} join {source} on {topic}.primary_source_id = {source}.source_id join {submission} on {submission}.source_id={source}.source_id
        join {user} on {topic}.user_id={user}.user_id where {topic}.topic_id = ?
        """
        print('submission_sql', submission_sql)


        # Debug query to select all columns from topic where topic_id matches
        debug_result = db.q("SELECT * FROM topic WHERE topic_id = ?", {topic_id})
        print("Debug query result:", debug_result)


        submission_result = db.q(submission_sql, {topic_id})        
        if len(submission_result) == 1:
            updated_submission = submission_result[0]
        else:
            if len(submission_result) > 1:
                return "Multiple submissions found", 404
            else:
                return "No submission found", 404
            
        # Add vote_score to the updated submission
        vote_score = db.q(f"""
            SELECT SUM(CASE WHEN vote_type = 1 THEN 1 WHEN vote_type = -1 THEN -1 ELSE 0 END) as vote_score
            FROM {topicVote}
            WHERE topic_id = ?
        """, [topic_id])[0]['vote_score']
        updated_submission['vote_score'] = vote_score if vote_score is not None else 0

        # Render the updated submission
        return renderSubmission(updated_submission)
    
    # Add these new routes to the setup_admin_routes function
    @app.get("/admin/confirm_delete/{topic_id}")
    def confirm_delete(topic_id: str, auth):
        # Query to get vote and comment counts
        counts = db.q(f"""
            SELECT 
                (SELECT COUNT(*) FROM {topicVote} WHERE topic_id = ?) as vote_count,
                (SELECT COUNT(*) FROM {comment} WHERE topic_id = ?) as comment_count
        """, [topic_id, topic_id])[0]

        content = Div(
            P(f"Are you sure you want to delete this topic? The topic has {counts['vote_count']} votes and {counts['comment_count']} comments."),
            Div(
                Button("Yes", hx_post=f"/admin/delete_submission/{topic_id}", hx_target="#delete-modal-container"),
                Button("No", hx_get="/admin/close_modal", hx_target="#delete-modal-container"),
                cls="flex justify-end space-x-2 mt-4"
            )
        )

        return Modal("Confirm Deletion", content, id="delete-confirmation-modal")

    @app.post("/admin/delete_submission/{topic_id}")
    def delete_submission(topic_id: str, auth):
        # Perform the deletion logic here
        # For example:
        # db.executescript(f"""
        #     DELETE FROM {topic} WHERE topic_id = ?;
        #     DELETE FROM {submission} WHERE submission_id = (SELECT submission_id FROM {topic} WHERE topic_id = ?);
        # """, [topic_id, topic_id])

        content = Div(
            P("The topic has been successfully deleted."),
            Button("Close", hx_get="/admin/close_modal", hx_target="#delete-modal-container", cls="mt-4")
        )

        return Modal("Success", content, id="success-modal")

    @app.get("/admin/close_modal")
    def close_modal():
        return ""  # Return an empty string to close the modal    
    
     
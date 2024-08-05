-- User table
CREATE TABLE User (
    user_id TEXT PRIMARY KEY,
    pseudonym TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    markdown_bio TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Comment table
CREATE TABLE Comment (
    comment_id TEXT PRIMARY KEY,
    user_id INTEGER,
    parent_id INTEGER,
    content TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES User(user_id),
    FOREIGN KEY (parent_comment_id) REFERENCES Comment(comment_id)
);

-- Tag table
CREATE TABLE Tag (
    tag_id TEXT PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    description TEXT
);

-- Tag Group table
CREATE TABLE TagGroup (
    group_id TEXT PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    description TEXT
);

-- Tag Group Association table
CREATE TABLE TagGroupAssociation (
    group_id INTEGER,
    tag_id INTEGER,
    PRIMARY KEY (group_id, tag_id),
    FOREIGN KEY (group_id) REFERENCES TagGroup(group_id),
    FOREIGN KEY (tag_id) REFERENCES Tag(tag_id)
);

-- Source table (abstract table for different types of sources)
CREATE TABLE Source (
    source_id TEXT PRIMARY KEY,
    url TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    source_type TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Submission table (inherits from Source)
CREATE TABLE Submission (
    source_id TEXT PRIMARY KEY,
    user_id INTEGER,
    FOREIGN KEY (source_id) REFERENCES Source(source_id),
    FOREIGN KEY (user_id) REFERENCES User(user_id)
);


-- Post table
CREATE TABLE Post (
    post_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    user_id INTEGER,
    primary_source_id INTEGER,
    rank INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Post Source Association table
CREATE TABLE PostSource (
    post_id INTEGER,
    source_id INTEGER,
    PRIMARY KEY (post_id, source_id),
    FOREIGN KEY (post_id) REFERENCES Post(post_id),
    FOREIGN KEY (source_id) REFERENCES Source(source_id)
);

-- Post Tag Association table
CREATE TABLE PostTag (
    post_id INTEGER,
    tag_id INTEGER,
    PRIMARY KEY (post_id, tag_id),
    FOREIGN KEY (post_id) REFERENCES Post(post_id),
    FOREIGN KEY (tag_id) REFERENCES Tag(tag_id)
);

-- Bookmark table
CREATE TABLE Bookmark (
    bookmark_id TEXT PRIMARY KEY,
    user_id INTEGER,
    post_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES User(user_id),
    FOREIGN KEY (post_id) REFERENCES Post(post_id)
);

-- Friends table
CREATE TABLE Friend (
    user_id INTEGER,
    friend_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, friend_id),
    FOREIGN KEY (user_id) REFERENCES User(user_id),
    FOREIGN KEY (friend_id) REFERENCES User(user_id)
);

-- Vote table for Posts
CREATE TABLE PostVote (
    vote_id TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL,
    post_id INTEGER NOT NULL,
    vote_type INTEGER NOT NULL, -- 1 for upvote, -1 for downvote
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES User(user_id),
    FOREIGN KEY (post_id) REFERENCES Post(post_id),
    UNIQUE(user_id, post_id) -- Ensures a user can only have one vote per post
);

-- Index for faster lookups
CREATE INDEX idx_post_vote_user_post ON PostVote(user_id, post_id);

-- Vote table for Comments
CREATE TABLE CommentVote (
    vote_id TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL,
    comment_id INTEGER NOT NULL,
    vote_type INTEGER NOT NULL, -- 1 for upvote, -1 for downvote
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES User(user_id),
    FOREIGN KEY (comment_id) REFERENCES Comment(comment_id),
    UNIQUE(user_id, comment_id) -- Ensures a user can only have one vote per comment
);

-- Index for faster lookups
CREATE INDEX idx_comment_vote_user_comment ON CommentVote(user_id, comment_id);
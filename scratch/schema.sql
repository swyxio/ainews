-- User table
CREATE TABLE User (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    pseudonym TEXT UNIQUE NOT NULL,
    markdown_bio TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Comment table
CREATE TABLE Comment (
    comment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    parent_comment_id INTEGER,
    content TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES User(user_id),
    FOREIGN KEY (parent_comment_id) REFERENCES Comment(comment_id)
);

-- Tag table
CREATE TABLE Tag (
    tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

-- Tag Group table
CREATE TABLE TagGroup (
    group_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
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
    source_id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    source_type TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Submission table (inherits from Source)
CREATE TABLE Submission (
    source_id INTEGER PRIMARY KEY,
    user_id INTEGER,
    FOREIGN KEY (source_id) REFERENCES Source(source_id),
    FOREIGN KEY (user_id) REFERENCES User(user_id)
);


-- Discussion Topic table
CREATE TABLE DiscussionTopic (
    topic_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    rank INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Discussion Topic Source Association table
CREATE TABLE DiscussionTopicSource (
    topic_id INTEGER,
    source_id INTEGER,
    PRIMARY KEY (topic_id, source_id),
    FOREIGN KEY (topic_id) REFERENCES DiscussionTopic(topic_id),
    FOREIGN KEY (source_id) REFERENCES Source(source_id)
);

-- Discussion Topic Tag Association table
CREATE TABLE DiscussionTopicTag (
    topic_id INTEGER,
    tag_id INTEGER,
    PRIMARY KEY (topic_id, tag_id),
    FOREIGN KEY (topic_id) REFERENCES DiscussionTopic(topic_id),
    FOREIGN KEY (tag_id) REFERENCES Tag(tag_id)
);

-- Bookmark table
CREATE TABLE Bookmark (
    bookmark_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    topic_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES User(user_id),
    FOREIGN KEY (topic_id) REFERENCES DiscussionTopic(topic_id)
);

-- Friends table
CREATE TABLE Friends (
    user_id INTEGER,
    friend_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, friend_id),
    FOREIGN KEY (user_id) REFERENCES User(user_id),
    FOREIGN KEY (friend_id) REFERENCES User(user_id)
);

-- Vote table for Discussion Topics
CREATE TABLE DiscussionTopicVote (
    vote_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    topic_id INTEGER NOT NULL,
    vote_type INTEGER NOT NULL, -- 1 for upvote, -1 for downvote
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES User(user_id),
    FOREIGN KEY (topic_id) REFERENCES DiscussionTopic(topic_id),
    UNIQUE(user_id, topic_id) -- Ensures a user can only have one vote per topic
);

-- Index for faster lookups
CREATE INDEX idx_discussion_topic_vote_user_topic ON DiscussionTopicVote(user_id, topic_id);

-- Vote table for Comments
CREATE TABLE CommentVote (
    vote_id INTEGER PRIMARY KEY AUTOINCREMENT,
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
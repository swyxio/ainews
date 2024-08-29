import random
from datetime import datetime
import uuid
from dotenv import load_dotenv
import os

# Example seed data, UUIDs are not Foreign Key Compliant in the Examples But Should Be In Real Data
# {"table": "user", "user_id": "550e8400-e29b-41d4-a716-446655440000", "username": "john_doe1", "email": "john@example.com", "password": "password", "markdown_bio": "I am john_doe1"}
#{"table":"friend", "user_id": "550e8400-e29b-41d4-a716-446655440000", "friend_id": "550e8400-e29b-41d4-a716-446655440001"}
#{"table": "source", "source_id": "550e8400-e29b-41d4-a716-446655440002", "url": "https://example.com/article1", "title": "Sample Article 1", "description": "This is a sample article for testing", "source_type": "article"}
#{"table": "submission", "type": "show", "source_id": "550e8400-e29b-41d4-a716-446655440002", "user_id": "550e8400-e29b-41d4-a716-446655440000", "state": "public"}
#{"table": "topic", "type": "show", "state": "top", "topic_id": "550e8400-e29b-41d4-a716-446655440005", "title": "Sample Article 1", "user_id": "550e8400-e29b-41d4-a716-446655440000", "primary_source_id": "550e8400-e29b-41d4-a716-446655440002", "description": "This is a sample article for testing"}
#{"table": "topic", "type": "ask", "state": "top", "topic_id": "550e8400-e29b-41d4-a716-446655440006", "title": "Sample Article 2", "user_id": "550e8400-e29b-41d4-a716-446655440000", "primary_source_id": "550e8400-e29b-41d4-a716-446655440002", "description": "This is a sample article for testing"}
#{"table": "topic", "type": "tell", "state": "top", "descripton":"test_description", "topic_id": "550e8400-e29b-41d4-a716-446655440007", "title": "Sample Article 3", "user_id": "550e8400-e29b-41d4-a716-446655440000", "primary_source_id": "550e8400-e29b-41d4-a716-446655440003", "description": "This is a sample article for testing"}
#{"table": "topic_source", "topic_id": "550e8400-e29b-41d4-a716-446655440021", "source_id": "550e8400-e29b-41d4-a716-446655440010"}

import uuid
import json

import random

valid_source_types = ["article", "video", "podcast", "book", "website"]
valid_topic_types = ["show", "ask", "tell"]
valid_topic_states = ["submission", "top", "archived", "hidden"]
valid_submission_types = ["show", "ask", "tell"]
valid_submission_states = ["submission", "top"]

    

def generate_realistic_username():
    first_names = ["John", "Jane", "Mike", "Emily", "Alex", "Sarah", "Chris", "Emma", "David", "Olivia"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
    return f"{random.choice(first_names).lower()}_{random.choice(last_names).lower()}{random.randint(1, 99)}"

def generate_realistic_email(username):
    domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "icloud.com"]
    return f"{username}@{random.choice(domains)}"

def generate_realistic_bio():
    interests = ["AI", "machine learning", "data science", "web development", "cybersecurity", "blockchain", "IoT", "cloud computing", "robotics", "virtual reality"]
    roles = ["software engineer", "data analyst", "product manager", "UX designer", "system administrator", "DevOps engineer", "full-stack developer", "AI researcher"]
    return f"I'm a {random.choice(roles)} passionate about {random.choice(interests)} and {random.choice(interests)}. Always learning and exploring new technologies."

def generate_user_data():
    user_id = str(uuid.uuid4())
    username = generate_realistic_username()
    user_data = {
        "table": "user",
        "user_id": user_id,
        "username": username,
        "email": generate_realistic_email(username),
        "password": str(uuid.uuid4())[:8],  # Generate a random 8-character password
        "markdown_bio": generate_realistic_bio()
    }
    return user_data

def generate_tag(tag_name:str):
    tag_id = str(uuid.uuid4())
    
    tag = {
        "table": "tag",
        "tag_id": tag_id,
        "name": tag_name,
        "description": f"Topics related to {tag_name}"
    }
    return tag

def generate_tag_group(group_name:str):
    group_id = str(uuid.uuid4())
    
    group = {
        "table": "tag_group",
        "group_id": group_id,
        "name": f"{group_name}",
        "description": f"A group for {group_name} related tags"
    }
    return group

def generate_tag_group_association(group_id, tag_id):
    return {
        "table": "tag_group_association",
        "group_id": group_id,
        "tag_id": tag_id
    }

def generate_submission(submission_type, title, description, submission_state, source_id, user_id):

    submission_id = str(uuid.uuid4())
    
    if submission_state not in valid_submission_states:
        raise ValueError(f"Invalid submission state. Must be one of {valid_submission_states}")
    
    if submission_type not in valid_submission_types:
        raise ValueError(f"Invalid submission type. Must be one of {valid_submission_types}")
    
    submission = {
        "table": "submission",
        "submission_id": submission_id,
        "type": submission_type,
        "source_id": source_id,
        "user_id": user_id,
        "state": submission_state,
        "title": title,
        "description": description, 
        "created_at": datetime.now().isoformat()
    }
    
    return submission

def generate_source(url, title, description, source_type, user_id):
    source_id = str(uuid.uuid4())
    
    if source_type not in valid_source_types:
        raise ValueError(f"Invalid source type. Must be one of {valid_source_types}")
    
    source = {
        "table": "source",
        "source_id": source_id,
        "url": url,
        "title": title,
        "description": description,
        "source_type": source_type,
        "user_id": user_id,
        "created_at": datetime.now().isoformat()
    }
    
    return source

def generate_topic(submission, source, topic_state=None, topic_type=None):
        topic_id = str(uuid.uuid4())
        user_id = submission['user_id']
        
        if topic_state not in valid_topic_states:
            raise ValueError(f"Invalid topic_state: {topic_state}. Must be one of {valid_topic_states}")
        
        if topic_type not in valid_topic_types:
            raise ValueError(f"Invalid topic_type: {topic_type}. Must be one of {valid_topic_types}")
        
        topic = {
            "table": "topic",
            "topic_id": topic_id,
            "title": "TopicTitle - " + submission['title'],
            "type": topic_type,
            "state": topic_state,
            "submission_id": submission['submission_id'],
            "user_id": user_id,
            "primary_source_id": source['source_id'] if source else None,
            "description": f"Topic based on: {submission['description']}",
            "rank": random.randint(1, 100),  # Random initial rank
            "created_at": datetime.now().isoformat()
        }
        
        return topic


def generate_topic_source(topic_id, source_id):
    topic_source = {
        "table": "topic_source",
        "topic_id": topic_id,
        "source_id": source_id
    }
    return topic_source

def generate_topic_tag(topic_id, tag_id):
    topic_tag = {
        "table": "topic_tag",
        "topic_id": topic_id,
        "tag_id": tag_id
    }
    return topic_tag

def generate_comment(user_id, topic_id, parent_id=None):
    comment = {
        "table": "comment",
        "comment_id": str(uuid.uuid4()),
        "user_id": user_id,
        "topic_id": topic_id,
        "parent_id": parent_id,
        "content": random.choice([
            "This new AI model shows promising results in natural language understanding.",
            "The latest cybersecurity measures seem inadequate against emerging threats.",
            "Cloud computing adoption is accelerating across various industries.",
            "Quantum computing breakthroughs could revolutionize cryptography.",
            "The ethics of AI decision-making in autonomous vehicles remain controversial.",
        ]),
        "created_at": datetime.now().isoformat()
    }
    return comment

def generate_comment_thread(user_ids, topic_id, max_depth=3, max_replies=5):
    def create_replies(parent_id, current_depth):
        if current_depth >= max_depth:
            return []

        num_replies = random.randint(1, max_replies)
        replies = []
        for _ in range(num_replies):
            comment = generate_comment(random.choice(user_ids), topic_id, parent_id)
            replies.append(comment)
            replies.extend(create_replies(comment['comment_id'], current_depth + 1))
        return replies

    root_comment = generate_comment(random.choice(user_ids), topic_id)
    thread = [root_comment]
    thread.extend(create_replies(root_comment['comment_id'], 1))
    return thread

def generate_comment_threads(user_ids, topic_ids, num_threads):
    all_threads = []
    for _ in range(num_threads):
        topic_id = random.choice(topic_ids)
        thread = generate_comment_thread(user_ids, topic_id)
        all_threads.extend(thread)
    return all_threads

def generate_topic_vote(user_id, topic_id, positive_weight=0.5):
    vote_types = [1, -1]  # 1 for upvote, -1 for downvote
    vote_type = random.choices(vote_types, weights=[positive_weight, 1 - positive_weight])[0]
    vote = {
        "table": "topic_vote",
        "vote_id": str(uuid.uuid4()),
        "user_id": user_id,
        "topic_id": topic_id,
        "vote_type": vote_type,
        "created_at": datetime.now().isoformat()
    }
    return vote

def generate_topic_votes(user_ids, topic_id, max_votes=10):
    votes = []
    num_votes = random.randint(0, max_votes)
    
    # Dictionary to keep track of user votes
    user_vote_count = {user_id: 0 for user_id in user_ids}
    
    # Generate a random positive_weight between 0.4 and 0.7
    positive_weight = random.uniform(0.4, 1.0)
    
    for _ in range(num_votes):
        # Choose a random user
        user_id = random.choice(user_ids)
        
        # Check if the user has reached the vote limit
        if user_vote_count[user_id] >= 5:
            continue
        
        # Generate a vote
        vote = generate_topic_vote(user_id, topic_id, positive_weight)
        
        # Update the user's vote count
        user_vote_count[user_id] += 1
        votes.append(vote)
    
    return votes

def generate_feedback(user_id):
    feedback_types = ["bug", "feature", "general"]
    feedback_type = random.choice(feedback_types)
    feedback = {
        "table": "feedback",
        "feedback_id": str(uuid.uuid4()),
        "type": feedback_type,
        "email": f"{user_id}@example.com",
        "title": f"{feedback_type.capitalize()} Feedback",
        "description": f"This is a {feedback_type} feedback.",
        "created_at": datetime.now().isoformat()
    }
    return feedback





def seed_data(num_users, generate_seed_file_path):
    print(f"Generating seed data to {generate_seed_file_path}")

    users_data_list = []
    for _ in range(num_users):
        user_data = generate_user_data()
        users_data_list.append(user_data)

    sdelap_user_id = str(uuid.uuid4())
    sdelap_user = {
        "table": "user",
        "user_id": sdelap_user_id,
        "username": "sdelap",
        "email": "sdelap@gmail.com",
        "password": "password",
        "markdown_bio": "I'm a software developer and a data scientist."
    }
    users_data_list.append(sdelap_user)

    user_roles_data_list = []
    user_roles_data_list.append({
        "table": "user_roles",
        "user_id": sdelap_user_id,
        "role": "admin"
    })
    print(f"Generated {len(user_roles_data_list)} roles..")


    tag_names = [
        "technology", "science", "programming", "AI", "machine learning",
        "data science", "web development", "cybersecurity", "blockchain",
        "IoT", "cloud computing", "robotics", "virtual reality",
        "augmented reality", "mobile apps", "big data", "DevOps",
        "software engineering", "UX/UI", "networking", "databases",
        "open source", "agile", "fintech", "edtech", "healthtech"
    ]

    # Generate tags for all tag names
    tag_data_list = []
    for tag_name in tag_names:
        tag = generate_tag(tag_name)
        tag_data_list.append(tag)
    
    print(f"Generated {len(tag_data_list)} tags.")

    group_names = [
        "Frontend", "Backend", "Data Science", "DevOps", "Security",
        "Mobile Development", "AI/ML", "Cloud Computing", "Emerging Technologies"
    ]
    # Generate tag groups for all group names
    tag_group_data_list = []
    for group_name in group_names:
        group = generate_tag_group(group_name)
        tag_group_data_list.append(group)    
    print(f"Generated {len(tag_group_data_list)} tag groups.")

    # Iterate over tags and tag groups to create associations
    tag_group_association_data_list = []
    used_tags = set()

    for group in tag_group_data_list:
        group_id = group['group_id']
        available_tags = [tag for tag in tag_data_list if tag['tag_id'] not in used_tags]
        
        # Ensure at least one tag per group
        num_tags = max(1, min(len(available_tags), random.randint(1, 3)))
        selected_tags = random.sample(available_tags, num_tags)
        
        for tag in selected_tags:
            tag_id = tag['tag_id']
            association = generate_tag_group_association(group_id, tag_id)
            tag_group_association_data_list.append(association)
            used_tags.add(tag_id)

    # Generate source data
    source_data = [
        {
            "url": "https://example.com/article1",
            "title": "The Future of AI",
            "description": "An in-depth look at the potential impact of artificial intelligence on various industries and society as a whole.",
            "source_type": "article"
        },
        {
            "url": "https://techblog.com/post2",
            "title": "Web Development Trends 2023",
            "description": "Exploring the latest technologies and methodologies shaping the future of web development.",
            "source_type": "website"
        },
        {
            "url": "https://news.tech/story3",
            "title": "Cybersecurity Best Practices",
            "description": "A comprehensive guide to protecting your digital assets and maintaining online security in an increasingly connected world.",
            "source_type": "article"
        },
        {
            "url": "https://devjournal.io/article4",
            "title": "Machine Learning in Healthcare",
            "description": "Examining how machine learning algorithms are revolutionizing diagnosis, treatment, and patient care in the medical field.",
            "source_type": "article"
        },
        {
            "url": "https://codeinsights.com/post5",
            "title": "The Rise of Quantum Computing",
            "description": "Delving into the principles of quantum computing and its potential to solve complex problems beyond the reach of classical computers.",
            "source_type": "website"
        },
        {
            "url": "https://techcrunch.com/article6",
            "title": "5G and IoT Revolution",
            "description": "Analyzing the synergy between 5G networks and the Internet of Things, and how it's transforming connectivity and smart devices.",
            "source_type": "article"
        },
        {
            "url": "https://wired.com/story7",
            "title": "Blockchain Beyond Cryptocurrency",
            "description": "Exploring innovative applications of blockchain technology in various sectors, from supply chain management to digital identity verification.",
            "source_type": "article"
        },
        {
            "url": "https://medium.com/tech/article8",
            "title": "Cloud Computing Innovations",
            "description": "Highlighting recent advancements in cloud technology and their impact on business scalability and efficiency.",
            "source_type": "website"
        },
        {
            "url": "https://hackernoon.com/post9",
            "title": "The Ethics of AI",
            "description": "A thought-provoking discussion on the ethical considerations surrounding artificial intelligence development and deployment.",
            "source_type": "article"
        },
        {
            "url": "https://dev.to/article10",
            "title": "DevOps Culture and Practices",
            "description": "An overview of DevOps methodologies and how they're improving software development and deployment processes.",
            "source_type": "article"
        },
        {
            "url": "https://infoq.com/news/article11",
            "title": "Big Data Analytics Trends",
            "description": "Examining the latest trends in big data analytics and how organizations are leveraging data for strategic decision-making.",
            "source_type": "article"
        },
        {
            "url": "https://thenextweb.com/post12",
            "title": "AR/VR in Education",
            "description": "Exploring the transformative potential of augmented and virtual reality technologies in educational settings.",
            "source_type": "website"
        },
        {
            "url": "https://venturebeat.com/article13",
            "title": "The Future of Work in Tech",
            "description": "Analyzing how technological advancements are reshaping the workplace and the skills needed for future tech careers.",
            "source_type": "article"
        },
        {
            "url": "https://zdnet.com/story14",
            "title": "Green Technology Innovations",
            "description": "Showcasing cutting-edge green technologies that are helping to address environmental challenges and promote sustainability.",
            "source_type": "article"
        },
        {
            "url": "https://arstechnica.com/article15",
            "title": "Robotics in Manufacturing",
            "description": "An in-depth look at how robotics and automation are revolutionizing manufacturing processes and increasing productivity.",
            "source_type": "article"
        },
        {
            "url": "https://techradar.com/news16",
            "title": "Open Source Software Trends",
            "description": "Highlighting the growing importance of open source software in modern technology stacks and development practices.",
            "source_type": "video"
        },
        {
            "url": "https://theverge.com/article17",
            "title": "Fintech Disruptions",
            "description": "Exploring how financial technology is reshaping traditional banking and financial services.",
            "source_type": "podcast"
        },
        {
            "url": "https://engadget.com/post18",
            "title": "Edge Computing Explained",
            "description": "A comprehensive guide to edge computing, its benefits, and its role in reducing latency and improving data processing efficiency.",
            "source_type": "website"
        },
        {
            "url": "https://gizmodo.com/article19",
            "title": "AI in Natural Language Processing",
            "description": "Examining the latest advancements in AI-powered natural language processing and their applications in various industries.",
            "source_type": "book"
        },
        {
            "url": "https://mashable.com/story20",
            "title": "The Impact of 3D Printing",
            "description": "Analyzing how 3D printing technology is revolutionizing manufacturing, healthcare, and other industries.",
            "source_type": "article"
        }
    ]

    source_data_list = []
    for source in source_data:
        source_entry = generate_source(
            url=source["url"],
            title=source["title"],
            description=source["description"],
            source_type=source["source_type"],
            user_id=random.choice(users_data_list)["user_id"]
        )
        source_data_list.append(source_entry)

    print(f"Generated {len(source_data_list)} sources.")

    # Generate submissions using the source_data_list
    submission_data_list = []
    for source in source_data_list:
        submission_entry = generate_submission(
            submission_type=random.choice(valid_submission_types),
            title=source["title"],
            description=f"Description based on source description: {source['description']}",
            submission_state=random.choice(valid_submission_states),
            source_id=source["source_id"],
            user_id=source["user_id"]
        )
        submission_data_list.append(submission_entry)
    print(f"Generated {len(submission_data_list)} submissions.")

    # Define titles outside the loops
    titles = [
        "New AI Model Achieves Human-Level Performance in Complex Problem Solving",
        "Breakthrough in Quantum Computing: 1000-Qubit Processor Unveiled",
        "Machine Learning Algorithm Predicts Stock Market Trends with 85% Accuracy",
        "Revolutionary Blockchain Platform Promises to Solve Scalability Issues",
        "IoT Devices Vulnerable to New Cybersecurity Threat, Experts Warn",
        "Cloud Computing Giants Announce Collaboration on Green Data Centers",
        "Robotics Startup Develops AI-Powered Prosthetic Limbs",
        "Virtual Reality Training Reduces Surgical Errors by 50%, Study Finds",
        "New Web Development Framework Promises 10x Faster Load Times",
        "Data Science Techniques Uncover Hidden Patterns in Climate Change Data"
    ]
    random.shuffle(titles)  # Shuffle the titles to ensure random selection without repetition

    # Generate 10 more submissions with no source
    for i in range(10):
        submission_type = random.choice(valid_submission_types)
        title = f"{submission_type.capitalize()}: {titles[i]}"
        description = f"This is a {submission_type} submission about {titles[i]}. It contains detailed information and insights about the topic."
        submission_entry = generate_submission(
            source_id=None,
            user_id=random.choice(users_data_list)["user_id"],
            submission_type=submission_type,            
            submission_state=random.choice(valid_submission_states),
            title=title,
            description=description
        )
        submission_data_list.append(submission_entry)
    print(f"Generated 10 additional submissions without sources. Total submissions: {len(submission_data_list)}")

    # Generate topics based on submission_data_list
    topic_data_list = []
    for submission in submission_data_list:
        topic_state = random.choice(valid_topic_states)
        topic_type = random.choice(valid_topic_types)
        
        # Find the corresponding source for this submission
        source = next((s for s in source_data_list if s['source_id'] == submission['source_id']), None)
        
        topic = generate_topic(submission, source, topic_state, topic_type)
        topic_data_list.append(topic)
    print(f"Generated {len(topic_data_list)} topics based on submissions.")


    # Associate Primary Sources
    topic_source_data_list = []
    for topic in topic_data_list:
        topic_source = generate_topic_source(topic['topic_id'], topic['primary_source_id'])
        topic_source_data_list.append(topic_source)

    # Associate Addition Sources
    topic_source_data_list = []
    for topic in topic_data_list:
        # Generate a random number of additional sources (0 to 3) for each topic
        num_additional_sources = random.randint(0, 3)
        available_sources = [s for s in source_data_list if s['source_id'] != topic['primary_source_id']]
        
        if available_sources and num_additional_sources > 0:
            additional_sources = random.sample(available_sources, min(num_additional_sources, len(available_sources)))
            for source in additional_sources:
                topic_source = generate_topic_source(topic['topic_id'], source['source_id'])
                topic_source_data_list.append(topic_source)
    print(f"Generated {len(topic_source_data_list)} topic_sources for topics.")

    # Associate Addition Sources
    topic_tag_data_list = []
    for topic in topic_data_list:
        # Generate a random number of additional sources (0 to 3) for each topic
        tag_count = random.randint(0, 3)
        
        if tag_data_list and tag_count > 0:
            tags_to_associate = random.sample(tag_data_list, min(tag_count, len(tag_data_list)))
            for tag in tags_to_associate:
                topic_tag = generate_topic_tag(topic['topic_id'], tag['tag_id'])
                topic_tag_data_list.append(topic_tag)
    # Ensure unique topic_id and tag_id combinations
    unique_topic_tags = set()
    unique_topic_tag_data_list = []
    for topic_tag in topic_tag_data_list:
        topic_tag_tuple = (topic_tag['topic_id'], topic_tag['tag_id'])
        if topic_tag_tuple not in unique_topic_tags:
            unique_topic_tags.add(topic_tag_tuple)
            unique_topic_tag_data_list.append(topic_tag)
    
    topic_tag_data_list = unique_topic_tag_data_list
    print(f"Generated {len(topic_tag_data_list)} tags for topics.")    

    # Generate comment threads for each topic
    comment_data_list = []
    for topic in topic_data_list:
        user_ids = [user['user_id'] for user in users_data_list]
        thread = generate_comment_thread(user_ids, topic['topic_id'])
        comment_data_list.extend(thread)
    print(f"Generated {len(comment_data_list)} comments for topics.")

    # Generate some additional random comments
    num_additional_comments = random.randint(10, 30)
    for _ in range(num_additional_comments):
        user_id = random.choice(users_data_list)['user_id']
        topic_id = random.choice(topic_data_list)['topic_id']
        comment = generate_comment(user_id, topic_id)
        comment_data_list.append(comment)
    print(f"Generated {num_additional_comments} additional random comments.")
    
    # Generate topic votes for each topic
    topic_vote_data_list = []
    for topic in topic_data_list:
        user_ids = [user['user_id'] for user in users_data_list]
        topic_votes = generate_topic_votes(user_ids, topic['topic_id'])
        topic_vote_data_list.extend(topic_votes)
    print(f"Generated {len(topic_vote_data_list)} votes for topics.")

    # Generate 10 feedback items
    feedback_data_list = []
    for _ in range(10):
        user_id = random.choice(users_data_list)['user_id']
        feedback = generate_feedback(user_id)
        feedback_data_list.append(feedback)
    print(f"Generated {len(feedback_data_list)} feedback items.")

    # Save seed data to example_seed.jsonl
    with open(generate_seed_file_path, 'w') as f:
        # Write users
        for user in users_data_list:
            f.write(json.dumps(user) + '\n')

        for user_role in user_roles_data_list:
            f.write(json.dumps(user_role) + '\n')
        
        # Write tags
        for tag in tag_data_list:
            f.write(json.dumps(tag) + '\n')
        
        # Write tag groups
        for group in tag_group_data_list:
            f.write(json.dumps(group) + '\n')
        
        # Write tag group associations
        for association in tag_group_association_data_list:
            f.write(json.dumps(association) + '\n')
        
        # Write sources
        for source in source_data_list:
            f.write(json.dumps(source) + '\n')
        
        # Write submissions
        for submission in submission_data_list:
            f.write(json.dumps(submission) + '\n')

        # Write topics
        for topic in topic_data_list:
            f.write(json.dumps(topic) + '\n')

        # Write topics
        for topic_source in topic_source_data_list:
            f.write(json.dumps(topic_source) + '\n')

        # Write topics
        for topic_tag in topic_tag_data_list:
            f.write(json.dumps(topic_tag) + '\n')

        for comment in comment_data_list:
            f.write(json.dumps(comment) + '\n')

        for topic_vote in topic_vote_data_list:
            f.write(json.dumps(topic_vote) + '\n')

        # Write feedback
        for feedback in feedback_data_list:
            f.write(json.dumps(feedback) + '\n')

    print(f"Seeding completed successfully to {generate_seed_file_path}.")


def main():
    load_dotenv()
    generate_seed_file_path = os.getenv('SEED_FILE_GENERATOR_FILENAME', './seed_data/example_seed.jsonl')
    seed_data(num_users=5, generate_seed_file_path=generate_seed_file_path)
    

if __name__ == "__main__":
    main()

import os
import json
import re
from datetime import datetime

# Path definitions
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
POSTS_DIR = os.path.join(ROOT_DIR, 'blog', 'posts')
OUTPUT_JSON = os.path.join(ROOT_DIR, 'blog', 'posts.json')
OUTPUT_RSS = os.path.join(ROOT_DIR, 'feed.xml')

def parse_date(date_str):
    # Try different formats
    formats = [
        "%B %d, %Y",  # June 6, 2026
        "%B %d %Y",
        "%Y-%m-%d",   # 2026-06-06
        "%d-%m-%Y",
        "%b %d, %Y"   # Jun 6, 2026
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    # Fallback to current date if parsing fails
    print(f"Warning: could not parse date '{date_str}', using current time.")
    return datetime.now()

def compile_blog():
    posts = []
    
    if not os.path.exists(POSTS_DIR):
        print(f"Error: Posts directory {POSTS_DIR} does not exist.")
        return
        
    for filename in os.listdir(POSTS_DIR):
        if filename.endswith('.md'):
            post_id = os.path.splitext(filename)[0]
            filepath = os.path.join(POSTS_DIR, filename)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            title = post_id.replace('-', ' ').title()
            date_str = "June 6, 2026"
            description = ""
            
            # Simple Jekyll YAML Front Matter Parsing
            if content.startswith('---'):
                parts = content.split('---')
                if len(parts) >= 3:
                    yaml_content = parts[1]
                    body_content = '---'.join(parts[2:])
                    
                    # Read YAML lines
                    for line in yaml_content.split('\n'):
                        if ':' in line:
                            key, val = line.split(':', 1)
                            key = key.strip().lower()
                            val = val.strip().strip("'\"")
                            if key == 'title':
                                title = val
                            elif key == 'date':
                                date_str = val
                            elif key == 'description':
                                description = val
                                
                    # If description is empty, auto-generate it from body content
                    if not description:
                        # Strip markdown tags and fetch first few sentences
                        text_only = re.sub(r'\[.*?\]\(.*?\)', '', body_content)
                        text_only = re.sub(r'[#*`_\-\[\]]', '', text_only)
                        words = text_only.split()
                        description = ' '.join(words[:40]) + '...'
            
            parsed_date = parse_date(date_str)
            
            posts.append({
                'id': post_id,
                'title': title,
                'date': date_str,
                'parsed_date': parsed_date,
                'description': description
            })
            
    # Sort posts by date descending
    posts.sort(key=lambda x: x['parsed_date'], reverse=True)
    
    # Write JSON output (excluding the datetime object)
    json_posts = []
    for p in posts:
        json_posts.append({
            'id': p['id'],
            'title': p['title'],
            'date': p['date'],
            'description': p['description']
        })
        
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(json_posts, f, indent=2, ensure_ascii=False)
    print(f"Successfully generated {OUTPUT_JSON} with {len(posts)} posts.")
    
    # Generate feed.xml
    rss_items = []
    for p in posts:
        # Format date for RSS: RFC 822 format (e.g. Sat, 06 Jun 2026 00:00:00 +0530)
        rss_date = p['parsed_date'].strftime("%a, %d %b %Y %H:%M:%S +0530")
        
        rss_items.append(f"""    <item>
      <title>{p['title']}</title>
      <link>https://surendrareddy.in/blog/view.html?post={p['id']}</link>
      <guid isPermaLink="true">https://surendrareddy.in/blog/view.html?post={p['id']}</guid>
      <pubDate>{rss_date}</pubDate>
      <description><![CDATA[{p['description']}]]></description>
    </item>""")
    
    rss_content = f"""<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>Surendra Reddy's Blog</title>
    <link>https://surendrareddy.in/blog/</link>
    <description>Thoughts about programming, robotics, and whatever else is on my mind</description>
    <language>en-us</language>
    <atom:link href="https://surendrareddy.in/feed.xml" rel="self" type="application/rss+xml" />
    <lastBuildDate>{datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0530")}</lastBuildDate>
{chr(10).join(rss_items)}
  </channel>
</rss>"""

    with open(OUTPUT_RSS, 'w', encoding='utf-8') as f:
        f.write(rss_content)
    print(f"Successfully generated {OUTPUT_RSS}.")

if __name__ == '__main__':
    compile_blog()

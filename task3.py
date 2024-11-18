import re
from wordcloud import WordCloud
import io
import base64
from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'mysecretkey'  # Secret key for form handling (needed by Flask-WTF)

# Example posts (with user attributes like age, gender, and region)
posts = [
    {"post_id": 1, "content": "I love technology and innovation", "user_id": 1, "comments": 5, "likes": 10, "age": 25, "gender": "female", "region": "US"},
    {"post_id": 2, "content": "Politics is getting crazy these days", "user_id": 2, "comments": 3, "likes": 20, "age": 30, "gender": "male", "region": "UK"},
    {"post_id": 3, "content": "The tech industry is booming in the US", "user_id": 1, "comments": 8, "likes": 15, "age": 25, "gender": "female", "region": "US"},
    {"post_id": 4, "content": "Looking forward to new tech gadgets", "user_id": 3, "comments": 2, "likes": 25, "age": 40, "gender": "male", "region": "CA"},
    {"post_id": 5, "content": "New innovation in AI is here", "user_id": 2, "comments": 4, "likes": 12, "age": 30, "gender": "male", "region": "UK"},
    {"post_id": 6, "content": "I am fascinated by space exploration and science", "user_id": 4, "comments": 10, "likes": 35, "age": 28, "gender": "female", "region": "AU"},
    {"post_id": 7, "content": "Climate change is the most pressing issue of our time", "user_id": 5, "comments": 7, "likes": 50, "age": 35, "gender": "male", "region": "US"},
    {"post_id": 8, "content": "Reading books about history and philosophy is my favorite hobby", "user_id": 6, "comments": 12, "likes": 20, "age": 50, "gender": "female", "region": "UK"},
    {"post_id": 9, "content": "I recently started learning about data science and machine learning", "user_id": 7, "comments": 5, "likes": 18, "age": 22, "gender": "male", "region": "IN"},
    {"post_id": 10, "content": "Traveling to new countries is the best way to learn about cultures", "user_id": 8, "comments": 8, "likes": 40, "age": 29, "gender": "female", "region": "CA"},
]

# Preprocess post content
def preprocess_content(content):
    
    # Cleans and normalizes the text content by: Converting to lowercase & Removing non-word characters
    content = content.lower()
    content = re.sub(r'\W+', ' ', content)  # Remove non-word characters
    return content

# Helper function to check if a post passes the filters
def passes_filters(post, keyword_filter=None, user_filter=None):
    
    #Checks if a post meets the filter criteria.

    # Apply user filters (age, gender, region)
    if user_filter:
        if 'age' in user_filter and user_filter['age'] and post['age'] not in user_filter['age']:
            return False
        if 'gender' in user_filter and user_filter['gender'] and post['gender'].lower() not in user_filter['gender']:
            return False
        if 'region' in user_filter and user_filter['region'] and post['region'].lower() not in user_filter['region']:
            return False

    # Apply keyword filters
    if keyword_filter:
        post_content = preprocess_content(post['content'])
        if 'exclude' in keyword_filter and keyword_filter['exclude']:
            if any(ex_kw in post_content.split() for ex_kw in keyword_filter['exclude']):
                return False
        if 'include' in keyword_filter and keyword_filter['include']:
            if not any(in_kw in post_content.split() for in_kw in keyword_filter['include']):
                return False

    return True

# Generate word frequencies from posts with filters
def generate_word_frequencies(posts, keyword_filter=None, user_filter=None):
    
    # Generates word frequencies from the provided posts, filtered by user and keyword filters.
    word_count = {}

    for post in posts:
        # Check if post passes the filters
        if not passes_filters(post, keyword_filter, user_filter):
            continue

        # Preprocess and count words
        words = preprocess_content(post['content']).split()
        for word in words:
            if word in word_count:
                word_count[word] += 1
            else:
                word_count[word] = 1

    return word_count

# Generate word cloud image as base64
def generate_word_cloud_image(word_frequencies):
    
    # Generates a word cloud image from word frequencies and encodes it as base64.
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(word_frequencies)
    img_io = io.BytesIO()
    wordcloud.to_image().save(img_io, 'PNG')
    img_io.seek(0)
    img_base64 = base64.b64encode(img_io.getvalue()).decode('utf-8')
    return img_base64

# Define form for user input (filters)
class FilterForm(FlaskForm):
    include_keywords = StringField('Include Keywords (comma-separated):')
    exclude_keywords = StringField('Exclude Keywords (comma-separated):')
    age_filter = StringField('Filter by Age (comma-separated):')
    gender_filter = StringField('Filter by Gender (comma-separated):')
    region_filter = StringField('Filter by Region (comma-separated):')
    submit = SubmitField('Generate Word Cloud')

@app.route("/", methods=["GET", "POST"])
def index():
    form = FilterForm()

    # Initial word cloud (before applying filters)
    initial_word_frequencies = generate_word_frequencies(posts)
    initial_word_cloud_image = generate_word_cloud_image(initial_word_frequencies)

    if form.validate_on_submit():
        try:
            # Get user inputs for filtering
            include_keywords = [kw.strip().lower() for kw in (form.include_keywords.data or "").split(",") if kw.strip()]
            exclude_keywords = [kw.strip().lower() for kw in (form.exclude_keywords.data or "").split(",") if kw.strip()]
            age_filter = [int(age.strip()) for age in (form.age_filter.data or "").split(",") if age.strip().isdigit()]
            gender_filter = [gender.strip().lower() for gender in (form.gender_filter.data or "").split(",") if gender.strip()]
            region_filter = [region.strip().lower() for region in (form.region_filter.data or "").split(",") if region.strip()]

            # Create filter dictionaries
            keyword_filter = {'include': include_keywords, 'exclude': exclude_keywords}
            user_filter = {'age': age_filter, 'gender': gender_filter, 'region': region_filter}

            # Generate filtered word frequencies
            word_frequencies = generate_word_frequencies(posts, keyword_filter=keyword_filter, user_filter=user_filter)

            # Generate filtered word cloud image
            word_cloud_image = generate_word_cloud_image(word_frequencies)

            # Render page with filtered word cloud
            return render_template("index.html", form=form, word_cloud_image=word_cloud_image, initial_word_cloud_image=initial_word_cloud_image)

        except Exception as e:
            print("Error while processing filters:", str(e))
            return "An error occurred while processing your filters. Please check your inputs and try again."

    # Render page with the initial word cloud (no filters applied)
    return render_template("index.html", form=form, initial_word_cloud_image=initial_word_cloud_image)

if __name__ == "__main__":
    app.run(debug=True)

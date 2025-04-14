from flask import Flask, render_template, request, redirect, url_for, session
import requests

app = Flask(__name__)
app.secret_key = "music_app_secret_key"

# This is the url of the apigateway that is used to call the lambda functions
API_BASE_URL = "not sharing this lol"

# Routes
@app.route("/")
def home():
    if 'email' in session:
        return redirect(url_for('main'))
    return redirect(url_for('login')) #default is login screen if there is no session

@app.route("/login", methods=['GET', 'POST'])
def login():
    error_message = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        try:
            # Call the authentication Lambda function via API Gateway
            response = requests.post(
                f"{API_BASE_URL}/auth/login",
                json={
                    'email': email,
                    'password': password
                }
            )
            
            response_data = response.json()
            
            if response.status_code == 200 and response_data.get('success'):
                session['email'] = email
                session['username'] = response_data.get('user_name')
                return redirect(url_for('main'))
            else:
                error_message = response_data.get('message', "Invalid email or password")
        except Exception as e:
            print("Error:", str(e))
            error_message = f"Login error: {str(e)}"
    
    return render_template('index.html', error_message=error_message)

@app.route("/register", methods=['GET', 'POST'])
def register():
    error_message = None
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        
        try:
            # Call the registration Lambda function via API Gateway
            response = requests.post(
                f"{API_BASE_URL}/auth/register",
                json={
                    'email': email,
                    'user_name': username,
                    'password': password
                }
            )
            
            response_data = response.json()
            
            if response.status_code == 200 and response_data.get('success'):
                return redirect(url_for('login'))
            else:
                error_message = response_data.get('message', "Registration failed")
        except Exception as e:
            print("Error:", str(e))
            error_message = f"Registration error: {str(e)}"
    
    return render_template('register.html', error_message=error_message)

@app.route("/main")
def main():
    if 'email' not in session:
        return redirect(url_for('login'))
    
    # Get the user's subscriptions from the subscription Lambda
    try:
        response = requests.get(
            f"{API_BASE_URL}/subscriptions",
            params={'email': session['email']},
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            subscriptions = response.json().get('subscriptions', [])
        else:
            subscriptions = []
            print("Error fetching subscriptions:", response.text)
    except Exception as e:
        print("Error fetching subscriptions:", str(e))
        subscriptions = []
    
    return render_template('main.html', 
                         username=session['username'],
                         subscriptions=subscriptions)

@app.route("/music", methods=['POST'])
def search():
    if 'email' not in session:
        return redirect(url_for('login'))
    
    # Get search criteria
    title = request.form.get('title', '')
    artist = request.form.get('artist', '')
    album = request.form.get('album', '')
    year = request.form.get('year', '')
    
    # Check if at least one field is filled
    if not any([title, artist, album, year]):
        return render_template('main.html', 
                             username=session['username'],
                             subscriptions=[],
                             search_results=[],
                             search_error="Please enter at least one search criteria.")
    
    try:
        # Call the music search Lambda via API Gateway
        response = requests.post(
            f"{API_BASE_URL}/music",
            json={
                'title': title,
                'artist': artist,
                'album': album,
                'year': year
            }
        )
        
        response_data = response.json()
        
        if response.status_code == 200:
            search_results = response_data.get('results', [])
            search_error = None if search_results else "No result is retrieved. Please query again"
        else:
            search_results = []
            search_error = response_data.get('message', "Error during search")
        
        # Get user's current subscriptions for the main page
        subscriptions_response = requests.get(
            f"{API_BASE_URL}/subscriptions",
            params={'email': session['email']},
            headers={'Content-Type': 'application/json'}
        )
        
        if subscriptions_response.status_code == 200:
            subscriptions = subscriptions_response.json().get('subscriptions', [])
        else:
            subscriptions = []
        
        return render_template('main.html', 
                             username=session['username'],
                             subscriptions=subscriptions,
                             search_results=search_results,
                             search_error=search_error)
    
    except Exception as e:
        print("Search error:", str(e))
        return render_template('main.html', 
                             username=session['username'],
                             subscriptions=[],
                             search_results=[],
                             search_error=f"Error during search: {str(e)}")

@app.route("/subscriptions", methods=['POST'])
def subscribe():
    if 'email' not in session:
        return redirect(url_for('login'))
    
    title = request.form.get('title')
    artist = request.form.get('artist')
    album = request.form.get('album', 'Unknown')
    year = int(request.form.get('year'))
    image_url = request.form.get('image_url', '')

    print("Subscription details:", title, artist, album, year, session['email'])
    
    try:
        # Call the subscription Lambda via API Gateway
        response = requests.post(
            f"{API_BASE_URL}/subscriptions",
            json={
                'email': session['email'],
                'title': title,
                'artist': artist,
                'album': album,
                'year': year,
                'image_url': image_url
            }
        )

        print("Subscription API response:", response.status_code, response.text)
    
    except Exception as e:
        print("Subscription error:", str(e))
    
    return redirect(url_for('main'))

@app.route("/unsubscribe", methods=['POST'])
def remove_subscription():
    if 'email' not in session:
        return redirect(url_for('login'))
    
    title = request.form.get('title')
    year = int(request.form.get('year'))
    
    try:
        response = requests.delete(
            f"{API_BASE_URL}/subscriptions",
            json={
                'email': session['email'],
                'title': title,
                'year': year
            }
        )
        
        print("Unsubscribe API response:", response.status_code, response.text)
    
    except Exception as e:
        print("Error removing subscription:", str(e))
    
    return redirect(url_for('main'))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
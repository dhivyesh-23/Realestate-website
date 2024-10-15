import os
from flask import Flask, render_template, redirect, request, url_for, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from models import get_employee, add_property, get_properties

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Flask-Login setup
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Upload configuration
UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Employee class for authentication
class Employee(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

# Load user for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    user = get_employee(user_id)
    if user:
        return Employee(user_id, user['username'])
    return None

# Helper function to check if uploaded file is an allowed image format
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = get_employee(username)
        if user and check_password_hash(user['password'], password):
            employee = Employee(user['_id'], user['username'])
            login_user(employee)
            return redirect(url_for('admin'))
        return 'Invalid credentials'
    return render_template('login.html')

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Admin page for managing properties (requires login)
@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        price = request.form['price']

        # Handle image file
        if 'image' not in request.files:
            return 'No image part'
        file = request.files['image']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_url = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            # Add property to the database
            add_property({
                'title': title,
                'description': description,
                'price': price,
                'image': image_url
            })
            return redirect(url_for('admin'))
    
    # Render admin page with the list of properties
    return render_template('admin.html', properties=get_properties())

# Run the app
if __name__ == "__main__":
    app.run(debug=True)

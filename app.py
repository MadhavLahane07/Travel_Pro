from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from werkzeug.security import generate_password_hash, check_password_hash
import random  # Add this at the top with other imports

app = Flask(__name__, 
    template_folder='templates',    # Explicitly set template folder
    static_folder='static'         # Explicitly set static folder
)

# Configuration
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///travel.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True  # Enable debug mode

# Ensure the instance folder exists
try:
    os.makedirs(app.instance_path)
except OSError:
    pass

# Initialize database
db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    travel_plans = db.relationship('TravelPlan', backref='user', lazy=True)
    saved_destinations = db.relationship('UserDestination', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Destination(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    bookings = db.relationship('Booking', backref='destination', lazy=True)
    user_destinations = db.relationship('UserDestination', backref='destination', lazy=True)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    destination_id = db.Column(db.Integer, db.ForeignKey('destination.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class TravelPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    destinations = db.relationship('UserDestination', backref='travel_plan', lazy=True)

class UserDestination(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    destination_id = db.Column(db.Integer, db.ForeignKey('destination.id'), nullable=False)
    travel_plan_id = db.Column(db.Integer, db.ForeignKey('travel_plan.id'))
    notes = db.Column(db.Text)
    visit_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def get_sample_destinations():
    all_destinations = [
        {
            'name': 'Bali, Indonesia',
            'description': 'Experience the perfect blend of culture and nature in Bali.',
            'price': 1999.99,
            'image_url': 'https://images.unsplash.com/photo-1573790387438-4da905039392?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2825&q=80'
        },
        {
            'name': 'Santorini, Greece',
            'description': 'Discover the stunning white architecture and blue waters of Santorini.',
            'price': 2799.99,
            'image_url': 'https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2787&q=80'
        },
        {
            'name': 'Kyoto, Japan',
            'description': 'Immerse yourself in traditional Japanese culture and temples.',
            'price': 2999.99,
            'image_url': 'https://images.unsplash.com/photo-1624253321171-1be53e12f5f4?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2786&q=80'
        },
        {
            'name': 'Venice, Italy',
            'description': 'Experience the romance of Venice\'s canals and historic architecture.',
            'price': 2599.99,
            'image_url': 'https://images.unsplash.com/photo-1514890547357-a9ee288728e0?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2940&q=80'
        },
        {
            'name': 'Machu Picchu, Peru',
            'description': 'Explore the ancient Incan citadel in the Andes Mountains.',
            'price': 3299.99,
            'image_url': 'https://images.unsplash.com/photo-1587595431973-160d0d94add1?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2940&q=80'
        },
        {
            'name': 'Maldives',
            'description': 'Relax in paradise with overwater bungalows and crystal-clear waters.',
            'price': 3999.99,
            'image_url': 'https://images.unsplash.com/photo-1514282401047-d79a71a590e8?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2865&q=80'
        },
        {
            'name': 'Swiss Alps',
            'description': 'Experience the majesty of the Swiss Alps with stunning mountain views.',
            'price': 2899.99,
            'image_url': 'https://images.unsplash.com/photo-1530122037265-a5f1f91d3b99?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2940&q=80'
        },
        {
            'name': 'Cape Town, South Africa',
            'description': 'Discover the beauty of Table Mountain and coastal landscapes.',
            'price': 2499.99,
            'image_url': 'https://images.unsplash.com/photo-1580060839134-75a5edca2e99?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2942&q=80'
        },
        {
            'name': 'Dubai, UAE',
            'description': 'Experience luxury and innovation in this modern desert metropolis.',
            'price': 2999.99,
            'image_url': 'https://images.unsplash.com/photo-1512453979798-5ea266f8880c?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2940&q=80'
        },
        {
            'name': 'Great Barrier Reef, Australia',
            'description': 'Dive into the world\'s largest coral reef system.',
            'price': 3199.99,
            'image_url': 'https://images.unsplash.com/photo-1582967788606-a171c1080cb0?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2940&q=80'
        },
        {
            'name': 'Paris, France',
            'description': 'Experience the romance and culture of the City of Light.',
            'price': 2699.99,
            'image_url': 'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2946&q=80'
        },
        {
            'name': 'Iceland',
            'description': 'Witness the Northern Lights and dramatic landscapes.',
            'price': 3499.99,
            'image_url': 'https://images.unsplash.com/photo-1504893524553-b855bce32c67?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2940&q=80'
        }
    ]
    # Randomly select 6 destinations
    return random.sample(all_destinations, 6)

# Create database tables and add sample data
def init_db():
    with app.app_context():
        # Create database directory if it doesn't exist
        db_path = os.path.dirname(app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', ''))
        if db_path and not os.path.exists(db_path):
            os.makedirs(db_path)
            
        db.create_all()
        
        # Clear existing destinations
        Destination.query.delete()
        
        # Add randomly selected destinations
        sample_destinations = get_sample_destinations()
        for dest_data in sample_destinations:
            destination = Destination(
                name=dest_data['name'],
                description=dest_data['description'],
                price=dest_data['price'],
                image_url=dest_data['image_url']
            )
            db.session.add(destination)
        
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error adding sample data: {e}")

@app.before_request
def refresh_destinations():
    # Only refresh destinations on the destinations page and home page
    if request.endpoint in ['destinations', 'home']:
        try:
            # Clear existing destinations
            Destination.query.delete()
            
            # Add new random destinations
            sample_destinations = get_sample_destinations()
            for dest_data in sample_destinations:
                destination = Destination(
                    name=dest_data['name'],
                    description=dest_data['description'],
                    price=dest_data['price'],
                    image_url=dest_data['image_url']
                )
                db.session.add(destination)
            
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error refreshing destinations: {e}")

# Routes
@app.route('/')
@app.route('/home')
def home():
    try:
        destinations = Destination.query.all()
        return render_template('index.html', destinations=destinations)
    except Exception as e:
        app.logger.error(f"Error in home route: {e}")
        return render_template('500.html'), 500

@app.route('/destinations')
def destinations():
    try:
        destinations = Destination.query.all()
        user = None
        if 'user_id' in session:
            user = User.query.get(session['user_id'])
        return render_template('destinations.html', destinations=destinations, user=user)
    except Exception as e:
        app.logger.error(f"Error in destinations route: {e}")
        return render_template('500.html'), 500

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/booking/<int:destination_id>', methods=['GET', 'POST'])
def booking(destination_id):
    try:
        destination = Destination.query.get_or_404(destination_id)
        if request.method == 'POST':
            booking = Booking(
                destination_id=destination_id,
                name=request.form['name'],
                email=request.form['email'],
                date=datetime.strptime(request.form['date'], '%Y-%m-%d').date()
            )
            db.session.add(booking)
            db.session.commit()
            flash('Booking successful! We will contact you soon.', 'success')
            return redirect(url_for('home'))
        return render_template('booking.html', destination=destination)
    except Exception as e:
        app.logger.error(f"Error in booking route: {e}")
        db.session.rollback()
        return render_template('500.html'), 500

@app.route('/test')
def test():
    return render_template('test.html')

# New routes for user management and travel planning
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return redirect(url_for('register'))
            
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return redirect(url_for('register'))
            
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
            
        flash('Invalid username or password', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out', 'success')
    return redirect(url_for('home'))

@app.route('/my-plans')
def my_plans():
    if 'user_id' not in session:
        flash('Please login to view your plans', 'error')
        return redirect(url_for('login'))
        
    user = User.query.get(session['user_id'])
    return render_template('my_plans.html', travel_plans=user.travel_plans)

@app.route('/create-plan', methods=['GET', 'POST'])
def create_plan():
    if 'user_id' not in session:
        flash('Please login to create a plan', 'error')
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        plan = TravelPlan(
            user_id=session['user_id'],
            title=request.form['title'],
            description=request.form['description'],
            start_date=datetime.strptime(request.form['start_date'], '%Y-%m-%d').date(),
            end_date=datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
        )
        db.session.add(plan)
        db.session.commit()
        flash('Travel plan created successfully!', 'success')
        return redirect(url_for('my_plans'))
        
    return render_template('create_plan.html')

@app.route('/save-destination/<int:destination_id>', methods=['POST'])
def save_destination(destination_id):
    if 'user_id' not in session:
        flash('Please login to save destinations', 'error')
        return redirect(url_for('login'))
        
    plan_id = request.form.get('plan_id')
    notes = request.form.get('notes')
    visit_date = request.form.get('visit_date')
    
    user_dest = UserDestination(
        user_id=session['user_id'],
        destination_id=destination_id,
        travel_plan_id=plan_id,
        notes=notes,
        visit_date=datetime.strptime(visit_date, '%Y-%m-%d').date() if visit_date else None
    )
    
    db.session.add(user_dest)
    db.session.commit()
    flash('Destination saved to your plan!', 'success')
    return redirect(url_for('destinations'))

@app.route('/delete-plan/<int:plan_id>', methods=['POST'])
def delete_plan(plan_id):
    if 'user_id' not in session:
        flash('Please login to delete plans', 'error')
        return redirect(url_for('login'))
        
    plan = TravelPlan.query.get_or_404(plan_id)
    
    # Check if the plan belongs to the current user
    if plan.user_id != session['user_id']:
        flash('You do not have permission to delete this plan', 'error')
        return redirect(url_for('my_plans'))
    
    try:
        # Delete associated destinations first
        UserDestination.query.filter_by(travel_plan_id=plan_id).delete()
        db.session.delete(plan)
        db.session.commit()
        flash('Travel plan deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting plan. Please try again.', 'error')
        
    return redirect(url_for('my_plans'))

@app.route('/destination/<int:destination_id>')
def destination_details(destination_id):
    try:
        destination = Destination.query.get_or_404(destination_id)
        user = None
        if 'user_id' in session:
            user = User.query.get(session['user_id'])
        return render_template('destination_details.html', destination=destination, user=user)
    except Exception as e:
        app.logger.error(f"Error in destination_details route: {e}")
        return render_template('500.html'), 500

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    app.logger.error(f'Page not found: {request.url}')
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f'Server Error: {error}')
    db.session.rollback()
    return render_template('500.html'), 500

# Create error templates if they don't exist
def create_error_templates():
    templates_dir = os.path.join(app.root_path, 'templates')
    
    # 404 template
    error_404_path = os.path.join(templates_dir, '404.html')
    if not os.path.exists(error_404_path):
        with open(error_404_path, 'w') as f:
            f.write("""{% extends "base.html" %}
{% block content %}
<div class="container py-5 text-center">
    <h1>404 - Page Not Found</h1>
    <p>The page you are looking for does not exist.</p>
    <a href="{{ url_for('home') }}" class="btn btn-primary">Go Home</a>
</div>
{% endblock %}""")
    
    # 500 template
    error_500_path = os.path.join(templates_dir, '500.html')
    if not os.path.exists(error_500_path):
        with open(error_500_path, 'w') as f:
            f.write("""{% extends "base.html" %}
{% block content %}
<div class="container py-5 text-center">
    <h1>500 - Internal Server Error</h1>
    <p>Something went wrong on our end. Please try again later.</p>
    <a href="{{ url_for('home') }}" class="btn btn-primary">Go Home</a>
</div>
{% endblock %}""")

if __name__ == '__main__':
    create_error_templates()  # Create error templates
    init_db()  # Initialize database and add sample data
    app.run(debug=True) 
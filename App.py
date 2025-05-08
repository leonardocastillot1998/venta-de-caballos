from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///horses.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

db = SQLAlchemy(app)

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Models
class Horse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(200))
    
class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    horse_id = db.Column(db.Integer, db.ForeignKey('horse.id'), nullable=False)
    horse = db.relationship('Horse', backref=db.backref('carts', lazy=True))

# Routes
@app.route('/')
def index():
    horses = Horse.query.all()
    return render_template('index.html', horses=horses)

@app.route('/add', methods=['GET', 'POST'])
def add_horse():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = float(request.form['price'])
        
        # Handle file upload
        if 'image' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        file = request.files['image']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
            
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            horse = Horse(name=name, description=description, price=price, image=filename)
            db.session.add(horse)
            db.session.commit()
            flash('Horse added successfully!')
            return redirect(url_for('index'))
            
    return render_template('add_horse.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_horse(id):
    horse = Horse.query.get_or_404(id)
    
    if request.method == 'POST':
        horse.name = request.form['name']
        horse.description = request.form['description']
        horse.price = float(request.form['price'])
        
        # Handle file upload if new image is provided
        if 'image' in request.files and request.files['image'].filename != '':
            file = request.files['image']
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            horse.image = filename
            
        db.session.commit()
        flash('Horse updated successfully!')
        return redirect(url_for('index'))
        
    return render_template('edit_horse.html', horse=horse)

@app.route('/delete/<int:id>')
def delete_horse(id):
    horse = Horse.query.get_or_404(id)
    db.session.delete(horse)
    db.session.commit()
    flash('Horse deleted successfully!')
    return redirect(url_for('index'))

@app.route('/add_to_cart/<int:horse_id>')
def add_to_cart(horse_id):
    cart_item = Cart(horse_id=horse_id)
    db.session.add(cart_item)
    db.session.commit()
    flash('Horse added to cart!')
    return redirect(url_for('index'))

@app.route('/cart')
def view_cart():
    cart_items = Cart.query.all()
    return render_template('cart.html', cart_items=cart_items)

@app.route('/remove_from_cart/<int:id>')
def remove_from_cart(id):
    cart_item = Cart.query.get_or_404(id)
    db.session.delete(cart_item)
    db.session.commit()
    flash('Horse removed from cart!')
    return redirect(url_for('cart'))

# Create database
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)

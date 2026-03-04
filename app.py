from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)

# Database configuration
database_url = os.environ.get('DATABASE_URL', 'sqlite:///students.db')
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Student Model with marks field
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    sap_id = db.Column(db.String(11), unique=True, nullable=False)
    gmail = db.Column(db.String(100), unique=True, nullable=False)
    marks = db.Column(db.Float, nullable=False)  # New marks field
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'student_name': self.student_name,
            'gender': self.gender,
            'sap_id': self.sap_id,
            'gmail': self.gmail,
            'marks': self.marks,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

# Create tables
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    students = Student.query.order_by(Student.student_name).all()
    return render_template('index.html', students=students)

@app.route('/add_student', methods=['POST'])
def add_student():
    try:
        student_name = request.form['student_name']
        gender = request.form['gender']
        sap_id = request.form['sap_id']
        gmail = request.form['gmail']
        marks = float(request.form['marks'])  # Get marks from form
        
        # Validation
        if len(sap_id) != 11 or not sap_id.isdigit():
            return jsonify({'error': 'SAP ID must be exactly 11 digits'}), 400
        
        if not gmail.endswith('@gmail.com'):
            return jsonify({'error': 'Email must be a Gmail address'}), 400
            
        if marks < 0 or marks > 100:
            return jsonify({'error': 'Marks must be between 0 and 100'}), 400
        
        new_student = Student(
            student_name=student_name,
            gender=gender,
            sap_id=sap_id,
            gmail=gmail,
            marks=marks  # Add marks to new student
        )
        
        db.session.add(new_student)
        db.session.commit()
        
        return jsonify({'success': True, 'student': new_student.to_dict()})
    
    except ValueError as e:
        return jsonify({'error': 'Invalid marks value'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/get_student/<int:student_id>')
def get_student(student_id):
    student = Student.query.get_or_404(student_id)
    return jsonify(student.to_dict())

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
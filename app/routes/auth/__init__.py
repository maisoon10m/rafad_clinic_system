"""
Authentication routes for Rafad Clinic System
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, session, abort
from flask_login import login_user, logout_user, login_required, current_user
from app.models import db, User
from app.forms.auth import LoginForm, RegistrationForm, PasswordResetRequestForm, PasswordResetForm
from sqlalchemy.exc import IntegrityError

# Create blueprint
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login route"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            # Update last login time
            user.update_last_login()
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                if user.role == 'admin':
                    next_page = url_for('admin.dashboard')
                elif user.role == 'doctor':
                    next_page = url_for('doctor.dashboard')
                else:
                    next_page = url_for('patient.dashboard')
            return redirect(next_page)
        flash('Invalid email or password.', 'danger')
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """User logout route"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration route with role selection"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            user = User(
                username=form.username.data,
                email=form.email.data,
                role=form.role.data  # Use the selected role
            )
            user.password = form.password.data
            db.session.add(user)
            db.session.flush()  # Generate user_id for the foreign key relationships
            
            # Create the appropriate profile based on role
            if form.role.data == 'patient':
                from app.models.patient import Patient
                patient = Patient(
                    user_id=user.id,
                    first_name=form.first_name.data,
                    last_name=form.last_name.data,
                    phone=form.phone.data,
                    date_of_birth=form.date_of_birth.data,
                    gender=form.gender.data,
                    address=form.address.data,
                    medical_history=form.medical_history.data if form.medical_history.data else None
                )
                db.session.add(patient)
            elif form.role.data == 'doctor':
                from app.models.doctor import Doctor
                doctor = Doctor(
                    user_id=user.id,
                    first_name=form.first_name.data,
                    last_name=form.last_name.data,
                    specialization=form.specialization.data,
                    phone=form.phone.data,
                    qualification=form.qualification.data,
                    bio=form.bio.data if form.bio.data else None,
                    experience_years=int(form.experience_years.data) if form.experience_years.data else 0
                )
                db.session.add(doctor)
            
            db.session.commit()
            flash(f'You have registered successfully as a {form.role.data.capitalize()}! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        except IntegrityError:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
            
    return render_template('auth/register.html', form=form)


@auth_bp.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    """Request password reset route"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            # In a real application, you would send an email with a reset link
            # For now, we'll just store a token in the session for demo purposes
            token = user.generate_reset_token()
            session['reset_token'] = token
            session['reset_email'] = user.email
            flash('Password reset instructions have been sent to your email.', 'info')
            return redirect(url_for('auth.login'))
        flash('If that email address is in our system, we have sent you instructions to reset your password.', 'info')
    return render_template('auth/reset_request.html', form=form)


@auth_bp.route('/create-admin', methods=['GET', 'POST'])
def create_admin():
    """Create admin account route - only accessible if no admin exists"""
    # Check if admin already exists
    admin_exists = User.query.filter_by(role='admin').first()
    if admin_exists:
        flash('An administrator already exists in the system.', 'danger')
        return redirect(url_for('auth.login'))
    
    form = RegistrationForm()
    # Remove role field from validation since we're forcing admin role
    delattr(form, 'role')
    
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            role='admin'  # Force admin role
        )
        user.password = form.password.data
        db.session.add(user)
        
        try:
            db.session.commit()
            flash('Administrator account has been created! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        except:
            db.session.rollback()
            flash('An error occurred during admin creation. Please try again.', 'danger')
            
    return render_template('auth/create_admin.html', form=form)


@auth_bp.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    """Password reset with token route"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    # In a real application, verify the token
    # For demo, check if it matches the session token
    if 'reset_token' not in session or token != session.get('reset_token'):
        flash('The password reset link is invalid or has expired.', 'danger')
        return redirect(url_for('main.index'))
    
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=session.get('reset_email')).first()
        if user:
            user.password = form.password.data
            db.session.commit()
            session.pop('reset_token', None)
            session.pop('reset_email', None)
            flash('Your password has been updated.', 'success')
            return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


@auth_bp.route('/profile')
@login_required
def profile():
    """User profile route"""
    # This is a placeholder - each role will have its own profile view
    if current_user.role == 'admin':
        return redirect(url_for('admin.profile'))
    elif current_user.role == 'doctor':
        return redirect(url_for('doctor.profile'))
    else:
        return redirect(url_for('patient.profile'))
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, make_response
import json
import os
import hashlib
from datetime import datetime, date, timedelta
from collections import defaultdict
import csv
import re
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key_here_change_this_in_production'
app.permanent_session_lifetime = timedelta(hours=24)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USERS_FILE = os.path.join(BASE_DIR, 'users.json')
FIELDS = ['Date', 'Category', 'Sub-Category', 'Amount', 'Remarks']

COLOR_MAP = {
    "Food": "#FF9999",
    "Rent": "#FFB266",
    "Mobile Recharge": "#FFFF99",
    "Health": "#99FF99",
    "Travel": "#99CCFF",
    "Fuel": "#CC99FF",
    "Shopping": "#FF66B2",
    "Other": "#B2B2B2",
    "Allowance": "#7FC97F",
    "Salary": "#BEAED4",
    "Profit": "#FDC086",
    "Cash": "#FFFF99",
    "Bonus": "#386CB0",
    "Other Income": "#F0027F",
    "Income": "#66BB6A",
    "Expense": "#FF8C00",
    "Sport": "#FFD700"
}

# Default subcategories with icons
DEFAULT_SUBCATEGORIES = {
    "Income": [{
        "name": "Allowance",
        "icon": "💸"
    }, {
        "name": "Salary",
        "icon": "💼"
    }, {
        "name": "Profit",
        "icon": "📈"
    }, {
        "name": "Cash",
        "icon": "💰"
    }, {
        "name": "Bonus",
        "icon": "🎁"
    }, {
        "name": "Other Income",
        "icon": "➕"
    }],
    "Expense": [{
        "name": "Food",
        "icon": "🍔"
    }, {
        "name": "Rent",
        "icon": "🏠"
    }, {
        "name": "Mobile Recharge",
        "icon": "📱"
    }, {
        "name": "Health",
        "icon": "💊"
    }, {
        "name": "Travel",
        "icon": "✈️"
    }, {
        "name": "Fuel",
        "icon": "⛽"
    }, {
        "name": "Shopping",
        "icon": "🛍️"
    }, {
        "name": "Sport",
        "icon": "⚽"
    }, {
        "name": "Other",
        "icon": "❓"
    }]
}


def load_users():
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'r') as f:
                return json.load(f)
    except PermissionError as e:
        app.logger.error(f"Permission denied reading {USERS_FILE}: {e}")
    return {}


def save_users(users):
    try:
        with open(USERS_FILE, 'w') as f:
            json.dump(users, f, indent=2)
    except PermissionError as e:
        app.logger.error(f"Permission denied writing {USERS_FILE}: {e}")
        raise


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password, hashed_password):
    return hash_password(password) == hashed_password


def is_logged_in():
    # Enhanced session validation
    if not session.get('logged_in', False):
        return False

    # Validate session integrity
    user_id = session.get('user_id')
    if not user_id:
        session.clear()
        return False

    # Check if user still exists
    users = load_users()
    if user_id not in users:
        session.clear()
        return False

    return True


def require_login():

    def decorator(f):

        def wrapper(*args, **kwargs):
            if check_session_timeout():
                return redirect(url_for('get_started'))
            if not is_logged_in():
                return redirect(url_for('signin'))
            update_last_activity()
            return f(*args, **kwargs)

        wrapper.__name__ = f.__name__
        return wrapper

    return decorator


def get_user_id():
    if is_logged_in():
        return session['user_id'], session.get('username')
    return None, None


def get_user_data_file(user_id):
    user_data_dir = os.path.join(BASE_DIR, 'user_data')
    if not os.path.exists(user_data_dir):
        os.makedirs(user_data_dir)
    return os.path.join(user_data_dir, f"{user_id}.json")


def get_user_subcategories_file(user_id):
    user_data_dir = os.path.join(BASE_DIR, 'user_data')
    if not os.path.exists(user_data_dir):
        os.makedirs(user_data_dir)
    return os.path.join(user_data_dir, f"{user_id}_subcategories.json")


def load_user_subcategories():
    user_id, _ = get_user_id()
    if not user_id:
        return DEFAULT_SUBCATEGORIES

    subcategories_file = get_user_subcategories_file(user_id)
    if os.path.exists(subcategories_file):
        with open(subcategories_file, 'r') as f:
            return json.load(f)
    else:
        # Initialize with default subcategories for new users
        save_user_subcategories(DEFAULT_SUBCATEGORIES)
        return DEFAULT_SUBCATEGORIES


def save_user_subcategories(subcategories):
    user_id, _ = get_user_id()
    if not user_id:
        return

    subcategories_file = get_user_subcategories_file(user_id)
    with open(subcategories_file, 'w') as f:
        json.dump(subcategories, f, indent=2)


def check_session_timeout():
    """Check if session has timed out (30 minutes of inactivity)"""
    if 'last_activity' in session:
        last_activity = datetime.fromisoformat(session['last_activity'])
        if (datetime.now() -
                last_activity).total_seconds() > 1800:  # 30 minutes
            session.clear()
            return True
    return False


def update_last_activity():
    """Update last activity timestamp"""
    session['last_activity'] = datetime.now().isoformat()


def load_data():
    user_id, _ = get_user_id()
    data_file = get_user_data_file(user_id)
    if os.path.exists(data_file):
        with open(data_file, 'r') as f:
            return json.load(f)
    return []


def save_data(records):
    user_id, _ = get_user_id()
    data_file = get_user_data_file(user_id)
    with open(data_file, 'w') as f:
        json.dump(records, f, indent=2)


@app.route('/')
def get_started():
    # Clear any existing session to ensure fresh start for new users
    session.clear()
    return render_template('get_started.html')


@app.route('/auth_choice')
def auth_choice():
    # Clear session to ensure fresh start
    session.clear()
    return render_template('auth_choice.html')


@app.route('/signup')
def signup():
    return render_template('signup.html')


@app.route('/signin')
def signin():
    return render_template('signin.html')


@app.route('/signup_process', methods=['POST'])
def signup_process():
    username = request.form['username']
    phone = request.form['phone']
    email = request.form['email'].lower().strip()
    password = request.form['password']
    confirm_password = request.form['confirm_password']
    step = request.form.get('step', '1')
    otp = request.form.get('otp', '')

    if not all([username, phone, email, password, confirm_password]):
        return render_template('signup.html', error='All fields are required')

    if len(username) < 3:
        return render_template('signup.html', error='Username too short')
    if not phone.isdigit() or len(phone) != 10:
        return render_template('signup.html', error='Phone must be 10 digits')
    if not email.lower().endswith('@gmail.com'):
        return render_template('signup.html',
                               error='Email must end with @gmail.com')

    password_pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$'
    if len(password) < 8 or not re.match(password_pattern, password):
        return render_template('signup.html',
                               error='Password requirements not met')
    if password != confirm_password:
        return render_template('signup.html', error='Passwords do not match')

    users = load_users()
    user_id = email
    if user_id in users:
        return render_template('signup.html', error='Email already registered')
    # Allow same phone number for multiple accounts
    # if any(u.get('phone') == phone for u in users.values()):
    #     return render_template('signup.html', error='Phone already registered')

    if step == '2':
        if not otp or not otp.isdigit() or len(otp) != 6:
            return render_template('signup.html', error='Invalid OTP')
        users[user_id] = {
            'username': username,
            'phone': phone,
            'email': email,
            'password': hash_password(password),
            'created_at': datetime.now().isoformat(),
            'verified': True
        }
        save_users(users)
        return render_template(
            'signin.html',
            success=
            'Account created successfully! Please sign in with your credentials.'
        )

    return render_template('signup.html', error='', step='2')


@app.route('/signin_process', methods=['POST'])
def signin_process():
    email = request.form['email'].lower().strip()
    password = request.form['password']
    if not email or not password:
        return render_template('signin.html',
                               error='Email and password required')
    if not email.endswith('@gmail.com'):
        return render_template('signin.html', error='Use a @gmail.com email')

    users = load_users()
    user = users.get(email)
    if not user or not verify_password(password, user['password']):
        return render_template('signin.html', error='Invalid credentials')

    # Clear any existing session first
    session.clear()

    # Create new session with user fingerprinting
    session.permanent = True
    session['user_id'] = email
    session['username'] = user['username']
    session['logged_in'] = True
    session['login_time'] = datetime.now().isoformat()
    session['user_agent'] = request.headers.get(
        'User-Agent', '')[:100]  # Store first 100 chars

    return redirect(url_for('home'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('get_started'))


@app.route('/forgot_password')
def forgot_password():
    return render_template('forgot_password.html')


@app.route('/forgot_password_process', methods=['POST'])
def forgot_password_process():
    phone = request.form.get('phone', '').strip()
    otp = request.form.get('otp', '').strip()
    new_password = request.form.get('new_password', '').strip()
    confirm_password = request.form.get('confirm_password', '').strip()
    new_email = request.form.get('new_email', '').strip()
    step = request.form.get('step', '1')

    users = load_users()

    if step == '1':
        # Step 1: Verify phone number exists
        if not phone or not phone.isdigit() or len(phone) != 10:
            return render_template(
                'forgot_password.html',
                error='Please enter a valid 10-digit phone number')

        # Find user with this phone number
        user_found = None
        for user_id, user_data in users.items():
            if user_data.get('phone') == phone:
                user_found = user_data
                break

        if not user_found:
            return render_template(
                'forgot_password.html',
                error='No account found with this phone number')

        # Generate and send OTP (in real implementation, send via SMS)
        otp_code = str(random.randint(100000, 999999))
        session['reset_otp'] = otp_code
        session['reset_phone'] = phone
        session['reset_timestamp'] = datetime.now().isoformat()

        return render_template(
            'forgot_password.html',
            step='2',
            phone=phone,
            success=f'OTP sent to {phone}. Your OTP is: {otp_code}')

    elif step == '2':
        # Step 2: Verify OTP and reset password
        if not otp or len(otp) != 6:
            return render_template('forgot_password.html',
                                   error='Please enter a valid 6-digit OTP',
                                   step='2',
                                   phone=phone)

        stored_otp = session.get('reset_otp')
        stored_phone = session.get('reset_phone')
        timestamp = session.get('reset_timestamp')

        if not stored_otp or stored_phone != phone:
            return render_template('forgot_password.html',
                                   error='Invalid session. Please start over.')

        # Check OTP expiry (10 minutes)
        if timestamp:
            otp_time = datetime.fromisoformat(timestamp)
            if (datetime.now() - otp_time).total_seconds() > 600:
                session.pop('reset_otp', None)
                session.pop('reset_phone', None)
                session.pop('reset_timestamp', None)
                return render_template(
                    'forgot_password.html',
                    error='OTP expired. Please request a new one.')

        if otp != stored_otp:
            return render_template('forgot_password.html',
                                   error='Invalid OTP. Please try again.',
                                   step='2',
                                   phone=phone)

        # Validate new password
        if not new_password or len(new_password) < 8:
            return render_template(
                'forgot_password.html',
                error='Password must be at least 8 characters long',
                step='2',
                phone=phone)

        password_pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$'
        if not re.match(password_pattern, new_password):
            return render_template(
                'forgot_password.html',
                error=
                'Password must contain uppercase, lowercase, number, and special character',
                step='2',
                phone=phone)

        if new_password != confirm_password:
            return render_template('forgot_password.html',
                                   error='Passwords do not match',
                                   step='2',
                                   phone=phone)

        # Validate new email if provided
        if new_email and not new_email.lower().endswith('@gmail.com'):
            return render_template('forgot_password.html',
                                   error='Email must end with @gmail.com',
                                   step='2',
                                   phone=phone)

        # Update user password and email
        for user_id, user_data in users.items():
            if user_data.get('phone') == phone:
                user_data['password'] = hash_password(new_password)
                if new_email:
                    # Check if new email is already used by another user
                    if new_email.lower() in [
                            uid.lower() for uid in users.keys()
                            if uid != user_id
                    ]:
                        return render_template(
                            'forgot_password.html',
                            error='Email already registered by another user',
                            step='2',
                            phone=phone)

                    # Move user data to new email key
                    user_data['email'] = new_email.lower()
                    users[new_email.lower()] = user_data
                    del users[user_id]
                break

        save_users(users)

        # Clear session
        session.pop('reset_otp', None)
        session.pop('reset_phone', None)
        session.pop('reset_timestamp', None)

        return render_template(
            'signin.html',
            success=
            'Password updated successfully! Please sign in with your new credentials.'
        )

    return render_template('forgot_password.html')


@app.route('/home')
@require_login()
def home():
    _, username = get_user_id()
    return render_template('home.html', username=username)


@app.route('/expense_dashboard')
@require_login()
def expense_dashboard():
    _, username = get_user_id()
    return render_template('expense_dashboard.html', username=username)


@app.route('/income_dashboard')
@require_login()
def income_dashboard():
    _, username = get_user_id()
    return render_template('income_dashboard.html', username=username)


@app.route('/add_record')
@require_login()
def add_record():
    category = request.args.get('category', '')
    return render_template('add_record.html', default_category=category)


@app.route('/add_record_form')
@require_login()
def add_record_form():
    category = request.args.get('category', '')
    return render_template('add_record.html', default_category=category)


@app.route('/submit_record', methods=['POST'])
@require_login()
def submit_record():
    records = load_data()

    # Handle custom category
    subcategory = request.form['subcategory']
    if subcategory == 'Others':
        subcategory = request.form.get('custom_subcategory', 'Others')

        # Add to user's subcategories if it's custom
        if subcategory != 'Others':
            user_subcategories = load_user_subcategories()
            category_type = request.form['category']

            # Check if custom subcategory already exists
            existing_names = [
                s['name'] for s in user_subcategories.get(category_type, [])
            ]
            if subcategory not in existing_names:
                user_subcategories[category_type].append({
                    'name': subcategory,
                    'icon': '📝'
                })
                save_user_subcategories(user_subcategories)

    new_record = {
        'Date': request.form['date'],
        'Category': request.form['category'],
        'Sub-Category': subcategory,
        'Amount': request.form['amount'],
        'Remarks': request.form.get('remarks', '')
    }

    if request.form.get('edit_index'):
        idx = int(request.form['edit_index'])
        records[idx] = new_record
    else:
        records.append(new_record)
    save_data(records)

    # Redirect based on category
    category = request.form['category']
    if category == 'Expense':
        return redirect(url_for('expense_dashboard'))
    else:
        return redirect(url_for('income_dashboard'))


@app.route('/manage_records')
@require_login()
def manage_records():
    records = load_data()
    category_filter = request.args.get('category', '')

    # Filter by category if specified
    if category_filter:
        records = [r for r in records if r['Category'] == category_filter]

    # Create a list of tuples with (record, original_index)
    indexed_records = [(record, idx) for idx, record in enumerate(load_data())]

    # Filter indexed records by category if specified
    if category_filter:
        indexed_records = [(record, idx) for record, idx in indexed_records
                           if record['Category'] == category_filter]

    # Sort by date (newest first) while keeping track of original indices
    indexed_records.sort(key=lambda x: x[0]['Date'], reverse=True)
    return render_template('manage_records.html',
                           indexed_records=indexed_records,
                           category_filter=category_filter)


@app.route('/edit_record/<int:index>')
@require_login()
def edit_record(index):
    records = load_data()
    if 0 <= index < len(records):
        return render_template('add_record.html',
                               record=records[index],
                               edit_index=index)
    return redirect(url_for('manage_records'))


@app.route('/delete_record/<int:index>')
@require_login()
def delete_record(index):
    records = load_data()
    if 0 <= index < len(records):
        del records[index]
        save_data(records)
    return redirect(url_for('manage_records'))


@app.route('/bulk_delete', methods=['POST'])
@require_login()
def bulk_delete():
    selected_indices = request.form.getlist('selected_records')
    if selected_indices:
        records = load_data()
        # Sort indices in descending order to delete from end to beginning
        indices = sorted([int(i) for i in selected_indices], reverse=True)
        for index in indices:
            if 0 <= index < len(records):
                del records[index]
        save_data(records)

    # Check where the request came from and redirect appropriately
    referer = request.headers.get('Referer', '')
    if 'show_data' in referer:
        return redirect(url_for('show_data'))
    else:
        return redirect(url_for('filtered_records'))


@app.route('/bulk_edit', methods=['POST'])
@require_login()
def bulk_edit():
    selected_indices = request.form.getlist('selected_records')
    if selected_indices and len(selected_indices) == 1:
        # Only allow editing one record at a time
        index = int(selected_indices[0])
        return redirect(url_for('edit_record', index=index))

    # Check where the request came from and redirect appropriately
    referer = request.headers.get('Referer', '')
    if 'show_data' in referer:
        return redirect(url_for('show_data'))
    else:
        return redirect(url_for('filtered_records'))


@app.route('/categories')
@require_login()
def categories():
    subcategories = load_user_subcategories()
    income_categories = subcategories.get('Income', [])
    expense_categories = subcategories.get('Expense', [])
    return render_template('categories.html',
                           income_categories=income_categories,
                           expense_categories=expense_categories)


@app.route('/manage_subcategories')
@require_login()
def manage_subcategories():
    subcategories = load_user_subcategories()
    return render_template(
        'manage_subcategories.html',
        income_subcategories=subcategories.get('Income', []),
        expense_subcategories=subcategories.get('Expense', []))


@app.route('/add_subcategory', methods=['POST'])
@require_login()
def add_subcategory():
    category_type = request.form['category_type']
    subcategory_name = request.form['subcategory_name'].strip()
    subcategory_icon = request.form['subcategory_icon'].strip()

    if not all([category_type, subcategory_name, subcategory_icon]):
        return redirect(url_for('manage_subcategories'))

    subcategories = load_user_subcategories()

    # Check if subcategory already exists
    existing_names = [
        subcat['name'] for subcat in subcategories.get(category_type, [])
    ]
    if subcategory_name in existing_names:
        return redirect(url_for('manage_subcategories'))

    # Add new subcategory
    if category_type not in subcategories:
        subcategories[category_type] = []

    subcategories[category_type].append({
        'name': subcategory_name,
        'icon': subcategory_icon
    })

    save_user_subcategories(subcategories)
    return redirect(url_for('manage_subcategories'))


@app.route('/edit_subcategory', methods=['POST'])
@require_login()
def edit_subcategory():
    original_name = request.form['original_name']
    category_type = request.form['category_type']
    new_name = request.form['subcategory_name'].strip()
    new_icon = request.form['subcategory_icon'].strip()

    if not all([original_name, category_type, new_name, new_icon]):
        return redirect(url_for('manage_subcategories'))

    subcategories = load_user_subcategories()

    # Find and update the subcategory
    for subcat in subcategories.get(category_type, []):
        if subcat['name'] == original_name:
            subcat['name'] = new_name
            subcat['icon'] = new_icon
            break

    save_user_subcategories(subcategories)
    return redirect(url_for('manage_subcategories'))


@app.route('/delete_subcategory', methods=['POST'])
@require_login()
def delete_subcategory():
    subcategory_name = request.form['subcategory_name']
    category_type = request.form['category_type']

    subcategories = load_user_subcategories()

    # Remove the subcategory
    if category_type in subcategories:
        subcategories[category_type] = [
            subcat for subcat in subcategories[category_type]
            if subcat['name'] != subcategory_name
        ]

    save_user_subcategories(subcategories)
    return redirect(url_for('manage_subcategories'))


@app.route('/get_subcategories')
@require_login()
def get_subcategories():
    subcategories = load_user_subcategories()
    return jsonify(subcategories)


@app.route('/category_records/<category>')
@require_login()
def category_records(category):
    records = load_data()
    filtered = [r for r in records if r['Sub-Category'] == category]
    filtered.sort(key=lambda x: x['Date'], reverse=True)
    return render_template('category_records.html',
                           records=filtered,
                           category=category)


@app.route('/show_data', methods=['GET', 'POST'])
@require_login()
def show_data():
    if request.method == 'POST':
        # Handle bulk actions from show_data page
        return redirect(url_for('show_data'))

    all_records = load_data()
    category_filter = request.args.get('category_type', '')

    # Create indexed records with original indices
    indexed_records = []
    for idx, record in enumerate(all_records):
        # Filter records by category type if specified
        if category_filter and record['Category'] != category_filter:
            continue
        indexed_records.append((record, idx))

    # Sort by date (newest first) while maintaining original indices
    indexed_records.sort(
        key=lambda x: datetime.strptime(x[0]['Date'], '%Y-%m-%d'),
        reverse=True)

    # Extract just the records for template (indices are handled in template)
    records = [record for record, idx in indexed_records]

    # Separate income and expense records for display
    income_records = [r for r in records if r['Category'] == 'Income']
    expense_records = [r for r in records if r['Category'] == 'Expense']

    return render_template('show_data.html',
                           indexed_records=indexed_records,
                           records=records,
                           income_records=income_records,
                           expense_records=expense_records,
                           category_filter=category_filter)


@app.route('/records')
@require_login()
def filtered_records():
    records = load_data()

    # Get filter parameters - default to current week
    category_type = request.args.get('category_type', '')
    selected_date = request.args.get('selected_date',
                                     date.today().strftime('%Y-%m-%d'))
    view_by = request.args.get('view_by', 'Week')
    group_by = request.args.get('group_by', 'Sub-Category')
    filter_subcategory = request.args.get('filter_subcategory', '')

    # Get available subcategories based on category type
    subcategories = load_user_subcategories()
    income_subcategories = [
        subcat['name'] for subcat in subcategories.get('Income', [])
    ]
    expense_subcategories = [
        subcat['name'] for subcat in subcategories.get('Expense', [])
    ]

    # Filter records based on parameters
    filtered_records = []
    if records:
        for record in records:
            match = True

            # Filter by category type (Income/Expense)
            if category_type and record['Category'] != category_type:
                match = False

            # Filter by subcategory
            if filter_subcategory and record[
                    'Sub-Category'] != filter_subcategory:
                match = False

            # Filter by date based on view_by (limit to max one month)
            if selected_date:
                try:
                    record_date = datetime.strptime(record['Date'],
                                                    '%Y-%m-%d').date()
                    filter_date = datetime.strptime(selected_date,
                                                    '%Y-%m-%d').date()

                    if view_by == 'Week':
                        start_week = filter_date - timedelta(
                            days=filter_date.weekday())
                        end_week = start_week + timedelta(days=6)
                        if not (start_week <= record_date <= end_week):
                            match = False
                    elif view_by == 'Month':
                        if record_date.year != filter_date.year or record_date.month != filter_date.month:
                            match = False
                    # Remove Year option to limit to max one month
                except:
                    match = False

            if match:
                filtered_records.append(record)

    # Sort by date (newest first)
    filtered_records.sort(
        key=lambda x: datetime.strptime(x['Date'], '%Y-%m-%d'), reverse=True)

    return render_template('filtered_records.html',
                           records=filtered_records,
                           category_type=category_type,
                           selected_date=selected_date,
                           view_by=view_by,
                           group_by=group_by,
                           filter_subcategory=filter_subcategory,
                           income_subcategories=income_subcategories,
                           expense_subcategories=expense_subcategories)


@app.route('/reports')
@require_login()
def reports():
    return render_template('reports.html')


@app.route('/settings')
@require_login()
def settings():
    _, username = get_user_id()
    return render_template('settings.html', username=username)


@app.route('/chart_data')
@require_login()
def chart_data():
    records = load_data()
    category_type = request.args.get('category_type', 'Expense')
    selected_date = request.args.get('selected_date',
                                     date.today().strftime('%Y-%m-%d'))
    view_by = request.args.get('view_by', 'Day')
    group_by = request.args.get('group_by', 'Sub-Category')
    filter_sub = request.args.get('filter_subcategory', '')

    try:
        sd = datetime.strptime(selected_date, "%Y-%m-%d").date()
    except:
        sd = date.today()

    if view_by == "Week":
        start = sd - timedelta(days=sd.weekday())
        end = start + timedelta(days=6)
    elif view_by == "Month":
        start = sd.replace(day=1)
        next_month = sd.replace(day=28) + timedelta(days=4)
        end = next_month.replace(day=1) - timedelta(days=1)
    elif view_by == "Year":
        start = sd.replace(month=1, day=1)
        end = sd.replace(month=12, day=31)
    else:
        start = end = sd

    data_group = defaultdict(float)
    for r in records:
        try:
            dt = datetime.strptime(r['Date'], "%Y-%m-%d").date()
            if not (start <= dt <= end): continue
            if r['Category'] != category_type: continue
            if filter_sub and r['Sub-Category'] != filter_sub: continue
            key = r['Category'] if group_by == "Category" else r['Sub-Category']
            data_group[key] += float(r['Amount'])
        except:
            continue

    chart_data = {
        'labels': list(data_group.keys()),
        'values': list(data_group.values()),
        'colors': [COLOR_MAP.get(k, '#CCCCCC') for k in data_group.keys()]
    }
    return jsonify(chart_data)


@app.route('/download_csv')
@require_login()
def download_csv():
    records = load_data()
    category = request.args.get('category', '')
    subcat = request.args.get('subcategory', '')
    from_date = request.args.get('from_date', '')
    to_date = request.args.get('to_date', '')

    filtered = []
    for r in records:
        match = True
        dt = r.get('Date')
        if category and r['Category'] != category: match = False
        if subcat and r['Sub-Category'] != subcat: match = False
        if from_date:
            try:
                if datetime.strptime(dt,
                                     "%Y-%m-%d").date() < datetime.strptime(
                                         from_date, "%Y-%m-%d").date():
                    match = False
            except:
                match = False
        if to_date:
            try:
                if datetime.strptime(dt,
                                     "%Y-%m-%d").date() > datetime.strptime(
                                         to_date, "%Y-%m-%d").date():
                    match = False
            except:
                match = False
        if match:
            filtered.append(r)

    if filtered:
        output = ''
        writer = csv.DictWriter(
            make_response().response if False else open(os.devnull, 'w'),
            fieldnames=FIELDS)  # dummy init
        output_io = ''
        from io import StringIO
        out = StringIO()
        writer = csv.DictWriter(out, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(filtered)
        csv_content = out.getvalue()
        out.close()
        response = make_response(csv_content)
        response.headers[
            'Content-Disposition'] = 'attachment; filename=expense_records.csv'
        response.headers['Content-Type'] = 'text/csv'
        return response

    return "No records to download."


if __name__ == '__main__':
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w') as f:
            json.dump({}, f)
    app.run(host='0.0.0.0', port=5000, debug=True)

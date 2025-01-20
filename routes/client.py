from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, Client, Dependent
from datetime import datetime

client_bp = Blueprint('client', __name__)

@client_bp.route('/clients', methods=['GET'])
@login_required
def clients():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    search_query = request.args.get('search', '')
    
    query = Client.query.filter_by(agent_id=current_user.id)
    if search_query:
        query = query.filter(Client.full_name.ilike(f'%{search_query}%'))
    
    pagination = query.order_by(Client.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False)
    clients = pagination.items
    
    return render_template('clients/clients.html', 
                         clients=clients, 
                         pagination=pagination,
                         search_query=search_query)

@client_bp.route('/clients/add', methods=['GET', 'POST'])
@login_required
def add_client():
    if request.method == 'POST':
        # Parse date of birth
        date_of_birth = None
        if request.form.get('date_of_birth'):
            try:
                date_of_birth = datetime.strptime(request.form['date_of_birth'], '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid date format for date of birth', 'danger')
                return redirect(url_for('client.add_client'))

        # Validate phone number
        phone = request.form.get('phone')
        if phone and len(phone) != 10:
            flash('Phone number must be exactly 10 digits', 'danger')
            return redirect(url_for('client.add_client'))

        client = Client(
            first_name=request.form['first_name'],
            last_name=request.form.get('last_name', ''),
            email=request.form.get('email'),
            phone=request.form.get('phone'),
            date_of_birth=date_of_birth,
            sex=request.form.get('sex'),
            address=request.form.get('address'),
            agent_id=current_user.id
        )
        db.session.add(client)
        db.session.commit()

        # Handle dependents if any
        dependent_first_names = request.form.getlist('dependent_first_name[]')
        dependent_last_names = request.form.getlist('dependent_last_name[]')
        dependent_dates_of_birth = request.form.getlist('dependent_date_of_birth[]')
        dependent_sexes = request.form.getlist('dependent_sex[]')
        dependent_relationships = request.form.getlist('dependent_relationship[]')

        for i in range(len(dependent_first_names)):
            if dependent_first_names[i].strip():  # Only add if first name is not empty
                # Parse dependent date of birth
                dependent_date_of_birth = None
                if dependent_dates_of_birth[i]:
                    try:
                        dependent_date_of_birth = datetime.strptime(dependent_dates_of_birth[i], '%Y-%m-%d').date()
                    except ValueError:
                        continue  # Skip this dependent if date is invalid

                dependent = Dependent(
                    first_name=dependent_first_names[i],
                    last_name=dependent_last_names[i] if i < len(dependent_last_names) else '',
                    date_of_birth=dependent_date_of_birth,
                    sex=dependent_sexes[i] if i < len(dependent_sexes) else None,
                    relationship=dependent_relationships[i],
                    client_id=client.id,
                    agent_id=current_user.id
                )
                db.session.add(dependent)
        
        db.session.commit()
        flash('Client added successfully!', 'success')
        return redirect(url_for('client.clients'))
    return render_template('clients/add_client.html')

@client_bp.route('/clients/<int:client_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_client(client_id):
    client = Client.query.get_or_404(client_id)
    if client.agent_id != current_user.id:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('client.clients'))
    
    if request.method == 'POST':
        # Parse date of birth
        date_of_birth = None
        if request.form.get('date_of_birth'):
            try:
                date_of_birth = datetime.strptime(request.form['date_of_birth'], '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid date format for date of birth', 'danger')
                return redirect(url_for('client.edit_client', client_id=client_id))

        # Validate phone number
        phone = request.form.get('phone')
        if phone and len(phone) != 10:
            flash('Phone number must be exactly 10 digits', 'danger')
            return redirect(url_for('client.edit_client', client_id=client_id))

        client.first_name = request.form['first_name']
        client.last_name = request.form.get('last_name', '')
        client.email = request.form.get('email')
        client.phone = request.form.get('phone')
        client.date_of_birth = date_of_birth
        client.sex = request.form.get('sex')
        client.address = request.form.get('address')
        
        # Handle dependents updates
        dependent_ids = request.form.getlist('dependent_id[]')
        dependent_first_names = request.form.getlist('dependent_first_name[]')
        dependent_last_names = request.form.getlist('dependent_last_name[]')
        dependent_dates_of_birth = request.form.getlist('dependent_date_of_birth[]')
        dependent_sexes = request.form.getlist('dependent_sex[]')
        dependent_relationships = request.form.getlist('dependent_relationship[]')

        # Update or create dependents
        for i in range(len(dependent_first_names)):
            if dependent_first_names[i].strip():
                # Parse dependent date of birth
                dependent_date_of_birth = None
                if dependent_dates_of_birth[i]:
                    try:
                        dependent_date_of_birth = datetime.strptime(dependent_dates_of_birth[i], '%Y-%m-%d').date()
                    except ValueError:
                        continue  # Skip this dependent if date is invalid

                if i < len(dependent_ids) and dependent_ids[i]:
                    # Update existing dependent
                    dependent = db.session.get(Dependent, int(dependent_ids[i]))
                    if dependent and dependent.client_id == client.id:
                        dependent.first_name = dependent_first_names[i]
                        dependent.last_name = dependent_last_names[i] if i < len(dependent_last_names) else ''
                        dependent.date_of_birth = dependent_date_of_birth
                        dependent.sex = dependent_sexes[i] if i < len(dependent_sexes) else None
                        dependent.relationship = dependent_relationships[i]
                else:
                    # Create new dependent
                    dependent = Dependent(
                        first_name=dependent_first_names[i],
                        last_name=dependent_last_names[i] if i < len(dependent_last_names) else '',
                        date_of_birth=dependent_date_of_birth,
                        sex=dependent_sexes[i] if i < len(dependent_sexes) else None,
                        relationship=dependent_relationships[i],
                        client_id=client.id,
                        agent_id=current_user.id
                    )
                    db.session.add(dependent)

        db.session.commit()
        flash('Client updated successfully!', 'success')
        return redirect(url_for('client.clients'))
    return render_template('clients/edit_client.html', client=client)

@client_bp.route('/clients/<int:client_id>/delete', methods=['POST'])
@login_required
def delete_client(client_id):
    client = Client.query.get_or_404(client_id)
    if client.agent_id != current_user.id:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('client.clients'))
    
    db.session.delete(client)
    db.session.commit()
    flash('Client deleted successfully!', 'success')
    return redirect(url_for('client.clients'))

@client_bp.route('/dependents/<int:dependent_id>/delete', methods=['POST'])
@login_required
def delete_dependent(dependent_id):
    dependent = Dependent.query.get_or_404(dependent_id)
    if dependent.agent_id != current_user.id:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('client.clients'))
    
    db.session.delete(dependent)
    db.session.commit()
    flash('Dependent deleted successfully!', 'success')
    return jsonify({'success': True}) 
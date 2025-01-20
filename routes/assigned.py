from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, AssignedPolicy, Policy, Client, Dependent
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

assigned_bp = Blueprint('assigned', __name__)

@assigned_bp.route('/assigned-policies', methods=['GET'])
@login_required
def assigned_policies():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    search_query = request.args.get('search', '')
    
    query = AssignedPolicy.query.filter_by(agent_id=current_user.id)
    if search_query:
        query = query.join(Policy).join(Client).filter(
            db.or_(
                Policy.name.ilike(f'%{search_query}%'),
                Client.first_name.ilike(f'%{search_query}%'),
                Client.last_name.ilike(f'%{search_query}%')
            )
        )
    
    pagination = query.order_by(AssignedPolicy.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False)
    assigned_policies = pagination.items
    
    return render_template('assigned/assigned_policies.html', 
                         assigned_policies=assigned_policies, 
                         pagination=pagination,
                         search_query=search_query)

@assigned_bp.route('/assigned-policies/assign', methods=['GET', 'POST'])
@login_required
def assign_policy():
    if request.method == 'POST':
        policy_id = request.form.get('policy_id')
        client_id = request.form.get('client_id')
        premium_amount = request.form.get('premium_amount')
        tenure_months = request.form.get('tenure_months')
        payment_cycle = request.form.get('payment_cycle')
        first_receipt_date = request.form.get('first_receipt_date')
        dependent_ids = request.form.getlist('dependent_ids')

        try:
            # Convert and validate data
            premium_amount = float(premium_amount)
            tenure_months = int(tenure_months)
            first_receipt_date = datetime.strptime(first_receipt_date, '%Y-%m-%d').date()
            expiry_date = first_receipt_date + relativedelta(months=tenure_months)

            # Create assigned policy
            assigned_policy = AssignedPolicy(
                policy_id=policy_id,
                client_id=client_id,
                agent_id=current_user.id,
                premium_amount=premium_amount,
                tenure_months=tenure_months,
                payment_cycle=payment_cycle,
                first_receipt_date=first_receipt_date,
                expiry_date=expiry_date
            )

            # Add selected dependents if it's a group policy
            policy = Policy.query.get(policy_id)
            if policy.is_group and dependent_ids:
                dependents = Dependent.query.filter(
                    Dependent.id.in_(dependent_ids),
                    Dependent.client_id == client_id
                ).all()
                assigned_policy.dependents.extend(dependents)

            db.session.add(assigned_policy)
            db.session.commit()
            flash('Policy assigned successfully!', 'success')
            return redirect(url_for('assigned.assigned_policies'))

        except (ValueError, TypeError):
            flash('Invalid input data. Please check your entries.', 'danger')
            return redirect(url_for('assigned.assign_policy'))

    # GET request - show form
    policies = Policy.query.filter_by(agent_id=current_user.id).all()
    clients = Client.query.filter_by(agent_id=current_user.id).all()
    return render_template('assigned/assign_policy.html', 
                         policies=policies,
                         clients=clients)

@assigned_bp.route('/get-client-dependents/<int:client_id>')
@login_required
def get_client_dependents(client_id):
    client = Client.query.get_or_404(client_id)
    if client.agent_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    dependents = [{'id': d.id, 'name': d.full_name, 'relationship': d.relationship} 
                 for d in client.dependents]
    return jsonify(dependents)

@assigned_bp.route('/get-policy-details/<int:policy_id>')
@login_required
def get_policy_details(policy_id):
    policy = Policy.query.get_or_404(policy_id)
    if policy.agent_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify({
        'is_group': policy.is_group,
        'name': policy.name,
        'provider': policy.provider,
        'category': policy.category
    })

@assigned_bp.route('/assigned-policies/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_assigned_policy(id):
    assigned_policy = AssignedPolicy.query.get_or_404(id)
    if assigned_policy.agent_id != current_user.id:
        flash('You do not have permission to edit this policy.', 'danger')
        return redirect(url_for('assigned.assigned_policies'))

    if request.method == 'POST':
        try:
            # Update fields
            assigned_policy.premium_amount = float(request.form.get('premium_amount'))
            assigned_policy.tenure_months = int(request.form.get('tenure_months'))
            assigned_policy.payment_cycle = request.form.get('payment_cycle')
            assigned_policy.first_receipt_date = datetime.strptime(request.form.get('first_receipt_date'), '%Y-%m-%d').date()
            assigned_policy.expiry_date = assigned_policy.first_receipt_date + relativedelta(months=assigned_policy.tenure_months)

            # Update dependents if it's a group policy
            if assigned_policy.policy.is_group:
                dependent_ids = request.form.getlist('dependent_ids')
                dependents = Dependent.query.filter(
                    Dependent.id.in_(dependent_ids),
                    Dependent.client_id == assigned_policy.client_id
                ).all() if dependent_ids else []
                assigned_policy.dependents = dependents

            db.session.commit()
            flash('Policy updated successfully!', 'success')
            return redirect(url_for('assigned.assigned_policies'))

        except (ValueError, TypeError):
            flash('Invalid input data. Please check your entries.', 'danger')
            return redirect(url_for('assigned.edit_assigned_policy', id=id))

    # GET request - show form
    client_dependents = []
    if assigned_policy.policy.is_group:
        client_dependents = Dependent.query.filter_by(client_id=assigned_policy.client_id).all()

    return render_template('assigned/edit_assigned_policy.html',
                         assigned_policy=assigned_policy,
                         client_dependents=client_dependents)

@assigned_bp.route('/assigned-policies/delete/<int:id>', methods=['POST'])
@login_required
def delete_assigned_policy(id):
    assigned_policy = AssignedPolicy.query.get_or_404(id)
    if assigned_policy.agent_id != current_user.id:
        flash('You do not have permission to delete this policy.', 'danger')
        return redirect(url_for('assigned.assigned_policies'))

    try:
        db.session.delete(assigned_policy)
        db.session.commit()
        flash('Policy deleted successfully!', 'success')
    except:
        db.session.rollback()
        flash('An error occurred while deleting the policy.', 'danger')

    return redirect(url_for('assigned.assigned_policies')) 
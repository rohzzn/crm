from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Policy
from datetime import datetime

policy_bp = Blueprint('policy', __name__)

@policy_bp.route('/policies', methods=['GET'])
@login_required
def policies():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    search_query = request.args.get('search', '')
    
    query = Policy.query.filter_by(agent_id=current_user.id)
    if search_query:
        query = query.filter(Policy.name.ilike(f'%{search_query}%'))
    
    pagination = query.order_by(Policy.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False)
    policies = pagination.items
    
    return render_template('policies/policies.html', 
                         policies=policies, 
                         pagination=pagination,
                         search_query=search_query)

@policy_bp.route('/policies/add', methods=['GET', 'POST'])
@login_required
def add_policy():
    if request.method == 'POST':
        policy = Policy(
            name=request.form['name'],
            provider=request.form['provider'],
            category=request.form['category'],
            is_group=bool(request.form.get('is_group')),
            description=request.form.get('description'),
            agent_id=current_user.id
        )
        db.session.add(policy)
        db.session.commit()
        flash('Policy added successfully!', 'success')
        return redirect(url_for('policy.policies'))
    return render_template('policies/add_policy.html')

@policy_bp.route('/policies/<int:policy_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_policy(policy_id):
    policy = Policy.query.get_or_404(policy_id)
    if policy.agent_id != current_user.id:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('policy.policies'))
    
    if request.method == 'POST':
        policy.name = request.form['name']
        policy.provider = request.form['provider']
        policy.category = request.form['category']
        policy.is_group = bool(request.form.get('is_group'))
        policy.description = request.form.get('description')
        
        db.session.commit()
        flash('Policy updated successfully!', 'success')
        return redirect(url_for('policy.policies'))
    return render_template('policies/edit_policy.html', policy=policy)

@policy_bp.route('/policies/<int:policy_id>/delete', methods=['POST'])
@login_required
def delete_policy(policy_id):
    policy = Policy.query.get_or_404(policy_id)
    if policy.agent_id != current_user.id:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('policy.policies'))
    
    db.session.delete(policy)
    db.session.commit()
    flash('Policy deleted successfully!', 'success')
    return redirect(url_for('policy.policies')) 
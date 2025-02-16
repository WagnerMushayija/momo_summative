from flask import Blueprint, jsonify, request, current_app, render_template
from sqlalchemy import func, desc, case, or_
from datetime import datetime, timedelta
from app.models import Transaction
from app import db
import traceback


bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """
    Render the main index page
    """
    try:
        # Fetch basic transaction summary for initial display
        total_income = db.session.query(
            func.sum(Transaction.amount)
        ).filter(Transaction.amount > 0).scalar() or 0

        total_expenses = db.session.query(
            func.sum(Transaction.amount)
        ).filter(Transaction.amount < 0).scalar() or 0

        # Log the summary for debugging
        current_app.logger.info(f"Total Income: {total_income}")
        current_app.logger.info(f"Total Expenses: {total_expenses}")

        return render_template('index.html')
    except Exception as e:
        current_app.logger.error(f"Error rendering index page: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return f"An error occurred: {str(e)}", 500

@bp.route('/api/transaction-summary', methods=['GET'])
def get_transaction_summary():
    """
    Provide comprehensive transaction summary for dashboard
    """
    try:
        # Get unique categories
        categories = db.session.query(
            Transaction.category,
            func.count(Transaction.id).label('transaction_count'),
            func.sum(Transaction.amount).label('total_amount')
        ).group_by(Transaction.category).all()

        # Monthly summary
        monthly_summary = Transaction.get_monthly_summary()

        return jsonify({
            'category_summary': [
                {
                    'category': cat[0],
                    'transaction_count': cat[1],
                    'total_amount': float(cat[2])
                } for cat in categories
            ],
            'monthly_summary': [
                {
                    'year': row[0],
                    'month': row[1],
                    'total_amount': float(row[2]),
                    'transaction_count': row[3]
                } for row in monthly_summary
            ]
        })
    except Exception as e:
        current_app.logger.error(f"Error in transaction summary: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve transaction summary',
            'details': str(e)
        }), 500

@bp.route('/api/transactions', methods=['GET'])
def get_transactions():
    """
    Retrieve transactions with advanced filtering and pagination
    """
    try:
        # Pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        # Filtering parameters
        category = request.args.get('category')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        min_amount = request.args.get('min_amount', type=float)
        max_amount = request.args.get('max_amount', type=float)

        # Base query
        query = Transaction.query

        # Apply filters
        if category:
            query = query.filter_by(category=category)

        if start_date:
            query = query.filter(Transaction.date_time >= datetime.fromisoformat(start_date))

        if end_date:
            query = query.filter(Transaction.date_time <= datetime.fromisoformat(end_date))

        if min_amount is not None:
            query = query.filter(Transaction.amount >= min_amount)

        if max_amount is not None:
            query = query.filter(Transaction.amount <= max_amount)

        # Sort by date, most recent first
        query = query.order_by(desc(Transaction.date_time))

        # Paginate
        paginated_transactions = query.paginate(page=page, per_page=per_page)

        return jsonify({
            'transactions': [t.to_dict() for t in paginated_transactions.items],
            'total_pages': paginated_transactions.pages,
            'current_page': page,
            'total_transactions': paginated_transactions.total
        })
    except Exception as e:
        current_app.logger.error(f"Error retrieving transactions: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve transactions',
            'details': str(e)
        }), 500

@bp.route('/api/categories', methods=['GET'])
def get_transaction_categories():
    """
    Retrieve unique transaction categories
    """
    try:
        categories = db.session.query(
            Transaction.category.distinct()
        ).order_by(Transaction.category).all()

        return jsonify({
            'categories': [cat[0] for cat in categories]
        })
    except Exception as e:
        current_app.logger.error(f"Error retrieving categories: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve categories',
            'details': str(e)
        }), 500

@bp.route('/api/financial-overview', methods=['GET'])
def get_financial_overview():
    """
    Comprehensive financial overview
    """
    try:
        # Income categories
        income_categories = ['INCOMING_MONEY']
        
        # Expense categories
        expense_categories = [
            'CODE_PAYMENTS', 'MOBILE_TRANSFERS', 'BANK_TRANSFERS', 
            'BUNDLES', 'CASHPOWER_PAYMENTS', 'WITHDRAWALS', 
            'THIRD_PARTY', 'BANK_DEPOSITS', 'AIRTIME_PAYMENTS'
        ]

        # Total income
        total_income = db.session.query(
            func.sum(Transaction.amount)
        ).filter(Transaction.category.in_(income_categories)).scalar() or 0

        # Total expenses
        total_expenses = db.session.query(
            func.sum(Transaction.amount)
        ).filter(Transaction.category.in_(expense_categories)).scalar() or 0

        # Net balance
        net_balance = total_income + total_expenses

        # Category summary (for pie chart)
        category_summary = db.session.query(
            Transaction.category,
            func.sum(Transaction.amount).label('total_amount'),
            func.count(Transaction.id).label('transaction_count')
        ).filter(Transaction.category.in_(expense_categories)).group_by(Transaction.category).order_by(
            func.sum(Transaction.amount).desc()
        ).all()

        # Monthly transaction summary
        monthly_summary = db.session.query(
            func.year(Transaction.date_time).label('year'),
            func.month(Transaction.date_time).label('month'),
            func.sum(Transaction.amount).label('total_amount'),
            func.count(Transaction.id).label('transaction_count')
        ).group_by('year', 'month').order_by('year', 'month').all()

        # Prepare response
        return jsonify({
            'total_income': float(total_income),
            'total_expenses': float(abs(total_expenses)),
            'net_balance': float(net_balance),
            'category_summary': [
                {
                    'category': cat[0],
                    'total_amount': float(cat[1]),
                    'transaction_count': cat[2]
                } for cat in category_summary
            ],
            'monthly_summary': [
                {
                    'year': row[0],
                    'month': row[1],
                    'total_amount': float(row[2]),
                    'transaction_count': row[3]
                } for row in monthly_summary
            ]
        })
    except Exception as e:
        current_app.logger.error(f"Error in financial overview: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({
            'error': 'Failed to retrieve financial overview',
            'details': str(e)
        }), 500

@bp.route('/api/search', methods=['GET'])
def search_transactions():
    """
    Advanced search endpoint for transactions
    """
    try:
        query_term = request.args.get('q', '').strip()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        if not query_term:
            return jsonify({
                'error': 'Search term is required',
                'transactions': [],
                'total_pages': 0,
                'current_page': page,
                'total_transactions': 0
            }), 400

        # Search across multiple fields
        search_query = Transaction.query.filter(
            or_(
                Transaction.sender.ilike(f'%{query_term}%'),
                Transaction.receiver.ilike(f'%{query_term}%'),
                Transaction.category.ilike(f'%{query_term}%'),
                Transaction.raw_message.ilike(f'%{query_term}%')
            )
        )

        # Paginate results
        paginated_results = search_query.order_by(
            desc(Transaction.date_time)
        ).paginate(page=page, per_page=per_page)

        return jsonify({
            'transactions': [t.to_dict() for t in paginated_results.items],
            'total_pages': paginated_results.pages,
            'current_page': page,
            'total_transactions': paginated_results.total
        })
    except Exception as e:
        current_app.logger.error(f"Error searching transactions: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({
            'error': 'Failed to search transactions',
            'details': str(e)
        }), 500

# Keep other routes from the previous implementation
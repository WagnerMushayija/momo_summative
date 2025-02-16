from app import db
from sqlalchemy import func, Column, Integer, String, DateTime, Text
from sqlalchemy.dialects.mysql import DECIMAL
from datetime import datetime

class Transaction(db.Model):
    """
    Transaction model representing financial transactions
    """
    # Explicitly set the table name to match the existing database table
    __tablename__ = 'transaction'
    
    # Use __table_args__ to handle existing table
    __table_args__ = {'extend_existing': True}

    # Primary key
    id = Column(Integer, primary_key=True)

    # Transaction details
    category = Column(String(50), nullable=False, index=True)
    date_time = Column(DateTime, nullable=False, index=True)
    amount = Column(DECIMAL(15, 2), nullable=False, index=True)
    
    # Transaction participants
    sender = Column(String(100), index=True)
    receiver = Column(String(100), index=True)
    
    # Additional transaction metadata
    transaction_id = Column(String(50), unique=True, index=True)
    raw_message = Column(Text)
    
    # Timestamp for record creation
    created_at = Column(
        DateTime, 
        default=datetime.utcnow, 
        server_default=func.now()
    )

    def to_dict(self):
        """
        Convert transaction to dictionary for API serialization
        
        Returns:
            dict: Serialized transaction data
        """
        return {
            'id': self.id,
            'category': self.category,
            'date_time': self.date_time.isoformat() if self.date_time else None,
            'amount': float(self.amount) if self.amount is not None else None,
            'sender': self.sender,
            'receiver': self.receiver,
            'transaction_id': self.transaction_id,
            'raw_message': self.raw_message,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    @classmethod
    def get_category_summary(cls, start_date=None, end_date=None):
        """
        Get summary of transactions grouped by category
        
        Args:
            start_date (datetime, optional): Start date for filtering
            end_date (datetime, optional): End date for filtering
        
        Returns:
            list: Summary of transactions by category
        """
        query = db.session.query(
            cls.category,
            func.count(cls.id).label('transaction_count'),
            func.sum(cls.amount).label('total_amount')
        ).group_by(cls.category)
        
        if start_date:
            query = query.filter(cls.date_time >= start_date)
        
        if end_date:
            query = query.filter(cls.date_time <= end_date)
        
        return query.all()

    @classmethod
    def get_monthly_summary(cls, start_date=None, end_date=None):
        """
        Get monthly transaction summary
        
        Args:
            start_date (datetime, optional): Start date for filtering
            end_date (datetime, optional): End date for filtering
        
        Returns:
            list: Monthly transaction summary
        """
        query = db.session.query(
            func.year(cls.date_time).label('year'),
            func.month(cls.date_time).label('month'),
            func.sum(cls.amount).label('total_amount'),
            func.count(cls.id).label('transaction_count')
        ).group_by('year', 'month')
        
        if start_date:
            query = query.filter(cls.date_time >= start_date)
        
        if end_date:
            query = query.filter(cls.date_time <= end_date)
        
        return query.order_by('year', 'month').all()

    def __repr__(self):
        """
        String representation of the transaction
        
        Returns:
            str: Transaction description
        """
        return (
            f"<Transaction {self.id}: "
            f"Category={self.category}, "
            f"Amount={self.amount}, "
            f"Date={self.date_time}>"
        )
    @classmethod
    def get_income_categories(cls):
        """
        Return list of income categories
        """
        return ['INCOMING_MONEY']

    @classmethod
    def get_expense_categories(cls):
        """
        Return list of expense categories
        """
        return[
            'WITHDRAWALS',
            'CODE_PAYMENTS',
            'MOBILE_TRANSFERS',
            'AIRTIME_PAYMENTS',
            'CASHPOWER_PAYMENTS',
            'THIRD_PARTY',
            'WITHDRAWALS_FROM_AGENTS',
            'BANK_TRANSFERS',
            'BUNDLES'
        ]
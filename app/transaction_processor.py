#transaction_processor.py
import xml.etree.ElementTree as ET
import re
from datetime import datetime
import json
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
import os

@dataclass
class TransactionData:
    category: str
    date_time: datetime
    amount: float
    sender: Optional[str]
    receiver: Optional[str]
    transaction_id: Optional[str]
    raw_message: str

class TransactionProcessor:
    def __init__(self, output_dir: str = "output"):
        self.categories = {
            "INCOMING_MONEY": r"(?!.*failed)(You have received \d+)|has been reversed",
            "CODE_PAYMENTS": r"(?!.*failed) Your payment | your payment",
            "MOBILE_TRANSFERS": r"(?!.*failed)(?!.*imbank\.bank)(\*165\*S\*.*transferred to |You have transferred|[A-Z][a-zA-Z\s]+ \(\d{12}\) has been completed)",
            "BANK_DEPOSITS": r"(?!.*failed)bank deposit",
            "AIRTIME_PAYMENTS": r"(?!.*failed)payment .* to Airtime",
            "CASHPOWER_PAYMENTS": r"(?!.*failed)(payment .* to MTN Cash Power) |ESICIA LTD ",
            "THIRD_PARTY": r"(?!.*failed)^(?!.*Data Bundle MTN)(\*164\*S\*Y'ello,A transaction of (\d+ RWF) by ([^ ]+)) |ONAFRIQ MAURITIUS|WASAC.",
            "BANK_TRANSFERS": r"(?!.*failed)imbank\.bank",
            "BUNDLES": r"(?!.*failed)(Data Bundle|Bundle MTN|Yello\!Umaze kugura|Bundles and Packs)",
            "WITHDRAWALS": r"(?!.*failed)withdrawn"
        }
        
        self.category_patterns = {cat: re.compile(pattern, re.IGNORECASE) 
                                for cat, pattern in self.categories.items()}
        
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
            
        logging.basicConfig(
            filename=f"{output_dir}/processing.log",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )
        
    def parse_xml(self, xml_file: str) -> List[str]:
        """Parse XML file and extract message bodies."""
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            messages = [sms.get("body", "") for sms in root.findall(".//sms")]
            logging.info(f"Successfully parsed {len(messages)} messages from XML")
            return messages
        except ET.ParseError as e:
            logging.error(f"XML parsing error: {e}")
            raise
        
    def extract_transaction_details(self, message: str) -> Optional[TransactionData]:
        """Extract transaction details from a message."""
        try:
            # Determine category
            category = next((cat for cat, pattern in self.category_patterns.items() 
                           if pattern.search(message)), "UNCATEGORIZED")
            
            # Extract amount
            amount_match = re.search(r"(\d+(?:,\d+)?)\s*RWF", message)
            amount = float(amount_match.group(1).replace(",", "")) if amount_match else 0.0
            
            # Extract datetime
            date_match = re.search(r"(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})", message)
            date_time = datetime.strptime(date_match.group(1), "%Y-%m-%d %H:%M:%S") if date_match else datetime.now()
            
            # Extract transaction ID
            txn_id_match = re.search(r"(?:Transaction Id:|TxId:)\s*(\d+)", message)
            txn_id = txn_id_match.group(1) if txn_id_match else None
            
            # Extract sender/receiver based on category
            sender = receiver = "Momo Balance"
            if category == "INCOMING_MONEY":
                sender_match = re.search(r"from\s+([^(]*)", message)
                sender = sender_match.group(1).strip() if sender_match else None
            elif category == "CODE_PAYMENTS":
                receiver_match = re.search(r"to\s+([A-Za-z\s]+)\s+\d+", message)
                receiver = receiver_match.group(1).strip() if receiver_match else None
            elif category == "MOBILE_TRANSFERS":
                receiver_match = re.search(r"to\s+([^(]*)", message)
                receiver = receiver_match.group(1).strip() if receiver_match else None
            elif category == "THIRD_PARTY":
                receiver_match = re.search(r"(?:by|to)\s+([A-Z\s]+?)(?=\s|$)", message)
                receiver = receiver_match.group(1).strip() if receiver_match else None
            elif category == "BANK_DEPOSITS":
                sender = "BANK"
            elif category == "BANK_TRANSFERS":
                sender = "BANK"
                receiver_match = re.search(r"to\s+([^(]*)", message)
                receiver = receiver_match.group(1).strip() if receiver_match else None
            elif category == "WITHDRAWALS":
                receiver = "Me"
            elif category == "CASHPOWER_PAYMENTS":
                receiver = "Cash Power"
            elif category == "BUNDLES":
                receiver = "Airtime_Balance"
            elif category == "AIRTIME_PAYMENTS"| "BUNDLES":
                receiver = "Airtime_Balance"
                
            return TransactionData(
                category=category,
                date_time=date_time,
                amount=amount,
                sender=sender,
                receiver=receiver,
                transaction_id=txn_id,
                raw_message=message
            )
        except Exception as e:
            logging.error(f"Error processing message: {e}\nMessage: {message[:100]}...")
            return None
            
    def save_to_file(self, transactions: List[TransactionData]):
        """Save transactions to respective category files."""
        try:
            categorized = {}
            for trans in transactions:
                categorized.setdefault(trans.category, []).append(trans)
                
            # Save each category to a separate JSON file
            for category, trans_list in categorized.items():
                filename = os.path.join(self.output_dir, f"{category.lower()}.json")
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump([
                        {
                            "datetime": t.date_time.isoformat(),
                            "amount": t.amount,
                            "sender": t.sender,
                            "receiver": t.receiver,
                            "transaction_id": t.transaction_id,
                            "raw_message": t.raw_message
                        } for t in trans_list
                    ], f, indent=2)
                logging.info(f"Saved {len(trans_list)} transactions to {filename}")
        except Exception as e:
            logging.error(f"Error saving to file: {e}")
            raise
            
    def process_file(self, xml_file: str) -> List[TransactionData]:
        """Main processing function."""
        try:
            messages = self.parse_xml(xml_file)
            transactions = [self.extract_transaction_details(msg) for msg in messages]
            transactions = [t for t in transactions if t]  # Filter out None values
            
            self.save_to_file(transactions)
            logging.info(f"Processing completed. Total transactions: {len(transactions)}")
            return transactions
        except Exception as e:
            logging.error(f"Processing failed: {e}")
            raise

    def get_category_summary(self, transactions: List[TransactionData]) -> Dict:
        """Generate summary statistics by category."""
        summary = {}
        for trans in transactions:
            if trans.category not in summary:
                summary[trans.category] = {
                    'count': 0,
                    'total_amount': 0,
                    'min_amount': float('inf'),
                    'max_amount': float('-inf')
                }
            
            stats = summary[trans.category]
            stats['count'] += 1
            stats['total_amount'] += trans.amount
            stats['min_amount'] = min(stats['min_amount'], trans.amount)
            stats['max_amount'] = max(stats['max_amount'], trans.amount)
        
        # Calculate averages and clean up infinity values
        for stats in summary.values():
            stats['avg_amount'] = stats['total_amount'] / stats['count']
            if stats['min_amount'] == float('inf'):
                stats['min_amount'] = 0
            if stats['max_amount'] == float('-inf'):
                stats['max_amount'] = 0
                
        return summary
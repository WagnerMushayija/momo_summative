# Fullstack SMS Data Processing Application

## Assignment Overview
This project involves designing and developing an enterprise-level fullstack application to process SMS data in XML format. The application will clean and categorize the data, store it in a relational database, and provide a frontend interface for analysis and visualization.

The dataset consists of approximately 1600 SMS messages from MTN MoMo, a Mobile Payment Service Provider in Rwanda. The goal is to extract meaningful insights from these messages and present them in an interactive dashboard.

## Learning Objectives
By completing this assignment, you will:
- Apply data cleaning and categorization techniques to extract insights from raw data.
- Design and implement a relational database schema for structured data storage.
- Develop a backend to handle database operations and integrate it with a frontend application.
- Build an interactive and user-friendly dashboard using HTML, CSS, and JavaScript.
- Demonstrate end-to-end problem-solving skills in fullstack application development.

## Deliverables
- **Python/JS Scripts**: For data cleaning, processing, and populating the database.
- **Database Schema**: Relational database design for SMS data storage.
- **Frontend Interface**: A dashboard to visualize and interact with the data.
- **Documentation**: A report explaining the approach, design decisions, and functionality of the application.

## Assignment Tasks
### 1. Data Cleaning and Processing (Backend)
#### Data Extraction
- Parse the provided XML file using JavaScript or Python libraries (e.g., `xml.etree.ElementTree`, `lxml`, `BeautifulSoup`).
- Extract and categorize SMS messages into the following types:
  - Incoming Money
  - Payments to Code Holders
  - Transfers to Mobile Numbers
  - Bank Deposits
  - Airtime Bill Payments
  - Cash Power Bill Payments
  - Transactions Initiated by Third Parties
  - Withdrawals from Agents
  - Bank Transfers
  - Internet and Voice Bundle Purchases

#### Data Cleaning
- Handle missing fields or erroneous data.
- Normalize text data (e.g., converting amounts to integers, formatting dates).

#### Logging
- Log unprocessed or ignored messages into a separate file for debugging and review.

### 2. Database Design and Implementation
#### Relational Database
- Design a schema that captures all relevant fields for each transaction type.
- Use SQLite, MySQL, or PostgreSQL for database implementation.

#### Data Insertion
- Develop a script to insert the cleaned and categorized data into the database.
- Ensure data integrity and handle duplicates or conflicting entries.

### 3. Frontend Dashboard Development
#### Dashboard Requirements
- Build an interactive dashboard using HTML, CSS, and JavaScript.
- Implement the following features:
  - **Search and Filter**: Enable users to search and filter transactions by type, date, or amount.
  - **Visualizations**: Use charts (e.g., bar charts, pie charts) to display:
    - Total transaction volume by type.
    - Monthly summaries of transactions.
    - Distribution of payments and deposits.
    - Additional relevant visualizations.
  - **Details View**: Show detailed information for selected transactions.

#### API Integration (Optional for Bonus Marks)
- Develop a simple backend API using Python (Flask/FastAPI) or NodeJS to fetch data from the database for the frontend.

## Getting Started
### Prerequisites
Ensure you have the following installed:
- **Python** (if using a Python backend)
- **Node.js** (if using a JavaScript backend)
- **Database System** (SQLite/MySQL/PostgreSQL)
- **Frontend Tools** (HTML, CSS, JavaScript, Chart.js for visualizations)

### Setup Instructions
1. Clone the repository:
   ```sh
   git clone https://github.com/your-repo/fullstack-sms-app.git
   cd fullstack-sms-app
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt  # For Python backend
   npm install  # For Node.js backend
   ```
3. Set up the database schema:
   ```sh
   python setup_database.py  # Python script to create tables
   ```
4. Run data processing:
   ```sh
   python process_sms.py  # Parses XML and inserts into DB
   ```
5. Start the backend server:
   ```sh
   python app.py  # Flask API
   ```
6. Start the frontend:
   ```sh
   open index.html  # Or use a local server
   ```

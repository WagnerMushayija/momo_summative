document.addEventListener('DOMContentLoaded', () => {
    // Configuration
    const API_BASE_URL = '/api';
    let currentPage = 1;
    let totalPages = 1;

    // Debug logging function
    const debugLog = (message, data) => {
        console.log(`[Dashboard Debug] ${message}`, data);
    };

    // Utility Functions
    const formatCurrency = (amount) => {
        // Handle potential NaN or null values
        const safeAmount = amount || 0;
        
        try {
            return new Intl.NumberFormat('en-RW', {
                style: 'currency',
                currency: 'RWF',
                minimumFractionDigits: 0,
                maximumFractionDigits: 0
            }).format(safeAmount);
        } catch (error) {
            console.error('Currency formatting error:', error);
            return `RWF ${safeAmount.toFixed(0)}`;
        }
    };

    const formatDate = (dateString) => {
        try {
            return new Date(dateString).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            });
        } catch (error) {
            console.error('Date formatting error:', error);
            return dateString;
        }
    };

    // DOM Element Selectors
    const elements = {
        // Navigation
        navButtons: document.querySelectorAll('.nav-btn'),
        sections: document.querySelectorAll('.section'),

        // Overview Section
        totalIncome: document.getElementById('total-income'),
        totalExpenses: document.getElementById('total-expenses'),
        netBalance: document.getElementById('net-balance'),
        
        // Charts
        categoryChart: document.getElementById('category-chart'),
        monthlyChart: document.getElementById('monthly-chart'),
        incomeExpenseChart: document.getElementById('income-expense-chart'),
        topCategoriesChart: document.getElementById('top-categories-chart'),
        
        // Transactions Section
        searchInput: document.getElementById('search-input'),
        categoryFilter: document.getElementById('category-filter'),
        startDateFilter: document.getElementById('start-date'),
        endDateFilter: document.getElementById('end-date'),
        transactionsBody: document.getElementById('full-transactions-body'),
        prevPageBtn: document.getElementById('prev-page'),
        nextPageBtn: document.getElementById('next-page'),
        pageInfo: document.getElementById('page-info'),

        // Analysis Section
        insightsContainer: document.getElementById('insights-container')
    };

    // Destroy existing chart if it exists
    const destroyExistingChart = (chartElement) => {
        if (chartElement && chartElement.chart) {
            chartElement.chart.destroy();
        }
    };

    // Chart Rendering Function
    const renderChart = (chartElement, chartType, chartData) => {
        if (!chartElement) {
            console.warn('Chart element not found');
            return null;
        }

        try {
            // Destroy any existing chart
            destroyExistingChart(chartElement);

            // Create new chart
            const ctx = chartElement.getContext('2d');
            const chart = new Chart(ctx, {
                type: chartType,
                data: chartData.data,
                options: chartData.options
            });

            // Store reference to chart on the canvas element
            chartElement.chart = chart;

            return chart;
        } catch (error) {
            console.error('Chart rendering error:', error);
            return null;
        }
    };

    // Fetch Financial Overview
    const fetchFinancialOverview = async () => {
        try {
            debugLog('Fetching financial overview');
            
            const response = await fetch(`${API_BASE_URL}/financial-overview`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            debugLog('Financial Overview Data:', data);

            // Validate and set default values
            const safeData = {
                total_income: data.total_income || 0,
                total_expenses: data.total_expenses || 0,
                net_balance: data.net_balance || 0,
                category_summary: data.category_summary || [],
                monthly_summary: data.monthly_summary || [],
                income_vs_expenses: data.income_vs_expenses || [],
                top_spending_categories: data.top_spending_categories || []
            };

            // Update summary cards
            if (elements.totalIncome) 
                elements.totalIncome.textContent = formatCurrency(safeData.total_income);
            if (elements.totalExpenses) 
                elements.totalExpenses.textContent = formatCurrency(safeData.total_expenses);
            if (elements.netBalance) 
                elements.netBalance.textContent = formatCurrency(safeData.net_balance);

            // Render Charts with null checks
            if (safeData.category_summary.length > 0) {
                renderCategoryChart(safeData.category_summary);
            }

            if (safeData.monthly_summary.length > 0) {
                renderMonthlyChart(safeData.monthly_summary);
            }

            // Only render these if data exists
            if (safeData.income_vs_expenses && safeData.income_vs_expenses.length > 0) {
                renderIncomeExpenseChart(safeData.income_vs_expenses);
            }

            if (safeData.top_spending_categories && safeData.top_spending_categories.length > 0) {
                renderTopSpendingCategories(safeData.top_spending_categories);
            }

            // Populate Category Filter
            if (safeData.category_summary.length > 0) {
                populateCategoryFilter(safeData.category_summary);
            }

        } catch (error) {
            console.error('Error fetching financial overview:', error);
            
            // Update UI to show error
            if (elements.totalIncome) 
                elements.totalIncome.textContent = 'Failed to load';
            if (elements.totalExpenses) 
                elements.totalExpenses.textContent = 'Failed to load';
            if (elements.netBalance) 
                elements.netBalance.textContent = 'Failed to load';
        }
    };

    // Category Chart Rendering
    const renderCategoryChart = (categorySummary) => {
        if (!elements.categoryChart || !categorySummary || categorySummary.length === 0) {
            console.warn('No category data to render');
            return;
        }

        debugLog('Rendering Category Chart', categorySummary);
        
        const chartData = {
            data: {
                labels: categorySummary.map(cat => cat.category),
                datasets: [{
                    data: categorySummary.map(cat => Math.abs(cat.total_amount)),
                    backgroundColor: [
                        '#FF6384', '#36A2EB', '#FFCE56', 
                        '#4BC0C0', '#9966FF', '#FF9F40'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Spending by Category'
                    }
                }
            }
        };

        renderChart(elements.categoryChart, 'pie', chartData);
    };

    // Monthly Chart Rendering
    const renderMonthlyChart = (monthlySummary) => {
        if (!elements.monthlyChart || !monthlySummary || monthlySummary.length === 0) {
            console.warn('No monthly data to render');
            return;
        }

        debugLog('Rendering Monthly Chart', monthlySummary);
        
        const chartData = {
            data: {
                labels: monthlySummary.map(m => `${m.year}-${m.month}`),
                datasets: [{
                    label: 'Monthly Transactions',
                    data: monthlySummary.map(m => Math.abs(m.total_amount)),
                    backgroundColor: '#36A2EB'
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Monthly Transaction Volumes'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return formatCurrency(value);
                            }
                        }
                    }
                }
            }
        };

        renderChart(elements.monthlyChart, 'bar', chartData);
    };

    // Income vs Expenses Chart Rendering
    const renderIncomeExpenseChart = (incomeVsExpenses) => {
        if (!elements.incomeExpenseChart || !incomeVsExpenses || incomeVsExpenses.length === 0) {
            console.warn('No income vs expenses data to render');
            return;
        }

        debugLog('Rendering Income vs Expenses Chart', incomeVsExpenses);
        
        const chartData = {
            data: {
                labels: incomeVsExpenses.map(m => `${m.year}-${m.month}`),
                datasets: [
                    {
                        label: 'Income',
                        data: incomeVsExpenses.map(m => m.income || 0),
                        borderColor: '#2ecc71',
                        backgroundColor: 'rgba(46, 204, 113, 0.2)'
                    },
                    {
                        label: 'Expenses',
                        data: incomeVsExpenses.map(m => Math.abs(m.expenses || 0)),
                        borderColor: '#e74c3c',
                        backgroundColor: 'rgba(231, 76, 60, 0.2)'
                    }
                ]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Income vs Expenses'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return formatCurrency(value);
                            }
                        }
                    }
                }
            }
        };

        renderChart(elements.incomeExpenseChart, 'line', chartData);
    };

    // Top Spending Categories Chart Rendering
    const renderTopSpendingCategories = (topCategories) => {
        if (!elements.topCategoriesChart || !topCategories || topCategories.length === 0) {
            console.warn('No top spending categories data to render');
            return;
        }

        debugLog('Rendering Top Spending Categories', topCategories);
        
        const chartData = {
            data: {
                labels: topCategories.map(cat => cat.category),
                datasets: [{
                    label: 'Top Spending Categories',
                    data: topCategories.map(cat => Math.abs(cat.total_spent)),
                    backgroundColor: '#e74c3c'
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Top Spending Categories'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return formatCurrency(value);
                            }
                        }
                    }
                }
            }
        };

        renderChart(elements.topCategoriesChart, 'bar', chartData);
    };

    // Transactions Table Rendering
    const renderTransactionsTable = (transactions) => {
        if (!elements.transactionsBody) return;

        if (!transactions || transactions.length === 0) {
            elements.transactionsBody.innerHTML = '<tr><td colspan="5">No transactions found</td></tr>';
            return;
        }

        elements.transactionsBody.innerHTML = transactions.map(trans => `
            <tr>
                <td>${formatDate(trans.date_time)}</td>
                <td>${trans.category}</td>
                <td>${formatCurrency(trans.amount)}</td>
                <td>${trans.sender || 'N/A'}</td>
                <td>${trans.receiver || 'N/A'}</td>
            </tr>
        `).join('');
    };

    // Fetch Transactions
    const fetchTransactions = async (page = 1, filters = {}) => {
        try {
            const queryParams = new URLSearchParams({
                page: page,
                per_page: 10,
                ...filters
            });

            const response = await fetch(`${API_BASE_URL}/transactions?${queryParams}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            // Render transactions
            renderTransactionsTable(data.transactions);

            // Update pagination
            currentPage = data.current_page;
            totalPages = data.total_pages;
            updatePagination();
        } catch (error) {
            console.error('Error fetching transactions:', error);
            // Show error in transactions table
            if (elements.transactionsBody) {
                elements.transactionsBody.innerHTML = `
                    <tr>
                        <td colspan="5">Error loading transactions: ${error.message}</td>
                    </tr>
                `;
            }
        }
    };

    // Search Transactions
    const searchTransactions = async (query) => {
        try {
            const encodedQuery = encodeURIComponent(query);
            const response = await fetch(`${API_BASE_URL}/search?q=${encodedQuery}`);
            
            if (!response.ok) {
                throw new Error('Search request failed');
            }
            
            const data = await response.json();
            renderTransactionsTable(data.transactions);
            
            // Update pagination
            currentPage = data.current_page;
            totalPages = data.total_pages;
            updatePagination();
        } catch (error) {
            console.error('Error searching transactions:', error);
            alert('Unable to perform search. Please try again.');
        }
    };

    // Pagination Update
    const updatePagination = () => {
        if (!elements.pageInfo || !elements.prevPageBtn || !elements.nextPageBtn) return;

        elements.pageInfo.textContent = `Page ${currentPage} of ${totalPages}`;
        elements.prevPageBtn.disabled = currentPage === 1;
        elements.nextPageBtn.disabled = currentPage === totalPages;
    };

    // Category Filter Population
    const populateCategoryFilter = (categorySummary) => {
        if (!elements.categoryFilter) return;

        const categories = [...new Set(categorySummary.map(cat => cat.category))];
        elements.categoryFilter.innerHTML = `
            <option value="">All Categories</option>
            ${categories.map(cat => `<option value="${cat}">${cat}</option>`).join('')}
        `;
    };

    // Navigation Handler
    const setupNavigation = () => {
        elements.navButtons.forEach(button => {
            button.addEventListener('click', () => {
                // Remove active class from all buttons and sections
                elements.navButtons.forEach(btn => btn.classList.remove('active'));
                elements.sections.forEach(section => section.classList.remove('active'));

                // Add active class to clicked button and corresponding section
                button.classList.add('active');
                document.getElementById(button.dataset.section).classList.add('active');
            });
        });
    };

   // Event Listeners Setup
   const setupEventListeners = () => {
    // Search input
    if (elements.searchInput) {
        elements.searchInput.addEventListener('input', (e) => {
            const query = e.target.value;
            if (query.length > 2) {
                searchTransactions(query);
            } else {
                fetchTransactions();
            }
        });
    }

    // Category filter
    if (elements.categoryFilter) {
        elements.categoryFilter.addEventListener('change', (e) => {
            const category = e.target.value;
            fetchTransactions(1, category ? { category } : {});
        });
    }

    // Date filters
    if (elements.startDateFilter) {
        elements.startDateFilter.addEventListener('change', () => {
            fetchTransactions(1, {
                start_date: elements.startDateFilter.value,
                end_date: elements.endDateFilter.value
            });
        });
    }

    if (elements.endDateFilter) {
        elements.endDateFilter.addEventListener('change', () => {
            fetchTransactions(1, {
                start_date: elements.startDateFilter.value,
                end_date: elements.endDateFilter.value
            });
        });
    }

    // Pagination buttons
    if (elements.prevPageBtn) {
        elements.prevPageBtn.addEventListener('click', () => {
            if (currentPage > 1) {
                fetchTransactions(currentPage - 1);
            }
        });
    }

    if (elements.nextPageBtn) {
        elements.nextPageBtn.addEventListener('click', () => {
            if (currentPage < totalPages) {
                fetchTransactions(currentPage + 1);
            }
        });
    }
};

// Initialize Dashboard
const initializeDashboard = async () => {
    // Setup UI components
    setupNavigation();
    setupEventListeners();

    // Fetch initial data
    await fetchFinancialOverview();
    await fetchTransactions();
};

// Start the dashboard
initializeDashboard();
});
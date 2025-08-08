Personal Finance Adviser Web Application
A full-stack web application designed to help users track their personal finances by integrating real-time transaction data and offering a modern, user-friendly interface.
Overview
This project provides a dashboard to monitor income, expenses, and budget status, with a pie chart to visualize spending categories. It connects to bank accounts via the Plaid API and includes a detailed transaction view with interactive features.
Features

Dashboard: Shows total income ($17,977.38), expenses ($1,512.66), and budget status, with a pie chart for categories like Food, Travel, and Other.
Plaid Integration: Links to bank accounts to fetch real-time transaction data (currently 27 records).
Modern UI/UX: Features a sleek design with glassmorphism, animations, and dark mode support based on browser settings.
Transaction Details: Displays transactions in a card-based layout with a filter option by name.
Authentication: Includes custom login and logout functionality.

Technologies Used

Backend: Python, Django
Frontend: HTML, CSS (Tailwind CSS), JavaScript (Chart.js)
API: Plaid API
Database: PostgreSQL
Tools: Git, VS Code

Installation

Clone the project repository and set up a virtual environment.
Install required dependencies using the provided instructions.
Configure environment variables with Plaid API credentials and database details.
Apply database migrations and run the development server.

Usage

Log in with a default user or register a new account.
Connect your bank account via the "Connect Bank Account" button.
Set a budget on the dashboard and view updated transactions and charts.
Use the filter on the transaction details page to search by name.

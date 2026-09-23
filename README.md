# AWS Cloud Bank Web Application 

A full-stack banking management web application built with **Python, Flask, and SQL**. The project was originally deployed on **AWS EC2 with Amazon RDS MySQL** and was later migrated to **Render with PostgreSQL**. The application can also be configured to use **SQLite for local development**.

## Project Overview

<img width="782" height="915" alt="Dashboard" src="https://github.com/user-attachments/assets/391ec16d-8089-47d3-92ca-1aca400b2942" />

This project is a web-based banking management system designed to demonstrate full-stack application development, relational database management, and cloud deployment.

The backend is built with **Python and Flask**, providing server-side application logic and routes for managing customers, bank accounts, transactions, payees, and account information.

The application was designed to work across multiple relational database environments:

## Features

### Customer Management

* Create customers
* View customer information
* Update customer information
* Delete customers
* Associate customers with accounts

### Bank Account Management

* Create chequing accounts
* Create savings accounts
* Update account information
* Delete accounts
* View account balances
* Close accounts

### Transactions

* Record deposits
* Process account transfers
* Process bill payments
* Update account balances
* View transaction history

### Payee Management

* Add payees
* Update payee information
* Delete payees
* Associate payees with customer accounts

### Database Dashboard

The application uses relational SQL queries and joins to combine customer and account information into a centralized dashboard.

## Database

The application uses a relational database to manage customers, accounts, and banking transactions.

Depending on the deployment environment, the project has used:

* **MySQL** — original AWS RDS deployment
* **PostgreSQL** — Render deployment
* **SQLite** — local development

The application performs common relational database operations including:

* `SELECT`
* `INSERT`
* `UPDATE`
* `DELETE`
* `JOIN`
* `LEFT JOIN`
* `UNION`

The database layer manages functionality for customers, chequing accounts, savings accounts, deposits, transfers, bill payments, account closures, and payees.





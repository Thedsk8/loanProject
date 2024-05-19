# Loan Management System

## Project Overview

This project is a Loan Management System designed to handle loan creation, approval, and repayment processes. This is created using python with Django Framework.
The system supports two user roles:
1. **Approver**: Can approve loan requests.
2. **Borrower**: Can borrow loans.

Main Logic:
1. **loan**: Loan folder contains logic about all the loan api and its model
2. **users**: User contains logic about users. Only required funcitonality is implemented here.

## POSTMAN
### Collection is attached in json format.

## Prerequisites

1. **Python**: Ensure Python is installed on your system.
2. **PostgreSQL**: Database setup requires PostgreSQL.

## Setup Instructions

### Step 1: Create Python Virtual Environment

1. Create a virtual environment:
   ```sh
   python -m venv venv
2. Activate Virtual Environment
   ```sh
   source venv/bin/activate
3. Install Requirement:
   ```sh
   pip install -r requirements.txt

### Step 2: Postgres Database Setup
1. Create databse:
   ```sh
   create database loans;
2. Create user:
   ```sh
   create role loans with password 'loans';
3. Alter Role:
   ```sh
   alter role loans with Login CreateDb;
4. Grant Privileges:
   ```sh
   grant all privileges on database loans to loans;


### Step 3: Create Postgres Tables
1. Run Command from directory where loan project is present:
   ```sh
   python manage.py migrate;

### Step 4: Create Initial Users
1. Automatically create some borrowers and approvers. Save their email IDs and passwords for testing:
   ```sh
   python manage.py create_initial_users;

### Step 5: Run Server
1. By default Server will run on port 8000
   ```sh
   python manage.py runserver;
   
### Alternative

#### Docker and Docker Compose file are also to run this setup, please use these if docker is installed in your system

Automated ETL Pipeline for Security Reporting
**Overview**

This project automates the process of collecting CSV and Excel reports from designated folders, transforming and cleaning the data, loading it into BigQuery, and visualizing the results in Looker.

The objective is to reduce manual effort in report consolidation and provide a scalable way to monitor the effectiveness of a security control through automated reporting and dashboards.

**Features**
Automatically scans folders for new CSV and Excel files
Consolidates multiple reports into a single dataset
Removes blank rows and unnecessary columns
Standardizes data formats
Loads transformed data into Google BigQuery
Calculates required metrics and percentages using SQL
Displays results in Looker dashboards
**
**Tech Stack****
Python
Pandas
Google BigQuery
SQL
Looker Studio / Looker
Google Cloud Platform
Workflow
Source files are placed in designated folders.
Python script reads and consolidates the files.
Data cleaning and transformations are performed.
Cleaned data is loaded into BigQuery.
SQL queries calculate reporting metrics.
Looker dashboards display the final results.
Example Use Case

The project can be used to monitor the effectiveness of a security measure by comparing outcomes across different respondent groups and calculating percentage distributions automatically.

****Future Improvements**
Scheduled execution using Cloud Functions or Cloud Run
Automated email reports
Robust detection and visualisation based on security responses
Additional dashboard metrics

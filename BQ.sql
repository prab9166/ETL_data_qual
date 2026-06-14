## BigQuery Transformation

After loading the transformed dataset into BigQuery, SQL queries are used to calculate percentage distributions and reporting metrics required for dashboarding.

Example:

SELECT
    Status,
    GENDER,
    ROUND(COUNT(TA)*100/SUM(COUNT(TA)) OVER(), 2) AS perct_of_total
FROM dataset.converted_file
GROUP BY Status, GENDER

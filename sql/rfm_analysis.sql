WITH rfm_raw_data AS (
    -- BOX 1: The Raw Numbers
    SELECT 
        CustomerID,
        DATE_DIFF(DATE('2011-12-10'), MAX(DATE(InvoiceDate)), DAY) AS Recency,
        COUNT(DISTINCT InvoiceNo) AS Frequency,
        ROUND(SUM(TotalSales), 2) AS Monetary
    FROM 
        `rfm-analytics-engine.rfm_data.raw_transactions`
    GROUP BY 
        CustomerID
),

rfm_scores AS (
    -- BOX 2: The 1-4 Grades
    SELECT 
        CustomerID,
        Recency,
        Frequency,
        Monetary,
        NTILE(4) OVER (ORDER BY Recency DESC) AS R_Score,
        NTILE(4) OVER (ORDER BY Frequency ASC) AS F_Score,
        NTILE(4) OVER (ORDER BY Monetary ASC) AS M_Score
    FROM 
        rfm_raw_data
)

-- FINAL OUTPUT: The Labels
SELECT 
    CustomerID,
    Recency,
    Frequency,
    Monetary,
    R_Score,
    F_Score,
    M_Score,
    
    -- Combine the three numbers into a single string (e.g., '444')
    CONCAT(CAST(R_Score AS STRING), CAST(F_Score AS STRING), CAST(M_Score AS STRING)) AS RFM_Score,
    
    -- Automatically assign a segment based on the grades
    CASE 
        WHEN R_Score = 4 AND F_Score = 4 AND M_Score = 4 THEN 'Champions'
        WHEN R_Score >= 3 AND F_Score >= 3 THEN 'Loyal Customers'
        WHEN R_Score >= 3 AND F_Score <= 2 THEN 'New / Promising'
        WHEN R_Score <= 2 AND F_Score >= 3 THEN 'At Risk / Needs Attention'
        WHEN R_Score <= 1 AND F_Score <= 1 THEN 'Lost / Churned'
        ELSE 'Average Customers'
    END AS Customer_Segment

FROM 
    rfm_scores
ORDER BY 
    RFM_Score DESC
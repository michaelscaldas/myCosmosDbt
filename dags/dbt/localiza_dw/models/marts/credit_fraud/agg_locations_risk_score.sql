SELECT
	location_region,
	avg(risk_score) AS risk_score_mean
FROM
	{{ ref('stg_credit_fraud') }}
WHERE
    location_region IN ('North America', 'South America', 'Asia', 'Africa', 'Europe')
GROUP BY
	1
ORDER BY
    2 DESC
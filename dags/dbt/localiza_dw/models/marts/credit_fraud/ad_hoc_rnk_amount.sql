WITH dedup AS (
    SELECT
        receiving_address,
        amount,
        "timestamp",
        ROW_NUMBER() OVER (PARTITION BY receiving_address ORDER BY "timestamp" DESC) AS row_num
    FROM
        {{ ref('stg_credit_fraud') }}
    WHERE
        transaction_type = 'sale'
    AND amount IS NOT NULL
)
SELECT
    receiving_address,
    amount,
    "timestamp"
FROM
    dedup
WHERE
    row_num = 1
ORDER BY
    amount DESC
LIMIT 3
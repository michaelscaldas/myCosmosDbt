with source as (

    {#-
    Normally we would select from the table here, but we are using seeds to load
    our data in this project
    #}
    select * from {{ source('credit_fraud', 'raw_credit_fraud') }}

),

clean_fraud_credit as (

    select
        CAST(timestamp AS BIGINT) AS timestamp,
        sending_address,
        receiving_address,
        COALESCE(
            NULLIF(
                REGEXP_REPLACE(amount, '[^0-9.]', '', 'g'),
                    ''
                )::FLOAT,
            NULL
        ) AS amount,
        transaction_type,
        location_region,
        ip_prefix,
        CAST(login_frequency AS INT) AS login_frequency,
        CAST(session_duration AS INT) AS session_duration,
        purchase_pattern,
        age_group,
        COALESCE(
            NULLIF(
                REGEXP_REPLACE(risk_score, '[^0-9.]', '', 'g'),
                    ''
                )::FLOAT,
            NULL
        ) AS risk_score,
        anomaly
    FROM source
    WHERE 1=1
        AND amount IS NOT NULL
        AND risk_score IS NOT NULL
        AND timestamp IS NOT NULL
        AND transaction_type IS NOT NULL
)

SELECT * FROM clean_fraud_credit

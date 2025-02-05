{% snapshot dm_transaction_type %}

{{
    config(
        target_schema='dm_credit_operations',
        unique_key='transaction_type',
        strategy='timestamp',
        updated_at='updated_at'
    )
}}

select 
    -- Gerando o ID baseado no transaction_type
    md5(transaction_type) as dim_id,
    transaction_type,
    max("timestamp") as updated_at
from 
    {{ ref('stg_credit_fraud') }}
group by 
    transaction_type

{% endsnapshot %}

WITH MEDIA_VENDAS_PROD AS (
    SELECT
        "v"."COD_LOJA",
        AVG("v"."QUANTIDADE") AS "MEDIA_PROD"
    FROM {{ ref('eventos_vendas') }} "v"
    JOIN {{ ref('dim_vendedor') }} "ve" ON "v"."COD_VENDEDOR" = "ve"."COD_VENDEDOR"
    WHERE "v"."COD_PRODUTO" = '{{ var("PROD") }}'
      AND "v"."DATA" BETWEEN '{{ var("DATA_INICIO") }}' AND '{{ var("DATA_FIM") }}'
    GROUP BY "v"."COD_LOJA"
    {% if var("LIMITE_QUANTIDADE", "") != "" %}
    HAVING SUM("v"."QUANTIDADE") > '{{ var("LIMITE_QUANTIDADE") }}'
    {% endif %}
)

SELECT "v1"."COD_VENDEDOR", "v1"."COD_PRODUTO", "m"."MEDIA_PROD" AS "MEDIA_QTD_PROD", SUM("v1"."QUANTIDADE") AS "TOTAL"
FROM {{ ref('eventos_vendas') }} "v1"
JOIN MEDIA_VENDAS_PROD "m" ON "v1"."COD_LOJA" = "m"."COD_LOJA"
WHERE "v1"."COD_PRODUTO" = '{{ var("PROD") }}'
  AND "v1"."DATA" BETWEEN '{{ var("DATA_INICIO") }}' AND '{{ var("DATA_FIM") }}'
  AND "v1"."QUANTIDADE" > "m"."MEDIA_PROD"
GROUP BY 1,2,3
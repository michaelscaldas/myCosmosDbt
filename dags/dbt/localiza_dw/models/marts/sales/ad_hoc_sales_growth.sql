WITH "VENDAS_ORDENADAS" AS (
    SELECT
        "v"."COD_VENDEDOR",
        "v"."DATA",
        "v"."QUANTIDADE",
        "v"."COD_PRODUTO",
        LAG("v"."QUANTIDADE") OVER (PARTITION BY "v"."COD_VENDEDOR" ORDER BY "v"."DATA") AS "QUANTIDADE_ANTERIOR"
    FROM {{ ref('eventos_vendas') }} "v"
    WHERE "v"."COD_PRODUTO" = '{{ var("PROD") }}'
      AND "v"."DATA" BETWEEN '{{ var("DATA_INICIO") }}' AND '{{ var("DATA_FIM") }}'
)

SELECT CONCAT('{{ var("DATA_INICIO") }}',' A ','{{ var("DATA_FIM") }}') AS "PERIODO", "COD_PRODUTO", "COD_VENDEDOR", "QUANTIDADE", "QUANTIDADE_ANTERIOR"
FROM "VENDAS_ORDENADAS"
GROUP BY 1,2,3,4,5
HAVING SUM(CASE
               WHEN "QUANTIDADE_ANTERIOR" IS NOT NULL
                    AND "QUANTIDADE" <= "QUANTIDADE_ANTERIOR"
               THEN 1
               ELSE 0
           END) = 0

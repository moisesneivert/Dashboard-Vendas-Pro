# Dicionário de dados

| Coluna | Tipo | Descrição |
|---|---|---|
| `sale_date` | data | Data da venda |
| `order_id` | texto | Identificador do pedido; pode repetir quando houver mais de um item |
| `region` | texto | Região comercial |
| `state` | texto | Unidade federativa |
| `category` | texto | Categoria do produto ou serviço |
| `product` | texto | Produto ou serviço vendido |
| `seller` | texto | Responsável pela venda |
| `channel` | texto | Canal comercial |
| `payment_status` | texto | Situação do pagamento |
| `quantity` | inteiro | Quantidade vendida |
| `unit_price` | decimal | Preço unitário |
| `unit_cost` | decimal | Custo unitário |

O dashboard calcula `revenue`, `cost`, `profit`, `margin_pct`, `month` e outros campos derivados.

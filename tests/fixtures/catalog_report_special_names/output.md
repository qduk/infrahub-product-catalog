# Catalog coverage report

1 product, 2 building blocks, 1 coverage claim.

## Coverage by product

| Product | Block "B" | Block (A) |
|---|---|---|
| Example Corp Tool "X" [beta] \| (v2) | — | Full |

Each claim's sources are listed on the claim in the catalog.

## Products per building block

```mermaid
xychart-beta
    title "Products per building block"
    x-axis ["Block #quot;B#quot;", "Block (A)"]
    y-axis "Products" 0 --> 1
    bar [0, 1]
    bar [0, 1]
```

The first bar series counts all products that cover the block. The second, drawn over it, counts products with full coverage. The difference is partial coverage.

## Map of products to building blocks

```mermaid
flowchart LR
    p1["Example Corp Tool #quot;X#quot; [beta] | (v2)"]
    b1["Block #quot;B#quot;"]
    b2["Block (A)"]
    p1 ==> b2
```

Thick lines show full coverage. Dotted lines show partial coverage.

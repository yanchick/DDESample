---
title: Дашбордик от Ян Олеговича
---



```sql categories
  select
       count(*) as count
  from authors
  group by paper_id

```

Среднее количество авторов на статью

<BigValue 
  data={categories} 
  value=count
/>
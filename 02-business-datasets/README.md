# Week 02 — Business Datasets (ypages.pk)

Curated Excel datasets extracted during internship for Pakistani business categories.

**Source focus:** ypages.pk  
**Prepared by:** Hammad Durrani

## What is inside

30 `.xlsx` files covering categories such as:

- Beauty Salons, Boutiques, Hair Transplant
- Dental / Heart / Plastic Surgery clinics
- Restaurants, Banquet Halls, Event Management
- Travel Agencies, Umrah Services, Rent A Car
- Security Services / Equipment, Packers and Movers
- Architects, Interior Designers, Furniture Manufacturers
- and other SME categories

## How to use

1. Open any `.xlsx` file in Excel, Google Sheets, or pandas  
2. Use as sample leads / training data for scraping or CRM experiments  
3. Combine with Week 03 pipeline ideas for automated enrichment  

```python
import pandas as pd
df = pd.read_excel("Resturants  Datasets ypages-byhammaddurrani.xlsx")
print(df.head())
```

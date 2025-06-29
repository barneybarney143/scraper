# scraper
Web Scraper to collect a list of links

## Vinted price checker

Create a CSV file where each line contains an item name and a maximum price separated by a comma. Example:

```
ray-ban napszemüveg,30000
nike cipő,15000
```

Run the checker with:

```
python vinted_checker.py items.csv
```

The script searches Vinted for each item and prints whether there is a listing below the specified price.

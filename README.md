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

The script performs a free-text search on Vinted for each item and checks the
first 20 results to see if any listing is available under the given price.

# Chinese-and-Cantonese-Bilingual-Database-Scraper

A web scraper that extracts Cantonese and corresponding Standard Chinese vocabulary data from the 香港中文大學 [現代標準漢語與粵語對照資料庫](https://apps.itsc.cuhk.edu.hk/hanyu/Page/Cover.aspx). 

The scraper fetches data concurrently, processes the content, and writes two CSV files:

- **original.csv**: Contains all scraped fields.
- **corresponding.csv**: Contains a filtered subset of the data.

## How to use
Execute the following commands in the terminal:
```
git clone https://github.com/Benson-mk/Chinese-and-Cantonese-Bilingual-Database-Scraper.git
cd Chinese-and-Cantonese-Bilingual-Database-Scraper
pip install -r requirements.txt
python main.py
```

## License

This program is distributed under the [MIT License](./LICENSE).

The data is Copyright © 2014. All Rights Reserved. Department of Chinese Language and Literature, The Chinese University of Hong Kong.

# Python

# Task
After spending the week learning the basics to cleaning and visualising data using python one of our final tasks was to import, clean, visualise and produce insights using Google Colab to run the code.

# Part A: Produce the Insight

- Prepare the data
- Make one justified cleaning decision
- Ask an analytical question
- Analyse before you plot
- Choose the visual deliberately
- Challenge the visual
- Communicate the result

```py
from google.colab import files
csv = files.upload()
```
```py
import pandas as pd
bs = pd.read_csv('Happiness.csv')
bs
```
|     | Country     | Region                          | Happiness Rank | Happiness Score | Lower Confidence Interval | Upper Confidence Interval | Economy (GDP per Capita) | Family  | Health (Life Expectancy) | Freedom |
|-----|-------------|---------------------------------|----------------|-----------------|---------------------------|---------------------------|--------------------------|---------|--------------------------|---------|
| 0   | Denmark     | Western Europe                  | 1              | 7.526           | 7.460                     | 7.592                     | 1.44178                  | 1.16374 | 0.79504                  | 0.57941 |
| 1   | Switzerland | Western Europe                  | 2              | 7.509           | 7.428                     | 7.590                     | 1.52733                  | 1.14524 | 0.86303                  | 0.58557 |
| 2   | Iceland     | Western Europe                  | 3              | 7.501           | 7.333                     | 7.669                     | 1.42666                  | 1.18326 | 0.86733                  | 0.56624 |
| 3   | Norway      | Western Europe                  | 4              | 7.498           | 7.421                     | 7.575                     | 1.57744                  | 1.12690 | 0.79579                  | 0.59609 |
| 4   | Finland     | Western Europe                  | 5              | 7.413           | 7.351                     | 7.475                     | 1.40598                  | 1.13464 | 0.81091                  | 0.57104 |
| 152 | Benin       | Sub-Saharan Africa              | 153            | 3.484           | 3.404                     | 3.564                     | 0.39499                  | 0.10419 | 0.21028                  | 0.39747 |
| 153 | Afghanistan | Southern Asia                   | 154            | 3.360           | 3.288                     | 3.432                     | 0.38227                  | 0.11037 | 0.17344                  | 0.16430 |
| 154 | Togo        | Sub-Saharan Africa              | 155            | 3.303           | 3.192                     | 3.414                     | 0.28123                  | 0.00000 | 0.24811                  | 0.34678 |
| 155 | Syria       | Middle East and Northern Africa | 156            | 3.069           | 2.936                     | 3.202                     | 0.74719                  | 0.14866 | 0.62994                  | 0.06912 |
| 156 | Burundi     | Sub-Saharan Africa              | 157            | 2.905           | 2.732                     | 3.078                     | 0.06831                  | 0.23442 | 0.15747                  | 0.04320 |

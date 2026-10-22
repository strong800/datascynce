# Йойофлот: поиск подозрительных пассажиров

Объединение и очистка данных о перелётах из 6 источников, восстановление типов поездок и поиск подозрительных пассажиров.

## Файлы

- `parse_xlsx.py` - читает посадочные талоны из xlsx
- `parse_sources.py` - читает json, xml, yaml и tab
- `analysis.ipynb` - очистка, объединение, типы поездок, критерии
- `figures/` - графики

## Запуск

Исходные данные лежат в папке выше (`../`).

```
python parse_xlsx.py ../YourBoardingPassDotAero data/boarding_passes.csv
python parse_sources.py
```

Потом запустить `analysis.ipynb`.

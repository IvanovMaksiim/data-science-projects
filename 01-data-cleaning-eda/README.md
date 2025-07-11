# EDA   Анализ рынка Airbnb в Нью-Йорке (2019)

**Краткое описание**: Исследование данных о бронировании жилья в NY за 2019 год с целью Exploratory Data Analysis. 

## Гипотезы
1. **H1**: Средняя цена аренды в Manhattan выше, чем в других районах.
2. **H2**: Объекты типа `Entire home/apt` имеют более высокую цену, чем комнаты.
3. **H3**: У популярных хостов (>100 отзывов) цена ниже, чем у новых.
4. **H4**: В районах с высокой плотностью предложений цена ниже (высокая конкуренция).
5. **H5**: Хосты с большим количеством объектов предлагают более низкие цены (эффект масштаба)

## Структура анализа 
Код разделен на логические этапы:  
1. **Загрузка и первичный осмотр**: Проверка пропусков, дубликатов, описательная статистика.  
2. **Нормализация данных**: Обработка выбросов, категориальных переменных.  
3. **Разведочный анализ**: Визуализации (гистограммы, boxplot, scatterplot).  
4. **Проверка гипотез**: Статистические тесты (t-test, корреляции и др.).  
5. **Выводы**: Итоговые наблюдения.

## Ключевые выводы
1. **Цены по районам**:
   - Аренда в Manhattan статистически значимо дороже, чем в Queens и Staten Island (p < 0.05).
2. **Тип жилья**:
   - `Entire home/apt` имеют значимо более высокую цену, чем `Shared room`.
3. **Активность хостов**:
   - Более крупные хосты устанавливают более высокие цены (возможно, из-за брендинга или качества обслуживания).

## Технологии и библиотеки
- **Python 3**
- **Основные библиотеки**:
  - `pandas`, `numpy` — обработка данных
  - `matplotlib`, `seaborn` — визуализация
  - `scipy`, `statsmodels` — статистические тесты

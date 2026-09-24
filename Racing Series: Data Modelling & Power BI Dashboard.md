# Racing Series: Data Modelling & Power BI Dashboard

## Project Overview

This project involved transforming a single spreadsheet containing data from a racing series into a relational data model in Excel, before connecting the model to Power BI to produce an interactive leaderboard and driver statistics dashboard.

The project demonstrates the ability to take raw data and turn it into a structured, analysis-ready dataset, while applying principles of data modelling, data cleaning, and relational database design.

## The Original Data

## The Restructured Data

## On to Power BI

### Importing and Loading the Data

![Power BI data import](images/powerbi_import)

![Restructured Power BI data](images/powerbi_load_data)

### Creating the Relationships

![Power BI data model relationships](images/powerbi_relationships)

### DAX Formulas

![DAX measures](images/powerbi_measures)

The following measures were created:

- `#Cars` — Counts the distinct number of cars used throughout the races.
- `#Champs` — Counts the number of championships.
- `#Races` — Counts the number of races.
- `#Tracks` — Counts the number of tracks raced.
- `Championship Points` — Calculates the total points earned.
- `Championship Position` — Ranks the driver by championship points.
- `driverRaces` — Counts the number of races per driver.
- `Finish Position Points` — Calculates the points earned based on the driver's finish position.
- `Finished` — Counts the number of races each driver has finished.
- `Penalty Points` — Counts the total deduction of points based on the number of penalties.
- `Podiums` — Counts the number of podiums per driver.
- `Poles` — Counts the number of poles per driver.
- `Start Position Points` — Calculates the points earned based on the driver's qualifying position.
- `Wins` — Counts the number of wins per driver.

## Finish Position Points

```DAX
Finish Position Points =
SUMX(
    race_results,
    VAR FinishPos = race_results[finish_pos]
    RETURN
        SWITCH(
            FinishPos,
            1, 25,
            2, 18,
            3, 15,
            4, 12,
            5, 10,
            6, 8,
            7, 6,
            8, 4,
            9, 2,
            10, 1,
            0
        )
)
```

## Start Position Points

```DAX
Start Position Points =
SUMX(
    race_results,
    VAR SeasonID = RELATED(races[season_id])
    VAR ReverseGrid = RELATED(races[reverse_grid])
    VAR StartPos = race_results[start_pos]
    RETURN
        IF(
            SeasonID >= 4
                && ReverseGrid <> "Yes"
                && StartPos >= 1
                && StartPos <= 6,
            7 - StartPos,
            0
        )
)
```

## Penalty Points Deductions

```DAX
Penalty Points =
-10 * SUM(race_results[penalties])
```

## Championship Points

```DAX
Championship Points =
CALCULATE(
    [Finish Position Points]
    + [Start Position Points]
    + [Penalty Points],
    FILTER(
        ALLSELECTED(races[round_number]),
        races[round_number] <= MAX(races[round_number])
    )
)
```

## Building the Dashboard

The final stage of the project was to use the relational model and DAX measures in Power BI to build an interactive racing-series dashboard, including leaderboard and driver statistics views.

---

*Source: [Racing Series: Data Modelling & Power BI Dashboard](https://sites.google.com/view/lawrenceparker/portfolio/racing-series)*

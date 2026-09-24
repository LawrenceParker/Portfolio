# Racing Series: Data Modelling & Power BI Dashboard

## Project Overview

This project involved transforming a single spreadsheet containing data from a racing series into a relational data model in Excel, before connecting the model to Power BI to produce an interactive leaderboard and driver statistics dashboard.

The project demonstrates the ability to take raw data and turn it into a structured, analysis-ready dataset, while applying principles of data modelling, data cleaning, and relational database design.

## The Original Data

## The Restructured Data

## On to Power BI

### Importing and Loading the Data

![Power BI data import](https://sites.google.com/sitesv-images-rt/AMxu72scqSMe-6onC3yH01gII4lJsDdwhDPeLTuoqxb4S088qacCrW4yQNXXaUE6BxBOguCTPuMEqNpm8UUlxPkU7BNDZuA4Pc_-O2LU0_p-WUnoBG432TF-u2GQ5LWiPiG9cUui_cklyrcpmwN72JqVUqIc-OQxUliOqIzxOJifXr2EVIc2XKc9iP0kTgMPVdKFeUA2aPM4YHVT32M11we4Sn-33rWp8qUl3QSJSVBg%3Dw1280)

![Restructured Power BI data](https://sites.google.com/sitesv-images-rt/AMxu72vvoFpK1XMCdveLTs9NmgLHMS2OdT4YiXkrv_Ifuc4rGiV7DItHH8RnjpnkZIyqdjvw4h9MJorPqMS6YV2sqXb9s6ixpFltBfbzVCyZtb15oPs-BqVZ0L8Dxu9zYgcWllAtlt3q9yptcHSGJI4eN8NmmLG8zG7N2VcMgu17c1Fb1qHPuv1HhJ8EqlVRLzJ0KwxRgp9Cbht5fip-6pB0FExHIYP0AMWMdghAXthm9yc%3Dw1280)

### Creating the Relationships

![Power BI data model relationships](https://sites.google.com/sitesv-images-rt/AMxu72tGce5Xp2__D1ZCmf3mO9pv11lerne4NBVN5awpt4NZYWdwFiZtRuWvqC8SbHxGcmm3Y22_dlwAId80mOn96exIbCqyxr8nIUHRvurLS1A7l5JVo9l9uAdkJuBnj3E_2r4XZ1OnoSz9IevjrLq8DeIlhwO8m1y_n7BsQIDLQ2mR_ddRRoX_e106E0HrEQ6oXBXkum6nOqb4Q1t1nlLb88ndkLNez4M6M2sXLuA2sv8%3Dw1280)

### DAX Formulas

![DAX measures](https://sites.google.com/sitesv-images-rt/AMxu72ukiWJtEw1xfyEArHUce6z5i0WLmOv6r3Q4lRSxgde1AY9knfap-f_aOLHJW6EMxn6Z4e52IYwKJBbIpkeGUaFegeipOt7hEcJRPK4-9PEyuf4cwjEl1CpAJvMWljupFsmvZcospM7HKgjdcmLP4GrvS6yk7Tmu155_YR5bf6Ox0lCGGzgd_tnAXl7I0v-rrEYkO_qbn4pHw7nSdsVIJwJ_o_Uw9enZzzUeoV6ZMuA%3Dw1280)

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

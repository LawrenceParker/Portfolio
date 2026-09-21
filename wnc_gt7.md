
## Original data structure
When originally collecting the data i placed it all in one large spreadsheet which also contained all the calculations for how many points scored per race.

![old data](images/old_data.png)

# Racing Series Data Modelling & Power BI Dashboard

## Project Overview

This project involved transforming a single spreadsheet containing data from a racing series into a relational data model in Excel, before connecting the model to Power BI to produce an interactive leaderboard and driver statistics dashboard.

The project demonstrates my ability to take **raw, manually maintained data and turn it into a structured, analysis-ready dataset**, while applying principles of data modelling, data cleaning, relational database design, and business intelligence.

---

## Project Objectives

The main objectives of the project were to:

* Transform a single flat spreadsheet into a relational data model.
* Reduce duplicated and inconsistent data.
* Separate different types of information into logical tables.
* Establish relationships between the tables using unique identifiers.
* Create a reusable data structure that could be expanded as more races were added.
* Connect the structured Excel model to Power BI.
* Create an interactive racing leaderboard.
* Calculate and visualise driver statistics and performance metrics.
* Make the underlying data easier to maintain and analyse.

---

## The Original Data

The starting point was a **single spreadsheet containing all of the data**.

The original structure combined multiple types of information within the same table, including information such as:

* Drivers
* Teams
* Races
* Tracks
* Race results
* Championship points
* Qualifying results
* Race positions

While this structure was suitable for manually recording results, it was not ideal for analytical reporting.

### Example of the original structure

| Date       | Season   | Round   | Race   | Race Name | Race Type  | Team Name | Track                | Driver          | Car                         | Car Class |
|------------|----------|---------|--------|-----------|------------|-----------|----------------------|-----------------|-----------------------------|-----------|
| 28/11/2023 | Season 1 | Round 1 | Race 1 | GT3 Cup   | Individual |           | Suzuka - Full Course | Alex Hoyle      | Mercedes - AMG GT3 16       | Gr.3      |
| 28/11/2023 | Season 1 | Round 1 | Race 1 | GT3 Cup   | Individual |           | Suzuka - Full Course | Conor Roberts   | Subaru - BRZ GT300 21       | Gr.3      |
| 28/11/2023 | Season 1 | Round 1 | Race 1 | GT3 Cup   | Individual |           | Suzuka - Full Course | Harry Richards  |                             | Gr.3      |
| 28/11/2023 | Season 1 | Round 1 | Race 1 | GT3 Cup   | Individual |           | Suzuka - Full Course | Joe McGhee      | Ferrari - 458 Italia GT3 13 | Gr.3      |
| 28/11/2023 | Season 1 | Round 1 | Race 1 | GT3 Cup   | Individual |           | Suzuka - Full Course | Lawrence Parker | McLaren - 650S GT3 15       | Gr.3      |

This approach resulted in information such as driver, team and circuit details being repeated across multiple rows.

---

# Data Transformation

## From Flat File to Relational Model

I redesigned the spreadsheet using a **relational data model**, separating the original dataset into multiple logical tables.

The model was designed around the principle of storing each type of information once and linking related records using unique IDs.

### New table structure

The final Excel model consisted of tables such as:

```text
Drivers
   │
   ├── DriverID
   ├── DriverName
   └── TeamID
          │
          ▼
Teams
   │
   ├── TeamID
   └── TeamName

Races
   │
   ├── RaceID
   ├── Round
   ├── RaceName
   └── CircuitID
          │
          ▼
Circuits
   │
   ├── CircuitID
   └── CircuitName

Results
   │
   ├── ResultID
   ├── RaceID
   ├── DriverID
   ├── QualifyingPosition
   ├── FinishingPosition
   └── Points
```

> Replace the example tables above with the actual tables used in my project.

---

## 🧩 Data Model

The relational structure allowed entities such as drivers, teams, races and circuits to be stored independently while the results table acted as the central source of performance data.

For example:

```text
             ┌──────────────┐
             │    Drivers   │
             │──────────────│
             │ DriverID     │
             │ DriverName   │
             │ TeamID       │
             └──────┬───────┘
                    │
                    │
             ┌──────▼───────┐
             │    Results   │
             │──────────────│
             │ ResultID     │
             │ DriverID     │
             │ RaceID       │
             │ FinishPos    │
             │ Points       │
             └──────┬───────┘
                    │
                    │
             ┌──────▼───────┐
             │     Races    │
             │──────────────│
             │ RaceID       │
             │ CircuitID    │
             │ Round        │
             └──────────────┘
```

This structure made it possible to analyse race results from different perspectives without repeatedly storing the same descriptive information.

---

# 🧹 Data Cleaning & Preparation

During the transformation process, I carried out a number of data preparation tasks, including:

* Removing duplicated information.
* Standardising driver names.
* Standardising team and circuit names.
* Creating unique identifiers.
* Separating descriptive information from transactional race results.
* Ensuring consistent data types.
* Checking for missing or invalid values.
* Structuring the tables so they could be related reliably.
* Preparing the model for future race results.

### Example

Instead of repeatedly storing:

```text
Driver A | Team 1
Driver A | Team 1
Driver A | Team 1
Driver A | Team 1
```

the model stores the driver and team information once and references them using IDs.

This improves consistency and makes the dataset easier to maintain.

---

# 📐 Relational Design

One of the main improvements was moving away from a single flat table towards a relational structure.

### Before

```text
One large table
│
├── Driver information
├── Team information
├── Race information
├── Circuit information
└── Result information
```

### After

```text
Drivers
Teams
Circuits
Races
Results
```

with relationships established through keys such as:

```text
DriverID
TeamID
CircuitID
RaceID
```

This allowed the model to behave more like a small relational database while still being maintained within Excel.

---

# 📈 Power BI

Once the Excel model was structured, I connected it to **Power BI** to create an interactive reporting layer.

The Power BI model used the relationships established within the structured dataset to allow results to be analysed across different dimensions.

## Dashboard Features

The dashboard included functionality such as:

### 🏆 Championship Leaderboard

A leaderboard showing drivers ranked according to their accumulated championship points.

Example:

| Position | Driver   | Points | Wins | Podiums |
| -------: | -------- | -----: | ---: | ------: |
|        1 | Driver A |    185 |    5 |       8 |
|        2 | Driver B |    164 |    4 |       7 |
|        3 | Driver C |    142 |    3 |       6 |

### 🏎️ Driver Statistics

Individual driver performance could be analysed using metrics such as:

* Total points
* Race starts
* Wins
* Podiums
* Average finishing position
* Best finishing position
* Average qualifying position
* Pole positions
* Points per race
* Number of DNFs

> Replace these metrics with the actual measures included in your dashboard.

---

# 📊 Dashboard Visualisations

The Power BI report included visualisations such as:

* Championship leaderboard
* Driver points comparison
* Driver performance over time
* Race-by-race results
* Finishing position distribution
* Qualifying vs finishing position
* Wins and podiums
* Driver-level performance breakdowns

### Interactive Features

Users could filter the report by dimensions such as:

* Driver
* Team
* Race
* Round
* Circuit
* Season

This allowed the same underlying dataset to support multiple types of analysis.

---

# 🧮 Power BI Measures

I also created calculated metrics within Power BI to turn the raw race results into meaningful performance statistics.

Example measures included:

```DAX
Total Points =
SUM(Results[Points])
```

```DAX
Race Wins =
CALCULATE(
    COUNTROWS(Results),
    Results[FinishingPosition] = 1
)
```

```DAX
Podiums =
CALCULATE(
    COUNTROWS(Results),
    Results[FinishingPosition] <= 3
)
```

```DAX
Average Finish =
AVERAGE(Results[FinishingPosition])
```

> Replace these examples with the actual DAX measures used in the project.

---

# 🔗 End-to-End Data Flow

The overall workflow was:

```text
Original Racing Spreadsheet
          │
          ▼
     Data Cleaning
          │
          ▼
   Data Transformation
          │
          ▼
 Relational Excel Model
          │
          ▼
     Power BI Model
          │
          ▼
 Calculated Measures
          │
          ▼
 Interactive Dashboard
          │
          ▼
Leaderboard & Driver Analytics
```

This created a complete workflow from **raw data collection through to business intelligence reporting**.

---

# 💡 Key Challenges

## Challenge 1 — Converting a Flat Dataset

The original spreadsheet was designed primarily for recording information rather than analysis.

I had to identify which fields represented separate entities and determine how they could be split into logical tables.

### Solution

I separated the data into individual entities and created unique IDs to establish relationships between them.

---

## Challenge 2 — Avoiding Duplicate Data

Driver, team, race and circuit information appeared repeatedly throughout the origina

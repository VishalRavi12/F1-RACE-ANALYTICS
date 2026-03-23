DROP TABLE IF EXISTS sprint_results CASCADE;
DROP TABLE IF EXISTS pit_stops CASCADE;
DROP TABLE IF EXISTS lap_times CASCADE;
DROP TABLE IF EXISTS qualifying CASCADE;
DROP TABLE IF EXISTS results CASCADE;
DROP TABLE IF EXISTS driver_standings CASCADE;
DROP TABLE IF EXISTS constructor_standings CASCADE;
DROP TABLE IF EXISTS constructor_results CASCADE;
DROP TABLE IF EXISTS races CASCADE;
DROP TABLE IF EXISTS status CASCADE;
DROP TABLE IF EXISTS constructors CASCADE;
DROP TABLE IF EXISTS drivers CASCADE;
DROP TABLE IF EXISTS circuits CASCADE;
DROP TABLE IF EXISTS seasons CASCADE;

CREATE TABLE seasons (
    year        INTEGER PRIMARY KEY,
    url         VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE circuits (
    circuit_id   SERIAL PRIMARY KEY,
    circuit_ref  VARCHAR(255) NOT NULL UNIQUE,
    name         VARCHAR(255) NOT NULL,
    location     VARCHAR(255),
    country      VARCHAR(255),
    lat          DECIMAL(10, 6),
    lng          DECIMAL(10, 6),
    alt          INTEGER,
    url          VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE drivers (
    driver_id    SERIAL PRIMARY KEY,
    driver_ref   VARCHAR(255) NOT NULL UNIQUE,
    number       INTEGER,
    code         VARCHAR(3),
    forename     VARCHAR(255) NOT NULL,
    surname      VARCHAR(255) NOT NULL,
    dob          DATE,
    nationality  VARCHAR(255),
    url          VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE constructors (
    constructor_id   SERIAL PRIMARY KEY,
    constructor_ref  VARCHAR(255) NOT NULL UNIQUE,
    name             VARCHAR(255) NOT NULL UNIQUE,
    nationality      VARCHAR(255),
    url              VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE status (
    status_id   SERIAL PRIMARY KEY,
    status      VARCHAR(255) NOT NULL
);

CREATE TABLE races (
    race_id     SERIAL PRIMARY KEY,
    year        INTEGER NOT NULL REFERENCES seasons(year),
    round       INTEGER NOT NULL CHECK (round > 0),
    circuit_id  INTEGER NOT NULL REFERENCES circuits(circuit_id),
    name        VARCHAR(255) NOT NULL,
    date        DATE NOT NULL,
    time        TIME,
    url         VARCHAR(255) NOT NULL UNIQUE,
    fp1_date    DATE,
    fp1_time    TIME,
    fp2_date    DATE,
    fp2_time    TIME,
    fp3_date    DATE,
    fp3_time    TIME,
    quali_date  DATE,
    quali_time  TIME,
    sprint_date DATE,
    sprint_time TIME,
    UNIQUE (year, round)
);

CREATE TABLE results (
    result_id        SERIAL PRIMARY KEY,
    race_id          INTEGER NOT NULL REFERENCES races(race_id),
    driver_id        INTEGER NOT NULL REFERENCES drivers(driver_id),
    constructor_id   INTEGER NOT NULL REFERENCES constructors(constructor_id),
    number           INTEGER,
    grid             INTEGER NOT NULL,
    position         INTEGER,
    position_text    VARCHAR(255) NOT NULL,
    position_order   INTEGER NOT NULL,
    points           DECIMAL(5, 2) NOT NULL DEFAULT 0,
    laps             INTEGER NOT NULL DEFAULT 0,
    time             VARCHAR(255),
    milliseconds     BIGINT,
    fastest_lap       INTEGER,
    rank             INTEGER,
    fastest_lap_time  VARCHAR(255),
    fastest_lap_speed VARCHAR(255),
    status_id        INTEGER NOT NULL REFERENCES status(status_id),
    UNIQUE (race_id, driver_id)
);

CREATE TABLE qualifying (
    qualify_id       SERIAL PRIMARY KEY,
    race_id          INTEGER NOT NULL REFERENCES races(race_id),
    driver_id        INTEGER NOT NULL REFERENCES drivers(driver_id),
    constructor_id   INTEGER NOT NULL REFERENCES constructors(constructor_id),
    number           INTEGER NOT NULL,
    position         INTEGER NOT NULL CHECK (position > 0),
    q1               VARCHAR(255),
    q2               VARCHAR(255),
    q3               VARCHAR(255),
    UNIQUE (race_id, driver_id)
);

CREATE TABLE sprint_results (
    sprint_result_id SERIAL PRIMARY KEY,
    race_id          INTEGER NOT NULL REFERENCES races(race_id),
    driver_id        INTEGER NOT NULL REFERENCES drivers(driver_id),
    constructor_id   INTEGER NOT NULL REFERENCES constructors(constructor_id),
    number           INTEGER,
    grid             INTEGER NOT NULL,
    position         INTEGER,
    position_text    VARCHAR(255) NOT NULL,
    position_order   INTEGER NOT NULL,
    points           DECIMAL(5, 2) NOT NULL DEFAULT 0,
    laps             INTEGER NOT NULL DEFAULT 0,
    time             VARCHAR(255),
    milliseconds     BIGINT,
    fastest_lap       INTEGER,
    rank             INTEGER,
    fastest_lap_time  VARCHAR(255),
    fastest_lap_speed VARCHAR(255),
    status_id        INTEGER NOT NULL REFERENCES status(status_id),
    UNIQUE (race_id, driver_id)
);

CREATE TABLE lap_times (
    race_id      INTEGER NOT NULL REFERENCES races(race_id),
    driver_id    INTEGER NOT NULL REFERENCES drivers(driver_id),
    lap          INTEGER NOT NULL CHECK (lap > 0),
    position     INTEGER,
    time         VARCHAR(255),
    milliseconds BIGINT,
    PRIMARY KEY (race_id, driver_id, lap)
);

CREATE TABLE pit_stops (
    race_id      INTEGER NOT NULL REFERENCES races(race_id),
    driver_id    INTEGER NOT NULL REFERENCES drivers(driver_id),
    stop         INTEGER NOT NULL CHECK (stop > 0),
    lap          INTEGER NOT NULL,
    time         TIME NOT NULL,
    duration     VARCHAR(255),
    milliseconds BIGINT,
    PRIMARY KEY (race_id, driver_id, stop)
);

CREATE TABLE driver_standings (
    driver_standing_id SERIAL PRIMARY KEY,
    race_id            INTEGER NOT NULL REFERENCES races(race_id),
    driver_id          INTEGER NOT NULL REFERENCES drivers(driver_id),
    points             DECIMAL(6, 2) NOT NULL DEFAULT 0,
    position           INTEGER,
    position_text      VARCHAR(255),
    wins               INTEGER NOT NULL DEFAULT 0,
    UNIQUE (race_id, driver_id)
);

CREATE TABLE constructor_standings (
    constructor_standing_id SERIAL PRIMARY KEY,
    race_id                INTEGER NOT NULL REFERENCES races(race_id),
    constructor_id         INTEGER NOT NULL REFERENCES constructors(constructor_id),
    points                 DECIMAL(6, 2) NOT NULL DEFAULT 0,
    position               INTEGER,
    position_text          VARCHAR(255),
    wins                   INTEGER NOT NULL DEFAULT 0,
    UNIQUE (race_id, constructor_id)
);

CREATE TABLE constructor_results (
    constructor_results_id SERIAL PRIMARY KEY,
    race_id                INTEGER NOT NULL REFERENCES races(race_id),
    constructor_id         INTEGER NOT NULL REFERENCES constructors(constructor_id),
    points                 DECIMAL(5, 2),
    status                 VARCHAR(255),
    UNIQUE (race_id, constructor_id)
);

CREATE INDEX idx_races_year ON races(year);
CREATE INDEX idx_races_circuit ON races(circuit_id);
CREATE INDEX idx_results_race ON results(race_id);
CREATE INDEX idx_results_driver ON results(driver_id);
CREATE INDEX idx_results_constructor ON results(constructor_id);
CREATE INDEX idx_lap_times_race ON lap_times(race_id);
CREATE INDEX idx_lap_times_driver ON lap_times(driver_id);
CREATE INDEX idx_pit_stops_race ON pit_stops(race_id);
CREATE INDEX idx_qualifying_race ON qualifying(race_id);
CREATE INDEX idx_driver_standings_race ON driver_standings(race_id);
CREATE INDEX idx_constructor_standings_race ON constructor_standings(race_id);
create index if not exists idx_qualifying_race_driver_position
    on qualifying (race_id, driver_id, position);

create index if not exists idx_pit_stops_race_driver_ms
    on pit_stops (race_id, driver_id, milliseconds);

create index if not exists idx_results_race_driver_position_order
    on results (race_id, driver_id, position_order);

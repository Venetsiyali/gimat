// ==========================================
// GIMAT Neo4j Initialization Script
// Hydrological Ontology Schema
// ==========================================

// Create constraints for unique identifiers
CREATE CONSTRAINT river_name_unique IF NOT EXISTS
FOR (r:River) REQUIRE r.name IS UNIQUE;

CREATE CONSTRAINT reach_id_unique IF NOT EXISTS
FOR (rr:RiverReach) REQUIRE rr.reach_id IS UNIQUE;

CREATE CONSTRAINT hydropost_id_unique IF NOT EXISTS
FOR (h:Hydropost) REQUIRE h.station_id IS UNIQUE;

CREATE CONSTRAINT reservoir_id_unique IF NOT EXISTS
FOR (res:Reservoir) REQUIRE res.reservoir_id IS UNIQUE;

CREATE CONSTRAINT meteo_id_unique IF NOT EXISTS
FOR (m:MeteoStation) REQUIRE m.station_id IS UNIQUE;

// Create indexes for frequently queried properties
CREATE INDEX river_basin_idx IF NOT EXISTS FOR (r:River) ON (r.basin);
CREATE INDEX reach_river_idx IF NOT EXISTS FOR (rr:RiverReach) ON (rr.river_name);
CREATE INDEX hydropost_river_idx IF NOT EXISTS FOR (h:Hydropost) ON (h.river_name);
CREATE INDEX reservoir_river_idx IF NOT EXISTS FOR (res:Reservoir) ON (res.river_name);

// Spatial indexes for geographic queries
CREATE POINT INDEX hydropost_location_idx IF NOT EXISTS FOR (h:Hydropost) ON (h.location);
CREATE POINT INDEX meteo_location_idx IF NOT EXISTS FOR (m:MeteoStation) ON (m.location);

// ==========================================
// Sample Data - Chirchiq Basin
// ==========================================

// Create Chirchiq River
CREATE (r:River {
    name: 'Chirchiq',
    basin: 'Syr Darya',
    length_km: 155,
    description: 'Major tributary of Syr Darya, flowing through Tashkent region',
    country: 'Uzbekistan'
});

// Create major reservoir - Charvak
CREATE (charvak:Reservoir {
    reservoir_id: 'RES_CHARVAK_001',
    name: 'Charvak Reservoir',
    river_name: 'Chirchiq',
    capacity_m3: 2000000000,
    surface_area_km2: 37.8,
    latitude: 41.6094,
    longitude: 70.0747,
    dam_height_m: 168,
    year_built: 1970,
    purpose: 'Hydropower, Irrigation, Flood Control'
});

// Create some hydroposts on Chirchiq
CREATE (hp1:Hydropost {
    station_id: 'HP_CHIRCHIQ_001',
    name: 'Chirchiq - Gazalkent',
    river_name: 'Chirchiq',
    latitude: 41.4833,
    longitude: 70.0167,
    river_km: 120,
    elevation_m: 800,
    operational_since: 1960
});

CREATE (hp2:Hydropost {
    station_id: 'HP_CHIRCHIQ_002',
    name: 'Chirchiq - Tashkent',
    river_name: 'Chirchiq',
    latitude: 41.3167,
    longitude: 69.2833,
    river_km: 50,
    elevation_m: 450,
    operational_since: 1955
});

CREATE (hp3:Hydropost {
    station_id: 'HP_CHIRCHIQ_003',
    name: 'Chirchiq - Chinoz',
    river_name: 'Chirchiq',
    latitude: 40.9394,
    longitude: 68.7711,
    river_km: 10,
    elevation_m: 340,
    operational_since: 1965
});

// Create river reaches
CREATE (reach1:RiverReach {
    reach_id: 'REACH_CHIRCHIQ_001',
    river_name: 'Chirchiq',
    upstream_km: 155,
    downstream_km: 120,
    length_km: 35,
    description: 'Upper Chirchiq - Mountain section'
});

CREATE (reach2:RiverReach {
    reach_id: 'REACH_CHIRCHIQ_002',
    river_name: 'Chirchiq',
    upstream_km: 120,
    downstream_km: 50,
    length_km: 70,
    description: 'Middle Chirchiq - Piedmont section'
});

CREATE (reach3:RiverReach {
    reach_id: 'REACH_CHIRCHIQ_003',
    river_name: 'Chirchiq',
    upstream_km: 50,
    downstream_km: 0,
    length_km: 50,
    description: 'Lower Chirchiq - Plain section'
});

// ==========================================
// Sample Data - Zarafshon Basin
// ==========================================

CREATE (z:River {
    name: 'Zarafshon',
    basin: 'Zarafshon',
    length_km: 877,
    description: 'Transboundary river flowing through Tajikistan and Uzbekistan',
    countries: ['Tajikistan', 'Uzbekistan']
});

CREATE (hp_z1:Hydropost {
    station_id: 'HP_ZARAFSHON_001',
    name: 'Zarafshon - Dupuli',
    river_name: 'Zarafshon',
    latitude: 39.5167,
    longitude: 67.8333,
    river_km: 350,
    operational_since: 1958
});

CREATE (hp_z2:Hydropost {
    station_id: 'HP_ZARAFSHON_002',
    name: 'Zarafshon - Samarkand',
    river_name: 'Zarafshon',
    latitude: 39.6542,
    longitude: 66.9597,
    river_km: 200,
    operational_since: 1950
});

// ==========================================
// Create Relationships
// ==========================================

// River reaches flow topology (Chirchiq)
MATCH (r1:RiverReach {reach_id: 'REACH_CHIRCHIQ_001'})
MATCH (r2:RiverReach {reach_id: 'REACH_CHIRCHIQ_002'})
CREATE (r1)-[:FLOWS_TO]->(r2);

MATCH (r2:RiverReach {reach_id: 'REACH_CHIRCHIQ_002'})
MATCH (r3:RiverReach {reach_id: 'REACH_CHIRCHIQ_003'})
CREATE (r2)-[:FLOWS_TO]->(r3);

// Hydroposts monitor reaches
MATCH (h:Hydropost {station_id: 'HP_CHIRCHIQ_001'})
MATCH (r:RiverReach {reach_id: 'REACH_CHIRCHIQ_002'})
CREATE (h)-[:MONITORS]->(r);

MATCH (h:Hydropost {station_id: 'HP_CHIRCHIQ_002'})
MATCH (r:RiverReach {reach_id: 'REACH_CHIRCHIQ_003'})
CREATE (h)-[:MONITORS]->(r);

MATCH (h:Hydropost {station_id: 'HP_CHIRCHIQ_003'})
MATCH (r:RiverReach {reach_id: 'REACH_CHIRCHIQ_003'})
CREATE (h)-[:MONITORS]->(r);

// Reservoir influences
MATCH (res:Reservoir {reservoir_id: 'RES_CHARVAK_001'})
MATCH (r:River {name: 'Chirchiq'})
CREATE (res)-[:LOCATED_ON]->(r);

MATCH (res:Reservoir {reservoir_id: 'RES_CHARVAK_001'})
MATCH (h:Hydropost {station_id: 'HP_CHIRCHIQ_001'})
CREATE (res)-[:INFLUENCES {distance_km: 20}]->(h);

MATCH (res:Reservoir {reservoir_id: 'RES_CHARVAK_001'})
MATCH (h:Hydropost {station_id: 'HP_CHIRCHIQ_002'})
CREATE (res)-[:INFLUENCES {distance_km: 90}]->(h);

// ==========================================
// Verification Queries
// ==========================================

// Show all nodes
// MATCH (n) RETURN n LIMIT 25;

// Show river network
// MATCH (r:River {name: 'Chirchiq'})<-[:LOCATED_ON*0..1]-(n)
// RETURN r, n;

// Show upstream/downstream connections
// MATCH path = (r1:RiverReach)-[:FLOWS_TO*]->(r2:RiverReach)
// WHERE r1.river_name = 'Chirchiq'
// RETURN path;

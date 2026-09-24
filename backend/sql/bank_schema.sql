-- Bank portal tables (see BANK_INSTRUCTIONS.md)

CREATE TABLE IF NOT EXISTS bank_officers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(15) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    organization VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS yield_certificates (
    id SERIAL PRIMARY KEY,
    farmer_id INTEGER REFERENCES farmers(id),
    bank_officer_id INTEGER REFERENCES bank_officers(id),
    crop_type VARCHAR(100),
    predicted_yield_min DECIMAL(10,2),
    predicted_yield_max DECIMAL(10,2),
    confidence_score DECIMAL(5,2),
    soil_health_score INTEGER,
    document_hash VARCHAR(64),
    verification_code VARCHAR(32),
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS loan_eligibility_scores (
    id SERIAL PRIMARY KEY,
    farmer_id INTEGER REFERENCES farmers(id),
    bank_officer_id INTEGER REFERENCES bank_officers(id),
    total_score INTEGER,
    soil_health_points INTEGER,
    yield_consistency_points INTEGER,
    farm_size_points INTEGER,
    crop_risk_points INTEGER,
    weather_risk_points INTEGER,
    score_breakdown JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS claim_verifications (
    id SERIAL PRIMARY KEY,
    farmer_id INTEGER REFERENCES farmers(id),
    bank_officer_id INTEGER REFERENCES bank_officers(id),
    claim_date DATE,
    claimed_loss_amount DECIMAL(12,2),
    claimed_reason VARCHAR(100),
    weather_data_on_claim_date JSONB,
    yield_prediction_at_time JSONB,
    verification_result VARCHAR(20),
    verification_explanation TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tracks every farmer profile lookup a bank officer performs (Farm Verification
-- search), so the Portfolio Map can include farmers who were searched/verified
-- even if no certificate, loan score, or claim was created yet.
CREATE TABLE IF NOT EXISTS bank_farmer_views (
    id SERIAL PRIMARY KEY,
    farmer_id INTEGER REFERENCES farmers(id),
    bank_officer_id INTEGER REFERENCES bank_officers(id),
    first_viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (farmer_id, bank_officer_id)
);

-- Marketing Data Pipeline Sample
-- This file contains marketing analytics pipeline

-- Campaign source data
CREATE TABLE raw_campaigns (
    campaign_id INT PRIMARY KEY,
    campaign_name VARCHAR(200),
    channel VARCHAR(50),
    start_date DATE,
    end_date DATE,
    budget DECIMAL(12,2),
    campaign_type VARCHAR(50)
);

CREATE TABLE raw_ad_clicks (
    click_id INT PRIMARY KEY,
    campaign_id INT,
    user_id VARCHAR(100),
    click_timestamp TIMESTAMP,
    device_type VARCHAR(50),
    source_url VARCHAR(500)
);

CREATE TABLE raw_conversions (
    conversion_id INT PRIMARY KEY,
    user_id VARCHAR(100),
    conversion_type VARCHAR(50),
    conversion_value DECIMAL(10,2),
    conversion_timestamp TIMESTAMP,
    attribution_campaign_id INT
);

-- Clean and enrich marketing data
CREATE TABLE clean_campaigns AS
SELECT 
    campaign_id,
    campaign_name,
    LOWER(channel) as channel,
    start_date,
    end_date,
    budget,
    campaign_type,
    DATEDIFF(end_date, start_date) + 1 as duration_days,
    budget / (DATEDIFF(end_date, start_date) + 1) as daily_budget
FROM raw_campaigns
WHERE start_date <= end_date 
    AND budget > 0;

CREATE TABLE user_interactions AS
SELECT 
    ac.user_id,
    ac.campaign_id,
    ac.click_timestamp,
    ac.device_type,
    cc.channel,
    cc.campaign_type,
    ROW_NUMBER() OVER (PARTITION BY ac.user_id ORDER BY ac.click_timestamp) as interaction_sequence
FROM raw_ad_clicks ac
JOIN clean_campaigns cc ON ac.campaign_id = cc.campaign_id
WHERE ac.click_timestamp BETWEEN cc.start_date AND cc.end_date;

-- Attribution and conversion analysis
CREATE TABLE attributed_conversions AS
SELECT 
    rc.conversion_id,
    rc.user_id,
    rc.conversion_type,
    rc.conversion_value,
    rc.conversion_timestamp,
    rc.attribution_campaign_id,
    cc.campaign_name,
    cc.channel,
    ui.device_type,
    ui.interaction_sequence,
    DATEDIFF(rc.conversion_timestamp, ui.click_timestamp) as time_to_conversion_days
FROM raw_conversions rc
JOIN clean_campaigns cc ON rc.attribution_campaign_id = cc.campaign_id
LEFT JOIN user_interactions ui ON rc.user_id = ui.user_id 
    AND rc.attribution_campaign_id = ui.campaign_id
WHERE rc.conversion_value > 0;

-- Campaign performance metrics
CREATE TABLE campaign_performance AS
SELECT 
    cc.campaign_id,
    cc.campaign_name,
    cc.channel,
    cc.campaign_type,
    cc.budget,
    COUNT(DISTINCT ui.user_id) as unique_users_reached,
    COUNT(ui.click_id) as total_clicks,
    COUNT(DISTINCT ac.conversion_id) as total_conversions,
    SUM(ac.conversion_value) as total_conversion_value,
    SUM(ac.conversion_value) / NULLIF(cc.budget, 0) as roi,
    COUNT(DISTINCT ac.conversion_id) / NULLIF(COUNT(ui.click_id), 0) * 100 as conversion_rate,
    SUM(ac.conversion_value) / NULLIF(COUNT(DISTINCT ac.conversion_id), 0) as avg_conversion_value
FROM clean_campaigns cc
LEFT JOIN user_interactions ui ON cc.campaign_id = ui.campaign_id
LEFT JOIN attributed_conversions ac ON cc.campaign_id = ac.attribution_campaign_id
GROUP BY cc.campaign_id, cc.campaign_name, cc.channel, cc.campaign_type, cc.budget;

-- Channel effectiveness analysis
CREATE TABLE channel_effectiveness AS
SELECT 
    cp.channel,
    COUNT(DISTINCT cp.campaign_id) as total_campaigns,
    SUM(cp.budget) as total_budget,
    SUM(cp.unique_users_reached) as total_reach,
    SUM(cp.total_conversions) as total_conversions,
    SUM(cp.total_conversion_value) as total_revenue,
    AVG(cp.roi) as average_roi,
    AVG(cp.conversion_rate) as average_conversion_rate,
    SUM(cp.total_conversion_value) / NULLIF(SUM(cp.budget), 0) as channel_roi
FROM campaign_performance cp
GROUP BY cp.channel
ORDER BY channel_roi DESC;

-- User journey analysis
CREATE TABLE user_journey_analysis AS
SELECT 
    ui.user_id,
    COUNT(DISTINCT ui.campaign_id) as campaigns_interacted,
    COUNT(ui.interaction_sequence) as total_interactions,
    MIN(ui.click_timestamp) as first_interaction,
    MAX(ui.click_timestamp) as last_interaction,
    MAX(ac.conversion_value) as highest_conversion_value,
    COUNT(DISTINCT ac.conversion_type) as conversion_types,
    STRING_AGG(DISTINCT ui.channel, ', ') as channels_used,
    CASE 
        WHEN COUNT(DISTINCT ac.conversion_id) > 0 THEN 'converter'
        WHEN COUNT(ui.interaction_sequence) > 3 THEN 'engaged_non_converter'
        ELSE 'low_engagement'
    END as user_segment
FROM user_interactions ui
LEFT JOIN attributed_conversions ac ON ui.user_id = ac.user_id
GROUP BY ui.user_id;

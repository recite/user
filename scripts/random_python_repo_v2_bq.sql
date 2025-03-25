-- Cost-Effective BigQuery Implementation for Random Python Repository Sampling
-- This query returns ALL Python repositories found in the sample

-- Define parameters
DECLARE hours_to_sample INT64 DEFAULT 10; -- Number of random hours to sample
DECLARE repos_per_hour INT64 DEFAULT 10; -- Repositories to sample per hour
DECLARE years_back INT64 DEFAULT 10; -- How many years to look back

-- Create a table of random dates and hours to sample from
CREATE TEMP TABLE random_dates AS (
  SELECT 
    FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE(), INTERVAL CAST(FLOOR(RAND() * (365 * years_back)) AS INT64) DAY)) AS day,
    CAST(FLOOR(RAND() * 24) AS INT64) AS hour
  FROM 
    UNNEST(GENERATE_ARRAY(1, hours_to_sample))
);

-- Create a table to collect sampled repositories
CREATE TEMP TABLE sampled_repos (
  repo_name STRING,
  repo_url STRING,
  created_at TIMESTAMP,
  sample_day STRING,
  sample_hour INT64,
  event_type STRING
);

-- For each random date, sample repositories efficiently
-- This loop replaces the expensive wildcard approach
FOR date_record IN (SELECT * FROM random_dates) DO
  -- Construct the specific table name for this date
  DECLARE table_name STRING;
  SET table_name = CONCAT('`githubarchive.day.', date_record.day, date_record.hour, '`');
  
  -- Execute a dynamic SQL statement to sample from just this one table
  EXECUTE IMMEDIATE format("""
    INSERT INTO sampled_repos
    SELECT
      repo.name AS repo_name,
      repo.url AS repo_url,
      created_at,
      '%s' AS sample_day,
      %d AS sample_hour,
      type AS event_type
    FROM
      %s TABLESAMPLE SYSTEM (5 PERCENT)
    WHERE
      (type = 'CreateEvent' OR type = 'PushEvent')
    ORDER BY RAND()
    LIMIT %d
  """, date_record.day, date_record.hour, table_name, repos_per_hour);
END FOR;

-- Get language information for repositories
-- Use a separate temp table to store language info
CREATE TEMP TABLE repo_languages AS (
  -- Sample a recent day's data for language information
  -- This is cheaper than scanning across all days
  WITH language_sources AS (
    -- First try to get language from PullRequestEvent payloads
    SELECT
      repo.name AS repo_name,
      JSON_EXTRACT_SCALAR(payload, '$.pull_request.base.repo.language') AS language
    FROM
      `githubarchive.day.20230101` TABLESAMPLE SYSTEM (10 PERCENT)
    WHERE
      type = 'PullRequestEvent'
      AND JSON_EXTRACT_SCALAR(payload, '$.pull_request.base.repo.language') IS NOT NULL
    
    UNION ALL
    
    -- Also try CreateEvent which sometimes has language info
    SELECT
      repo.name AS repo_name,
      JSON_EXTRACT_SCALAR(payload, '$.repository.language') AS language
    FROM
      `githubarchive.day.20230101` TABLESAMPLE SYSTEM (10 PERCENT)
    WHERE
      type = 'CreateEvent'
      AND JSON_EXTRACT_SCALAR(payload, '$.repository.language') IS NOT NULL
  )
  
  SELECT
    repo_name,
    language
  FROM
    language_sources
  GROUP BY
    repo_name, language
);

-- Final result - join sampled repos with language info and filter for Python
-- Removed the LIMIT 10 to return ALL Python repositories found
SELECT
  r.repo_name,
  r.repo_url,
  r.created_at,
  CONCAT(r.sample_day, '-', r.sample_hour) AS sampled_from,
  'Python' AS language  -- We're filtering for Python only
FROM
  sampled_repos r
JOIN  -- Using INNER JOIN to only keep repos with language info
  repo_languages rl
ON
  r.repo_name = rl.repo_name
WHERE
  rl.language = 'Python'
ORDER BY
  r.repo_name;  -- Ordering by repo name for consistency
# Database Schema & Data Flow

**Project Name:** Nexus Gaming Leaderboard System

To adhere strictly to Service-Oriented Architecture (SOA) principles, databases are isolated per service. There is no central monolithic database, ensuring that if one engine's database goes down or locks, the other engines remain operational.

## 1. Player Engine Database (Django)

Stores persistent player profiles and authentication data. Managed via Django's ORM.

**Table: `players**`

| Column       | Type        | Constraints         | Description                                    |
| ------------ | ----------- | ------------------- | ---------------------------------------------- |
| `id`         | UUID        | Primary Key, UUIDv4 | The globally unique identifier for the player. |
| `username`   | VARCHAR(50) | Unique, Not Null    | The player's public display name.              |
| `created_at` | TIMESTAMP   | Default NOW()       | Account creation timestamp.                    |
| `is_active`  | BOOLEAN     | Default TRUE        | Soft-delete flag for account management.       |

## 2. Match Engine Database (Node.js)

Stores high-throughput raw match data. Optimized for heavy write operations. Managed via Prisma or Knex.js.

**Table: `match_scores**`

| Column        | Type      | Constraints         | Description                                                   |
| ------------- | --------- | ------------------- | ------------------------------------------------------------- |
| `id`          | UUID      | Primary Key, UUIDv4 | The globally unique identifier for the specific match record. |
| `player_id`   | UUID      | Indexed, Not Null   | The UUIDv4 belonging to the player who achieved the score.    |
| `score`       | INT       | Not Null            | The final numerical score of the match.                       |
| `recorded_at` | TIMESTAMP | Default NOW()       | Time the match was submitted and recorded.                    |

---

## Cross-Service Data Flow & Consistency

Because the databases are physically separated, standard SQL `JOIN` operations across tables are impossible.

### The "Soft" Foreign Key Pattern

The `player_id` column in the `match_scores` table is a **soft foreign key**. The Match Engine database does not strictly enforce this relationship at the SQL level because it has no access to the `players` table. It simply trusts the UUIDv4 provided by the API Gateway.

### Data Aggregation (The Join)

When the Leaderboard Engine needs to display the top scores with their associated usernames, it performs the "join" over the network:

1. It queries the Match Engine for the top 10 scores and their associated `player_id` UUIDv4s.
2. It takes those 10 UUIDv4s and queries the Player Engine via an internal HTTP GET request to fetch the matching `username` strings.
3. It maps the usernames to the scores in memory.
4. It returns the fully populated JSON array back to the API Gateway.
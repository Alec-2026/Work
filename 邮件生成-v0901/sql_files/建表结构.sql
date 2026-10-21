-- 创建语音质检的记录表
CREATE TABLE tag_marketing_script_v2
(
    request       Nullable(String),
    response      String,
    status        Nullable(String),
    request_model Nullable(String),
    input_token   Int64,
    output_token  Int64,
    cost          Nullable(Float32),
    use_time      Nullable(Float32),
    is_test       Int32,
    time          Nullable(Float32),
    date          String,
    remote_addr   Nullable(String),
    business      String,
    code          Nullable(Int64)
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(toDate(date))
ORDER BY (toDate(date), business)
SETTINGS index_granularity = 8192;
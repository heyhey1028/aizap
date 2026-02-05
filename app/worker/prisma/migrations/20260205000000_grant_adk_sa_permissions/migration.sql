-- ADK サービスアカウントに PostgreSQL テーブル権限を付与
-- マイグレーションは worker-sa で実行されるため、テーブルのオーナーは worker-sa になる
-- ADK は adk-sa で接続するため、明示的な GRANT が必要

DO $$
BEGIN
  -- dev 環境
  IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'aizap-adk-sa@aizap-dev.iam') THEN
    -- 既存テーブルへの権限付与
    GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public 
      TO "aizap-adk-sa@aizap-dev.iam";
    -- 今後作成されるテーブルへの権限自動付与
    ALTER DEFAULT PRIVILEGES IN SCHEMA public
      GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES 
      TO "aizap-adk-sa@aizap-dev.iam";
  END IF;
  
  -- prod 環境
  IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'aizap-adk-sa@aizap-prod.iam') THEN
    -- 既存テーブルへの権限付与
    GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public 
      TO "aizap-adk-sa@aizap-prod.iam";
    -- 今後作成されるテーブルへの権限自動付与
    ALTER DEFAULT PRIVILEGES IN SCHEMA public
      GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES 
      TO "aizap-adk-sa@aizap-prod.iam";
  END IF;
END $$;

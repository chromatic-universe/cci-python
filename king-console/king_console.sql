CREATE TABLE "payload_policy" ("idx" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL , "provider" CHAR NOT NULL  DEFAULT mongo, "run_interval " INTEGER NOT NULL  DEFAULT 10, "run_on_start" INTEGER NOT NULL  DEFAULT 0, "query_on_start" INTEGER NOT NULL  DEFAULT 1, "daemonize" INTEGER NOT NULL  DEFAULT 0, "timestamp" DATETIME NOT NULL  DEFAULT CURRENT_TIMESTAMP, "moniker" CHAR NOT NULL , "provider_type" CHAR NOT NULL  DEFAULT document, "batch_size" INTEGER DEFAULT 5, "active" INTEGER DEFAULT 0);
CREATE TABLE "session_call_history" ("idx" INTEGER PRIMARY KEY  NOT NULL ,"session_name" INTEGER NOT NULL ,"call_segment" CHAR NOT NULL ,"call_moniker" CHAR NOT NULL ,"call_params" CHAR NOT NULL  DEFAULT (NULL) ,"timestamp" DATETIME DEFAULT (CURRENT_TIMESTAMP) ,"payload_special" BLOB, "payload" CHAR NOT NULL  DEFAULT '(empty)');
CREATE TABLE "session_notes" ( "session_name" CHAR PRIMARY KEY NOT NULL , "snippet" CHAR NOT NULL ,"metatag" CHAR);
CREATE TABLE "session_payload_atoms" ("idx" INTEGER PRIMARY KEY  NOT NULL ,"payload" CHAR NOT NULL ,"payload_special" BLOB,"size" INTEGER NOT NULL  DEFAULT (0) ,"cache_pending" INTEGER DEFAULT (0) , "session_call_idx" INTEGER);
CREATE TABLE "sessions" ("idx" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL  UNIQUE , "session_name" CHAR NOT NULL  UNIQUE , "session_user" CHAR NOT NULL , "context" CHAR, "timestamp" DATETIME DEFAULT CURRENT_TIMESTAMP, "session_moniker" CHAR DEFAULT king_console, "device_id" CHAR DEFAULT '0.0.0.0', "status" INTEGER NOT NULL  DEFAULT 1);
CREATE VIEW "session_payload_impl" AS  select  a.session_name ,  a.context , a.session_moniker ,
            b.timestamp , b.call_segment  , b.call_moniker , b.call_params  ,
            c.size , c.payload
from sessions a , session_call_history  b   , session_payload_atoms c
where a.session_name =  b.session_name and b.idx = c.session_call_idx and c.cache_pending = 1;
CREATE TRIGGER update_payload AFTER INSERT 
ON session_call_history
BEGIN
   INSERT INTO session_payload_atoms( payload , size , cache_pending , session_call_idx  )
                                                                          VALUES ( new.payload  , length( new.payload ) , 1  , new.idx );
                                                                                            
END;
CREATE UNIQUE INDEX "idx_payload_policy" ON "payload_policy" ("provider" ASC, "moniker" ASC, "provider_type" ASC);

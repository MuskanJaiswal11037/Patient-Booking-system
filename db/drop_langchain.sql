-- Active: 1773814904573@@127.0.0.1@5432@langchain_db
DROP table IF exists checkpoint_blobs;
DROP table IF exists checkpoints;
DROP table IF exists checkpoint_writes;
DROP table IF exists checkpoint_migrations;

select count(*) from checkpoint_blobs;
select count(*) from checkpoints;  




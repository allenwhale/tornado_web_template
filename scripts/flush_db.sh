#!/bin/sh
PSQL="env psql"
PSQL_FILE="./psql.sql"
DBHOST=""
DBUSER=""
DBNAME=""
DBPASSWORD=""
export PGPASSWORD=${DBPASSWORD}
${PSQL} -h ${DBHOST} -d ${DBNAME} -U ${DBUSER} < ${PSQL_FILE}
unset PGPASSWORD

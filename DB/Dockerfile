FROM postgres:17
ADD db/scripts/1_init.sql /docker-entrypoint-initdb.d
ADD db/scripts/2_copy.sql /docker-entrypoint-initdb.d
RUN mkdir /data
ADD db/data/data1.csv /data
RUN chmod a+r /docker-entrypoint-initdb.d/*
RUN chmod a+r /data/*
EXPOSE 5432
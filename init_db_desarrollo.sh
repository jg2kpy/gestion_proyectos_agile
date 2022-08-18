sudo service postgresql start

sudo -u postgres psql -U postgres -d postgres -c "alter user postgres with password 'postgres';"
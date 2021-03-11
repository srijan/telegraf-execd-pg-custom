# PostgreSQL Custom Input Plugin for Telegraf

For more details, please see the blog post: https://www.srijn.net/2021/03/advanced-postgresql-monitoring-using-telegraf/

## Requirements

Since this is a custom plugin for Telegraf, so telegraf is required.

Python packages required:

- psycopg2
- pytz
- dateutil
- pytoml

`line_protocol.py` is taken from the [influxdb python
sdk](https://github.com/influxdata/influxdb-python) so that installing the whole
sdk is not required.

## How to use

1. Copy the repo files to some location in the target system
2. Install dependencies (mentioned above)
3. Setup telegraf to run this plugin using execd.

   Sample config snippet (assuming that the script is kept in
   `/etc/telegraf/scripts/pg_custom/`):

   ``` toml
   [[inputs.execd]]
     interval = "300s"
     data_format = "influx"
     command = ["/usr/bin/python", "/etc/telegraf/scripts/pg_custom/postgresql_query.py", "/etc/telegraf/scripts/pg_custom/postgresql_custom_data.conf"]
     restart_delay = "60s"
     signal = "STDIN"

   [[outputs.influxdb]]
     urls = ["http://127.0.0.1:8086"]
     database = "telegraf"
   ```

4. Setup PostgreSQL credentials so that this plugin can run queries. There are
   two common ways to do that:

   a. Create telegraf user with superuser access, but don't create a password

   ```sql
   CREATE USER telegraf SUPERUSER CONNECTION LIMIT 3;
   ```

   Since telegraf plugins run with the telegraf user, this should be sufficient.

   b. If PostgreSQL is not running on the same host that telegraf is running on,
   the above method will not work. In that case, create a new user with
   superuser access, and give it a password. Use the same command as above, but
   add a password.

   Then, the `postgresql_custom_data.conf` file can to edited to have the
   address parameter like:

   ```toml
   address="host=127.0.0.1 user=telegraf password=secret"
   ```

5. Add your queries in the `postgresql_custom_data.conf`. Some sample queries
   are included.

6. Start telegraf, and check logs. If everything is working correctly, you
   should see something like this:

   ```
   I! [inputs.execd] Starting process: /usr/bin/python [/etc/telegraf/scripts/pg_custom/postgresql_query.py /etc/telegraf/scripts/pg_custom/postgresql_custom_data.conf]
   ```

   If not, there should be enough in the logs to debug further.

7. A sample grafana dashboard is also availabled as an exported json in this repo.


from datetime import datetime
from dateutil import tz

def convertUTCtoLocalTime(timestamp_string):
# convert UTC timestamp created by psql tweet db to EST local time 
# returns new timestamp string in EST time

    print "converting: " + timestamp_string

    # METHOD 1: Hardcode zones:
    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('America/New_York')

    # METHOD 2: Auto-detect zones:
    # from_zone = tz.tzutc()
    # to_zone = tz.tzlocal()

    # utc = datetime.utcnow()
    utc = datetime.strptime(timestamp_string, '%Y-%m-%d %H:%M:%S')

    # Tell the datetime object that it's in UTC time zone since 
    # datetime objects are 'naive' by default
    utc = utc.replace(tzinfo=from_zone)

    # Convert time zone
    eastern = utc.astimezone(to_zone)
    print "converted"
    return eastern

datetime_now = '2015-07-01 16:53:42.636711'
datetime_expire = '2015-07-04 17:23:42.636711'

converted = convertUTCtoLocalTime(datetime_now)
print converted 


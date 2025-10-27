-- FESTIVALS LIST
select
    case 
        when start_month = end_month then to_char(to_date(start_month::text, 'MM'), 'FMMonth')
        else to_char(to_date(start_month::text, 'MM'), 'FMMonth') 
             || ' - ' || 
             to_char(to_date(end_month::text, 'MM'), 'FMMonth')
    end as month_range,
    type,
	name,
    location
from travel.festivals
where type in (
    'Sakura', 
    'Cultural festival', 
    'Cultural festival / Obon',
    'Nature festival',
    'Seasonal event',
    'Fireworks display',
    'Dance festival',
    'Fire festival'
     ) and
     (start_month in (10, 4, 3) OR end_month in (10, 4, 3, 8, 9))
order by start_month;
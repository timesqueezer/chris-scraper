# -*- coding: utf-8 -*-
from datetime import datetime
from dateutil.parser import parse

import scrapy


class UniKielSpider(scrapy.Spider):
    name = 'uni-kiel'
    allowed_domains = ['www.uni-kiel.de/de/veranstaltungen/ueberblick']
    start_urls = ['http://www.uni-kiel.de/de/veranstaltungen/ueberblick/']

    def parse(self, response):
        for event_item in (response.css('.teasernews-list-item') + response.css('.news-list-item')):
            event_date_loc = event_item.css('.news-item__event-date')[0].extract()
            event_date_loc = event_date_loc \
                .replace('<div class="news-item__event-date">', '') \
                .replace('</div>', '') \
                .replace('\t', '') \
                .replace('\n', '') \
                .strip()

            event_time = None
            event_date_loc_split = event_date_loc.split(' | ')
            if len(event_date_loc_split) == 2:
                event_date, event_loc = event_date_loc_split

            elif len(event_date_loc_split) == 3:
                event_date, event_loc, event_time = event_date_loc_split

            event_end = None
            event_date_split = event_date.split(' - ')
            if len(event_date_split) == 2:
                event_start, event_end = event_date_split
            elif len(event_date_split) == 1:
                event_start = event_date_split[0]

            event_start = parse(event_start)
            if event_end:
                event_end = parse(event_end)

            if event_time:
                self.log('got time')
                event_time_split = event_time.split(' bis ')
                if len(event_time_split) == 1:
                    event_time = datetime.strptime(event_time_split[0], '%H:%M')
                    event_start = event_start.replace(hour=event_time.hour, minute=event_time.minute)

                elif len(event_time_split) == 2:
                    event_start_time = datetime.strptime(event_time_split[0], '%H:%M')
                    event_start = event_start.replace(hour=event_start_time.hour, minute=event_start_time.minute)

                    event_end_time = datetime.strptime(event_time_split[1], '%H:%M')
                    if event_end:
                        event_end = event_end.replace(hour=event_end_time.hour, minute=event_end_time.minute)

            event_title = None
            event_title_el = event_item.css('.news-list-item__headline').xpath('.//a/span')
            if len(event_title_el) == 0:
                event_title_el = event_item.css('.news-list-item__headline').xpath('.//span')

            event_title = event_title_el[0].extract().replace('<span>', '').replace('</span>', '')

            yield {
                'location': event_loc,
                'date_start': event_start,
                'date_end': event_end,
                'title': event_title,
            }

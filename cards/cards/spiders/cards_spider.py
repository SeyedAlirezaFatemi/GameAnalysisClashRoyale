import scrapy


class CardsSpider(scrapy.Spider):
    name = "cards"
    start_urls = [
        "https://clashroyale.fandom.com/wiki/Cards",
    ]

    def parse(self, response):
        columns = []
        for row in response.css("table.wikitable.sortable > tbody > tr"):
            if len(row.css("th")) != 0:
                # Header row
                columns = row.css("th").xpath("text()").getall()
                columns = list(filter(lambda column: column != "\n", columns))
                yield {"columns": columns}
            else:
                vals = []
                for col in row.css("td"):
                    if len(col.css("a")) != 0:
                        # vals.append(col.css("a").xpath("@title").get())
                        vals.append(col.css("a").xpath("text()").get())
                    else:
                        vals.append(col.xpath("text()").get())
                info = dict()
                for column, val in zip(columns, vals):
                    info[column] = val.replace("\n", "")
                yield info
                yield scrapy.Request(
                    url=response.urljoin(info["Card"]), callback=self.parse_card_page
                )

    def parse_card_page(self, response):
        columns = ["EXTRA", "Card"] + (
            response.css("#unit-attributes-table tr")[0]
            .css("th")
            .xpath("text()")
            .getall()
        )
        columns = list(
            map(lambda col: col.strip(), filter(lambda column: column != "\n", columns))
        )
        columns = columns[:-2]  # Ignore type and rarity
        vals = ["", response.css("#firstHeading").xpath("text()").get().strip()] + (
            response.css("#unit-attributes-table tr")[1]
            .css("td")
            .xpath("text()")
            .getall()
        )
        vals = list(map(lambda val: val.strip(), filter(lambda val: val != "\n", vals)))
        yield dict(zip(columns, vals))

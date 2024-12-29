from scrapy import cmdline

if __name__ == '__main__':
    # get the reviews
    # scrapy the reviews of the app with app_id 2358720, and limit the amount to 200
    # and set the filter of reviews to simplified chinese
    cmdline.execute([
        "scrapy", "crawl", "review",
        "-a", "language=simplified chinese",
        "-a", "app_id=2358720",
        "-a", "amount_limit=200",
        "-O", "review_output.json"
    ])

    # get the app info
    # scrapy the app info of the apps with app_id 2358720 and 1245620
    cmdline.execute([
        "scrapy", "crawl", "app_info",
        "-a", "app_ids=2358720,1245620",
        "-O", "app_info_output.json"
    ])

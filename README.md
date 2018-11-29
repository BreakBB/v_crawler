# v_crawler

v_crawler is a simple project to crawl the Amazon Prime Video platform for movies and series.

It is using the [Scrapy Framework](https://github.com/scrapy/scrapy) and extracts various information about the found content and saves them to a AWS DynamoDB table.

## Requirements

### Privoxy

1. Install Privoxy
2. Uncomment the following line in the **config.txt**:
     
    ```forward-socks4a   /               127.0.0.1:9050 .```

3. Change the given port from _9050_ to _9150_

### TOR

1. Install the TOR browser and have it running
2. If you want to make use of the TOR service you have to skip step 2 of Privoxy and change the ports inside the code to 9050.

### AWS DynamoDB

1. Create the DynamoDB tables<br>
    a. name them "amazon_video_de" and "amazon_video_com" with "movie_id" as primary key of type string.<br>
    b. if you want to name them differently you have to set those names in the code
2. Make sure to have your AWS credentials stored under

    ```C:\Users\<UserName>\.aws``` or ```~/.aws```
    
### Python dependencies

1. Install the python dependencies using the **requirements.txt**
 

Assignment is part of COMS 6998 Cloud Computing & Big Data course at Columbia University

Personalized Restaurant Recommendations Assistant, using AWS S3, API Gateway, and Lambda. 
We are using Yelp API for restaurant data, and DynamoDB/OpenSearch for efficient storage.

# Link to hosted website
http://dining-concierge.com.s3-website-us-east-1.amazonaws.com/

## Files/Folders Included:
1. /frontend - contains all frontend code<br>
2. /lambda_functions<br>
   a. LF0.py - LF0 lambda function<br>
   b. LF1.py - LF1 lambda function<br>
   c. LF2.py - LF2 lambda function - also includes code to save user search history (extra credit)<br>
   d. past-search-recommendation.py - Lambda function to give recommendations based on search history of the user (extra credit)<br>
   e. dynamo_db_import.py - Lambda function for importing the scraped data into DynamoDB<br>
3. /Yelp Scrapper
   a. main_yelp.ipynb - script to scrape data from yelp and store in restaurant.csv<br>
   b. restaurant.csv - data scraped using yelp api<br>
   c. /ElasticSearch<br>
      i. Elasticsearch_json_data.ipynb - converts restaurant.csv to restaurant.json (the data format required to be uploaded to OpenSearch)<br>
4. AI Customer Service API-test-stage-swagger.yaml<br>

Team Members 
Smrithi Prakash and Varsha Meghana Kanmuri

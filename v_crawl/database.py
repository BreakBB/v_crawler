import boto3


class Database:
    dynamo_db = None
    table = None

    def __init__(self, table):
        self.dynamo_db = boto3.client("dynamodb")
        self.table = table
        return

    def put_item(self, movie_item):
        try:
            response = self.dynamo_db.put_item(
                TableName=self.table,
                Item={
                    'movie_id': {"S": movie_item['movie_id']},
                    'url': {"S": movie_item['url']},
                    'title': {"S": movie_item['title']},
                    'rating': {"N": str(movie_item['rating'])},
                    'imdb': {"N": str(movie_item['imdb'])},
                    'genres': {"SS": movie_item['genres']},
                    'year': {"N": str(movie_item['year'])},
                    'fsk': {"N": str(movie_item['fsk'])}
                },
                ConditionExpression="movie_id <> :movie_id_value",
                ExpressionAttributeValues={
                    ":movie_id_value": {"S": movie_item['movie_id']}
                }
            )
        except self.dynamo_db.exceptions.ConditionalCheckFailedException:
            print("put_item failed because item is already in DB")
            return

        print("Successfully added new item to DB")
        return

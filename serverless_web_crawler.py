from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_lambda_python_alpha as _alambda,
    aws_dynamodb as _dynamodb,
    aws_sqs as _sqs,
    aws_lambda_event_sources as _event_sources,
)
from constructs import Construct


class ServerlessWebCrawlerStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Dynamo Model
        # PK: VisitedURL
        # SK: RunId#Date
        # SourceURL (Where did I come from?)
        # RootURL (Where did I start?)

        # Dynamo - VisitedUrls Table
        table = _dynamodb.Table(
            self,
            "VisitedURLs",
            table_name="VisitedURLs",
            partition_key=_dynamodb.Attribute(
                name="visitedURL", type=_dynamodb.AttributeType.STRING
            ),
            sort_key=_dynamodb.Attribute(
                name="runId", type=_dynamodb.AttributeType.STRING
            ),
            billing_mode=_dynamodb.BillingMode.PAY_PER_REQUEST,
        )

        # SQS - PendingCrawls
        crawlerQueue = _sqs.Queue(self, "Crawler", queue_name="Crawler")
        crawlerDLQ = _sqs.Queue(self, "Crawler-DLQ", queue_name="Crawler-DLQ")

        # Initiator

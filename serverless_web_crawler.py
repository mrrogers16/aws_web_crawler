from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_lambda_python_alpha as _alambda,
    aws_dynamodb as _dynamodb,
    aws_sqs as _sqs,
    aws_lambda_event_sources as _event_sources,
)
from constructs import Construct

from app.plugins.iam import IAMPlugin
from app.plugins.ec2 import EC2Plugin
from app.plugins.s3 import S3Plugin
from app.plugins.cloudtrail import CloudTrailPlugin
from app.plugins.securityhub import SecurityHubPlugin
from app.plugins.config_service import ConfigPlugin
from app.plugins.networking import NetworkingPlugin
from app.plugins.rds import RDSPlugin
from app.plugins.lambda_service import LambdaPlugin
from app.plugins.kms import KMSPlugin
from app.plugins.containers import ContainersPlugin
from app.plugins.dynamodb import DynamoDBPlugin
from app.plugins.governance import GovernancePlugin

def get_plugins():
    return [
        IAMPlugin(), EC2Plugin(), S3Plugin(), CloudTrailPlugin(),
        SecurityHubPlugin(), ConfigPlugin(), NetworkingPlugin(),
        RDSPlugin(), LambdaPlugin(), KMSPlugin(), ContainersPlugin(),
        DynamoDBPlugin(), GovernancePlugin()
    ]

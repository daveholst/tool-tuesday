"""An AWS Python Pulumi program"""

import pulumi
import pulumi_aws as aws
import infra.iam as iam
import json

region = aws.config.region

custom_stage_name = "dev"

##################
## Lambda Function
##################

# Create a Lambda function, using code from the `./app` folder.

lambda_func = aws.lambda_.Function(
    "tool_tuesday_lambda",
    role=iam.lambda_role.arn,
    runtime="python3.9",
    handler="tool_tuesday/handler.handler",
    code=pulumi.AssetArchive({".": pulumi.FileArchive("./infra/artifact.zip")}),
    timeout=30,
    memory_size=2048,
)

####################################################################
##
## API Gateway REST API (API Gateway V1 / original)
##    /{proxy+} - passes all requests through to the lambda function
##
####################################################################

# Create a single Swagger spec route handler for a Lambda function.
def swagger_route_handler(arn):
    return {
        "x-amazon-apigateway-any-method": {
            "x-amazon-apigateway-integration": {
                "uri": f"arn:aws:apigateway:{region}:lambda:path/2015-03-31/functions/{arn}/invocations",
                "passthroughBehavior": "when_no_match",
                "httpMethod": "POST",
                "type": "aws_proxy",
            },
        },
    }


# Create the API Gateway Rest API, using a swagger spec.
rest_api = aws.apigateway.RestApi(
    "api",
    body=lambda_func.arn.apply(
        lambda arn: json.dumps(
            {
                "swagger": "2.0",
                "info": {"title": "api", "version": "1.0"},
                "paths": {
                    "/{proxy+}": swagger_route_handler(arn),
                },
            }
        )
    ),
)

# Create a deployment of the Rest API.
deployment = aws.apigateway.Deployment(
    "api-deployment",
    rest_api=rest_api.id,
    # Note: Set to empty to avoid creating an implicit stage, we'll create it
    # explicitly below instead.
    stage_name="",
)

# Create a stage, which is an addressable instance of the Rest API. Set it to point at the latest deployment.
stage = aws.apigateway.Stage(
    "api-stage",
    rest_api=rest_api.id,
    deployment=deployment.id,
    stage_name=custom_stage_name,
)

# Give permissions from API Gateway to invoke the Lambda
rest_invoke_permission = aws.lambda_.Permission(
    "api-rest-lambda-permission",
    action="lambda:invokeFunction",
    function=lambda_func.name,
    principal="apigateway.amazonaws.com",
    source_arn=deployment.execution_arn.apply(lambda arn: arn + "*/*"),
)

#########################################################################
# Create an HTTP API and attach the lambda function to it
##    /{proxy+} - passes all requests through to the lambda function
##
#########################################################################

http_endpoint = aws.apigatewayv2.Api("http-api-pulumi-example", protocol_type="HTTP")

http_lambda_backend = aws.apigatewayv2.Integration(
    "example",
    api_id=http_endpoint.id,
    integration_type="AWS_PROXY",
    connection_type="INTERNET",
    description="Lambda example",
    integration_method="POST",
    integration_uri=lambda_func.arn,
    passthrough_behavior="WHEN_NO_MATCH",
)

url = http_lambda_backend.integration_uri

http_route = aws.apigatewayv2.Route(
    "example-route",
    api_id=http_endpoint.id,
    route_key="ANY /{proxy+}",
    target=http_lambda_backend.id.apply(lambda targetUrl: "integrations/" + targetUrl),
)

http_stage = aws.apigatewayv2.Stage(
    "dev-stage",
    api_id=http_endpoint.id,
    route_settings=[
        {
            "route_key": http_route.route_key,
            "throttling_burst_limit": 1,
            "throttling_rate_limit": 0.5,
        }
    ],
    auto_deploy=True,
)

# Give permissions from API Gateway to invoke the Lambda
http_invoke_permission = aws.lambda_.Permission(
    "api-http-lambda-permission",
    action="lambda:invokeFunction",
    function=lambda_func.name,
    principal="apigateway.amazonaws.com",
    source_arn=http_endpoint.execution_arn.apply(lambda arn: arn + "*/*"),
)

# get zone
dh_wtf_domain_zone = aws.route53.get_zone(name="dh.wtf").zone_id

# # route53 domain
# dns_record = aws.route53

# us_provider = aws.Provider("usProvider", region="us-east-2")


tool_dh_wtf_cert_arn = "arn:aws:acm:ap-southeast-2:739766728346:certificate/c62c754f-5eb4-4ef4-b2f6-4cc93f4bafef"

api_domain_name = aws.apigatewayv2.DomainName(
    "exampleDomainName",
    domain_name="tool.dh.wtf",
    domain_name_configuration=aws.apigatewayv2.DomainNameDomainNameConfigurationArgs(
        certificate_arn=tool_dh_wtf_cert_arn,
        endpoint_type="REGIONAL",
        security_policy="TLS_1_2",
    ),
    # opts=pulumi.ResourceOptions(provider=us_provider),
)
example_record = aws.route53.Record(
    "exampleRecord",
    name=api_domain_name.domain_name,
    type="A",
    zone_id=dh_wtf_domain_zone,
    aliases=[
        aws.route53.RecordAliasArgs(
            name=api_domain_name.domain_name_configuration.target_domain_name,
            zone_id=api_domain_name.domain_name_configuration.hosted_zone_id,
            evaluate_target_health=False,
        )
    ],
)


# Export the https endpoint of the running Rest API
pulumi.export(
    "apigateway-rest-endpoint",
    deployment.invoke_url.apply(lambda url: url + custom_stage_name + "/{proxy+}"),
)
# See "Outputs" for (Inputs and Outputs)[https://www.pulumi.com/docs/intro/concepts/inputs-outputs/] the usage of the pulumi.Output.all function to do string concatenation
pulumi.export(
    "apigatewayv2-http-endpoint",
    pulumi.Output.all(http_endpoint.api_endpoint, http_stage.name).apply(
        lambda values: values[0] + "/" + values[1] + "/"
    ),
)

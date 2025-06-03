# Hello World Python App

## Disclaimer

> ⚠️ **Important Disclaimer:**
> The instructions below are only applicable if you
> **already have full access** to the EIAP Ecosystem.
> If you do not have this access, **please do not proceed.**

**Note:**
If you need help accessing the EIAP Ecosystem, contact support
at this **email address:** intelligent.automation.platform@ericsson.com

## Introduction

This is a simple Hello World Python App with the following three endpoints:

- **/sample-app/python/hello** is a sample endpoint.

- **/sample-app/python/health** is an endpoint for an external agent to
  monitor the App liveliness.

- **/sample-app/python/metrics** is an endpoint that presents
  the number of successful and failed invocations of
  the '/sample-app/python/hello' endpoint.

## Build Docker Image

Rename the `Dockerfile-template` file to `Dockerfile`.

```bash
mv Dockerfile-template Dockerfile
```

Replace `<PYTHON_IMAGE_NAME>` in the Dockerfile with a slim Python base image.
Refer to: [Python on Docker™ Hub](https://hub.docker.com/_/python)

Run the following command to build the image.

```bash
docker build . -t proj-eric-oss-drop/eric-oss-hello-world-python-app:<VERSION> --build-arg APP_VERSION=<VERSION>
```

## Run Docker Image

A port binding on port 8050 is done to expose the endpoints.

```bash
docker run -p 8050:8050 --rm --name python-sample-app proj-eric-oss-drop/eric-oss-hello-world-python-app:<VERSION>
```

Run a curl request to the /sample-app/python/hello endpoint of the app.
The request should return a "Hello World!!" response.

```bash
curl -is localhost:8050/sample-app/python/hello
```

Example Output:

```http
HTTP/1.1 200 OK
Date: Thu, 17 Jun 2021 14:46:46 GMT
Content-Length: 13
Content-Type: text/plain; charset=utf-8

Hello World!!
```

## Build the CSAR package

For this step, install the [App Package Tool](https://developer.intelligentautomationplatform.ericsson.net/#capabilities/app-administration/tutorial-package-app).

Once installed, the tool will be available as a Docker image
named `armdocker.rnd.ericsson.se/proj-eric-oss-dev-test/releases/eric-oss-app-package-tool:latest`

**Note:** In the commands below, make sure to replace `<VERSION>`
with the correct Python Sample App version. Run the following commands
from within your project directory
`eric-oss-hello-world-python-app-<VERSION>`.

```bash
mkdir -p helloworldAppPackage
```

The zip file includes a `csar` directory, which has the structure of the
CSAR package.

```bash
cp -r ./csar/* ./helloworldAppPackage/
```

Run the following command to generate an archive of the chart.

```bash
helm package ./charts/eric-oss-hello-world-python-app/
```

Move the created .tgz file to the OtherDefinitions/ASD directory.

```bash
mv eric-oss-hello-world-python-app-<VERSION>.tgz ./helloworldAppPackage/OtherDefinitions/ASD/
```

Create a folder where the CSAR app package will be stored into.

```bash
mkdir csar-output
```

Generate an archive of the Docker image and store it temporarily in the `csar-output`
directory.

```bash
docker save proj-eric-oss-drop/eric-oss-hello-world-python-app:<VERSION> -o csar-output/docker.tar
```

Run the following command locally to create a CSAR app package using the
eric-oss-app-package-tool.

```bash
docker run --init --rm \
  --volume $PWD/csar-output/:/tmp/csar/ \
  --volume $HOME/.docker:/root/.docker \
  --volume /var/run/docker.sock:/var/run/docker.sock \
  --workdir /target \
  --volume $PWD/helloworldAppPackage:/target \
  armdocker.rnd.ericsson.se/proj-eric-oss-dev-test/releases/eric-oss-app-package-tool:latest \
  generate --tosca /target/Metadata/Tosca.meta \
  --name helloworldAppPackage \
  --images /tmp/csar/docker.tar \
  --helm3 \
  --output /tmp/csar
```

Run the following command to verify if the CSAR Package was created successfully.

```bash
ls ./csar-output
```

`helloworldAppPackage.csar` is visible in the directory.

## Onboard the App

### Prerequisites for Onboarding

Contact the platform administrator to request the following:

- A CA certificate, needed for secure communication with the platform APIs.
- Client Access to the platform with the required roles, needed for authorized
communication with the platform APIs used to *onboard and instantiate* the
Hello World App. You will receive a Client ID and Client Secret from the
platform administrator. Include the required roles listed below in the request.

| Role                                                            | Role Description                                                              |
| --------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| AppMgr_Application_Administrator                                | Administrator access to App Administration onboarding and instantiating Apps. |
| AppMgr_Application_Operator                                     | Operator access to App Administration onboarding and instantiating Apps.      |
| Exposure_Application_Administrator                              | Access to Service Exposure Onboarding APIs for the Apps.                      |
| UserAdministration_ExtAppRbac_Application_SecurityAdministrator | Access to Service Exposure Access control APIs for the Apps.                  |

See [Client Access to REST APIs](https://developer.intelligentautomationplatform.ericsson.net/#tutorials/client-access)
 for further details on client authentication.

Use the following command to generate a valid access token:

```bash
curl --cacert <PATH_TO_CA_CERTIFICATE> --request POST \
https://<eic-host>/auth/realms/master/protocol/openid-connect/token \
--header 'content-type: application/x-www-form-urlencoded' \
--data "grant_type=client_credentials&client_id=<IAM_CLIENT_ID>&client_secret=<IAM_CLIENT_SECRET>"
```

This command returns an access token, which is used in the commands in the
following steps. See the following example of a response containing the
access token:

```bash
  "access_token": "eyJhbGciOiJSUze168rQBwD4....",
  "expires_in": 300,
  "refresh_expires_in": 0,
  "token_type": "Bearer",
  "not-before-policy": 0,
  "scope": "profile"
```

### Steps for Onboarding

Onboard the **Hello World CSAR App Package** using [App Administration](https://developer.intelligentautomationplatform.ericsson.net/#capabilities/app-administration/developer-guide-manage?chapter=onboard).

To start the onboarding of the Hello World CSAR app,
run the following command in a command line tool.

```bash
curl --cacert <PATH_TO_CA_CERTIFICATE> --location --request POST 'https://<eic-host>/app-onboarding/v2/app-packages' \
--header 'Authorization: Bearer <access-token>' \
--header 'accept: application/json' \
--form 'file=@"<PATH_TO_CSAR>/helloworldAppPackage.csar"'
```

Example of command result:

```json
{
  "fileName": "helloworldAppPackage.csar",
  "onboardingJob": {
    "id": "af036040-a732-4af9-b65a-8103da56c35c",
    "href": "/onboarding-jobs/af036040-a732-4af9-b65a-8103da56c35c"
  }
}
```

An onboarding-job `id` is shown in the command result
(a2f0a43d-730a-4991-8481-746c3e76556e in the example).
This is the `JOB_ID`. Use the `JOB_ID` to get the
status of the onboarding process in the following commands:

```bash
curl --cacert <PATH_TO_CA_CERTIFICATE> --location --request GET 'https://<eic-host>/app-onboarding/v2/onboarding-jobs/<JOB_ID>' \
--header 'Authorization: Bearer <access-token>' \
--header 'accept: application/json'
```

It can take several minutes for the status to change to `ONBOARDED`.
Repeat the command until the status is changed to `ONBOARDED`.

Example of command result:

```json
{
  "id": "af036040-a732-4af9-b65a-8103da56c35c",
  "fileName": "helloworldAppPackage.csar",
  "packageVersion": "3.1.1-0",
  "packageSize": "51.7659MiB",
  "vendor": "Ericsson",
  "type": "rApp",
  "onboardStartedAt": "2025-05-31T13:51:56.616Z",
  "status": "ONBOARDED",
  "onboardEndedAt": "2025-05-31T13:51:59.955Z",
  "events": [
    {
      "type": "INFO",
      "title": "Stored 1 out of 4 artifacts",
      "detail": "Uploaded eric-oss-hello-world-python-appASD.yaml",
      "occurredAt": "2025-05-31T13:51:58.042Z"
    },
    {
      "type": "INFO",
      "title": "Stored 2 out of 4 artifacts",
      "detail": "Uploaded eric-oss-hello-world-python-app",
      "occurredAt": "2025-05-31T13:51:58.043Z"
    },
    {
      "type": "INFO",
      "title": "Stored 3 out of 4 artifacts",
      "detail": "Uploaded docker.tar",
      "occurredAt": "2025-05-31T13:51:59.792Z"
    },
    {
      "type": "INFO",
      "title": "Stored 4 out of 4 artifacts",
      "detail": "Uploaded metadata.json",
      "occurredAt": "2025-05-31T13:51:59.812Z"
    }
  ],
  "self": {
    "href": "/onboarding-jobs/af036040-a732-4af9-b65a-8103da56c35c"
  },
  "app": {
    "id": "rapp-ericsson-eric-oss-hello-world-python-app-3-1-1-0",
    "href": "app-lifecycle-management/v3/apps/rapp-ericsson-eric-oss-hello-world-python-app-3-1-1-0"
  }
}
```

The `APP_ID` is the `id` of the `app` returned in the previous
command (rapp-ericsson-eric-oss-hello-world-python-app-3-1-1-0 in the example).
Run the following command to initialize the App.

```bash
curl --cacert <PATH_TO_CA_CERTIFICATE> --location --request POST 'https://<eic-host>/app-lifecycle-management/v3/apps/<APP_ID>/initialization-actions' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer <access-token>' \
-d '{"action": "INITIALIZE"}'
```

Example of command result:

```json
{
  "app": {
    "status": "INITIALIZING",
    "id": "rapp-ericsson-eric-oss-hello-world-python-app-3-1-1-0",
    "href": "/apps/rapp-ericsson-eric-oss-hello-world-python-app-3-1-1-0"
  }
}
```

Repeat the following command until the status is changed to `INITIALIZED`.

```shell
curl --cacert <PATH_TO_CA_CERTIFICATE> --location --request GET 'https://<eic-host>/app-lifecycle-management/v3/apps/<APP_ID>' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer <access-token>'
```

Example of command result:

```json
{
  "id": "rapp-ericsson-eric-oss-hello-world-python-app-3-1-1-0",
  "type": "rApp",
  "provider": "Ericsson",
  "name": "eric-oss-hello-world-python-app",
  "version": "3.1.1-0",
  "mode": "DISABLED",
  "status": "INITIALIZED",
  "createdAt": "2025-05-31T13:51:59.931Z",
  "components": [
    {
      "type": "ASD",
      "name": "eric-oss-hello-world-python-app",
      "version": "3.1.1-0",
      "artifacts": [
        {
          "name": "docker.tar",
          "type": "IMAGE"
        },
        {
          "name": "eric-oss-hello-world-python-appASD.yaml",
          "type": "OPAQUE"
        },
        {
          "name": "eric-oss-hello-world-python-app",
          "type": "HELM"
        }
      ]
    },
    {
      "type": "SECURITYMANAGEMENT",
      "name": "security-mgmt",
      "version": "1.0.0",
      "artifacts": [
        {
          "name": "metadata.json",
          "type": "OPAQUE"
        }
      ]
    }
  ],
  "permissions": [
    {
      "resource": "kafka",
      "scope": "GLOBAL"
    }
  ],
  "roles": [],
  "events": [
    {
      "type": "INITIALIZE",
      "title": "SUCCEEDED",
      "detail": "INITIALIZE has successfully completed",
      "createdAt": "2025-05-31T13:55:50.421Z"
    },
    {
      "type": "INITIALIZE",
      "title": "STARTED",
      "detail": "INITIALIZE has started",
      "createdAt": "2025-05-31T13:55:34.171Z"
    },
    {
      "type": "CREATE",
      "title": "SUCCEEDED",
      "detail": "CREATE has successfully completed",
      "createdAt": "2025-05-31T13:51:59.945Z"
    }
  ],
  "self": {
    "href": "/apps/rapp-ericsson-eric-oss-hello-world-python-app-3-1-1-0"
  }
}
```

Run the following command to switch the app mode from 'DISABLED' to 'ENABLED'.

```bash
curl --cacert <PATH_TO_CA_CERTIFICATE> --location --request PUT 'https://<eic-host>/app-lifecycle-management/v3/apps/<APP_ID>/mode' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer <access-token>' \
-d '{"mode": "ENABLED"}'
```

Example of command result:

```json
{
  "mode": "ENABLED",
  "app": {
    "id": "rapp-ericsson-eric-oss-hello-world-python-app-3-1-1-0",
    "href": "/apps/rapp-ericsson-eric-oss-hello-world-python-app-3-1-1-0"
  }
}
```

## Instantiate the App

This section describes how the App can communicate with IAM and produce logs to
 the platform. The App is instantiated using App Administration and the API is
 exposed and secured by the Service Exposure capability.

### Prerequisites for Instantiation

- You need the access token generated in **Onboard the App** prerequisite to
 access the App Manager for instantiating the Hello World CSAR App Package.
- Contact your platform administrator to generate the required App key,
 certificates key, certificates, and the secrets which store them. The
  details of the secrets, keys, certs and EIC endpoint details will be passed
   to App Administration through the `userDefinedHelmParameters` when
    instantiating the App. The required parameters are:
  - The `iamBaseUrl`, as the `/sample-app/python/hello` endpoint of this
   sample App first communicates with IAM to obtain a client token (login)
    before returning the "Hello World!!" string output.
  - The `authenticationType` defines the authentication method based on the
   iamBaseUrl protocol—set to `x509` for mTLS endpoints or `client-secret` for
    TLS endpoints.
  - The `platformCaCertSecretName` and `platformCaCertFileName` to enable
   secure TLS communication. Refer to
    [App Certificate Provisioning Developer Guide](https://developer.intelligentautomationplatform.ericsson.net/#capabilities/app-cert-provisioning/developer-guide)
     to understand how certificates are loaded into the App during
      instantiation for secure communication.
  - The `appSecretName`, `logEndpoint`,
   `appKeyFileName`, `appCertFileName`
    for mTLS communication. For more information on the variable values
     required, see [App Logging Developer Guide to Produce logs](https://developer.intelligentautomationplatform.ericsson.net/#capabilities/app-logging/how-to-produce-logs?chapter=identify-environment-and-secret-variables-names).

### Steps for Instantiation

Use the App Administration capability to instantiate the
 **Hello World CSAR App**. For more details on instantiating an App, see
  [App Administration](https://developer.intelligentautomationplatform.ericsson.net/#capabilities/app-administration/developer-guide-manage?chapter=instantiate).
Run the following commands to start the instantiation process using the
 `APP_ID` from **Onboard the App**.

#### Create App Instance

```shell
curl --cacert <PATH_TO_CA_CERTIFICATE> --location --request POST 'https://<eic-host>/app-lifecycle-management/v3/app-instances' \
--header 'accept: application/json' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer <access-token>' \
-d '{
  "appId": "<APP_ID>"
}'
```

Example command result:

```json
{
  "id": "rapp-ericsson-eric-oss-hello-world-python-app-68129972",
  "appId": "rapp-ericsson-eric-oss-hello-world-python-app-3-1-1-0",
  "status": "UNDEPLOYED",
  "credentials": {
    "clientId": "rapp-ericsson-eric-oss-hello-world-python-app-68129972"
  },
  "componentInstances": [
    {
      "name": "eric-oss-hello-world-python-app",
      "version": "3.1.1-0",
      "type": "ASD",
      "deployState": "UNDEPLOYED",
      "properties": {
        "userDefinedHelmParameters": {
          "global.clientCredentials.secret.clientIdKey": "clientId",
          "global.clientCredentials.secret.name": "rapp-ericsson-eric-oss-hello-world-python-app-68129972-cc"
        },
        "namespace": "<namespace>",
        "timeout": 5
      }
    },
    {
      "name": "security-mgmt",
      "version": "1.0.0",
      "type": "SECURITYMANAGEMENT",
      "properties": {
        "authenticatorType": "client-x509"
      }
    }
  ],
  "self": {
    "href": "/app-instances/rapp-ericsson-eric-oss-hello-world-python-app-68129972"
  },
  "app": {
    "href": "/apps/rapp-ericsson-eric-oss-hello-world-python-app-3-1-1-0"
  }
}
```

An app-instance `id` is shown in the command result
 (rapp-ericsson-eric-oss-hello-world-python-app-68129972 in the example). This
 is the `APP_INSTANCE_ID` used in the following commands.

#### Deploy App Instance

> All `userDefinedHelmParameters` are required for successful instantiation
 of your App.

```shell
curl --cacert <PATH_TO_CA_CERTIFICATE> --location --request POST 'https://<eic-host>/app-lifecycle-management/v3/app-instances/<APP_INSTANCE_ID>/deployment-actions' \
  --header 'accept: application/json' \
  --header 'Content-Type: application/json' \
  --header 'Authorization: Bearer <access-token>' \
  -d '{
  "type": "DEPLOY",
  "additionalData": {
    "componentInstances": [
      {
        "name": "eric-oss-hello-world-python-app",
        "properties": {
          "timeout": 5,
          "userDefinedHelmParameters": {
            "iamBaseUrl": "https://<eic-host>",
            "logEndpoint": "<LOG_ENDPOINT>",
            "platformCaCertSecretName": "<PLATFORM_CA_CERT_SECRET>",
            "appSecretName": "<APP_MTLS_SECRET>",
            "platformCaCertFileName": "<PLATFORM_CA_CERT_FILENAME>",
            "appKeyFileName": "<APP_PRIVATE_KEY>",
            "appCertFileName": "<APP_CERTIFICATE>",
            "authenticationType": "<AUTHENTICATION_TYPE>"
          }
        }
      }
    ]
  }
}'
```

See the following example command result:

```json
{
  "type": "DEPLOY",
  "additionalData": {
    "componentInstances": [
      {
        "name": "eric-oss-hello-world-python-app",
        "properties": {
          "timeout": 5,
          "userDefinedHelmParameters": {
            "platformCaCertSecretName": "<PLATFORM_CA_CERT_SECRET>",
            "platformCaCertFileName": "<PLATFORM_CA_CERT_FILENAME>",
            "iamBaseUrl": "https://<eic-host>",
            "appSecretName": "<APP_MTLS_SECRET>",
            "logEndpoint": "<LOG_ENDPOINT>",
            "appKeyFileName": "<APP_PRIVATE_KEY>",
            "appCertFileName": "<APP_CERTIFICATE>",
            "authenticationType": "<AUTHENTICATION_TYPE>",
            "global.clientCredentials.secret.name": "<CLIENT_SECRET>",
            "global.clientCredentials.secret.clientIdKey": "<CLIENT_ID>"
          }
        }
      }
    ]
  },
  "appInstance": {
    "status": "DEPLOYING",
        "href": "/app-instances/rapp-ericsson-eric-oss-hello-world-python-app-68129972"
  }
}
```

Use the App instance ID in the following command to check the instantiation
 status. Repeat the command until the health status is changed
  to `"status":"DEPLOYED"`.

```shell
curl --cacert <PATH_TO_CA_CERTIFICATE> --location --request GET 'https://<eic-host>/app-lifecycle-management/v3/app-instances/<APP_INSTANCE_ID>' \
--header 'accept: application/json' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer <access-token>'
```

```json
{
  "id": "rapp-ericsson-eric-oss-hello-world-python-app-68129972",
  "appId": "rapp-ericsson-eric-oss-hello-world-python-app-3-1-1-0",
  "status": "DEPLOYED",
  "createdAt": "2025-05-31T14:01:01.741Z",
  "updatedAt": "2025-05-31T14:04:16.300Z",
  "credentials": {
    "clientId": "rapp-ericsson-eric-oss-hello-world-python-app-68129972"
  },
  "componentInstances": [
    {
      "name": "eric-oss-hello-world-python-app",
      "version": "3.1.1-0",
      "type": "ASD",
      "deployState": "DEPLOYED",
      "properties": {
        "userDefinedHelmParameters": {
          "iamBaseUrl": "https://<eic-host>",
          "logEndpoint": "<LOG_ENDPOINT>",
          "platformCaCertSecretName": "<PLATFORM_CA_CERT_SECRET>",
          "appSecretName": "<APP_MTLS_SECRET>",
          "platformCaCertFileName": "<PLATFORM_CA_CERT_FILENAME>",
          "appKeyFileName": "<APP_PRIVATE_KEY>",
          "appCertFileName": "<APP_CERTIFICATE>",
          "authenticationType": "<AUTHENTICATION_TYPE>",
          "global.clientCredentials.secret.name": "<CLIENT_SECRET>",
          "global.clientCredentials.secret.clientIdKey": "<CLIENT_ID>"
        },
        "namespace": "<namespace>",
        "timeout": 5
      }
    },
    {
      "name": "security-mgmt",
      "version": "1.0.0",
      "type": "SECURITYMANAGEMENT",
      "properties": {
        "authenticatorType": "client-x509"
      }
    }
  ],
  "events": [
    {
      "type": "DEPLOY",
      "title": "SUCCEEDED",
      "detail": "DEPLOY has successfully completed",
      "createdAt": "2025-05-31T14:04:16.297Z"
    },
    {
      "type": "DEPLOY",
      "title": "STARTED",
      "detail": "DEPLOY has started",
      "createdAt": "2025-05-31T14:04:15.609Z"
    },
    {
      "type": "CREATE",
      "title": "SUCCEEDED",
      "detail": "CREATE has successfully completed",
      "createdAt": "2025-05-31T14:01:01.753Z"
    }
  ],
  "self": {
    "href": "/app-instances/rapp-ericsson-eric-oss-hello-world-python-app-68129972"
  },
  "app": {
    "href": "/apps/rapp-ericsson-eric-oss-hello-world-python-app-3-1-1-0"
  }
}
```

To view your logs, access EIC and open your log viewer.
Within the log viewer, you can filter for App Logging and view the results.

#### Onboard the Hello World Python App APIs

Use Service Exposure to expose the Hello World App API.
For details, see [Service Exposure - Developer Guide](https://developer.intelligentautomationplatform.ericsson.net/#capabilities/service-exposure/api-exposure-developer-guide).

To create an API to be onboarded, run the following commands:

```bash
curl --cacert <PATH_TO_CA_CERTIFICATE> --location --request POST 'https://<eic-host>/hub/apiprovisioning/v1/admin/v3/apis' \
--header 'Authorization: Bearer <access-token>' \
--header 'Content-Type: application/json' \
--data '{
  "serviceCapabilityId": "hello-world-python-route-001",
  "status": "active",
  "apiPrefix": "/app/ericsson-helloWorldPythonApp",
  "apiName": "hello-world-python-route",
  "apiVersion": "v1",
  "apiCategory": "/APIGM/category/api",
  "apiDefinition": [
    {
      "operationName": "/sample-app/python/hello/GET",
      "urlPattern": "/sample-app/python/hello",
      "methods": [
        "GET"
      ]
    }
  ]
}'
```

To create an endpoint for the previously generated API, run the
following command:

```bash
curl --cacert <PATH_TO_CA_CERTIFICATE> --location --request POST 'https://<eic-host>/hub/apiprovisioning/v1/admin/v3/apis/hello-world-python-route-001/endpoints' \
--header 'Authorization: Bearer <access-token>' \
--header 'Content-Type: application/json' \
--data '{
  "endpointId": "python-hello-001",
  "serverUrl": "http://eric-oss-hello-world-python-app:8050"
}'
```

To bind the plugin for authorization of the previously
generated API, run the following command:

```bash
curl --cacert <PATH_TO_CA_CERTIFICATE> --location --request PUT 'https://<eic-host>/hub/apiprovisioning/v1/admin/v3/apis/hello-world-python-route-001/phases/auth/plugin-list' \
--header 'Authorization: Bearer <access-token>' \
--header 'Content-Type: application/json' \
--data '[
  {
    "name": "requestPartyTokenInterceptor"
  }
]'
```

To configure the binded plugin for authorization,
run the following command:

```bash
curl --cacert <PATH_TO_CA_CERTIFICATE> --location --request PUT 'https://<eic-host>/hub/apiprovisioning/v1/admin/v3/apis/hello-world-python-route-001/plugins/requestPartyTokenInterceptor/configuration' \
--header 'Authorization: Bearer <access-token>' \
--header 'Content-Type: application/json' \
--data '{
  "configurationSchemaVersion": "v0",
  "configuration": {
    "defaultResourceServer": "eo"
  }
}'
```

#### Manage access control for the Hello World Python App APIs

To allow access to the API endpoints provided by the 'Hello World' App,
Role-Based Access Control (RBAC) configuration is required. To add the
RBAC policy run the following curl command:

```bash
curl --cacert <PATH_TO_CA_CERTIFICATE> --location --request POST 'https://<eic-host>/idm/rolemgmt/v1/extapp/rbac' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer <access-token>' \
--data '{
    "tenant": "master",
  "roles": [
    {
      "name": "Python_SampleApp_Application_Administrator"
    }
  ],
  "authorization": {
    "resources": [
      {
        "name": "python_sample_app_hello",
        "type": "urn:eo:resources:extrapp",
        "ownerManagedAccess": false,
        "uris": [
          "/app/ericsson-helloWorldPythonApp/hello-world-python-route/v1/sample-app/python/hello"
        ],
        "scopes": [
          {
            "name": "PATCH"
          },
          {
            "name": "DELETE"
          },
          {
            "name": "GET"
          },
          {
            "name": "POST"
          },
          {
            "name": "PUT"
          }
        ]
      }
    ],
    "policies": [
      {
        "name": "Python Sample App Hello Policy",
        "type": "role",
        "logic": "POSITIVE",
        "decisionStrategy": "UNANIMOUS",
        "config": {
          "roles": "[{\"id\":\"Python_SampleApp_Application_Administrator\",\"required\":false}]"
        }
      },
      {
        "name": "Python Sample App Hello Permission",
        "type": "scope",
        "logic": "POSITIVE",
        "decisionStrategy": "AFFIRMATIVE",
        "config": {
          "resources": "[\"python_sample_app_hello\"]",
          "scopes": "[\"GET\",\"PUT\",\"POST\",\"DELETE\",\"PATCH\"]",
          "applyPolicies": "[\"Python Sample App Hello Policy\"]"
        }
      }
    ],
    "scopes": [
      {
        "name": "GET"
      },
      {
        "name": "POST"
      },
      {
        "name": "DELETE"
      },
      {
        "name": "PUT"
      },
      {
        "name": "PATCH"
      }
    ]
  }
}'
```

To access the `/sample-app/python/hello` endpoint, the new role
`Python_SampleApp_Application_Administrator` must be assigned to any
client accessing the endpoint.

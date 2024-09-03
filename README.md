# Hello World Python App

## Disclaimer

> ⚠️ **Important Disclaimer:**
>
> The instructions below are only applicable if you **already have full access** to the EIAP Ecosystem.
>
> If you do not have this access, **please do not proceed.**

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
Refer to: [Python on Docker™ Hub](https://hub.docker.com/_python)

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

```python
HTTP/1.1 200 OK
Date: Thu, 17 Jun 2021 14:46:46 GMT
Content-Length: 13
Content-Type: text/plain; charset=utf-8

Hello World!!
```

## Build the CSAR package

For this step, install the [App Package Tool](https://developer.intelligentautomationplatform.ericsson.net/#capabilities/app-onboarding/app-package-tool).

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

The user with the required roles is authenticated and a JSession ID is
available for accessing the required platform APIs.

For onboarding the Hello World App, the user logged into the system must
have all following permissions:

| Role                                                            | Role Description                                             |
| --------------------------------------------------------------- | ------------------------------------------------------------ |
| AppMgrAdmin                                                     | Access to App Manager onboarding and instantiating Apps.     |
| Exposure_Application_Administrator                              | Access to Service Exposure Onboarding APIs for the Apps.     |
| UserAdministration_ExtAppRbac_Application_SecurityAdministrator | Access to Service Exposure Access control APIs for the Apps. |

Use the following command to generate a valid Jsession ID:

> Contact your platform administrator for the CA certificate
required in the commands below.

```bash
curl --cacert <PATH_TO_CA_CERTIFICATE> --location --request POST 'https://<EIC_GAS_HOST>/auth/v1/login' \
--header 'X-Login: <USERNAME>' \
--header 'X-password: <PASSWORD>'
```

This command returns a JSession ID which is used in the commands in the
following steps. See the following example of JSession ID:

```c02c353a-77b8-4fae-989a-9beadf4f604c```

| Key                | Description                                                                |
|--------------------|----------------------------------------------------------------------------|
| EIC_GAS_HOST       | GUI Aggregator Service (GAS) is the EIC OSS Portal Hostname                |
| UserName           | User Name created in the IAM                                               |
| Password           | Password credential created in the IAM                                     |

### Steps for Onboarding

Onboard the **Hello World CSAR App Package** using [App Onboarding](https://developer.intelligentautomationplatform.ericsson.net/#capabilities/app-onboarding/developer-guide-use-cases).

To start the onboarding of the Hello World CSAR app,
run the following command in a bash window.

```bash
curl --cacert <PATH_TO_CA_CERTIFICATE> --location --request POST 'https://<EIC_GAS_HOST>/app-manager/onboarding/v1/apps' \
--header 'accept: application/json' \
--form 'file=@"<PATH_TO_CSAR>/helloworldAppPackage.csar"' \
--header 'Cookie: JSESSIONID=<GENERATED_JSESSION_ID>'
```

Example of command result:

```json
{
  "id": 8,
  "name": "helloworldAppPackage.csar",
  "username": "Unknown",
  "version": "1.1.1",
  "size": "100MB",
  "vendor": "Unknown",
  "type": "APP",
  "onboardedDate": "2022-08-19T11:33:03.955+00:00",
  "status": "UPLOADED",
  "mode": "DISABLED"
}
```

The id, shown in the command result, is `APP_ONBOARDING_ID`
(8 in the example). Use the `APP_ONBOARDING_ID` to get the status of
the onboarding process in the following commands:

```bash
curl --cacert <PATH_TO_CA_CERTIFICATE> --location --request GET 'https://<EIC_GAS_HOST>/app-manager/onboarding/v1/apps/<APP_ONBOARDING_ID>' \
--header 'accept: application/json' \
--header 'Cookie: JSESSIONID=<GENERATED_JSESSION_ID>'
```

It can take up to five minutes for the status to change to ONBOARDED.
Repeat the command till the status is changed to ONBOARDED.

Example of command result:

```json
{
  "id": 8,
  "name": "helloworldAppPackage.csar",
  "username": "Unknown",
  "version": "1.1.1",
  "size": "100MB",
  "vendor": "Unknown",
  "type": "APP",
  "onboardedDate": "2022-08-19T11:33:03.955+00:00",
  "status": "ONBOARDED",
  "mode": "DISABLED",
  "artifacts": [
    {
      "id": 12,
      "name": "docker.tar",
      "type": "IMAGE",
      "version": "--",
      "status": "COMPLETED",
      "location": "<app-manager-resource-location>"
    },
    {
      "id": 11,
      "name": "eric-oss-hello-world-python-app",
      "type": "HELM",
      "version": "1.0.0-0",
      "status": "COMPLETED",
      "location": "/api/eric-oss-hello-world-python-app_2.9.985/charts/eric-oss-hello-world-python-app/1.0.0-0"
    }
  ],
  "events": []
}
```

Run the following command to switch the app mode from 'DISABLED' to 'ENABLED'.

```bash
curl --cacert <PATH_TO_CA_CERTIFICATE> --location --request PUT 'https://<EIC_GAS_HOST>/app-manager/onboarding/v1/apps/<APP_ONBOARDING_ID>' \
-H 'Content-Type: application/json' \
-d '{"mode": "ENABLED"}' \
--header 'Cookie: JSESSIONID=<GENERATED_JSESSION_ID>'
```

Example of command result:

```json
{
  "id": 8,
  "name": "helloworldAppPackage.csar",
  "username": "Unknown",
  "version": "1.1.1",
  "size": "100MB",
  "vendor": "Unknown",
  "type": "APP",
  "onboardedDate": "2022-08-19T11:33:03.955+00:00",
  "status": "ONBOARDED",
  "mode": "ENABLED",
  "artifacts": [
    {
      "id": 12,
      "name": "docker.tar",
      "type": "IMAGE",
      "version": "--",
      "status": "COMPLETED",
      "location": "<app-manager-resource-location>"
    },
    {
      "id": 11,
      "name": "eric-oss-hello-world-python-app",
      "type": "HELM",
      "version": "1.0.0-0",
      "status": "COMPLETED",
      "location": "/api/eric-oss-hello-world-python-app_2.9.985/charts/eric-oss-hello-world-python-app/1.0.0-0"
    }
  ],
  "events": []
}
```

## Instantiate the App

### Prerequisites for Instantiation

- You need the JSession ID generated in **Onboard the App** prerequisite
  to access the App Manager for instantiating the Hello World CSAR App Package.
- Contact your platform administrator to generate required App key,
  certificates, and secret name in which they are stored.

### Steps for Instantiation

Use the APP LCM capability to instantiate the **Hello World CSAR App**.
For more details on this capability, see [App LCM](https://developer.intelligentautomationplatform.ericsson.net/#capabilities/app-lifecycle-management/developer-guide).

Run the following command to start the instantiation process using
the appOnboarding ID from **Onboard the App**.

```bash
curl --cacert <PATH_TO_CA_CERTIFICATE> --location --request POST 'https://<EIC_GAS_HOST>/app-manager/lcm/app-lcm/v1/app-instances' \
--header 'accept: application/json' \
--header 'Content-Type: application/json' \
-d '{"appId": <ONBOARDED_APP_ID>,
    "additionalParameters": {
        "platformSecretName": "<PLATFORM_SECRET>",
        "caCertFileName": "tls.crt",
        "caCertMountPath": "cacerts",
        "iamBaseUrl": "https://<IAM_HOST_URL>",
        "rAppLogCertsSecretName": "<APP_MTLS_SECRET>",
        "logCACertSecretName": "la-cacert-secret",
        "logEndpoint": "<LOG_ENDPOINT>",
        "rAppLogTlsKeyFileName": "<APP_PRIVATE_KEY>",
        "rAppLogTlsCertFileName": "<APP_CERTIFICATE>",
        "logTlsCACertFileName": "<LOG_AGGREGATOR_CA_CERTIFICATE>",
        "logCaFilePath": "</PATH/TO/CA/LOG/FILE/>",
        "rAppLogCertFilePath": "</PATH/TO/APP/LOG/FILE/>"
}}' \
--header 'Cookie: JSESSIONID=<GENERATED_JSESSION_ID>'
```

> All additional parameters are required for
successful instantiation of your App.

The `iamBaseUrl` is required as the `/sample-app/python/hello` endpoint of this
sample app first communicates with IAM to obtain a client token (login)
before returning the `Hello World!\n` string output.

`platformSecretName`, `caCertFileName`, and `caCertMountPath` are required to enable
secure TLS communication. See [App Certificate Provisioning Developer Guide](https://developer.intelligentautomationplatform.ericsson.net/#capabilities/app-cert-provisioning/developer-guide)
to understand how the certificates are loaded into the App during
instantiation for secure communication.

Use the prerequisites gathered from your platform administrator to
populate the additional parameters:
`rAppLogCertsSecretName`, `logCACertSecretName`, `logEndpoint`,
`rAppLogTlsKeyFileName`, `rAppLogTlsCertFileName`, `logTlsCACertFileName`.
For more information on variables values required,
see [App Logging Developer Guide to Produce logs.](https://developer.intelligentautomationplatform.ericsson.net/#capabilities/app-logging/how-to-produce-logs?chapter=identify-environment-and-secret-variables-names)

The `logCaFilePath` and `rAppLogCertFilePath` are configurable file paths to
the `CACert` and App log files respectively.

See the following example command result:

```json
{
  "id": 5,
  "appOnBoardingAppId": 8,
  "healthStatus": "PENDING",
  "targetStatus": "INSTANTIATED",
  "createdTimestamp": "2022-08-19T11:37:02.491951Z",
  "additionalParameters": "{
         \"platformSecretName\":\"iam-cacert-secret\",
         \"caCertFileName\":\"tls.crt\",
         \"caCertMountPath\":\"cacerts\",
         \"iamBaseUrl\":\"https://<IAM_HOST_URL>\",
         \"rAppLogCertsSecretName\":\"<APP_MTLS_SECRET>\",
         \"logCACertSecretName\":\"la-cacert-secret\",
         \"logEndpoint\":\"<LOG_ENDPOINT>\",
         \"rAppLogTlsKeyFileName\":\"<APP_PRIVATE_KEY>\",
         \"rAppLogTlsCertFileName\":\"<APP_CERTIFICATE>\",
         \"logTlsCACertFileName\":\"<LOG_AGGREGATOR_CA_CERTIFICATE>\",
         \"logCaFilePath\":\"</PATH/TO/CA/LOG/FILE/>\",
         \"rAppLogCertFilePath\":\"</PATH/TO/APP/LOG/FILE/>\"
}","links": [
  {
    "rel": "self",
    "href": "https://eric-oss-app-lcm/app-manager/lcm/app-lcm/v1/app-instances/5"
  },
  {
    "rel": "artifact-instances",
    "href": "https://eric-oss-app-lcm/app-manager/lcm/app-lcm/v1/app-instances/5/artifact-instances"
  },
  {
    "rel": "app",
    "href": "https://eric-oss-app-lcm/app-manager/onboarding/v1/apps/8"
  },
  {
    "rel": "artifacts",
    "href": "https://eric-oss-app-lcm/app-manager/onboarding/v1/apps/8/artifacts"
  }
]
}
```

The ID returned by the command output is the instantiation ID, in the
previous example `"id:5"`. Use the instantiation app ID in the
following command to check the instantiation status.
Repeat the command until the health status is changed
to `"healthStatus":"INSTANTIATED"`.

```bash
curl --cacert <PATH_TO_CA_CERTIFICATE> --location --request GET 'https://<EIC_GAS_HOST>/app-manager/lcm/app-lcm/v1/app-instances/<INSTANTIATION_APP_ID>' \
-H 'accept: application/json' \
-H 'Content-Type: application/json' \
--header 'Cookie: JSESSIONID=<GENERATED_JSESSION_ID>'
```

Example of command result:

```json
{
  "id": 5,
  "appOnBoardingAppId": 8,
  "healthStatus": "INSTANTIATED",
  "targetStatus": "INSTANTIATED",
  "createdTimestamp": "2022-08-19T11:37:02.491951Z",
  "additionalParameters": "{
         \"platformSecretName\":\"iam-cacert-secret\",
         \"caCertFileName\":\"tls.crt\",
         \"caCertMountPath\":\"cacerts\",
         \"iamBaseUrl\":\"https://<IAM_HOST_URL>\",
         \"rAppLogCertsSecretName\":\"<APP_MTLS_SECRET>\",
         \"logCACertSecretName\":\"la-cacert-secret\",
         \"logEndpoint\":\"<LOG_ENDPOINT>\",
         \"rAppLogTlsKeyFileName\":\"<APP_PRIVATE_KEY>\",
         \"rAppLogTlsCertFileName\":\"<APP_CERTIFICATE>\",
         \"logTlsCACertFileName\":\"<LOG_AGGREGATOR_CA_CERTIFICATE>\",
         \"logCaFilePath\":\"</PATH/TO/CA/LOG/FILE/>\",
         \"rAppLogCertFilePath\":\"</PATH/TO/APP/LOG/FILE/>\"
}","links": [
  {
    "rel": "self",
    "href": "https://eric-oss-app-lcm/app-manager/lcm/app-lcm/v1/app-instances/5"
  },
  {
    "rel": "artifact-instances",
    "href": "https://eric-oss-app-lcm/app-manager/lcm/app-lcm/v1/app-instances/5/artifact-instances"
  },
  {
    "rel": "app",
    "href": "https://eric-oss-app-lcm/app-manager/onboarding/v1/apps/8"
  },
  {
    "rel": "artifacts",
    "href": "https://eric-oss-app-lcm/app-manager/onboarding/v1/apps/8/artifacts"
  }
]
}
```

## Onboard the Hello World Python App APIs

Run the following command to onboard the Hello World App APIs.

```bash
curl --cacert <PATH_TO_CA_CERTIFICATE> --location --request POST 'https://<EIC_GAS_HOST>/v1/routes' \
--header 'Cookie: JSESSIONID=<JSESSIONID>' \
--header 'Content-Type: application/json' \
--data '{
  "id": "hello-world-python-route-001",
  "predicates": [
    {
      "name": "Path",
      "args": {
        "_genkey_0": "/sample-app/python/hello"
      }
    }
  ],
  "uri": "http://eric-oss-hello-world-python-app:8050"
}'
```

## Manage access control for the Hello World Python App APIs

To allow access to the API end points provided by the 'Hello World' App,
Role-Based Access Control (RBAC) configuration is required. To add the
RBAC policy run the following curl command.

```bash
curl --cacert <PATH_TO_CA_CERTIFICATE> --location --request POST 'https://<EIC_GAS_HOST>/idm/rolemgmt/v1/extapp/rbac' \
--header 'Content-Type: application/json' \
--header 'Cookie: JSESSIONID=<GENERATED_JSESSION_ID>' \
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
          "/sample-app/python/hello"
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
user accessing the endpoint.

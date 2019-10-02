# Cerberus | The Secrets Guardian

This project is a simple (for now) secrets manager.
It was named after Cerberus, the guardian of the entrance to hell. Now, its gonna guard your passwords either.

This project is based on a serverless infrastructure, which make it pretty more cheap on the cloud and easy to manage.

## How to use it

To make a proper use of this project, you need an aws account, an iam profile with access to the resources created by this project, and serverless framework.

First things first.

1. Install serverless by running:
```
npm install -g serverless
```

2. Clone this repo
```
git clone https://github.com/Caduedu14/cerberus
```

3. Cd to the cloned repo, and install the dependencies by executing:
```
npm install
```

4. After installing, you will need a user with some specific permissions. To do it, you can run the script located on root of this project.

    You can do it using an existing user by running:

    ```shell
    python configure_permissions.py --new-user
    ```
    Or with an existing user:
    ```bash
    python confgure_permission.py --user {username}
    ```
5. After your user is properly configured with the necessary permissions, just deploy the project with:
```bash
serverless deploy --profile {configured_user_profile}
```

This project uses a serverless plugin to configure domains managers for api gateway, however, its disabled by default. To enable it, simply modify the variables.yaml file and set enable_custom_domain to `true`. And configure the other dependent variables (`domain_name`, `certificate_name`, `create_route53_record`, `endpoint_type`).

## Provisioned resources
When you deploy this project, you will have to following resources on your aws account:
- An Api Gateway with 2 endpoints:
  - /get_secret
  - /add_secret

- An Api Gateway UsagePlan key

- If `enable_custom_domain = true` it will generate:
  - A domain for Api Gateway
  - Route 53 records (if enabled)


- 4 lambda functions:
  - get_secret
  - add_secret
  - encrypt_secret
  - decrypt_secret

- An IAM role with the lambdas permissions
- A DynamoDB table for storing the passwords
- A KMS Key to protect your passwords
- A KMS alias key

# Recomendation

To use this project in its best, I recommend you to use the [`cerberus-cli](https://github.com/Caduedu14/cerberus-cli) project which is gonna give you a pretty command line interface to use this project using your linux terminal.

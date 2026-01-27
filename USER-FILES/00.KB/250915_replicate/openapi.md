Replicate’s public HTTP API documentation is available as a machine-readable OpenAPI schema in JSON format.

Download the schema at [**api.replicate.com/openapi.json**](https://api.replicate.com/openapi.json)

[](#what-is-openapi)What is OpenAPI?
------------------------------------

OpenAPI (formerly known as Swagger) is a specification for describing the structure of HTTP APIs, including all their endpoints, HTTP methods, input parameters, request and response formats, and other metadata.

OpenAPI schemas are useful as raw reference material when learning about an API, but they’re also great for dynamically generating client libraries, [reference documentation](/docs/reference/http), tests, and tools for interacting with HTTP APIs.

OpenAPI is also the industry-standard format for AI [function calling](https://docs.anthropic.com/en/docs/build-with-claude/tool-use) (also called “tool use”), which enables products like [Anthropic Claude](https://github.com/anthropics/anthropic-cookbook/blob/main/tool_use/extracting_structured_json.ipynb) and [OpenAI GPT Actions](https://platform.openai.com/docs/actions/actions-library) to auto-discover the structure of HTTP APIs and interact with them dynamically.

[](#exploring-the-schema)Exploring the schema
---------------------------------------------

Here’s an example using cURL and [jq](https://jqlang.github.io/jq/) to print all the API paths in your terminal:

```shell
curl -s https://api.replicate.com/openapi.json | jq -r '.paths | keys[]'
/account
/collections
/collections/{collection_slug}
/deployments
/deployments/{deployment_owner}/{deployment_name}
/deployments/{deployment_owner}/{deployment_name}/predictions
/hardware
/models
/models/{model_owner}/{model_name}
/models/{model_owner}/{model_name}/predictions
/models/{model_owner}/{model_name}/versions
/models/{model_owner}/{model_name}/versions/{version_id}
/models/{model_owner}/{model_name}/versions/{version_id}/trainings
/predictions
/predictions/{prediction_id}
/predictions/{prediction_id}/cancel
/trainings
/trainings/{training_id}
/trainings/{training_id}/cancel
/webhooks/default/secret
```

[](#dereferencing)Dereferencing
-------------------------------

OpenAPI schemas are written in [JSON Schema](https://json-schema.org/), a format which allows you to have multiple references to the same object (see [`$ref`](https://json-schema.org/understanding-json-schema/structuring#dollarref)). References are great for keeping the schema DRY (Don’t Repeat Yourself), but they can make the schema a bit harder to read and use as a consumer.

To make the schema easier to work with, it’s helpful to “dereference” it. This means replacing all the references with the actual objects.

Here’s an example of how `$ref`s appear in the schema:

```json
{
  "parameters": [
    {
      "$ref": "#/components/parameters/prefer_header"
    }
  ],
}
```

And here’s what that same object looks like after dereferencing:

```json
{
  "parameters": [
    {
      "prefer_header": {
        "description": "Leave the request open and wait for the model to finish generating output.",
        "in": "header",
        "name": "Prefer",
        "schema": {
          "example": "wait=5",
          "pattern": "^wait(=([1-9]|[1-9][0-9]|60))?$",
          "type": "string"
        }
      }
    }
  ]
}
```

There are many open-source libraries for dereferencing OpenAPI schemas.

Here’s some example code showing how to dereference Replicate’s OpenAPI schema using Node.js and the popular and well-maintained [@apidevtools/json-schema-ref-parser](https://www.npmjs.com/package/@apidevtools/json-schema-ref-parser) npm package:

```js
import $RefParser from "@apidevtools/json-schema-ref-parser";
const res = await fetch("https://api.replicate.com/openapi.json");
const rawSchema = await res.json();
const dereferencedSchema = await $RefParser.dereference(rawSchema);
console.log(dereferencedSchema);
```

That will print the entire dereferenced schema to the console:

```js
{
  externalDocs: {
    description: 'Replicate HTTP API',
    url: 'https://replicate.com/docs/reference/http'
  },
  openapi: '3.1.0',
  paths: {
    '/account': { get: [Object] },
    '/collections': { get: [Object] },
    '/collections/{collection_slug}': { get: [Object] },
    '/deployments': { get: [Object], post: [Object] },
    '/deployments/{deployment_owner}/{deployment_name}': { delete: [Object], get: [Object], patch: [Object] },
    '/deployments/{deployment_owner}/{deployment_name}/predictions': { post: [Object] },
    '/hardware': { get: [Object] },
    '/models': { get: [Object], post: [Object], query: [Object] },
    '/models/{model_owner}/{model_name}': { delete: [Object], get: [Object] },
    '/models/{model_owner}/{model_name}/predictions': { post: [Object] },
    '/models/{model_owner}/{model_name}/versions': { get: [Object] },
    '/models/{model_owner}/{model_name}/versions/{version_id}': { delete: [Object], get: [Object] },
    '/models/{model_owner}/{model_name}/versions/{version_id}/trainings': { post: [Object] },
    '/predictions': { get: [Object], post: [Object] },
    '/predictions/{prediction_id}': { get: [Object] },
    '/predictions/{prediction_id}/cancel': { post: [Object] },
    '/trainings': { get: [Object] },
    '/trainings/{training_id}': { get: [Object] },
    '/trainings/{training_id}/cancel': { post: [Object] },
    '/webhooks/default/secret': { get: [Object] }
  },
  security: [ { bearerAuth: [] } ],
  servers: [ { url: 'https://api.replicate.com/v1' } ]
}
```

[](#model-schemas)Model schemas
-------------------------------

Every model on Replicate also has its own API schema.

You can programmatically fetch the full input and output schema for any Replicate model using the [`models.get`](/docs/reference/http#operation/models.get) API endpoint.

Here’s an example using cURL and [jq](https://jqlang.github.io/jq/) to print the input schema for the [black-forest-labs/flux-schnell](https://replicate.com/black-forest-labs/flux-schnell) model:

```shell
curl -s \
  -H "Authorization: Bearer $REPLICATE_API_TOKEN" \
  https://api.replicate.com/v1/models/black-forest-labs/flux-schnell \
  | jq .latest_version.openapi_schema.components.schemas.Input.properties
```

And here’s the output:

```json
{
  "seed": {
    "type": "integer",
    "title": "Seed",
    "x-order": 3,
    "description": "Random seed. Set for reproducible generation"
  },
  "prompt": {
    "type": "string",
    "title": "Prompt",
    "x-order": 0,
    "description": "Prompt for generated image"
  },
  "go_fast": {
    "type": "boolean",
    "title": "Go Fast",
    "default": true,
    "x-order": 7,
    "description": "Run faster predictions with model optimized for speed (currently fp8 quantized); disable to run in original bf16"
  },
  "megapixels": {
    "allOf": [
      {
        "$ref": "#/components/schemas/megapixels"
      }
    ],
    "default": "1",
    "x-order": 8,
    "description": "Approximate number of megapixels for generated image"
  },
  "num_outputs": {
    "type": "integer",
    "title": "Num Outputs",
    "default": 1,
    "maximum": 4,
    "minimum": 1,
    "x-order": 2,
    "description": "Number of outputs to generate"
  },
  "aspect_ratio": {
    "allOf": [
      {
        "$ref": "#/components/schemas/aspect_ratio"
      }
    ],
    "default": "1:1",
    "x-order": 1,
    "description": "Aspect ratio for the generated image"
  },
  "output_format": {
    "allOf": [
      {
        "$ref": "#/components/schemas/output_format"
      }
    ],
    "default": "webp",
    "x-order": 4,
    "description": "Format of the output images"
  },
  "output_quality": {
    "type": "integer",
    "title": "Output Quality",
    "default": 80,
    "maximum": 100,
    "minimum": 0,
    "x-order": 5,
    "description": "Quality when saving the output images, from 0 to 100. 100 is best quality, 0 is lowest quality. Not relevant for .png outputs"
  },
  "disable_safety_checker": {
    "type": "boolean",
    "title": "Disable Safety Checker",
    "default": false,
    "x-order": 6,
    "description": "Disable safety checker for generated images."
  }
}
```

To learn more about how Replicate model interfaces are defined, see the [Cog documentation](https://cog.run/python).
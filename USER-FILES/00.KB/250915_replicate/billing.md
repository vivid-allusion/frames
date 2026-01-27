[](#billing)Billing
-------------------

For accounts that are billed via prepaid credit, you’ll first purchase credit and any usage deducts from your credit balance. To learn more, see our page on [prepaid credit](https://replicate.com/docs/topics/billing/prepaid-credit).

For accounts that are billed in arrears, at the beginning of the month we’ll charge you for your usage from the previous month.

Sometimes, if your usage crosses certain limits for the first time, we’ll charge you early. This helps us catch fraud before it becomes a problem. If that happens, we’ll email you a receipt right away using the email address configured when you set up billing. The amount will show up as a credit on your next invoice.

To view and configure your billing email address, go to the [billing settings](https://replicate.com/account/billing) page and click **Manage billing**.

You can find your current usage and manage your billing settings on your [account page](https://replicate.com/account/billing).

[](#lifecycle-of-an-instance)Lifecycle of an instance
-----------------------------------------------------

Offline

Offline

TypeDuration

*   Setup time
    
    0.0s
*   Active time
    
    0.0s
*   Idle time
    
    0.0s

Offline

When a model isn’t under demand, we scale it down to the minimum number of instances set (0 by default - you can customize this for deployments).

Setting up

When requests start to come in for a model, or the request volume is too high for the model's current scale to cope with, we set up an instance (up to a maximum - you can customize this for deployments). This can take a few seconds as we perform setup work like downloading weights.

Active

Once the model instance has finished setting up, it can start processing the queue of requests.

Idle

When there's a gap in requests, the instance will go idle for a few minutes rather than shutting down immediately, so it can stay responsive and avoid needing to set up from scratch every time.

[](#public-models)Public models
-------------------------------

When you use a public model on Replicate, you only pay for the time it’s active processing your requests. Setup and idle time for the model is free.

By default, you share a hardware pool with other customers, meaning your requests enter a shared queue alongside other customer requests. This means you will sometimes encounter [cold boots](https://replicate.com/docs/how-does-replicate-work#cold-boots) or scaling limits depending on how other customers are using the model.

If you would like more control over how the model is run, you can use a [deployment](https://replicate.com/docs/deployments) and have your own instances and request queue.

[](#private-models)Private models
---------------------------------

Unlike public models, most private models (with the exception of [fast booting fine-tunes](#fast-booting-fine-tunes)) run on dedicated hardware and you don’t have to share a queue with anyone else. This means you pay for all the time instances of the model are online: the time they spend setting up; the time they spend idle, waiting for requests; and the time they spend active, processing your requests.

As with public models, if you would like more control over how a private model is run, you can use a [deployment](https://replicate.com/docs/deployments).

Here’s an example using [Meta’s Llama 3.1 405B Instruct](https://replicate.com/meta/meta-llama-3.1-405b-instruct):

Tokens

Count

Price

Input

Write a limerick about llamas

8

$0.0000760

Output

There once was a llama named Sue,\\n  
Whose favorite color was blue,\\n  
She lived in the Andes,\\n  
With her friends eating candies\\n  
And together they all played kazoo.

43

$0.0004085

Total

51

$0.0004845

[](#models-that-call-other-models)Models that call other models
---------------------------------------------------------------

When you run a model that calls other models, you’re billed for the compute time of the root model and for any downstream models it calls. You can view the list of downstream models in the model’s Pricing section.

If the model fails, you will be billed for the duration of the run, plus the cost of the downstream models that were called before the failure occurred.

[](#fast-booting-fine-tunes)Fast booting fine-tunes
---------------------------------------------------

Sometimes, we’re able to optimize how a trained model is run so it boots fast. This works by using a common, shared pool of hardware running a base model. In these cases, we only ever charge you for the time the model is active and processing your requests, regardless of whether or not it’s public or private.

Fast booting fine-tunes are labeled as such in the model’s version list. You can also see which versions support the creation of fast booting models when training.

[](#deployments)Deployments
---------------------------

[Deployments](https://replicate.com/docs/deployments) are a feature that allow you to, among other things, control the hardware and scaling parameters of any model. Like with private models, we charge for all the time deployment instances are online: the time they spend setting up; the time they spend idle, waiting for requests; and the time they spend active, processing your requests.

In addition to the benefits of having a stable endpoint and graceful rollouts of versions, you might want to use a deployment if, for example:

*   you want to configure a public model owned by someone else to run on different hardware
*   you have steady use of a model and want to avoid being impacted by other customers using it
*   you know your expected request rate and want to avoid cold boots
*   you have a private model with a consistent, predictable request rate

Note that well-tuned deployments are usually only marginally more expensive than public models, because, despite paying for setup and idle time for deployment instances, when configured correctly, they should only be setting up or idle for a fraction of the time they’re active.

[](#failed-and-canceled-runs)Failed and canceled runs
-----------------------------------------------------

For all models, if a run fails, we don’t charge you. If you cancel a run for an official model, you may still be charged. For models that charge based on time, we charge you for the time it ran up until that point.

For private models and deployments, failed and canceled runs are billed for the time the instances they ran on were active, as normal.

[](#hardware)Hardware
---------------------

Different models run on different hardware. You’ll find the hardware specifications under the “Run time and cost” heading on each model’s page. Check out [stability-ai/sdxl](https://replicate.com/stability-ai/sdxl#performance) for an example.

If a model is one you created on Replicate, you can adjust which hardware to use in the model’s settings. You can also specify hardware for a deployment.

[](#free-limits)Free limits
---------------------------

You can run [select models](https://replicate.com/collections/try-for-free) on Replicate for free, but after a bit you’ll be asked to set up billing.

Some features are only available to customers with billing set up.
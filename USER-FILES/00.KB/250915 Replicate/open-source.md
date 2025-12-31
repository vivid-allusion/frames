![So many packages...](/_content/assets/open-source.DPD6bhkU_ZcFpPt.webp)

Open-source is a big deal at Replicate.

One of our goals as a team has always been to help unlock the power of machine learning by building flexible and well-designed open-source tools. We’re motivated by the experimentation and innovation that happens when ideas can grow beyond the confines of academic papers and take life as reproducible, open-source code.

This page highlights some of the open-source projects and tools we maintain. For the full list, see the [@replicate](https://github.com/replicate) organization on GitHub.

[](#api-client-libraries)API client libraries
---------------------------------------------

SDKs for working with Replicate’s [HTTP API](/docs/reference/http).

[replicate/replicate-javascript](https://github.com/replicate/replicate-javascript) -  Node.js client for the Replicate API with ESM and CommonJS support. Works on multiple runtimes like Node.js, Bun, and Deno, and serverless platforms like CloudFlare Workers, Vercel functions, and AWS Lambda.

[replicate/replicate-python](https://github.com/replicate/replicate-python) -  Python client for the Replicate API that lets you run models from your Python code, Jupyter notebooks, and Google Colab.

[replicate/replicate-go](https://github.com/replicate/replicate-go) -  Go client. It lets you run models from your Golang code, and everything else you can do with Replicate's HTTP API.

[replicate/replicate-swift](https://github.com/replicate/replicate-swift) -  Swift client. Use it to build apps for iOS, macOS, visionOS, tvOS, and watchOS.

[](#building-models)Building models
-----------------------------------

The tools we use to define, package, and continuously deploy models on Replicate.

[replicate/cog](https://github.com/replicate/cog) -  Containers for machine learning. Cog provides a Go CLI and Python API for defining and packaging machine learning models in standard, production-ready Docker containers. Every model you run on Replicate is packaged with Cog.

[replicate/cog-safe-push](https://github.com/replicate/cog-safe-push) -  Safely push new versions of your Cog model by making sure it works and is backwards-compatible with previous versions.

[replicate/setup-cog](https://github.com/replicate/setup-cog) -  A GitHub Action for Cog so you can run, test, and push models as part of your CI/CD pipeline.

[andreasjansson/autocog](https://github.com/andreasjansson/autocog) -  Simplify the process of creating Cog models by using GPT-4 to generate predict.py and cog.yaml automatically.

[replicate/pget](https://github.com/replicate/pget) -  High-performance concurrent file downloader built in Go. Useful for parallelized downloads of huge weights files.

[replicate/cli](https://github.com/replicate/cli) -  The official command-line interface for Replicate.

[](#running-models)Running models
---------------------------------

Open-source tools created and maintained by Replicate staff.

[zeke/all-the-public-replicate-models](https://github.com/zeke/all-the-public-replicate-models) -  A daily-updated npm package containing metadata for all public Replicate models.

[ai-prompts/prompt-lists](https://github.com/ai-prompts/prompt-lists) -  Lists to generate prompts.

[fofr/prompter.fofr.ai](https://github.com/fofr/prompter.fofr.ai) -  An app for generating text prompts.

[fofr/replicate-predict](https://github.com/fofr/replicate-predict) -  A JavaScript wrapper to run and save batches of API calls on Replicate.

[pwntus/replicate-webhook-proxy](https://github.com/pwntus/replicate-webhook-proxy) -  Receive Replicate webhook events through a websocket connection, right in your browser or Node.js code.

[zeke/aimg](https://github.com/zeke/aimg) -  Generate AI images with Replicate and save them to disk.

[zeke/ml-ipsum](https://github.com/zeke/ml-ipsum) -  Lorem ipsum meets machine learning. False positive rate velit elit prediction aute id. Serving officia excepteur hyperplane.

[zeke/promptmaker](https://github.com/zeke/promptmaker) -  Generate random artistic text prompts for generative models.

[zeke/yolox](https://github.com/zeke/yolox) -  Use language models to write one-line shell commands.

[](#boilerplates)Boilerplates
-----------------------------

Starter projects and templates to help you quickly begin developing apps using Replicate.

[replicate/cog-examples](https://github.com/replicate/cog-examples) -  Example models built with Cog.

[replicate/create-replicate](https://github.com/replicate/create-replicate) -  A Node.js CLI that works with npx to quickly spin up projects for running models with Replicate's API.

[replicate/getting-started-nextjs](https://github.com/replicate/getting-started-nextjs) -  Example app that demonstrates how to use Replicate's API with Next.js. Uses Next.js App Router, React Server Components, and illustrates how to use webhooks with Replicate.

[replicate/llama-chat](https://github.com/replicate/llama-chat) -  Example app that demonstrates how to use Replicate's API with Next.js.

[](#demo-apps)Demo apps
-----------------------

Example apps showing common patterns for using Replicate’s API.

[replicate/kontext-realtime](https://github.com/replicate/kontext-realtime) -  Create and edit images with voice commands.

[replicate/ideogram-inpainting-example-js](https://github.com/replicate/ideogram-inpainting-example-js) -  Node.js demo app for inpainting images using Ideogram.

[replicate/green-screen-creator](https://github.com/replicate/green-screen-creator) -  Track an object in a video and add a green screen to the background.

[replicate/reflux](https://github.com/replicate/reflux) -  Image editor for combining multiple LoRA fine-tunes.

[fofr/waveformer](https://github.com/fofr/waveformer) -  Text to music using MusicGen.

[replicate/quirky](https://github.com/replicate/quirky) -  Make really cool QR codes with AI.

[replicate/inpainter](https://github.com/replicate/inpainter) -  Remove objects from images.

[replicate/outpainter](https://github.com/replicate/outpainter) -  Expand the contents of an image using generative fill.

[replicate/zoo](https://github.com/replicate/zoo) -  Compare image models like SDXL, Stable Diffusion, and DALL-E.

[replicate/scribble-diffusion](https://github.com/replicate/scribble-diffusion) -  Turn your sketch into a refined image using AI.

[replicate/tilemaker](https://github.com/replicate/tilemaker) -  Make your next wallpaper with tiled stable diffusion.

[replicate/paint-by-text](https://github.com/replicate/paint-by-text) -  Edit your photos using written instructions, with the help of an AI.

[replicate/replicate-support-bot](https://github.com/replicate/replicate-support-bot) -  A Discord bot that answers questions about Replicate.

[](#flux)Flux
-------------

Tools for working with [Flux](https://replicate.com/black-forest-labs), the state-of-the-art open-source image generation model from Black Forest Labs.

[replicate/cog-flux](https://github.com/replicate/cog-flux) -  Inference code for Flux Schnell and Flux Dev.

[replicate/flux-fine-tuner](https://github.com/replicate/flux-fine-tuner) -  Fine-tuning code for Flux.

[zeke/flux-fine-tune-action](https://github.com/zeke/flux-fine-tune-action) -  GitHub Actions workflow for fine-tuning Flux. Store your training data in a GitHub repo and train a custom version of Flux.

[replicate/reflux](https://github.com/replicate/reflux) -  Flux LoRA image editor built on Nuxt
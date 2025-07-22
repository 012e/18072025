# Project Reflection

## Your overall concept understanding of the project

We are creating a customer support chatbot by utilizing existing documentation and applying the RAG technique.

## The approach and solution you chose, and why

I will split this answer into mutliple parts

### Scraping

For getting data from the support site, I can either use a library or create my own api wrapper. But I decided to go with the latter since:
1. The libraries don't have async api which is very slow for our purpose (scraping a massive amount of data)
2. There are only 3 endpoints to scrape (categories, sections, and articles) which should be fairly quick to implement.

For converting article body from html to markdown I decided to use [markdownify](https://github.com/matthewwithanm/python-markdownify). I do not want to write my own algorithm when there are other well-maintained libraries available.

### Uploading

I try to use async APIs as much as possible, since uploading the documents sequentially is fairly slow. I initially tried to use batch uploading support from the OpenAI Python SDK, but more than half of the uploads failed, so I implemented my own batch upload solution.

### Syncing changes

I had to use redis to persist the article ids alongside their hash to avoid reuploading the whole collection every time I redeploy.


## How do you learn something new like this if you haven’t learned it before

To learn new things, there are many possible approaches that I use:

1. Read the official framework/library documentation to extract as much crucial information as possible.
2. Ask LLMs for simple questions.
3. For more in depth understanding of the technology I would listen to talks or read books on related topics (e.g. I consider Spring Framework or ASP.NET Core to be very complex and I have spent quite some times reading books on these topics).

## Your thoughts, suggestions on how OptiBots can be improved, what potential challenges you think we will be facing

There are many problems with my current implementation/design that could be furthermore improved:

### Using OpenAI's service

There are quite a few issues I encountered when using OpenAI's assistants and vector store API.
- **Being vendor lock-in**: Our application will need massive refactoring/rewrite to change to another provider.
- **Cumbersome developer experience**: The features are incomplete: no endpoints to update a vector by ID, no endpoints for searching assistants/vector store using their name, etc
- **Performance**: It literally takes seconds for a single query to complete.

To mitigate those issues we can **deploy our own vector database**: For project of such small scale, we can just store the vector straight inside our relational databases (e.g. PostgreSQL with pgvector, or just [sqlite](https://turso.tech/vector)).

### Python as the programming language of choice

Python is notoriously bad for parallel processing because of the GIL. If we need to scrape and process more data I would recommend switching to another programming language like Go or Java.

### Deployment

I currently deploy the application on DigitalOcean, using the cheapest plan that costs $5 a month for a service that only runs once every 2 hours. 
We can possibly reduce the cost down to $0 using serverless platforms that support proper cronjobs.
